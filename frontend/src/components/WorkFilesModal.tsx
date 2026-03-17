import { useRef, useState, useCallback, useEffect, type DragEvent, type ChangeEvent } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Download, ExternalLink, Link2, Loader2, Paperclip, Upload, X } from 'lucide-react'
import { toast } from 'sonner'
import { Modal } from '@/components/ui/modal'
import { Button } from '@/components/ui/button'
import { fileService } from '@/services/fileService'
import { useAuthStore } from '@/stores/authStore'
import type { WorkWithStatus } from '@/types/work'
import type { StudyFile } from '@/types/file'
import { FileCategory, fileCategoryLabels } from '@/types/file'
import { canOpenInBrowser, formatFileSize, isAllowedFileType, MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB, ALLOWED_EXTENSIONS } from '@/lib/fileUtils'
import { getErrorMessage } from '@/lib/errorUtils'
import { FilePickerModal } from '@/components/files/FilePickerModal'

interface WorkFilesModalProps {
  work: WorkWithStatus
  onClose: () => void
}

export function WorkFilesModal({ work, onClose }: WorkFilesModalProps) {
  const queryClient = useQueryClient()
  const currentUserId = useAuthStore((s) => s.user?.id)

  // Fetch files attached to this work
  const { data: files = [], isLoading } = useQuery({
    queryKey: ['files', 'work', work.id],
    queryFn: ({ signal }) => fileService.getFiles(undefined, undefined, signal, work.id),
  })

  // Upload state
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [category, setCategory] = useState<FileCategory>(FileCategory.LAB)
  const [isDragOver, setIsDragOver] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<number | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [detachingId, setDetachingId] = useState<number | null>(null)
  const [showFilePicker, setShowFilePicker] = useState(false)
  const [isAttaching, setIsAttaching] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const abortRef = useRef<AbortController | null>(null)

  const isUploading = uploadProgress !== null

  // Abort in-flight uploads on unmount
  useEffect(() => {
    return () => {
      abortRef.current?.abort()
    }
  }, [])

  // File action handlers
  async function handleDownload(file: StudyFile) {
    try {
      await fileService.downloadFile(file.id, file.filename)
    } catch (error) {
      toast.error(getErrorMessage(error))
    }
  }

  async function handleOpen(file: StudyFile) {
    try {
      await fileService.openFile(file.id)
    } catch (error) {
      toast.error(getErrorMessage(error))
    }
  }

  async function handleDetach(file: StudyFile) {
    setDetachingId(file.id)
    try {
      await fileService.updateFile(file.id, { work_id: null })
      await queryClient.invalidateQueries({ queryKey: ['files'] })
    } catch (error) {
      toast.error(getErrorMessage(error))
    } finally {
      setDetachingId(null)
    }
  }

  async function handleAttachExisting(fileIds: number[]) {
    setIsAttaching(true)
    try {
      await Promise.all(
        fileIds.map((id) => fileService.updateFile(id, { work_id: work.id })),
      )
      await queryClient.invalidateQueries({ queryKey: ['files'] })
      const count = fileIds.length
      toast.success(count === 1 ? 'Файл прикреплён' : `Прикреплено файлов: ${count}`)
      setShowFilePicker(false)
    } catch (error) {
      toast.error(getErrorMessage(error))
    } finally {
      setIsAttaching(false)
    }
  }

  // Upload zone handlers
  const validateAndAdd = useCallback((newFiles: File[]) => {
    setUploadError(null)
    const errors: string[] = []
    const valid: File[] = []
    for (const f of newFiles) {
      if (!isAllowedFileType(f)) {
        errors.push(`${f.name}: недопустимый тип`)
      } else if (f.size > MAX_FILE_SIZE_BYTES) {
        errors.push(`${f.name}: превышен размер ${MAX_FILE_SIZE_MB} MB`)
      } else {
        valid.push(f)
      }
    }
    if (errors.length) setUploadError(errors.join('; '))
    if (valid.length) setSelectedFiles((prev) => [...prev, ...valid])
  }, [])

  const handleDrop = useCallback(
    (e: DragEvent) => {
      e.preventDefault()
      setIsDragOver(false)
      if (isUploading) return
      const dropped = Array.from(e.dataTransfer.files)
      if (dropped.length) validateAndAdd(dropped)
    },
    [isUploading, validateAndAdd],
  )

  const handleInputChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const picked = Array.from(e.target.files ?? [])
      if (picked.length) validateAndAdd(picked)
      e.target.value = ''
    },
    [validateAndAdd],
  )

  const handleUpload = async () => {
    if (!selectedFiles.length) return
    setUploadError(null)
    const filesToUpload = selectedFiles
    const controller = new AbortController()
    abortRef.current = controller
    try {
      for (let i = 0; i < filesToUpload.length; i++) {
        await fileService.uploadFile({
          file: filesToUpload[i],
          category,
          subject_id: work.subject_id,
          work_id: work.id,
          onProgress: (p) =>
            setUploadProgress(Math.round((i / filesToUpload.length) * 100 + p / filesToUpload.length)),
          signal: controller.signal,
        })
      }
      setSelectedFiles([])
      setCategory(FileCategory.LAB)
      setUploadProgress(null)
      await queryClient.invalidateQueries({ queryKey: ['files'] })
      const count = filesToUpload.length
      toast.success(count === 1 ? 'Файл прикреплён' : `Прикреплено файлов: ${count}`)
    } catch (error) {
      setUploadProgress(null)
      if (!controller.signal.aborted) {
        toast.error(getErrorMessage(error))
      }
    } finally {
      abortRef.current = null
    }
  }

  return (
    <Modal
      open={true}
      onClose={onClose}
      title={`Файлы работы${isLoading ? '' : ` (${files.length})`}`}
    >
      <div className="space-y-4">
        {/* File list */}
        {isLoading ? (
          <div className="flex items-center justify-center py-6">
            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
          </div>
        ) : files.length === 0 ? (
          <div className="text-center py-6 text-muted-foreground">
            <Paperclip className="h-8 w-8 mx-auto mb-2 opacity-40" />
            <p className="text-sm">Нет прикреплённых файлов</p>
          </div>
        ) : (
          <div className="space-y-2">
            {files.map((file) => {
              const openable = canOpenInBrowser(file.mime_type)
              const isOwner = file.uploaded_by === currentUserId
              const isDetaching = detachingId === file.id
              return (
                <div
                  key={file.id}
                  className="flex items-center gap-2 p-2 rounded-lg border bg-card"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{file.filename}</p>
                    <p className="text-xs text-muted-foreground">
                      {fileCategoryLabels[file.category] ?? file.category} · {formatFileSize(file.size)}
                    </p>
                  </div>
                  <div className="flex gap-1 shrink-0">
                    {openable && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleOpen(file)}
                        title="Открыть в браузере"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDownload(file)}
                      title="Скачать"
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                    {isOwner && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDetach(file)}
                        disabled={isDetaching}
                        title="Открепить от работы"
                      >
                        {isDetaching ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <X className="h-4 w-4 text-muted-foreground" />
                        )}
                      </Button>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {/* Upload section */}
        <div className="border-t pt-4 space-y-3">
          {/* Attach existing file button */}
          <Button
            variant="outline"
            className="w-full"
            onClick={() => setShowFilePicker(true)}
          >
            <Link2 className="h-4 w-4 mr-2" />
            Прикрепить существующий файл
          </Button>

          {/* Drop zone */}
          <div
            data-testid="work-files-dropzone"
            className={`border-2 border-dashed rounded-lg p-4 text-center transition-colors ${
              isDragOver
                ? 'border-primary bg-primary/5'
                : 'border-muted-foreground/25 hover:border-muted-foreground/50'
            } ${isUploading ? 'opacity-50 pointer-events-none' : 'cursor-pointer'}`}
            onDragOver={(e) => { e.preventDefault(); if (!isUploading) setIsDragOver(true) }}
            onDragLeave={(e) => { e.preventDefault(); setIsDragOver(false) }}
            onDrop={handleDrop}
            onClick={() => !isUploading && inputRef.current?.click()}
            role="button"
            tabIndex={isUploading ? -1 : 0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault()
                inputRef.current?.click()
              }
            }}
            aria-label="Прикрепить файл к работе"
          >
            <Upload className="mx-auto h-6 w-6 text-muted-foreground mb-1" />
            <p className="text-xs text-muted-foreground">
              Перетащите файлы или нажмите для выбора
            </p>
            <p className="text-xs text-muted-foreground/70 mt-0.5">
              {ALLOWED_EXTENSIONS.join(', ')} — до {MAX_FILE_SIZE_MB} MB
            </p>
            <input
              ref={inputRef}
              type="file"
              multiple
              className="hidden"
              accept={ALLOWED_EXTENSIONS.map((ext) => `.${ext}`).join(',')}
              onChange={handleInputChange}
            />
          </div>

          {uploadError && (
            <p className="text-xs text-destructive" role="alert">{uploadError}</p>
          )}

          {/* Selected files */}
          {selectedFiles.length > 0 && !isUploading && (
            <div className="space-y-1">
              {selectedFiles.map((f, i) => (
                <div key={`${f.name}-${f.lastModified}`} className="flex items-center gap-2 p-2 bg-muted rounded text-sm">
                  <span className="flex-1 truncate">{f.name}</span>
                  <span className="text-xs text-muted-foreground shrink-0">{formatFileSize(f.size)}</span>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6"
                    onClick={() => setSelectedFiles((prev) => prev.filter((_, idx) => idx !== i))}
                    aria-label={`Убрать ${f.name}`}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              ))}
            </div>
          )}

          {/* Category select + upload button */}
          {selectedFiles.length > 0 && !isUploading && (
            <div className="flex gap-2">
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value as FileCategory)}
                className="flex h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                aria-label="Категория файла"
              >
                {Object.entries(fileCategoryLabels).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
              <Button onClick={handleUpload} className="flex-1 whitespace-nowrap">
                <Upload className="h-4 w-4 mr-1" />
                {selectedFiles.length > 1 ? `Прикрепить (${selectedFiles.length})` : 'Прикрепить'}
              </Button>
            </div>
          )}

          {/* Upload progress */}
          {isUploading && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Загрузка... {uploadProgress}%</span>
            </div>
          )}
        </div>
      </div>

      {/* File picker modal */}
      {showFilePicker && (
        <FilePickerModal
          onSelect={handleAttachExisting}
          onClose={() => setShowFilePicker(false)}
          excludeFileIds={files.map((f) => f.id)}
          isAttaching={isAttaching}
        />
      )}
    </Modal>
  )
}

export default WorkFilesModal
