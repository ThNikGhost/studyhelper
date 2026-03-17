import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Check, Loader2, Paperclip, Search } from 'lucide-react'
import { Modal } from '@/components/ui/modal'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { fileService } from '@/services/fileService'
import { fileCategoryLabels } from '@/types/file'
import { formatFileSize } from '@/lib/fileUtils'

interface FilePickerModalProps {
  onSelect: (fileIds: number[]) => void
  onClose: () => void
  excludeFileIds: number[]
  isAttaching: boolean
}

export function FilePickerModal({
  onSelect,
  onClose,
  excludeFileIds,
  isAttaching,
}: FilePickerModalProps) {
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set())
  const [search, setSearch] = useState('')

  const { data: allFiles = [], isLoading } = useQuery({
    queryKey: ['files', 'all'],
    queryFn: ({ signal }) => fileService.getFiles(undefined, undefined, signal),
  })

  // Show only unattached files, excluding already-attached ones
  const excludeSet = useMemo(() => new Set(excludeFileIds), [excludeFileIds])
  const availableFiles = useMemo(() => {
    const filtered = allFiles.filter(
      (f) => f.work_id === null && !excludeSet.has(f.id),
    )
    if (!search.trim()) return filtered
    const q = search.toLowerCase()
    return filtered.filter(
      (f) =>
        f.filename.toLowerCase().includes(q) ||
        (f.subject_name && f.subject_name.toLowerCase().includes(q)),
    )
  }, [allFiles, excludeSet, search])

  function toggleFile(id: number) {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  return (
    <Modal open={true} onClose={onClose} title="Прикрепить существующий файл">
      <div className="space-y-3">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Поиск по имени файла..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>

        {/* File list */}
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
          </div>
        ) : availableFiles.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <Paperclip className="h-8 w-8 mx-auto mb-2 opacity-40" />
            <p className="text-sm">
              {search.trim() ? 'Ничего не найдено' : 'Нет свободных файлов'}
            </p>
          </div>
        ) : (
          <div className="max-h-64 overflow-y-auto space-y-1">
            {availableFiles.map((file) => {
              const isSelected = selectedIds.has(file.id)
              return (
                <button
                  key={file.id}
                  type="button"
                  onClick={() => toggleFile(file.id)}
                  className={`w-full flex items-center gap-2 p-2 rounded-lg border text-left transition-colors ${
                    isSelected
                      ? 'border-primary bg-primary/5'
                      : 'border-transparent hover:bg-accent/50'
                  }`}
                >
                  <div
                    className={`h-5 w-5 rounded border flex items-center justify-center shrink-0 ${
                      isSelected
                        ? 'bg-primary border-primary text-primary-foreground'
                        : 'border-muted-foreground/30'
                    }`}
                  >
                    {isSelected && <Check className="h-3 w-3" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{file.filename}</p>
                    <p className="text-xs text-muted-foreground">
                      {fileCategoryLabels[file.category] ?? file.category}
                      {file.subject_name ? ` · ${file.subject_name}` : ''}
                      {' · '}
                      {formatFileSize(file.size)}
                    </p>
                  </div>
                </button>
              )
            })}
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-2 pt-2">
          <Button type="button" variant="outline" className="flex-1" onClick={onClose}>
            Отмена
          </Button>
          <Button
            className="flex-1"
            disabled={selectedIds.size === 0 || isAttaching}
            onClick={() => onSelect(Array.from(selectedIds))}
          >
            {isAttaching ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <>
                <Paperclip className="h-4 w-4 mr-1" />
                Прикрепить{selectedIds.size > 0 ? ` (${selectedIds.size})` : ''}
              </>
            )}
          </Button>
        </div>
      </div>
    </Modal>
  )
}
