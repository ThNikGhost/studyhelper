import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNetworkStatus } from '@/hooks/useNetworkStatus'
import { ArrowLeft, RefreshCw, Loader2, FolderOpen } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Modal } from '@/components/ui/modal'
import { toast } from 'sonner'
import { FileDropzone } from '@/components/files/FileDropzone'
import { FileList } from '@/components/files/FileList'
import fileService from '@/services/fileService'
import subjectService from '@/services/subjectService'
import type { StudyFile, FileCategory } from '@/types/file'
import { fileCategoryLabels } from '@/types/file'

export function FilesPage() {
  const isOnline = useNetworkStatus()
  const queryClient = useQueryClient()

  const [filterSubjectId, setFilterSubjectId] = useState<string>('')
  const [filterCategory, setFilterCategory] = useState<string>('')
  const [uploadProgress, setUploadProgress] = useState<number | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<StudyFile | null>(null)

  // Fetch subjects for filters and dropzone
  const { data: subjects = [] } = useQuery({
    queryKey: ['subjects'],
    queryFn: ({ signal }) => subjectService.getSubjects(undefined, signal),
  })

  // Fetch files
  const {
    data: files = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: [
      'files',
      filterSubjectId || undefined,
      filterCategory || undefined,
    ],
    queryFn: ({ signal }) =>
      fileService.getFiles(
        filterSubjectId ? Number(filterSubjectId) : undefined,
        filterCategory || undefined,
        signal,
      ),
  })

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: ({
      file,
      category,
      subjectId,
    }: {
      file: File
      category: FileCategory
      subjectId: number | null
    }) =>
      fileService.uploadFile({
        file,
        category,
        subject_id: subjectId,
        onProgress: (p) => setUploadProgress(p),
      }),
    onSuccess: () => {
      setUploadProgress(null)
      toast.success('Файл загружен')
      queryClient.invalidateQueries({ queryKey: ['files'] })
    },
    onError: () => {
      setUploadProgress(null)
      toast.error('Ошибка загрузки файла')
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => fileService.deleteFile(id),
    onSuccess: () => {
      setDeleteTarget(null)
      toast.success('Файл удалён')
      queryClient.invalidateQueries({ queryKey: ['files'] })
    },
    onError: () => {
      toast.error('Ошибка удаления файла')
    },
  })

  const handleUpload = async (
    file: File,
    category: FileCategory,
    subjectId: number | null,
  ) => {
    await uploadMutation.mutateAsync({ file, category, subjectId })
  }

  const handleDeleteConfirm = () => {
    if (deleteTarget) {
      deleteMutation.mutate(deleteTarget.id)
    }
  }

  return (
    <div className="container mx-auto px-4 py-6 max-w-4xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Link to="/">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div className="flex items-center gap-2">
            <FolderOpen className="h-6 w-6 text-amber-500" />
            <h1 className="text-2xl font-bold">Файлы</h1>
          </div>
        </div>
        <Button
          variant="outline"
          size="icon"
          onClick={() => refetch()}
          disabled={!isOnline}
          aria-label="Обновить"
        >
          <RefreshCw className="h-4 w-4" />
        </Button>
      </div>

      {/* Upload zone */}
      <div className="mb-6">
        <FileDropzone
          subjects={subjects}
          onUpload={handleUpload}
          disabled={!isOnline}
          uploadProgress={uploadProgress}
        />
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-2 mb-4">
        <select
          value={filterSubjectId}
          onChange={(e) => setFilterSubjectId(e.target.value)}
          className="flex h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          aria-label="Фильтр по предмету"
        >
          <option value="">Все предметы</option>
          {subjects.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name}
            </option>
          ))}
        </select>

        <select
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
          className="flex h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          aria-label="Фильтр по категории"
        >
          <option value="">Все категории</option>
          {Object.entries(fileCategoryLabels).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </div>

      {/* File list */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : error ? (
        <div className="text-center py-12 text-destructive">
          <p className="text-sm">Ошибка загрузки файлов</p>
        </div>
      ) : (
        <FileList
          files={files}
          onDelete={(file) => setDeleteTarget(file)}
          disabled={!isOnline}
        />
      )}

      {/* Delete confirmation modal */}
      <Modal
        open={deleteTarget !== null}
        onClose={() => setDeleteTarget(null)}
        title="Удалить файл?"
      >
        <p className="text-sm text-muted-foreground mb-4">
          Файл <strong>{deleteTarget?.filename}</strong> будет удалён без возможности
          восстановления.
        </p>
        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={() => setDeleteTarget(null)}>
            Отмена
          </Button>
          <Button
            variant="destructive"
            onClick={handleDeleteConfirm}
            disabled={deleteMutation.isPending}
          >
            {deleteMutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin mr-1" />
            ) : null}
            Удалить
          </Button>
        </div>
      </Modal>
    </div>
  )
}

export default FilesPage
