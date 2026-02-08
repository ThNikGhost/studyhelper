import { useState, useRef, useCallback, type DragEvent, type ChangeEvent } from 'react'
import { Upload, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ProgressBar } from '@/components/ui/progress-bar'
import { FileCategory, fileCategoryLabels } from '@/types/file'
import type { Subject } from '@/types/subject'
import { isAllowedFileType, formatFileSize, MAX_FILE_SIZE_BYTES, ALLOWED_EXTENSIONS } from '@/lib/fileUtils'

interface FileDropzoneProps {
  subjects: Subject[]
  onUpload: (file: File, category: FileCategory, subjectId: number | null) => Promise<void>
  disabled?: boolean
  uploadProgress: number | null
}

export function FileDropzone({ subjects, onUpload, disabled, uploadProgress }: FileDropzoneProps) {
  const [isDragOver, setIsDragOver] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [category, setCategory] = useState<FileCategory>(FileCategory.LECTURE)
  const [subjectId, setSubjectId] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const isUploading = uploadProgress !== null

  const validateFile = useCallback((file: File): string | null => {
    if (!isAllowedFileType(file)) {
      return `Недопустимый тип файла. Разрешённые: ${ALLOWED_EXTENSIONS.join(', ')}`
    }
    if (file.size > MAX_FILE_SIZE_BYTES) {
      return `Файл слишком большой. Максимум: ${MAX_FILE_SIZE_BYTES / 1024 / 1024} MB`
    }
    return null
  }, [])

  const handleFile = useCallback(
    (file: File) => {
      setError(null)
      const validationError = validateFile(file)
      if (validationError) {
        setError(validationError)
        return
      }
      setSelectedFile(file)
    },
    [validateFile],
  )

  const handleDragOver = useCallback(
    (e: DragEvent) => {
      e.preventDefault()
      if (!disabled && !isUploading) setIsDragOver(true)
    },
    [disabled, isUploading],
  )

  const handleDragLeave = useCallback((e: DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback(
    (e: DragEvent) => {
      e.preventDefault()
      setIsDragOver(false)
      if (disabled || isUploading) return

      const file = e.dataTransfer.files[0]
      if (file) handleFile(file)
    },
    [disabled, isUploading, handleFile],
  )

  const handleInputChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file) handleFile(file)
      // Reset input so the same file can be re-selected
      e.target.value = ''
    },
    [handleFile],
  )

  const handleUpload = async () => {
    if (!selectedFile) return
    setError(null)
    try {
      await onUpload(selectedFile, category, subjectId ? Number(subjectId) : null)
      setSelectedFile(null)
      setCategory(FileCategory.LECTURE)
      setSubjectId('')
    } catch {
      // Error handled by parent via toast
    }
  }

  const handleClear = () => {
    setSelectedFile(null)
    setError(null)
  }

  return (
    <div className="space-y-3">
      {/* Drop zone */}
      <div
        data-testid="dropzone"
        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          isDragOver
            ? 'border-primary bg-primary/5'
            : 'border-muted-foreground/25 hover:border-muted-foreground/50'
        } ${disabled || isUploading ? 'opacity-50 pointer-events-none' : 'cursor-pointer'}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !disabled && !isUploading && inputRef.current?.click()}
        role="button"
        tabIndex={disabled || isUploading ? -1 : 0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            inputRef.current?.click()
          }
        }}
        aria-label="Область загрузки файлов"
      >
        <Upload className="mx-auto h-8 w-8 text-muted-foreground mb-2" />
        <p className="text-sm text-muted-foreground">
          Перетащите файл сюда или нажмите для выбора
        </p>
        <p className="text-xs text-muted-foreground mt-1">
          {ALLOWED_EXTENSIONS.join(', ')} — до 50 MB
        </p>
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept={ALLOWED_EXTENSIONS.map((ext) => `.${ext}`).join(',')}
          onChange={handleInputChange}
          data-testid="file-input"
        />
      </div>

      {/* Error message */}
      {error && (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      )}

      {/* Selected file preview */}
      {selectedFile && !isUploading && (
        <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{selectedFile.name}</p>
            <p className="text-xs text-muted-foreground">{formatFileSize(selectedFile.size)}</p>
          </div>
          <Button variant="ghost" size="icon" onClick={handleClear} aria-label="Убрать файл">
            <X className="h-4 w-4" />
          </Button>
        </div>
      )}

      {/* Category + Subject selects + Upload button */}
      {selectedFile && !isUploading && (
        <div className="flex flex-col sm:flex-row gap-2">
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value as FileCategory)}
            className="flex h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            aria-label="Категория файла"
          >
            {Object.entries(fileCategoryLabels).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>

          <select
            value={subjectId}
            onChange={(e) => setSubjectId(e.target.value)}
            className="flex h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            aria-label="Предмет"
          >
            <option value="">Без предмета</option>
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>

          <Button onClick={handleUpload} disabled={disabled} className="whitespace-nowrap">
            <Upload className="h-4 w-4 mr-1" />
            Загрузить
          </Button>
        </div>
      )}

      {/* Upload progress */}
      {isUploading && (
        <div className="space-y-1">
          <ProgressBar value={uploadProgress} color="bg-primary" showLabel />
          <p className="text-xs text-muted-foreground text-center">Загрузка...</p>
        </div>
      )}
    </div>
  )
}
