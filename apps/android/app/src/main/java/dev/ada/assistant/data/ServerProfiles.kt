package dev.ada.assistant.data

import android.content.Context
import java.net.URI
import java.net.UnknownHostException
import java.io.IOException
import java.io.InterruptedIOException
import javax.net.ssl.SSLException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import okhttp3.HttpUrl
import okhttp3.HttpUrl.Companion.toHttpUrlOrNull
import okhttp3.OkHttpClient
import okhttp3.Request
import java.util.concurrent.TimeUnit

/** Parse the original path before HttpUrl normalizes dot segments or backslashes. */
fun serverOrigin(value: String, allowDebugHttp: Boolean = false): HttpUrl? = try {
    val raw = value.trim()
    require(raw.length <= 2048)
    val uri = URI(raw)
    val url = raw.toHttpUrlOrNull()
    if (url == null || raw.contains('\\') || raw.any { it.isISOControl() } ||
        uri.rawUserInfo != null || uri.rawQuery != null || uri.rawFragment != null ||
        uri.rawPath !in listOf(null, "", "/") || url.port == 0 ||
        url.username.isNotEmpty() || url.password.isNotEmpty() ||
        (url.scheme != "https" && !(allowDebugHttp && url.scheme == "http" && url.host in ConnectionCredential.debugHttpHosts))) null
    else url
} catch (_: Exception) { null }

@Serializable
data class ServerProfile(val label: String, val origin: String) {
    companion object {
        fun parse(label: String, origin: String): ServerProfile? {
            if (label.any { it.isISOControl() } || label.trim().length !in 1..40 || origin.trim().length > 512) return null
            return serverOrigin(origin)?.let { ServerProfile(label.trim(), it.toString()) }
        }
    }
}

@Serializable private data class ServerAddress(val version: Int, val label: String, val origin: String)

/** Metadata only: no credential, selected identity, auto-connect flag or trust override. */
object ServerProfiles {
    private val json = Json { ignoreUnknownKeys = false }
    fun decodeImport(value: String): ServerProfile? = try {
        if (value.length > 2048) null else {
            val address = json.decodeFromString<ServerAddress>(value)
            if (address.version != 1) null else ServerProfile.parse(address.label, address.origin)
        }
    } catch (_: Exception) { null }
    fun encodeImport(profile: ServerProfile): String {
        require(ServerProfile.parse(profile.label, profile.origin) == profile)
        return json.encodeToString(ServerAddress(1, profile.label, profile.origin))
    }
    fun decodeSaved(value: String): List<ServerProfile> = try {
        if (value.length > 24_576) emptyList() else json.decodeFromString<List<ServerProfile>>(value).also { list ->
            require(list.size <= 12 && list.map { it.origin }.distinct().size == list.size)
            require(list.all { ServerProfile.parse(it.label, it.origin) == it })
        }
    } catch (_: Exception) { emptyList() }
    fun encodeSaved(profiles: List<ServerProfile>): String {
        val value = json.encodeToString(profiles)
        require(decodeSaved(value) == profiles)
        return value
    }
}

class ServerProfilePreferences(context: Context) {
    private val preferences = context.applicationContext.getSharedPreferences("server-addresses", Context.MODE_PRIVATE)
    fun load(): List<ServerProfile> = runCatching { ServerProfiles.decodeSaved(preferences.getString("profiles", "[]") ?: "[]") }.getOrDefault(emptyList())
    fun save(profiles: List<ServerProfile>): Boolean = runCatching {
        preferences.edit().putString("profiles", ServerProfiles.encodeSaved(profiles)).commit()
    }.getOrDefault(false)
}

fun connectionFailure(error: IOException): ApiFailure = when (error) {
    is SSLException -> ApiFailure.Tls
    is UnknownHostException -> ApiFailure.Dns
    is InterruptedIOException -> ApiFailure.Timeout
    else -> ApiFailure.Unreachable
}

/** No Authorization header/cookie. Standard platform trust/hostname checks are never relaxed. */
class HttpServerProbe {
    private val client = OkHttpClient.Builder().followRedirects(false).followSslRedirects(false)
        .retryOnConnectionFailure(false).callTimeout(10, TimeUnit.SECONDS).build()
    suspend fun check(origin: HttpUrl): ApiResult<Unit> = withContext(Dispatchers.IO) {
        try {
            client.newCall(Request.Builder().url(origin.newBuilder().addPathSegments("health/ready").build())
                .header("Accept", "application/json").header("Cache-Control", "no-store").build()).execute().use { response ->
                if (response.code in listOf(502, 504)) return@withContext ApiResult.Failure(ApiFailure.Unreachable)
                if (response.code !in listOf(200, 503)) return@withContext ApiResult.Failure(ApiFailure.IncompatibleContract)
                if (response.header("Content-Type")?.substringBefore(';')?.trim()?.lowercase() != "application/json")
                    return@withContext ApiResult.Failure(if (response.code == 503) ApiFailure.Http(503) else ApiFailure.IncompatibleContract)
                val body = response.body ?: return@withContext ApiResult.Failure(ApiFailure.IncompatibleContract)
                val bytes = ByteArray(1025)
                var size = 0
                body.byteStream().use { input ->
                    while (size < bytes.size) {
                        val count = input.read(bytes, size, bytes.size - size)
                        if (count == -1) break
                        size += count
                    }
                }
                if (size > 1024) return@withContext ApiResult.Failure(if (response.code == 503) ApiFailure.Http(503) else ApiFailure.IncompatibleContract)
                val payload = runCatching { adaJson.parseToJsonElement(String(bytes, 0, size, Charsets.UTF_8)).jsonObject }.getOrNull()
                if (response.code == 503) return@withContext ApiResult.Failure(
                    if (payload?.get("detail")?.jsonPrimitive?.content == "database_not_ready") ApiFailure.ServerNotReady else ApiFailure.Http(503))
                if (payload == null) return@withContext ApiResult.Failure(ApiFailure.IncompatibleContract)
                if (payload["status"]?.jsonPrimitive?.content != "ready" || payload["schema"]?.jsonPrimitive?.content?.matches(Regex("[0-9]{4}")) != true)
                    return@withContext ApiResult.Failure(ApiFailure.IncompatibleContract)
                ApiResult.Success(Unit)
            }
        } catch (error: IOException) { ApiResult.Failure(connectionFailure(error)) }
        catch (_: Exception) { ApiResult.Failure(ApiFailure.IncompatibleContract) }
    }
}
