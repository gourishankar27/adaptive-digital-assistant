package dev.ada.assistant

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import dev.ada.assistant.audio.*
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import android.os.SystemClock
import java.nio.ByteBuffer
import java.nio.ByteOrder
import androidx.test.core.app.ActivityScenario
import androidx.core.content.ContextCompat
import android.content.Intent
import android.media.*
import dev.ada.assistant.data.SessionIdentity
import java.util.UUID

/** Real pinned JNI/model execution on public synthetic/test words. No server credentials. */
@RunWith(AndroidJUnit4::class)
class PrivateVoiceNativeTest {
    private fun publicAudio():FloatArray {
        val raw=InstrumentationRegistry.getInstrumentation().context.assets.open("speech-public.wav").use { it.readBytes() }
        val pcm=ByteBuffer.wrap(raw).order(ByteOrder.LITTLE_ENDIAN)
        var start=12; var length=0
        while(start+8<=raw.size) {
            val size=pcm.getInt(start+4)
            if(String(raw,start,4,Charsets.US_ASCII)=="data") {length=size; start+=8; break}
            start+=8+size+(size%2)
        }
        require(length>0 && length<=raw.size-start)
        return FloatArray(length/2) {pcm.getShort(start+it*2)/32768f}
    }
    private fun runtime(): LocalSpeechRuntime {
        val r=LocalSpeechFactory.create(InstrumentationRegistry.getInstrumentation().targetContext)
        assumeTrue("Optional speech evaluation bundle required",r.available)
        r.install(); assertTrue(r.installed); return r
    }
    @Test fun publicAsrAndKeywordModelsExecuteLocally() {
        val r=runtime()
        val raw=InstrumentationRegistry.getInstrumentation().context.assets.open("speech-public.wav").use { it.readBytes() }
        val pcm=ByteBuffer.wrap(raw).order(ByteOrder.LITTLE_ENDIAN)
        var start=12; var length=0
        while(start+8<=raw.size) {
            val size=pcm.getInt(start+4)
            if(String(raw,start,4,Charsets.US_ASCII)=="data") { length=size; start+=8; break }
            start+=8+size+(size%2)
        }
        require(length>0 && length<=raw.size-start)
        val samples=FloatArray(length/2) { pcm.getShort(start+it*2)/32768f }
        val began=SystemClock.elapsedRealtime()
        var words=""
        r.recognizer().use { decoder ->
            var offset=0
            while(offset<samples.size) { val end=minOf(offset+320,samples.size); decoder.accept(samples.copyOfRange(offset,end)); while(decoder.ready()) decoder.decode(); offset=end }
            decoder.accept(FloatArray(8000)); decoder.finish(); while(decoder.ready()) decoder.decode(); words=decoder.text()
        }
        assertTrue("Public speech must produce actual model words",words.isNotBlank())
        r.wakeDetector().use { detector -> assertFalse(detector.accept(FloatArray(16000))) }
        val elapsed=SystemClock.elapsedRealtime()-began
        InstrumentationRegistry.getInstrumentation().sendStatus(0,android.os.Bundle().apply { putLong("native_asr_elapsed_ms",elapsed); putInt("recognized_characters",words.length) })
        samples.fill(0f)
    }
    @Test fun feminineNeuralVoiceProducesBoundedAudioAndRecognizesHelloAda() {
        val r=runtime()
        val began=SystemClock.elapsedRealtime()
        var samples=FloatArray(0)
        r.synthesizer().use { engine ->
            assertEquals(24000,engine.sampleRate)
            samples=engine.generate("Hello Ada",1,1f) { false }
            assertTrue(samples.size in 2400..240000)
            assertTrue(samples.any { kotlin.math.abs(it)>.005f })
        }
        // 24kHz -> 16kHz test resampling. Detector sees only the chosen public wake phrase.
        val converted=FloatArray(samples.size*2/3) { i -> samples[(i*3/2).coerceAtMost(samples.lastIndex)] }
        var detected=false
        r.wakeDetector().use { detector ->
            for(i in converted.indices step 320) if(detector.accept(converted.copyOfRange(i,minOf(converted.size,i+320)))) detected=true
            for(i in 0..100) if(detector.accept(FloatArray(320))) detected=true
        }
        InstrumentationRegistry.getInstrumentation().sendStatus(0,android.os.Bundle().apply { putLong("neural_wake_elapsed_ms",SystemClock.elapsedRealtime()-began); putInt("audio_samples",samples.size); putBoolean("synthetic_wake_detected",detected) })
        assertTrue("Pinned Hello Ada tokens must detect the public synthetic phrase",detected)
        samples.fill(0f); converted.fill(0f)
    }
    @Test fun acceleratedTwoTenAndThirtyMinuteStreamsPreserveEveryPublicSegment() {
        val r=runtime(); val phrase=publicAudio(); val silence=FloatArray(320)
        for(minutes in listOf(2,10,30)) {
            val transcript=ContinuousTranscript(); var frames=0L
            val began=SystemClock.elapsedRealtime(); val before=android.os.Debug.getPss()
            r.recognizer().use {decoder ->
                repeat(minutes*2) {
                    // Thirty seconds per block, including a >20s silent pause. Feed
                    // accelerated model input, NOT a claim of microphone endurance.
                    for(offset in 0 until 30*16000 step 320) {
                        val block=if(offset<phrase.size) phrase.copyOfRange(offset,minOf(offset+320,phrase.size)) else silence
                        decoder.accept(block); frames+=block.size
                        while(decoder.ready()) decoder.decode()
                        if(decoder.endpoint()) {transcript.commit(decoder.text(),frames*1000/16000); decoder.reset()}
                    }
                }
                decoder.accept(FloatArray(8000)); decoder.finish(); while(decoder.ready()) decoder.decode()
                transcript.commit(decoder.text(),frames*1000/16000)
            }
            val segments=transcript.segments()
            assertEquals("Every public phrase survives internal endpoints and silence",minutes*2,segments.size)
            assertTrue(segments.all {it.text.isNotBlank() && it.sha256==dev.ada.assistant.data.voiceHash(it.text)})
            assertEquals((0 until minutes*2).toList(),segments.map {it.sequence})
            assertTrue(transcript.text().length<=32768)
            val after=android.os.Debug.getPss()
            InstrumentationRegistry.getInstrumentation().sendStatus(0,android.os.Bundle().apply {
                putInt("accelerated_audio_minutes",minutes); putInt("segments",segments.size)
                putLong("elapsed_ms",SystemClock.elapsedRealtime()-began); putLong("pss_before_kib",before); putLong("pss_after_kib",after)
            })
        }
        phrase.fill(0f)
    }
    @Test fun publicKeywordPositiveAndConfusableNegativeSet() {
        val r=runtime()
        r.synthesizer().use {voice ->
            for(phrase in listOf("Hello Ada","Hello Adam","Hello there","Yellow radar","The green cup is on the desk")) {
                val raw=voice.generate(phrase,1,1f) {false}
                val samples=FloatArray(raw.size*2/3) {raw[(it*3/2).coerceAtMost(raw.lastIndex)]}
                var found=false
                r.wakeDetector().use {kws ->
                    for(i in samples.indices step 320) if(kws.accept(samples.copyOfRange(i,minOf(i+320,samples.size)))) found=true
                    repeat(100) {if(kws.accept(FloatArray(320))) found=true}
                }
                assertEquals("Public keyword case: $phrase",phrase=="Hello Ada",found)
                raw.fill(0f); samples.fill(0f)
            }
        }
    }
    @Test fun realForegroundServiceDetectsPublicSpeakerSampleAndStopReleasesMicrophone() {
        val r=runtime(); val context=InstrumentationRegistry.getInstrumentation().targetContext
        assumeTrue(context.packageName.startsWith("dev.ada.validation."))
        val manager=context.getSystemService(AudioManager::class.java)
        assumeTrue("Audible media volume required",manager.getStreamVolume(AudioManager.STREAM_MUSIC)>0)
        var samples=FloatArray(0)
        r.synthesizer().use {samples=it.generate("Hello Ada",1,1f) {false}}
        ActivityScenario.launch(PrivateVoiceReviewActivity::class.java).use {scenario ->
            try {
                scenario.onActivity {activity ->
                    WakeAuthority.arm(WakeAuthority.Grant(SessionIdentity("https://validation.invalid/",UUID(0,32)),UUID(0,32),UUID(0,32),0,System.currentTimeMillis()+120000))
                    ContextCompat.startForegroundService(activity,Intent(activity,HelloAdaService::class.java))
                }
                val ready=SystemClock.elapsedRealtime()+10000
                while(!HelloAdaService.status.value.startsWith("Armed") && SystemClock.elapsedRealtime()<ready) SystemClock.sleep(100)
                assertTrue(HelloAdaService.status.value.startsWith("Armed"))
                SystemClock.sleep(2000)
                // Deliberately separate public fixture driver. Production playback
                // preempts wake and cannot feed ADA's own voice into her detector.
                val track=AudioTrack.Builder().setAudioAttributes(AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_MEDIA).setContentType(AudioAttributes.CONTENT_TYPE_SPEECH).build())
                    .setAudioFormat(AudioFormat.Builder().setSampleRate(24000).setChannelMask(AudioFormat.CHANNEL_OUT_MONO).setEncoding(AudioFormat.ENCODING_PCM_FLOAT).build())
                    .setBufferSizeInBytes(65536).setTransferMode(AudioTrack.MODE_STREAM).build()
                try {track.play(); assertEquals(samples.size,track.write(samples,0,samples.size,AudioTrack.WRITE_BLOCKING)); SystemClock.sleep(4000)}
                finally {track.stop(); track.release()}
                val detected=HelloAdaService.status.value.startsWith("Hello Ada detected")
                InstrumentationRegistry.getInstrumentation().sendStatus(0,android.os.Bundle().apply {putBoolean("public_speaker_wake",detected);putLong("microphone_frames",HelloAdaService.publicFrames);putFloat("microphone_peak",HelloAdaService.publicPeak);putString("service_state",HelloAdaService.status.value)})
                assertTrue("Real microphone/service must detect the public speaker phrase",detected)
            } finally {
                scenario.onActivity {it.stopService(Intent(it,HelloAdaService::class.java)); WakeAuthority.revoke()}
                val until=SystemClock.elapsedRealtime()+5000
                while(VoiceAudioCoordinator.busy() && SystemClock.elapsedRealtime()<until) SystemClock.sleep(100)
                assertFalse(VoiceAudioCoordinator.busy()); assertNull(WakeAuthority.current()); samples.fill(0f)
            }
        }
    }
}
