import { useState } from 'react'
import { Download, Loader2, Trash2 } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import type { StudyFile } from '@/types/file'
import { fileCategoryLabels } from '@/types/file'
import { formatFileSize, getFileIcon } from '@/lib/fileUtils'
import { fileService } from '@/services/fileService'
import { getErrorMessage } from '@/lib/errorUtils'

interface FileListProps {
  files: StudyFile[]
  onDelete: (file: StudyFile) => void
  disabled?: boolean
}

export function FileList({ files, onDelete, disabled }: FileListProps) {
  const [downloadingId, setDownloadingId] = useState<number | null>(null)

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
        const categoryLabel =
          fileCategoryLabels[file.category] ?? file.category
        const date = new Date(file.created_at).toLocaleDateString('ru-RU', {
          day: 'numeric',
          month: 'short',
          year: 'numeric',
        })
        const isDownloading = downloadingId === file.id

        return (
          <div
            key={file.id}
            className="flex items-center gap-3 p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
          >
            <Icon className="h-8 w-8 text-muted-foreground shrink-0" />

            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{file.filename}</p>
              <div className="flex flex-wrap gap-x-3 gap-y-0.5 text-xs text-muted-foreground">
                <span className="inline-flex items-center px-1.5 py-0.5 rounded bg-muted text-muted-foreground">
                  {categoryLabel}
                </span>
                {file.subject_name && <span>{file.subject_name}</span>}
                <span>{formatFileSize(file.size)}</span>
                <span>{date}</span>
              </div>
            </div>

            <div className="flex gap-1 shrink-0">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleDownload(file)}
                disabled={isDownloading || disabled}
                aria-label={`Скачать ${file.filename}`}
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
