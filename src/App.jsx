import { useState, useCallback } from 'react'
import { FileUploader } from './components/FileUploader'
import { AnalysisResult } from './components/AnalysisResult'
import { Header } from './components/Header'
import { motion, AnimatePresence } from 'framer-motion'
import { ShieldCheck, Activity } from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || '/api'

function App() {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [file, setFile] = useState(null)

  const handleFileUpload = useCallback(async (uploadedFile) => {
    setFile(uploadedFile)
    setIsAnalyzing(true)
    setResult(null)
    setError(null)

    const formData = new FormData()
    formData.append('file', uploadedFile)

    try {
      const response = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errData = await response.json()
        throw new Error(errData.detail || `Error ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message || 'Error al conectar con el servidor de análisis.')
    } finally {
      setIsAnalyzing(false)
    }
  }, [])

  const resetAnalysis = () => {
    setFile(null)
    setResult(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col relative overflow-hidden">
      {/* Background glow effects */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600/20 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-600/20 rounded-full blur-[120px] pointer-events-none" />

      <Header />

      <main className="flex-1 flex flex-col items-center justify-center p-6 relative z-10 w-full max-w-5xl mx-auto mt-16 mb-12">

        <div className="text-center mb-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium mb-6"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>AI Detection Engine 2025 — Motor Real</span>
          </motion.div>
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-4xl md:text-6xl font-bold tracking-tight mb-4 bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-slate-400"
          >
            Detecta la Huella de la IA
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-slate-400 text-lg md:text-xl max-w-2xl mx-auto"
          >
            Sube documentos, imágenes, PDFs o código fuente. Nuestro motor analiza perplejidad,
            ráfagas y patrones léxicos para detectar si fue escrito por una IA.
          </motion.p>
        </div>

        <div className="w-full max-w-3xl">
          <AnimatePresence mode="wait">
            {/* Estado inicial: sin archivo */}
            {!file && !isAnalyzing && !result && !error && (
              <motion.div
                key="uploader"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.3 }}
              >
                <FileUploader onUpload={handleFileUpload} />
              </motion.div>
            )}

            {/* Estado: analizando */}
            {isAnalyzing && (
              <motion.div
                key="analyzing"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center justify-center py-20 glass rounded-3xl border border-slate-700/50"
              >
                <div className="relative">
                  <div className="w-24 h-24 rounded-full border-4 border-slate-800 border-t-blue-500 animate-spin" />
                  <Activity className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 text-blue-400 animate-pulse" />
                </div>
                <h3 className="mt-8 text-2xl font-semibold text-white">Analizando {file?.name}...</h3>
                <p className="mt-2 text-slate-400">Calculando perplejidad, ráfagas y patrones de IA</p>
                <div className="mt-6 w-64 h-2 bg-slate-800 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: '100%' }}
                    transition={{ duration: 8, ease: 'linear' }}
                    className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                  />
                </div>
              </motion.div>
            )}

            {/* Estado: error */}
            {error && (
              <motion.div
                key="error"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-col items-center justify-center py-16 glass rounded-3xl border border-red-500/30 text-center px-8"
              >
                <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center mb-4">
                  <span className="text-3xl">⚠️</span>
                </div>
                <h3 className="text-xl font-semibold text-red-400 mb-2">Error en el Análisis</h3>
                <p className="text-slate-400 mb-6 max-w-md">{error}</p>
                <button
                  onClick={resetAnalysis}
                  className="px-6 py-2 rounded-full bg-slate-800 hover:bg-slate-700 text-white font-medium transition-colors border border-slate-700"
                >
                  Intentar de Nuevo
                </button>
              </motion.div>
            )}

            {/* Estado: resultado */}
            {result && (
              <motion.div
                key="result"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <AnalysisResult result={result} onReset={resetAnalysis} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  )
}

export default App
