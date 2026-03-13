import { ShieldCheck, Cpu } from 'lucide-react'

export function Header() {
  return (
    <header className="w-full px-6 py-4 flex items-center justify-between border-b border-white/5 relative z-20 backdrop-blur-md bg-slate-950/50">
      <div className="flex items-center gap-2 text-white">
        <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-xl shadow-[0_0_15px_rgba(59,130,246,0.5)]">
          <ShieldCheck className="w-6 h-6 text-white" />
        </div>
        <span className="font-bold text-xl tracking-tight hidden sm:block w-[150px]">DetectorPRO</span>
      </div>
      
      <nav className="flex items-center gap-8 text-sm font-medium text-slate-400">
        <a href="#" className="hover:text-white transition-colors">Cómo Funciona</a>
        <a href="#" className="hover:text-white transition-colors">API</a>
        <a href="#" className="hover:text-white transition-colors">Deep Research</a>
      </nav>

      <div className="flex items-center gap-4">
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          Sistemas Operativos
        </div>
        <button className="bg-white text-slate-950 hover:bg-blue-50 px-5 py-2 rounded-full font-semibold text-sm transition-all shadow-[0_0_20px_rgba(255,255,255,0.1)] hover:shadow-[0_0_25px_rgba(255,255,255,0.2)]">
          Probar Gratis
        </button>
      </div>
    </header>
  )
}
