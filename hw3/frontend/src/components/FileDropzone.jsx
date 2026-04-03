/**
 * FileDropzone — drag-and-drop file upload zone.
 * Props:
 *   onFile(file) — called when a valid file is selected
 *   accept       — MIME type map (react-dropzone format), default any
 *   maxSize      — bytes, default 10MB
 *   label        — prompt text
 *   currentFile  — File | null currently staged
 */
import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import { UploadCloud, File, X, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'

const MAX_SIZE = 10 * 1024 * 1024 // 10 MB

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 ** 2).toFixed(1)} MB`
}

export default function FileDropzone({
  onFile,
  accept,
  maxSize = MAX_SIZE,
  label = 'Drop your file here or click to browse',
  currentFile,
}) {
  const onDrop = useCallback(
    (accepted, rejected) => {
      if (rejected.length > 0) {
        const err = rejected[0].errors[0]
        if (err.code === 'file-too-large') {
          toast.error(`File too large — max ${formatBytes(maxSize)}`)
        } else if (err.code === 'file-invalid-type') {
          toast.error('File type not allowed')
        } else {
          toast.error(err.message)
        }
        return
      }
      if (accepted.length > 0) {
        onFile(accepted[0])
      }
    },
    [onFile, maxSize]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxSize,
    accept,
    multiple: false,
  })

  return (
    <div className="space-y-3">
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''}`}
      >
        <input {...getInputProps()} />
        <motion.div
          animate={isDragActive ? { scale: 1.1 } : { scale: 1 }}
          transition={{ type: 'spring', stiffness: 400, damping: 20 }}
        >
          <UploadCloud
            size={36}
            className={`transition-colors ${isDragActive ? 'text-cyan-400' : 'text-slate-600'}`}
          />
        </motion.div>
        <div className="text-center">
          <p className={`text-sm font-display transition-colors ${isDragActive ? 'text-cyan-400' : 'text-slate-400'}`}>
            {isDragActive ? 'Release to upload' : label}
          </p>
          <p className="text-xs text-slate-600 mt-1">
            Max size: {formatBytes(maxSize)}
          </p>
        </div>
      </div>

      {/* Staged file preview */}
      <AnimatePresence>
        {currentFile && (
          <motion.div
            className="flex items-center gap-3 px-4 py-3 bg-cyan-500/5 border border-cyan-500/20 rounded-xl"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{    opacity: 0, height: 0 }}
          >
            <File size={16} className="text-cyan-400 shrink-0" />
            <div className="flex-1 min-w-0">
              <p className="text-sm text-slate-200 truncate font-mono">{currentFile.name}</p>
              <p className="text-xs text-slate-500">{formatBytes(currentFile.size)}</p>
            </div>
            <button
              type="button"
              onClick={() => onFile(null)}
              className="p-1 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
            >
              <X size={14} />
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
