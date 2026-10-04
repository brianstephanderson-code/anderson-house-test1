package house.anderson.amigos

import android.content.res.AssetManager
import com.k2fsa.sherpa.onnx.FeatureConfig
import com.k2fsa.sherpa.onnx.KeywordSpotter
import com.k2fsa.sherpa.onnx.KeywordSpotterConfig
import com.k2fsa.sherpa.onnx.OnlineModelConfig
import com.k2fsa.sherpa.onnx.OnlineStream
import com.k2fsa.sherpa.onnx.OnlineTransducerModelConfig

class WakeEngine(private val assets: AssetManager) {
    companion object {
        private const val DIR = "kws"
        private const val ENCODER = "kws/encoder-epoch-13-avg-2-chunk-16-left-64.int8.onnx"
        private const val DECODER = "kws/decoder-epoch-13-avg-2-chunk-16-left-64.onnx"
        private const val JOINER = "kws/joiner-epoch-13-avg-2-chunk-16-left-64.int8.onnx"
        private const val TOKENS = "kws/tokens.txt"
        private const val EMPTY_KEYWORDS = "kws/empty_keywords.txt"
        private const val HEY_TOMO = "HH EY1 T OW1 M OW0 @HEY_TOMO"
    }

    private var spotter: KeywordSpotter? = null
    private var stream: OnlineStream? = null

    @Synchronized
    fun start() {
        if (spotter == null) {
            val transducer = OnlineTransducerModelConfig().apply {
                encoder = ENCODER
                decoder = DECODER
                joiner = JOINER
            }
            val model = OnlineModelConfig().apply {
                this.transducer = transducer
                tokens = TOKENS
                numThreads = 1
                provider = "cpu"
                modelType = "zipformer2"
                debug = false
            }
            val feat = FeatureConfig().apply {
                sampleRate = 16000
                featureDim = 80
            }
            val cfg = KeywordSpotterConfig().apply {
                featConfig = feat
                modelConfig = model
                maxActivePaths = 4
                keywordsFile = EMPTY_KEYWORDS
                keywordsScore = 1.5f
                keywordsThreshold = 0.40f
                numTrailingBlanks = 1
            }
            spotter = KeywordSpotter(assets, cfg)
        }
        stream?.release()
        stream = spotter!!.createStream(HEY_TOMO)
        check(stream!!.ptr != 0L) { "Wake-word stream could not be created" }
    }

    @Synchronized
    fun accept(samples: FloatArray, sampleRate: Int): Boolean {
        val sp = spotter ?: return false
        val st = stream ?: return false
        st.acceptWaveform(samples, sampleRate)
        while (sp.isReady(st)) {
            sp.decode(st)
            val keyword = sp.getResult(st).keyword
            if (!keyword.isNullOrBlank()) {
                sp.reset(st)
                return true
            }
        }
        return false
    }

    @Synchronized
    fun close() {
        try { stream?.release() } catch (_: Throwable) {}
        stream = null
        try { spotter?.release() } catch (_: Throwable) {}
        spotter = null
    }
}
