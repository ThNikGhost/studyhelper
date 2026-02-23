import { useRef, useState } from 'react'
import { Download, ExternalLink, Loader2, Pencil, Trash2 } from 'lucide-react'
import { toast } from 'sonner'
import { useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import type { StudyFile } from '@/types/file'
import { FileCategory, fileCategoryLabels } from '@/types/file'
import { canOpenInBrowser, formatFileSize, getFileIcon } from '@/lib/fileUtils'
import { fileService } from '@/services/fileService'
import { getErrorMessage } from '@/lib/errorUtils'

interface FileListProps {
  files: StudyFile[]
  onDelete: (file: StudyFile) => void
  disabled?: boolean
}

const ALL_CATEGORIES = Object.values(FileCategory)

export function FileList({ files, onDelete, disabled }: FileListProps) {
  const queryClient = useQueryClient()
  const [downloadingId, setDownloadingId] = useState<number | null>(null)
  const [openingId, setOpeningId] = useState<number | null>(null)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [savingId, setSavingId] = useState<number | null>(null)
  const selectRef = useRef<HTMLSelectElement>(null)

  async function handleDownload(file: StudyFile) {
    setDownloadingId(file.id)
    try {
      await fileService.downloadFile(file.id, file.filename)
    } catch (error) {
      toast.error(getErrorMessage(error))
    } finally {
      setDownloadingId(null)
    }
  }

  async function handleOpen(file: StudyFile) {
    setOpeningId(file.id)
    try {
      await fileService.openFile(file.id)
    } catch (error) {
      toast.error(getErrorMessage(error))
    } finally {
      setOpeningId(null)
    }
  }

  function startEditing(file: StudyFile) {
    setEditingId(file.id)
    // Focus select on next tick after render
    setTimeout(() => selectRef.current?.focus(), 0)
  }

  function cancelEditing() {
    setEditingId(null)
  }

  async function handleCategoryChange(file: StudyFile, newCategory: string) {
    if (newCategory === file.category) {
      setEditingId(null)
      return
    }
    setSavingId(file.id)
    setEditingId(null)
    try {
      await fileService.updateFileCategory(file.id, newCategory)
      await queryClient.invalidateQueries({ queryKey: ['files'] })
    } catch (error) {
      toast.error(getErrorMessage(error))
    } finally {
      setSavingId(null)
    }
  }

  if (files.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <p className="text-sm">Файлов пока нет</p>
        <p className="text-xs mt-1">Загрузите первый файл с помощью формы выше</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {files.map((file) => {
        const Icon = getFileIcon(file.mime_type)
        const categoryLabel = fileCategoryLabels[file.category] ?? file.category
        const date = new Date(file.created_at).toLocaleDateString('ru-RU', {
          day: 'numeric',
          month: 'short',
          year: 'numeric',
        })
        const isDownloading = downloadingId === file.id
        const isOpening = openingId === file.id
        const isEditing = editingId === file.id
        const isSaving = savingId === file.id
        const openable = canOpenInBrowser(file.mime_type)

        return (
          <div
            key={file.id}
            className="flex items-center gap-3 p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors group"
          >
            <Icon className="h-8 w-8 text-muted-foreground shrink-0" />

            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{file.filename}</p>
              <div className="flex flex-wrap gap-x-3 gap-y-0.5 text-xs text-muted-foreground">
                {isEditing ? (
                  <select
                    ref={selectRef}
                    defaultValue={file.category}
                    className="text-xs bg-background border rounded px-1 py-0.5 focus:outline-none focus:ring-1 focus:ring-ring"
                    onChange={(e) => handleCategoryChange(file, e.target.value)}
                    onBlur={cancelEditing}
                    onKeyDown={(e) => e.key === 'Escape' && cancelEditing()}
                  >
                    {ALL_CATEGORIES.map((cat) => (
                      <option key={cat} value={cat}>
                        {fileCategoryLabels[cat]}
                      </option>
                    ))}
                  </select>
                ) : (
                  <span className="inline-flex items-center gap-1">
                    <span className="inline-flex items-center px-1.5 py-0.5 rounded bg-muted text-muted-foreground">
                      {isSaving ? '...' : categoryLabel}
                    </span>
                    <button
                      type="button"
                      aria-label="Изменить категорию"
                      className="opacity-0 group-hover:opacity-100 transition-opacity p-0.5 hover:text-foreground"
                      onClick={() => startEditing(file)}
                      disabled={disabled || isSaving}
                    >
                      <Pencil className="h-3 w-3" />
                    </button>
                  </span>
                )}
                {file.subject_name && <span>{file.subject_name}</span>}
                <span>{formatFileSize(file.size)}</span>
                <span>{date}</span>
              </div>
            </div>

            <div className="flex gap-1 shrink-0">
              {openable && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleOpen(file)}
                  disabled={isOpening || isDownloading || disabled}
                  aria-label={`Открыть ${file.filename}`}
                  title="Открыть в браузере"
                >
                  {isOpening ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <ExternalLink className="h-4 w-4" />
                  )}
                </Button>
              )}

              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleDownload(file)}
                disabled={isDownloading || isOpening || disabled}
                aria-label={`Скачать ${file.filename}`}
                title="Скачать"
              >
                {isDownloading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Download className="h-4 w-4" />
                )}
              </Button>

              <Button
                variant="ghost"
                size="icon"
                onClick={() => onDelete(file)}
                disabled={disabled}
                aria-label={`Удалить ${file.filename}`}
              >
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            </div>
          </div>
        )
      })}
    </div>
  )
}
