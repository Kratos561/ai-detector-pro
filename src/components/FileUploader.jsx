import { UploadCloud, FileType, CheckCircle } from 'lucide-react'
import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import clsx from 'clsx'

export function FileUploader({ onUpload }) {
  const [isHovered, setIsHovered] = useState(false)

  const onDrop = useCallback(acceptedFiles => {
    if (acceptedFiles?.length > 0) {
      onUpload(acceptedFiles[0])
    }
  }, [onUpload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxFiles: 1,
  })

  return (
    <div 
      {...getRootProps()}
      className={clsx(
        "relative overflow-hidden rounded-3xl border-2 border-dashed transition-all duration-300 ease-in-out cursor-pointer group glass",
        isDragActive || isHovered 
          ? "border-blue-500 bg-blue-500/5 py-32" 
          : "border-slate-700 hover:border-blue-500/50 hover:bg-slate-800/30 py-24"
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <input {...getInputProps()} />
      
      {/* Background glow when active */}
      <div className={clsx(
        "absolute inset-0 bg-gradient-to-br from-blue-500/10 via-transparent to-purple-500/10 opacity-0 transition-opacity duration-500",
        (isDragActive || isHovered) && "opacity-100"
      )} />

      <div className="relative z-10 flex flex-col items-center justify-center text-center px-4">
        <div className={clsx(
          "p-4 rounded-full mb-6 transition-all duration-300",
          isDragActive ? "bg-blue-500/20 text-blue-400 scale-110" : "bg-slate-800 text-slate-400 group-hover:bg-slate-700/50 group-hover:text-slate-300"
        )}>
          <UploadCloud className="w-10 h-10" />
        </div>
        
        <h3 className="text-xl md:text-2xl font-semibold mb-2 text-white">
          {isDragActive ? "Suelta el archivo aquí..." : "Haz clic o arrastra un archivo"}
        </h3>
        
        <p className="text-slate-400 mb-8 max-w-sm mx-auto">
          Soporta Texto (TXT, DOCX, PDF), Imágenes (JPG, PNG) y Código Fuente (.JS, .PY, etc.)
        </p>

        <div className="flex items-center gap-4 text-sm text-slate-500 font-medium">
          <div className="flex items-center gap-1 bg-slate-800/50 px-3 py-1.5 rounded-full border border-slate-700/50">
            <CheckCircle className="w-3 h-3 text-emerald-400" />
            <span>Seguro y privado</span>
          </div>
          <div className="flex items-center gap-1 bg-slate-800/50 px-3 py-1.5 rounded-full border border-slate-700/50">
            <FileType className="w-3 h-3 text-blue-400" />
            <span>Todos los formatos</span>
          </div>
        </div>
      </div>
    </div>
  )
}
