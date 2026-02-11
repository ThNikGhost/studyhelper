import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNetworkStatus } from '@/hooks/useNetworkStatus'
import { useNavigate } from 'react-router-dom'
import { Plus, Pencil, Trash2, RefreshCw, ArrowLeft, BookOpen, Loader2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Modal } from '@/components/ui/modal'
import { ProgressBar } from '@/components/ui/progress-bar'
import { SubjectProgressCard } from '@/components/subjects/SubjectProgressCard'
import { toast } from 'sonner'
import subjectService from '@/services/subjectService'
import workService from '@/services/workService'
import { calculateSemesterProgress, getProgressBarColor, getProgressColor } from '@/lib/progressUtils'
import type { Subject, SubjectCreate, Semester } from '@/types/subject'

export function SubjectsPage() {
  const isOnline = useNetworkStatus()
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [selectedSemesterId, setSelectedSemesterId] = useState<number | undefined>(undefined)
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [editingSubject, setEditingSubject] = useState<Subject | null>(null)
  const [deleteConfirmSubject, setDeleteConfirmSubject] = useState<Subject | null>(null)

  // Form state
  const [formData, setFormData] = useState<SubjectCreate & { total_hours: number | null }>({
    name: '',
    short_name: '',
    description: '',
    semester_id: 0,
    planned_classes: null,
    total_hours: null,
  })

  // Fetch semesters
  const { data: semesters = [], isLoading: semestersLoading } = useQuery<Semester[]>({
    queryKey: ['semesters'],
    queryFn: ({ signal }) => subjectService.getSemesters(signal),
  })

  // Fetch current semester
  const { data: currentSemester } = useQuery<Semester | null>({
    queryKey: ['semesters', 'current'],
    queryFn: ({ signal }) => subjectService.getCurrentSemester(signal),
  })

  // Auto-select current semester
  const effectiveSemesterId = selectedSemesterId ?? currentSemester?.id

  // Fetch subjects for selected semester
  const {
    data: subjects = [],
    isLoading: subjectsLoading,
    error,
    refetch,
  } = useQuery<Subject[]>({
    queryKey: ['subjects', effectiveSemesterId],
    queryFn: ({ signal }) => subjectService.getSubjects(effectiveSemesterId, signal),
    enabled: effectiveSemesterId !== undefined || semesters.length > 0,
  })

  // Fetch all works for progress calculation
  const { data: works = [] } = useQuery({
    queryKey: ['works'],
    queryFn: ({ signal }) => workService.getWorks(undefined, signal),
  })

  // Calculate progress per subject
  const semesterProgress = useMemo(
    () => calculateSemesterProgress(works, subjects),
    [works, subjects],
  )

  const progressBySubject = useMemo(() => {
    const map = new Map<number, (typeof semesterProgress.subjects)[0]>()
    for (const sp of semesterProgress.subjects) {
      map.set(sp.subjectId, sp)
    }
    return map
  }, [semesterProgress])

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: SubjectCreate) => subjectService.createSubject(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subjects'] })
      toast.success('Предмет добавлен')
      closeModal()
    },
    onError: () => {
      toast.error('Не удалось добавить предмет')
    },
  })

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<SubjectCreate> }) =>
      subjectService.updateSubject(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subjects'] })
      toast.success('Предмет обновлён')
      closeModal()
    },
    onError: () => {
      toast.error('Не удалось обновить предмет')
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => subjectService.deleteSubject(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subjects'] })
      toast.success('Предмет удалён')
      setDeleteConfirmSubject(null)
    },
    onError: () => {
      toast.error('Не удалось удалить предмет')
    },
  })

  // Modal handlers
  const openAddModal = () => {
    setFormData({
      name: '',
      short_name: '',
      description: '',
      semester_id: effectiveSemesterId || semesters[0]?.id || 0,
      planned_classes: null,
      total_hours: null,
    })
    setEditingSubject(null)
    setIsAddModalOpen(true)
  }

  const openEditModal = (subject: Subject) => {
    setFormData({
      name: subject.name,
      short_name: subject.short_name || '',
      description: subject.description || '',
      semester_id: subject.semester_id,
      planned_classes: subject.planned_classes,
      total_hours: subject.total_hours,
    })
    setEditingSubject(subject)
    setIsAddModalOpen(true)
  }

  const closeModal = () => {
    setIsAddModalOpen(false)
    setEditingSubject(null)
    setFormData({
      name: '',
      short_name: '',
      description: '',
      semester_id: 0,
      planned_classes: null,
      total_hours: null,
    })
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (editingSubject) {
      updateMutation.mutate({ id: editingSubject.id, data: formData })
    } else {
      createMutation.mutate(formData)
    }
  }

  const isLoading = semestersLoading || subjectsLoading
  const isMutating = createMutation.isPending || updateMutation.isPending || deleteMutation.isPending

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container max-w-2xl mx-auto px-4 py-6">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-muted rounded w-1/3" />
            <div className="h-12 bg-muted rounded" />
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-24 bg-muted rounded" />
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container max-w-2xl mx-auto px-4 py-6">
          <Card>
            <CardContent className="py-10 text-center">
              <p className="text-destructive mb-4">Ошибка загрузки предметов</p>
              <Button onClick={() => refetch()}>Попробовать снова</Button>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container max-w-2xl mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <Link to="/">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <h1 className="text-2xl font-bold flex-1">Предметы</h1>
          <Button variant="ghost" size="icon" onClick={() => refetch()} title="Обновить">
            <RefreshCw className="h-5 w-5" />
          </Button>
        </div>

        {/* Semester selector */}
        <Card className="mb-6">
          <CardContent className="py-3 px-4">
            <Label htmlFor="semester-select" className="text-sm text-muted-foreground">
              Семестр
            </Label>
            <select
              id="semester-select"
              className="w-full mt-1 px-3 py-2 bg-background border rounded-md text-sm"
              value={effectiveSemesterId || ''}
              onChange={(e) => setSelectedSemesterId(e.target.value ? Number(e.target.value) : undefined)}
            >
              {semesters.map((semester) => (
                <option key={semester.id} value={semester.id}>
                  {semester.name} {semester.is_current && '(текущий)'}
                </option>
              ))}
            </select>
          </CardContent>
        </Card>

        {/* Overall progress summary */}
        {subjects.length > 0 && semesterProgress.total > 0 && (
          <Card className="mb-6">
            <CardContent className="py-3 px-4">
              <div className="flex items-baseline justify-between mb-1">
                <span className="text-sm font-medium">Общий прогресс</span>
                <span
                  className={`text-sm font-semibold ${getProgressColor(semesterProgress.percentage)}`}
                >
                  {semesterProgress.completed} из {semesterProgress.total} ({semesterProgress.percentage}%)
                </span>
              </div>
              <ProgressBar
                value={semesterProgress.percentage}
                color={getProgressBarColor(semesterProgress.percentage)}
              />
            </CardContent>
          </Card>
        )}

        {/* Add button */}
        <Button className="w-full mb-6" onClick={openAddModal} disabled={!isOnline}>
          <Plus className="h-4 w-4 mr-2" />
          Добавить предмет
        </Button>

        {/* Subjects list with progress */}
        <div className="space-y-3">
          {subjects.map((subject) => (
            <div key={subject.id} className="relative">
              <SubjectProgressCard
                subject={subject}
                progress={progressBySubject.get(subject.id)}
                onClick={() => navigate(`/works?subject_id=${subject.id}`)}
              />
              {/* Edit/Delete buttons overlay */}
              <div className="absolute top-3 right-3 flex gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7"
                  onClick={(e) => {
                    e.stopPropagation()
                    openEditModal(subject)
                  }}
                  disabled={!isOnline}
                  title="Редактировать"
                >
                  <Pencil className="h-3.5 w-3.5" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7"
                  onClick={(e) => {
                    e.stopPropagation()
                    setDeleteConfirmSubject(subject)
                  }}
                  disabled={!isOnline}
                  title="Удалить"
                >
                  <Trash2 className="h-3.5 w-3.5 text-destructive" />
                </Button>
              </div>
            </div>
          ))}
        </div>

        {/* Empty state */}
        {subjects.length === 0 && (
          <Card>
            <CardContent className="py-10 text-center text-muted-foreground">
              <BookOpen className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Нет предметов в этом семестре</p>
              <p className="text-sm mt-1">Добавьте первый предмет</p>
            </CardContent>
          </Card>
        )}

        {/* Add/Edit Modal */}
        <Modal
          open={isAddModalOpen}
          onClose={closeModal}
          title={editingSubject ? 'Редактировать предмет' : 'Новый предмет'}
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="name">Название *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Математический анализ"
                required
              />
            </div>

            <div>
              <Label htmlFor="short_name">Сокращение</Label>
              <Input
                id="short_name"
                value={formData.short_name || ''}
                onChange={(e) => setFormData({ ...formData, short_name: e.target.value })}
                placeholder="Матан"
              />
            </div>

            <div>
              <Label htmlFor="description">Описание</Label>
              <textarea
                id="description"
                className="w-full px-3 py-2 bg-background border rounded-md text-sm min-h-[80px]"
                value={formData.description || ''}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Дополнительная информация о предмете"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="planned_classes">Кол-во пар</Label>
                <Input
                  id="planned_classes"
                  type="number"
                  min={0}
                  max={500}
                  value={formData.planned_classes ?? ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      planned_classes: e.target.value ? Number(e.target.value) : null,
                    })
                  }
                  placeholder="32"
                />
              </div>
              <div>
                <Label htmlFor="total_hours">Всего часов</Label>
                <Input
                  id="total_hours"
                  type="number"
                  min={0}
                  max={2000}
                  value={formData.total_hours ?? ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      total_hours: e.target.value ? Number(e.target.value) : null,
                    })
                  }
                  placeholder="108"
                  disabled={editingSubject?.total_hours !== null && editingSubject?.total_hours !== undefined}
                />
              </div>
            </div>
            <p className="text-xs text-muted-foreground -mt-2">
              Количество пар для посещаемости. Часы импортируются из ЛК.
            </p>

            <div>
              <Label htmlFor="modal-semester">Семестр *</Label>
              <select
                id="modal-semester"
                className="w-full px-3 py-2 bg-background border rounded-md text-sm"
                value={formData.semester_id}
                onChange={(e) => setFormData({ ...formData, semester_id: Number(e.target.value) })}
                required
              >
                {semesters.map((semester) => (
                  <option key={semester.id} value={semester.id}>
                    {semester.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex gap-2 pt-2">
              <Button type="button" variant="outline" className="flex-1" onClick={closeModal}>
                Отмена
              </Button>
              <Button type="submit" className="flex-1" disabled={isMutating}>
                {isMutating ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : editingSubject ? (
                  'Сохранить'
                ) : (
                  'Добавить'
                )}
              </Button>
            </div>
          </form>
        </Modal>

        {/* Delete confirmation modal */}
        <Modal
          open={deleteConfirmSubject !== null}
          onClose={() => setDeleteConfirmSubject(null)}
          title="Удалить предмет?"
        >
          <p className="text-muted-foreground mb-4">
            Вы уверены, что хотите удалить предмет "{deleteConfirmSubject?.name}"?
            Это действие нельзя отменить.
          </p>
          <div className="flex gap-2">
            <Button
              type="button"
              variant="outline"
              className="flex-1"
              onClick={() => setDeleteConfirmSubject(null)}
            >
              Отмена
            </Button>
            <Button
              type="button"
              variant="destructive"
              className="flex-1"
              disabled={deleteMutation.isPending}
              onClick={() => deleteConfirmSubject && deleteMutation.mutate(deleteConfirmSubject.id)}
            >
              {deleteMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                'Удалить'
              )}
            </Button>
          </div>
        </Modal>
      </div>
    </div>
  )
}

export default SubjectsPage
