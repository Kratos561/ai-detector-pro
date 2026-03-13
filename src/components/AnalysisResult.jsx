import { FileText, Activity, Zap, AlignLeft, Server, RefreshCw, Download } from 'lucide-react'
import { motion } from 'framer-motion'
import clsx from 'clsx'

export function AnalysisResult({ result, onReset }) {
  const isAI = result.ai_probability > 50

  const handleDownload = () => {
    const content = JSON.stringify(result, null, 2)
    const blob = new Blob([content], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `ai-report-${result.file_name}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="glass p-8 md:p-10 rounded-3xl relative overflow-hidden text-left shadow-2xl border border-slate-700/30">
      {/* Glow dinámico */}
      <div className={clsx(
        "absolute top-0 right-0 w-[400px] h-[400px] rounded-full blur-[150px] pointer-events-none opacity-15 -translate-y-1/2 translate-x-1/2",
        isAI ? "bg-red-500" : "bg-emerald-500"
      )} />

      {/* Header del reporte */}
      <div className="flex flex-wrap justify-between items-start gap-4 mb-10">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-slate-800/80 border border-slate-700/50 flex flex-col items-center justify-center p-2">
            <FileText className="w-6 h-6 text-slate-300 mb-0.5" />
            <span className="text-[9px] font-bold text-slate-400 tracking-wider">{result.file_format}</span>
          </div>
          <div>
            <h2 className="text-xl font-bold text-white mb-1 truncate max-w-xs md:max-w-sm" title={result.file_name}>
              {result.file_name}
            </h2>
            <p className="text-slate-500 text-sm">{result.file_size_kb} KB · {result.word_count} palabras · {result.sentence_count} oraciones</p>
          </div>
        </div>
        <div className="flex gap-2">
          <button onClick={handleDownload} className="p-2 rounded-xl border border-slate-700 hover:bg-slate-800 text-slate-400 hover:text-white transition-all" title="Descargar reporte JSON">
            <Download className="w-4 h-4" />
          </button>
          <button onClick={onReset} className="flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-700 text-sm font-medium hover:bg-slate-800 hover:text-white transition-all text-slate-400">
            <RefreshCw className="w-3.5 h-3.5" /> Nuevo
          </button>
        </div>
      </div>

      {/* Veredicto + Barras */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
        <div className="space-y-6">
          <div>
            <p className="text-xs uppercase tracking-widest text-slate-500 font-semibold mb-3">Veredicto Final</p>
            <div className={clsx(
              "inline-flex items-center gap-2 px-4 py-2 rounded-full border text-sm font-bold mb-4",
              isAI
                ? "bg-red-500/10 border-red-500/30 text-red-400"
                : "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
            )}>
              <span className={clsx("w-2 h-2 rounded-full animate-pulse", isAI ? "bg-red-400" : "bg-emerald-400")} />
              {isAI ? "Generado por Inteligencia Artificial" : "Escrito por un Humano"}
            </div>
            <div className="flex items-end gap-2">
              <span className={clsx(
                "text-7xl font-black tracking-tighter",
                isAI
                  ? "text-red-400 drop-shadow-[0_0_20px_rgba(248,113,113,0.4)]"
                  : "text-emerald-400 drop-shadow-[0_0_20px_rgba(52,211,153,0.4)]"
              )}>
                {isAI ? result.ai_probability : result.human_probability}%
              </span>
            </div>
            <p className="text-slate-500 text-sm mt-1">probabilidad de {isAI ? 'IA' : 'humano'}</p>
          </div>

          <div className="space-y-3">
            <ProgressBar label="Inteligencia Artificial" value={result.ai_probability} color="bg-red-500" />
            <ProgressBar label="Escritura Humana" value={result.human_probability} color="bg-emerald-500" />
          </div>
        </div>

        {/* Métricas técnicas */}
        <div className="bg-slate-900/50 rounded-2xl p-6 border border-slate-800/60">
          <h3 className="text-xs uppercase tracking-widest text-slate-500 font-semibold mb-6 flex items-center gap-2">
            <Server className="w-3.5 h-3.5" /> Métricas del Motor
          </h3>
          <div className="space-y-5">
            <MetricRow
              icon={<AlignLeft className="w-4 h-4" />}
              title="Perplejidad"
              value={result.perplexity}
              desc="Previsibilidad del vocabulario. Valores bajos = IA."
              status={result.perplexity < 40 ? 'ai' : 'human'}
            />
            <MetricRow
              icon={<Activity className="w-4 h-4" />}
              title="Ráfagas (Burstiness)"
              value={result.burstiness}
              desc="Variación de longitud de oraciones. Bajo = Machine."
              status={result.burstiness < 30 ? 'ai' : 'human'}
            />
            <MetricRow
              icon={<Zap className="w-4 h-4" />}
              title="Humanizador Detectado"
              value={result.humanizer_detected ? "Sí — Patrón de Bypass" : "No Detectado"}
              desc="Herramientas como BypassGPT o Undetectable AI."
              status={result.humanizer_detected ? 'ai' : 'human'}
            />
          </div>
        </div>
      </div>

      {/* Patrones encontrados */}
      {result.patterns_found?.length > 0 && (
        <div className="border-t border-slate-800 pt-6">
          <p className="text-xs uppercase tracking-widest text-slate-500 font-semibold mb-3">Patrones de IA Detectados</p>
          <div className="flex flex-wrap gap-2">
            {result.patterns_found.map((p, i) => (
              <span key={i} className="px-3 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-red-300 text-xs font-mono">
                {p}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function ProgressBar({ label, value, color }) {
  return (
    <div>
      <div className="flex justify-between text-sm mb-1.5 font-medium">
        <span className="text-slate-400">{label}</span>
        <span className="text-white font-bold">{value}%</span>
      </div>
      <div className="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 1.2, ease: 'easeOut', delay: 0.3 }}
          className={clsx("h-full rounded-full", color)}
        />
      </div>
    </div>
  )
}

function MetricRow({ icon, title, value, desc, status }) {
  return (
    <div className="flex gap-3 items-start">
      <div className={clsx(
        "p-2 rounded-xl mt-0.5 border flex-shrink-0",
        status === 'ai'
          ? "bg-red-500/10 text-red-400 border-red-500/20"
          : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
      )}>
        {icon}
      </div>
      <div>
        <div className="flex items-baseline gap-2 flex-wrap">
          <h4 className="text-white font-medium text-sm">{title}</h4>
          <span className={clsx(
            "text-sm font-bold",
            status === 'ai' ? "text-red-400" : "text-emerald-400"
          )}>{value}</span>
        </div>
        <p className="text-slate-500 text-xs mt-0.5 leading-relaxed">{desc}</p>
      </div>
    </div>
  )
}
