package dev.ada.assistant.audio

import android.content.Context
import com.k2fsa.sherpa.onnx.*

object LocalSpeechFactory {
    fun create(context: Context): LocalSpeechRuntime = SherpaLocalSpeech(context.applicationContext)
}

private class SherpaLocalSpeech(context: Context) : LocalSpeechRuntime {
    private val files = PackagedSpeechModels(context)
    override val available = true
    override val installed get() = files.installed
    override val modelDigest = "3810755ce7c3ab26b42a8bcf39d191308fa27fb0f53358823ba46141d03b7eb3"
    override fun install() = files.install()
    override fun remove() = files.remove()
    private fun model(group: String) = OnlineModelConfig(
        transducer = if(group == "asr") OnlineTransducerModelConfig(
            encoder=files.path("asr/encoder-epoch-99-avg-1.int8.onnx"),decoder=files.path("asr/decoder-epoch-99-avg-1.int8.onnx"),joiner=files.path("asr/joiner-epoch-99-avg-1.int8.onnx"))
        else OnlineTransducerModelConfig(encoder=files.path("kws/encoder-epoch-12-avg-2-chunk-16-left-64.int8.onnx"),decoder=files.path("kws/decoder-epoch-12-avg-2-chunk-16-left-64.int8.onnx"),joiner=files.path("kws/joiner-epoch-12-avg-2-chunk-16-left-64.int8.onnx")),
        tokens=files.path("$group/tokens.txt"),numThreads=2,debug=false,provider="cpu",modelType=if(group=="kws") "zipformer2" else "zipformer")
    override fun recognizer(): StreamingSpeechDecoder {
        files.beginUse("asr")
        val engine=try { OnlineRecognizer(config=OnlineRecognizerConfig(modelConfig=model("asr"),enableEndpoint=true,
            endpointConfig=EndpointConfig(rule1=EndpointRule(false,8f,0f),rule2=EndpointRule(true,2f,0f),rule3=EndpointRule(false,0f,30f)))) } catch(t:Throwable) { files.endUse(); throw t }
        val stream=try {engine.createStream()} catch(t:Throwable) {try {engine.release()} finally {files.endUse()}; throw t}
        return object : StreamingSpeechDecoder {
            override fun accept(samples: FloatArray) = stream.acceptWaveform(samples,16000)
            override fun ready() = engine.isReady(stream)
            override fun decode() = engine.decode(stream)
            override fun text() = engine.getResult(stream).text
            override fun endpoint() = engine.isEndpoint(stream)
            override fun reset() = engine.reset(stream)
            override fun finish() = stream.inputFinished()
            override fun close() { try {try {stream.release()} finally {engine.release()}} finally {files.endUse()} }
        }
    }
    override fun wakeDetector(): WakeWordDecoder {
        files.beginUse("kws")
        val engine=try { KeywordSpotter(config=KeywordSpotterConfig(modelConfig=model("kws"),keywordsFile=files.path("kws/keywords.txt"),keywordsThreshold=.5f,numTrailingBlanks=8)) } catch(t:Throwable) { files.endUse(); throw t }
        val stream=try {engine.createStream()} catch(t:Throwable) {try {engine.release()} finally {files.endUse()}; throw t}
        return object : WakeWordDecoder {
            override fun accept(samples: FloatArray): Boolean {
                stream.acceptWaveform(samples,16000)
                while(engine.isReady(stream)) engine.decode(stream)
                val found=engine.getResult(stream).keyword.isNotEmpty()
                if(found) engine.reset(stream)
                return found
            }
            override fun close() { try {try {stream.release()} finally {engine.release()}} finally {files.endUse()} }
        }
    }
    override fun synthesizer(): LocalVoiceSynthesizer {
        files.beginUse("tts")
        val engine=try { OfflineTts(config=OfflineTtsConfig(model=OfflineTtsModelConfig(
            kokoro=OfflineTtsKokoroModelConfig(model=files.path("tts/model.onnx"),voices=files.path("tts/voices.bin"),tokens=files.path("tts/tokens.txt"),dataDir=files.path("tts/espeak-ng-data")),numThreads=2,debug=false),maxNumSentences=1)) } catch(t:Throwable) { files.endUse(); throw t }
        return object : LocalVoiceSynthesizer {
            override val sampleRate get() = engine.sampleRate()
            override fun generate(text: String, voice: Int, speed: Float, cancelled: () -> Boolean): FloatArray {
                require(text.length <= 240 && voice in setOf(1,2,3,4))
                var total=0
                // The pinned JNI looks up invoke(float[]): Integer. An explicit class
                // retains that typed bridge with Kotlin 2's invokedynamic default.
                val generated=engine.generateWithCallback(text,voice,speed,object : (FloatArray) -> Int {
                    override fun invoke(samples: FloatArray): Int {
                        total+=samples.size
                        return if(cancelled() || total>768000) 0 else 1
                    }
                })
                require(generated.samples.size<=768000)
                return generated.samples
            }
            override fun close() { try { engine.release() } finally { files.endUse() } }
        }
    }
}
