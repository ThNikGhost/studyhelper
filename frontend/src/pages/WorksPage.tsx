import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNetworkStatus } from '@/hooks/useNetworkStatus'
import {
  Plus,
  Pencil,
  Trash2,
  RefreshCw,
  ArrowLeft,
  ClipboardList,
  Calendar,
  Filter,
  Loader2,
  X,
  Clock,
  Paperclip,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Modal } from '@/components/ui/modal'
import { toast } from 'sonner'
import {
  formatDeadline,
  getDeadlineColor,
  appendTimezoneOffset,
  toLocalDatetimeString,
} from '@/lib/dateUtils'
import { useUserSettings } from '@/hooks/useUserSettings'
import workService from '@/services/workService'
import subjectService from '@/services/subjectService'
import { WorkFilesModal } from '@/components/WorkFilesModal'
import type {
  WorkWithStatus,
  WorkCreate,
  WorkType,
  WorkStatus,
  WorkStatusUpdate,
} from '@/types/work'
import {
  WorkType as WorkTypeConst,
  WorkStatus as WorkStatusConst,
  workTypeLabels,
  workStatusLabels,
  workStatusColors,
} from '@/types/work'
import type { Subject, Semester } from '@/types/subject'

export function WorksPage() {
  const isOnline = useNetworkStatus()
  const queryClient = useQueryClient()
  const { settings } = useUserSettings()
  const fullyHiddenIds = useMemo(() => {
    const hs = settings.hiddenSubjects
    const ids = new Set<number>()
    for (const [id, types] of Object.entries(hs)) {
      if (types === null) ids.add(Number(id))
    }
    return ids
  }, [settings.hiddenSubjects])
  const [filterSubjectId, setFilterSubjectId] = useState<number | undefined>(undefined)
  const [filterStatus, setFilterStatus] = useState<WorkStatus | undefined>(undefined)
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [editingWork, setEditingWork] = useState<WorkWithStatus | null>(null)
  const [deleteConfirmWork, setDeleteConfirmWork] = useState<WorkWithStatus | null>(null)
  const [statusModalWork, setStatusModalWork] = useState<WorkWithStatus | null>(null)
  const [filesModalWork, setFilesModalWork] = useState<WorkWithStatus | null>(null)

  // Form state for work
  const [formData, setFormData] = useState<WorkCreate>({
    title: '',
    description: '',
    work_type: WorkTypeConst.HOMEWORK,
    deadline: '',
    max_grade: undefined,
    subject_id: 0,
  })

  // Split date/time state for deadline
  const [deadlineDate, setDeadlineDate] = useState('')
  const [deadlineTime, setDeadlineTime] = useState('')

  // Batch mode state
  interface BatchRow {
    title: string
    deadlineDate: string
    deadlineTime: string
  }
  const [isBatchMode, setIsBatchMode] = useState(false)
  const [batchRows, setBatchRows] = useState<BatchRow[]>([
    { title: '', deadlineDate: '', deadlineTime: '' },
  ])

  // Form state for status
  const [statusForm, setStatusForm] = useState<WorkStatusUpdate>({
    status: undefined,
    grade: undefined,
    notes: '',
  })

  // Fetch current semester to filter subjects in the create/edit form
  const { data: currentSemester, isSuccess: semesterLoaded } = useQuery<Semester | null>({
    queryKey: ['semesters', 'current'],
    queryFn: ({ signal }) => subjectService.getCurrentSemester(signal),
  })

  // All subjects — for getSubjectName() and edit modal (works may span past semesters)
  const { data: allSubjects = [] } = useQuery<Subject[]>({
    queryKey: ['subjects'],
    queryFn: ({ signal }) => subjectService.getSubjects(undefined, signal),
  })

  // Current-semester subjects — for the create/edit form only
  const { data: subjects = [] } = useQuery<Subject[]>({
    queryKey: ['subjects', currentSemester?.id],
    queryFn: ({ signal }) => subjectService.getSubjects(currentSemester?.id, signal),
    enabled: semesterLoaded,
  })

  // Fetch works
  const {
    data: works = [],
    isLoading,
    error,
    refetch,
  } = useQuery<WorkWithStatus[]>({
    queryKey: ['works', filterSubjectId, filterStatus],
    queryFn: ({ signal }) =>
      workService.getWorks(
        { subject_id: filterSubjectId, status: filterStatus },
        signal,
      ),
  })

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: WorkCreate) => workService.createWork(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['works'] })
      toast.success('Работа добавлена')
      closeModal()
    },
    onError: () => {
      toast.error('Не удалось добавить работу')
    },
  })

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<WorkCreate> }) =>
      workService.updateWork(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['works'] })
      toast.success('Работа обновлена')
      closeModal()
    },
    onError: () => {
      toast.error('Не удалось обновить работу')
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => workService.deleteWork(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['works'] })
      toast.success('Работа удалена')
      setDeleteConfirmWork(null)
    },
    onError: () => {
      toast.error('Не удалось удалить работу')
    },
  })

  // Update status mutation
  const updateStatusMutation = useMutation({
    mutationFn: ({ workId, data }: { workId: number; data: WorkStatusUpdate }) =>
      workService.updateWorkStatus(workId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['works'] })
      toast.success('Статус обновлён')
      setStatusModalWork(null)
    },
    onError: () => {
      toast.error('Не удалось обновить статус')
    },
  })

  // Modal handlers
  const openAddModal = () => {
    setFormData({
      title: '',
      description: '',
      work_type: WorkTypeConst.HOMEWORK,
      deadline: '',
      max_grade: undefined,
      subject_id: subjects[0]?.id || 0,
    })
    setDeadlineDate('')
    setDeadlineTime('')
    setIsBatchMode(false)
    setBatchRows([{ title: '', deadlineDate: '', deadlineTime: '' }])
    setEditingWork(null)
    setIsAddModalOpen(true)
  }

  const openEditModal = (work: WorkWithStatus) => {
    let date = ''
    let time = ''
    if (work.deadline) {
      const local = toLocalDatetimeString(work.deadline)
      date = local.slice(0, 10)
      time = work.deadline_has_time ? local.slice(11, 16) : ''
    }
    setFormData({
      title: work.title,
      description: work.description || '',
      work_type: work.work_type,
      deadline: work.deadline || '',
      max_grade: work.max_grade ?? undefined,
      subject_id: work.subject_id,
    })
    setDeadlineDate(date)
    setDeadlineTime(time)
    setIsBatchMode(false)
    setEditingWork(work)
    setIsAddModalOpen(true)
  }

  const openStatusModal = (work: WorkWithStatus) => {
    setStatusForm({
      status: work.my_status?.status || WorkStatusConst.NOT_STARTED,
      grade: work.my_status?.grade ?? undefined,
      notes: work.my_status?.notes || '',
    })
    setStatusModalWork(work)
  }

  const closeModal = () => {
    setIsAddModalOpen(false)
    setEditingWork(null)
    setFormData({
      title: '',
      description: '',
      work_type: WorkTypeConst.HOMEWORK,
      deadline: '',
      max_grade: undefined,
      subject_id: 0,
    })
    setDeadlineDate('')
    setDeadlineTime('')
    setIsBatchMode(false)
    setBatchRows([{ title: '', deadlineDate: '', deadlineTime: '' }])
  }

  /** Build deadline + deadline_has_time from date/time inputs. */
  const buildDeadline = (date: string, time: string) => {
    if (!date) return { deadline: null, deadline_has_time: true }
    if (time) {
      return {
        deadline: appendTimezoneOffset(`${date}T${time}`),
        deadline_has_time: true,
      }
    }
    // Date only — store as 23:59 local (end of day), flag false
    return {
      deadline: appendTimezoneOffset(`${date}T23:59`),
      deadline_has_time: false,
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const { deadline, deadline_has_time } = buildDeadline(deadlineDate, deadlineTime)
    const submitData = {
      ...formData,
      deadline,
      deadline_has_time,
      max_grade: formData.max_grade || null,
    }
    if (editingWork) {
      updateMutation.mutate({ id: editingWork.id, data: submitData })
    } else {
      createMutation.mutate(submitData as WorkCreate)
    }
  }

  // Batch submit
  const batchCreateMutation = useMutation({
    mutationFn: async (items: WorkCreate[]) => {
      const results = await Promise.allSettled(items.map((d) => workService.createWork(d)))
      const succeeded = results.filter((r) => r.status === 'fulfilled').length
      const failed = results.filter((r) => r.status === 'rejected').length
      return { succeeded, failed }
    },
    onSuccess: ({ succeeded, failed }) => {
      queryClient.invalidateQueries({ queryKey: ['works'] })
      if (failed === 0) {
        toast.success(`Добавлено работ: ${succeeded}`)
        closeModal()
      } else {
        toast.warning(`Добавлено: ${succeeded}, ошибок: ${failed}`)
        // modal remains open so the user can retry failed rows
      }
    },
    onError: () => {
      toast.error('Не удалось добавить работы')
    },
  })

  const handleBatchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const validRows = batchRows.filter((r) => r.title.trim())
    if (validRows.length === 0) return

    const items: WorkCreate[] = validRows.map((row) => {
      const { deadline, deadline_has_time } = buildDeadline(row.deadlineDate, row.deadlineTime)
      return {
        title: row.title.trim(),
        description: formData.description || null,
        work_type: formData.work_type,
        deadline,
        deadline_has_time,
        max_grade: formData.max_grade || null,
        subject_id: formData.subject_id,
      }
    })

    batchCreateMutation.mutate(items)
  }

  const handleStatusSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (statusModalWork) {
      updateStatusMutation.mutate({
        workId: statusModalWork.id,
        data: statusForm,
      })
    }
  }

  const isMutating =
    createMutation.isPending ||
    updateMutation.isPending ||
    deleteMutation.isPending ||
    updateStatusMutation.isPending ||
    batchCreateMutation.isPending

  // Get subject name by id (uses all subjects to handle works from past semesters)
  const getSubjectName = (id: number) => {
    const subject = allSubjects.find((s) => s.id === id)
    return subject?.short_name || subject?.name || `Предмет ${id}`
  }

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
                <div key={i} className="h-32 bg-muted rounded" />
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
              <p className="text-destructive mb-4">Ошибка загрузки работ</p>
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
          <h1 className="text-2xl font-bold flex-1">Работы</h1>
          <Button variant="ghost" size="icon" onClick={() => refetch()} title="Обновить">
            <RefreshCw className="h-5 w-5" />
          </Button>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardContent className="py-3 px-4">
            <div className="flex items-center gap-2 mb-2">
              <Filter className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Фильтры</span>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label htmlFor="filter-subject" className="text-xs">
                  Предмет
                </Label>
                <select
                  id="filter-subject"
                  className="w-full mt-1 px-2 py-1.5 bg-background border rounded-md text-sm"
                  value={filterSubjectId || ''}
                  onChange={(e) =>
                    setFilterSubjectId(e.target.value ? Number(e.target.value) : undefined)
                  }
                >
                  <option value="">Все предметы</option>
                  {subjects.filter((s) => !fullyHiddenIds.has(s.id)).map((subject) => (
                    <option key={subject.id} value={subject.id}>
                      {subject.short_name || subject.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <Label htmlFor="filter-status" className="text-xs">
                  Статус
                </Label>
                <select
                  id="filter-status"
                  className="w-full mt-1 px-2 py-1.5 bg-background border rounded-md text-sm"
                  value={filterStatus || ''}
                  onChange={(e) =>
                    setFilterStatus((e.target.value as WorkStatus) || undefined)
                  }
                >
                  <option value="">Все статусы</option>
                  {Object.entries(workStatusLabels).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Add button */}
        <Button
          className="w-full mb-6"
          onClick={openAddModal}
          disabled={!isOnline || !semesterLoaded || subjects.length === 0}
        >
          <Plus className="h-4 w-4 mr-2" />
          Добавить работу
        </Button>

        {/* Works list */}
        <div className="space-y-3">
          {works.filter((w) => !fullyHiddenIds.has(w.subject_id)).map((work) => (
            <Card key={work.id}>
              <CardContent className="py-4 px-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    {/* Title and type */}
                    <div className="flex items-center gap-2 flex-wrap">
                      <ClipboardList className="h-4 w-4 text-orange-500 shrink-0" />
                      <h3 className="font-medium">{work.title}</h3>
                      <span className="text-xs px-2 py-0.5 rounded bg-muted">
                        {workTypeLabels[work.work_type]}
                      </span>
                    </div>

                    {/* Subject */}
                    <p className="text-sm text-muted-foreground mt-1">
                      {getSubjectName(work.subject_id)}
                    </p>

                    {/* Deadline */}
                    {work.deadline && (
                      <div
                        className={`flex items-center gap-1 text-sm mt-2 ${getDeadlineColor(work.deadline)}`}
                      >
                        <Calendar className="h-3.5 w-3.5" />
                        <span>{formatDeadline(work.deadline, work.deadline_has_time)}</span>
                      </div>
                    )}

                    {/* Status badge - clickable */}
                    <button
                      onClick={() => openStatusModal(work)}
                      className={`inline-block mt-2 text-xs px-2 py-1 rounded cursor-pointer hover:opacity-80 transition-opacity ${
                        workStatusColors[work.my_status?.status || WorkStatusConst.NOT_STARTED]
                      }`}
                    >
                      {workStatusLabels[work.my_status?.status || WorkStatusConst.NOT_STARTED]}
                      {work.my_status?.grade !== null && work.my_status?.grade !== undefined && (
                        <span className="ml-1">
                          ({work.my_status.grade}
                          {work.max_grade ? `/${work.max_grade}` : ''})
                        </span>
                      )}
                    </button>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-1 shrink-0">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setFilesModalWork(work)}
                      title="Файлы работы"
                    >
                      <Paperclip className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => openEditModal(work)}
                      disabled={!isOnline}
                      title="Редактировать"
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setDeleteConfirmWork(work)}
                      disabled={!isOnline}
                      title="Удалить"
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Empty state */}
        {works.filter((w) => !fullyHiddenIds.has(w.subject_id)).length === 0 && (
          <Card>
            <CardContent className="py-10 text-center text-muted-foreground">
              <ClipboardList className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Нет работ</p>
              <p className="text-sm mt-1">Добавьте первую работу</p>
            </CardContent>
          </Card>
        )}

        {/* Add/Edit Work Modal */}
        <Modal
          open={isAddModalOpen}
          onClose={closeModal}
          title={editingWork ? 'Редактировать работу' : 'Новая работа'}
        >
          {/* Single/Batch toggle (only for new works) */}
          {!editingWork && (
            <div className="flex gap-1 mb-4 p-1 bg-muted rounded-lg">
              <button
                type="button"
                className={`flex-1 text-sm py-1.5 rounded-md transition-colors ${!isBatchMode ? 'bg-background shadow-sm font-medium' : 'text-muted-foreground hover:text-foreground'}`}
                onClick={() => setIsBatchMode(false)}
              >
                Одна работа
              </button>
              <button
                type="button"
                className={`flex-1 text-sm py-1.5 rounded-md transition-colors ${isBatchMode ? 'bg-background shadow-sm font-medium' : 'text-muted-foreground hover:text-foreground'}`}
                onClick={() => setIsBatchMode(true)}
              >
                Несколько работ
              </button>
            </div>
          )}

          <form onSubmit={isBatchMode ? handleBatchSubmit : handleSubmit} className="space-y-4">
            {/* Common fields: subject, type (always shown) */}
            {!isBatchMode && (
              <div>
                <Label htmlFor="title">Название *</Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="Лабораторная работа №1"
                  required
                />
              </div>
            )}

            <div>
              <Label htmlFor="subject">Предмет *</Label>
              <select
                id="subject"
                className="w-full px-3 py-2 bg-background border rounded-md text-sm"
                value={formData.subject_id}
                onChange={(e) => setFormData({ ...formData, subject_id: Number(e.target.value) })}
                required
              >
                <option value="">Выберите предмет</option>
                {(editingWork ? allSubjects : subjects).filter((s) => !fullyHiddenIds.has(s.id)).map((subject) => (
                  <option key={subject.id} value={subject.id}>
                    {subject.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <Label htmlFor="work_type">Тип работы *</Label>
              <select
                id="work_type"
                className="w-full px-3 py-2 bg-background border rounded-md text-sm"
                value={formData.work_type}
                onChange={(e) =>
                  setFormData({ ...formData, work_type: e.target.value as WorkType })
                }
                required
              >
                {Object.entries(workTypeLabels).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            {/* Deadline: split date/time (single mode only) */}
            {!isBatchMode && (
              <div>
                <Label>Дедлайн</Label>
                <div className="flex gap-2 mt-1">
                  <Input
                    type="date"
                    value={deadlineDate}
                    onChange={(e) => setDeadlineDate(e.target.value)}
                    className="flex-1"
                  />
                  <div className="relative flex-1">
                    <Input
                      type="time"
                      value={deadlineTime}
                      onChange={(e) => setDeadlineTime(e.target.value)}
                      placeholder="Время"
                      className={deadlineTime ? 'pr-8' : ''}
                    />
                    {deadlineTime && (
                      <button
                        type="button"
                        onClick={() => setDeadlineTime('')}
                        className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                        title="Убрать время"
                      >
                        <X className="h-3.5 w-3.5" />
                      </button>
                    )}
                  </div>
                </div>
                {deadlineDate && !deadlineTime && (
                  <p className="text-xs text-muted-foreground mt-1">
                    <Clock className="h-3 w-3 inline mr-1" />
                    Дедлайн привязан ко дню (без времени)
                  </p>
                )}
              </div>
            )}

            <div>
              <Label htmlFor="max_grade">Макс. оценка</Label>
              <Input
                id="max_grade"
                type="number"
                min="0"
                value={formData.max_grade ?? ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    max_grade: e.target.value ? Number(e.target.value) : undefined,
                  })
                }
                placeholder="100"
              />
            </div>

            <div>
              <Label htmlFor="description">Описание</Label>
              <textarea
                id="description"
                className="w-full px-3 py-2 bg-background border rounded-md text-sm min-h-[80px]"
                value={formData.description || ''}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Дополнительная информация"
              />
            </div>

            {/* Batch rows */}
            {isBatchMode && (
              <div>
                <Label>Работы *</Label>
                <div className="space-y-2 mt-1">
                  {batchRows.map((row, idx) => (
                    <div key={idx} className="flex gap-2 items-start">
                      <div className="flex-1 space-y-1">
                        <Input
                          value={row.title}
                          onChange={(e) => {
                            const updated = [...batchRows]
                            updated[idx] = { ...row, title: e.target.value }
                            setBatchRows(updated)
                          }}
                          placeholder={`Название работы ${idx + 1}`}
                          required
                        />
                        <div className="flex gap-2">
                          <Input
                            type="date"
                            value={row.deadlineDate}
                            onChange={(e) => {
                              const updated = [...batchRows]
                              updated[idx] = { ...row, deadlineDate: e.target.value }
                              setBatchRows(updated)
                            }}
                            className="flex-1"
                          />
                          <Input
                            type="time"
                            value={row.deadlineTime}
                            onChange={(e) => {
                              const updated = [...batchRows]
                              updated[idx] = { ...row, deadlineTime: e.target.value }
                              setBatchRows(updated)
                            }}
                            className="flex-1"
                          />
                        </div>
                      </div>
                      {batchRows.length > 1 && (
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          className="shrink-0 mt-1"
                          onClick={() => setBatchRows(batchRows.filter((_, i) => i !== idx))}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="mt-2 w-full"
                  onClick={() =>
                    setBatchRows([...batchRows, { title: '', deadlineDate: '', deadlineTime: '' }])
                  }
                >
                  <Plus className="h-3.5 w-3.5 mr-1" />
                  Добавить строку
                </Button>
              </div>
            )}

            <div className="flex gap-2 pt-2">
              <Button type="button" variant="outline" className="flex-1" onClick={closeModal}>
                Отмена
              </Button>
              <Button type="submit" className="flex-1" disabled={isMutating}>
                {isMutating ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : editingWork ? (
                  'Сохранить'
                ) : isBatchMode ? (
                  `Добавить (${batchRows.filter((r) => r.title.trim()).length})`
                ) : (
                  'Добавить'
                )}
              </Button>
            </div>
          </form>
        </Modal>

        {/* Status Modal */}
        <Modal
          open={statusModalWork !== null}
          onClose={() => setStatusModalWork(null)}
          title="Изменить статус"
        >
          <form onSubmit={handleStatusSubmit} className="space-y-4">
            <div>
              <Label htmlFor="status">Статус</Label>
              <select
                id="status"
                className="w-full px-3 py-2 bg-background border rounded-md text-sm"
                value={statusForm.status || ''}
                onChange={(e) =>
                  setStatusForm({ ...statusForm, status: e.target.value as WorkStatus })
                }
              >
                {Object.entries(workStatusLabels).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <Label htmlFor="grade">
                Оценка {statusModalWork?.max_grade ? `(макс: ${statusModalWork.max_grade})` : ''}
              </Label>
              <Input
                id="grade"
                type="number"
                min="0"
                max={statusModalWork?.max_grade ?? undefined}
                value={statusForm.grade ?? ''}
                onChange={(e) =>
                  setStatusForm({
                    ...statusForm,
                    grade: e.target.value ? Number(e.target.value) : undefined,
                  })
                }
                placeholder="Оценка"
              />
            </div>

            <div>
              <Label htmlFor="notes">Заметки</Label>
              <textarea
                id="notes"
                className="w-full px-3 py-2 bg-background border rounded-md text-sm min-h-[80px]"
                value={statusForm.notes || ''}
                onChange={(e) => setStatusForm({ ...statusForm, notes: e.target.value })}
                placeholder="Личные заметки"
              />
            </div>

            <div className="flex gap-2 pt-2">
              <Button
                type="button"
                variant="outline"
                className="flex-1"
                onClick={() => setStatusModalWork(null)}
              >
                Отмена
              </Button>
              <Button type="submit" className="flex-1" disabled={updateStatusMutation.isPending}>
                {updateStatusMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  'Сохранить'
                )}
              </Button>
            </div>
          </form>
        </Modal>

        {/* Work files modal */}
        {filesModalWork && (
          <WorkFilesModal
            work={filesModalWork}
            onClose={() => setFilesModalWork(null)}
          />
        )}

        {/* Delete confirmation modal */}
        <Modal
          open={deleteConfirmWork !== null}
          onClose={() => setDeleteConfirmWork(null)}
          title="Удалить работу?"
        >
          <p className="text-muted-foreground mb-4">
            Вы уверены, что хотите удалить работу "{deleteConfirmWork?.title}"? Это действие
            нельзя отменить.
          </p>
          <div className="flex gap-2">
            <Button
              type="button"
              variant="outline"
              className="flex-1"
              onClick={() => setDeleteConfirmWork(null)}
            >
              Отмена
            </Button>
            <Button
              type="button"
              variant="destructive"
              className="flex-1"
              disabled={deleteMutation.isPending}
              onClick={() => deleteConfirmWork && deleteMutation.mutate(deleteConfirmWork.id)}
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

export default WorksPage
