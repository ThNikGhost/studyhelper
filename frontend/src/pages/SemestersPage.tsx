import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Pencil, Trash2, ArrowLeft, Calendar, Check } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import subjectService from '@/services/subjectService'
import type { Semester, SemesterCreate } from '@/types/subject'

// Simple modal component
function Modal({
  open,
  onClose,
  title,
  children,
}: {
  open: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
}) {
  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      <Card className="relative z-10 w-full max-w-md mx-4">
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>{children}</CardContent>
      </Card>
    </div>
  )
}

// Get current academic year
function getCurrentAcademicYear(): { yearStart: number; yearEnd: number } {
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth() + 1 // 1-12
  // Academic year starts in September
  if (month >= 9) {
    return { yearStart: year, yearEnd: year + 1 }
  }
  return { yearStart: year - 1, yearEnd: year }
}

export function SemestersPage() {
  const queryClient = useQueryClient()
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [editingSemester, setEditingSemester] = useState<Semester | null>(null)
  const [deleteConfirmSemester, setDeleteConfirmSemester] = useState<Semester | null>(null)

  // Default form values
  const { yearStart, yearEnd } = getCurrentAcademicYear()
  const defaultFormData: SemesterCreate = {
    number: 1,
    year_start: yearStart,
    year_end: yearEnd,
    name: '',
  }

  const [formData, setFormData] = useState<SemesterCreate>(defaultFormData)

  // Fetch semesters
  const {
    data: semesters = [],
    isLoading,
    error,
    refetch,
  } = useQuery<Semester[]>({
    queryKey: ['semesters'],
    queryFn: () => subjectService.getSemesters(),
  })

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: SemesterCreate) => subjectService.createSemester(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['semesters'] })
      closeModal()
    },
  })

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<SemesterCreate> }) =>
      subjectService.updateSemester(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['semesters'] })
      closeModal()
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => subjectService.deleteSemester(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['semesters'] })
      setDeleteConfirmSemester(null)
    },
  })

  // Set current mutation
  const setCurrentMutation = useMutation({
    mutationFn: (id: number) => subjectService.setCurrentSemester(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['semesters'] })
    },
  })

  // Generate semester name
  const generateName = (number: number, yearStart: number, yearEnd: number): string => {
    const season = number % 2 === 1 ? 'Осенний' : 'Весенний'
    return `${season} семестр ${yearStart}/${yearEnd}`
  }

  // Modal handlers
  const openAddModal = () => {
    const name = generateName(defaultFormData.number, defaultFormData.year_start, defaultFormData.year_end)
    setFormData({ ...defaultFormData, name })
    setEditingSemester(null)
    setIsAddModalOpen(true)
  }

  const openEditModal = (semester: Semester) => {
    setFormData({
      number: semester.number,
      year_start: semester.year_start,
      year_end: semester.year_end,
      name: semester.name,
    })
    setEditingSemester(semester)
    setIsAddModalOpen(true)
  }

  const closeModal = () => {
    setIsAddModalOpen(false)
    setEditingSemester(null)
    setFormData(defaultFormData)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (editingSemester) {
      updateMutation.mutate({ id: editingSemester.id, data: formData })
    } else {
      createMutation.mutate(formData)
    }
  }

  // Auto-update name when number or years change
  const handleFieldChange = (field: keyof SemesterCreate, value: number | string) => {
    const newData = { ...formData, [field]: value }

    // Auto-generate name if not manually edited
    if (field !== 'name') {
      const autoName = generateName(
        field === 'number' ? (value as number) : newData.number,
        field === 'year_start' ? (value as number) : newData.year_start,
        field === 'year_end' ? (value as number) : newData.year_end
      )
      newData.name = autoName
    }

    setFormData(newData)
  }

  const isMutating =
    createMutation.isPending ||
    updateMutation.isPending ||
    deleteMutation.isPending ||
    setCurrentMutation.isPending

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container max-w-2xl mx-auto px-4 py-6">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-muted rounded w-1/3" />
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
              <p className="text-destructive mb-4">Ошибка загрузки семестров</p>
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
          <h1 className="text-2xl font-bold flex-1">Семестры</h1>
        </div>

        {/* Add button */}
        <Button className="w-full mb-6" onClick={openAddModal}>
          <Plus className="h-4 w-4 mr-2" />
          Добавить семестр
        </Button>

        {/* Semesters list */}
        <div className="space-y-3">
          {semesters.map((semester) => (
            <Card key={semester.id} className={semester.is_current ? 'border-primary' : ''}>
              <CardContent className="py-4 px-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-blue-500 shrink-0" />
                      <h3 className="font-medium">{semester.name}</h3>
                      {semester.is_current && (
                        <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded">
                          текущий
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      Семестр #{semester.number} • {semester.year_start}/{semester.year_end}
                    </p>
                  </div>
                  <div className="flex gap-1 shrink-0">
                    {!semester.is_current && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setCurrentMutation.mutate(semester.id)}
                        disabled={isMutating}
                        title="Сделать текущим"
                      >
                        <Check className="h-4 w-4" />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => openEditModal(semester)}
                      title="Редактировать"
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setDeleteConfirmSemester(semester)}
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
        {semesters.length === 0 && (
          <Card>
            <CardContent className="py-10 text-center text-muted-foreground">
              <Calendar className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Нет семестров</p>
              <p className="text-sm mt-1">Создайте первый семестр</p>
            </CardContent>
          </Card>
        )}

        {/* Add/Edit Modal */}
        <Modal
          open={isAddModalOpen}
          onClose={closeModal}
          title={editingSemester ? 'Редактировать семестр' : 'Новый семестр'}
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="name">Название *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Осенний семестр 2025/2026"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="year_start">Год начала *</Label>
                <Input
                  id="year_start"
                  type="number"
                  min={2000}
                  max={2100}
                  value={formData.year_start}
                  onChange={(e) => handleFieldChange('year_start', Number(e.target.value))}
                  required
                />
              </div>
              <div>
                <Label htmlFor="year_end">Год окончания *</Label>
                <Input
                  id="year_end"
                  type="number"
                  min={2000}
                  max={2100}
                  value={formData.year_end}
                  onChange={(e) => handleFieldChange('year_end', Number(e.target.value))}
                  required
                />
              </div>
            </div>

            <div>
              <Label htmlFor="number">Номер семестра *</Label>
              <Input
                id="number"
                type="number"
                min={1}
                max={12}
                value={formData.number}
                onChange={(e) => handleFieldChange('number', Number(e.target.value))}
                required
              />
              <p className="text-xs text-muted-foreground mt-1">
                Нечётный = осенний, чётный = весенний
              </p>
            </div>

            <div className="flex gap-2 pt-2">
              <Button type="button" variant="outline" className="flex-1" onClick={closeModal}>
                Отмена
              </Button>
              <Button type="submit" className="flex-1" disabled={isMutating}>
                {editingSemester ? 'Сохранить' : 'Создать'}
              </Button>
            </div>
          </form>
        </Modal>

        {/* Delete confirmation modal */}
        <Modal
          open={deleteConfirmSemester !== null}
          onClose={() => setDeleteConfirmSemester(null)}
          title="Удалить семестр?"
        >
          <p className="text-muted-foreground mb-4">
            Вы уверены, что хотите удалить семестр "{deleteConfirmSemester?.name}"? Все связанные
            предметы также будут удалены. Это действие нельзя отменить.
          </p>
          <div className="flex gap-2">
            <Button
              type="button"
              variant="outline"
              className="flex-1"
              onClick={() => setDeleteConfirmSemester(null)}
            >
              Отмена
            </Button>
            <Button
              type="button"
              variant="destructive"
              className="flex-1"
              disabled={isMutating}
              onClick={() => deleteConfirmSemester && deleteMutation.mutate(deleteConfirmSemester.id)}
            >
              Удалить
            </Button>
          </div>
        </Modal>
      </div>
    </div>
  )
}

export default SemestersPage
