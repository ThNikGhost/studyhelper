import { useState, useMemo, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Plus,
  Pencil,
  Trash2,
  ArrowLeft,
  Users,
  Mail,
  Phone,
  Send,
  User,
  Camera,
  Loader2,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import classmateService from '@/services/classmateService'
import uploadService from '@/services/uploadService'
import type { Classmate, ClassmateCreate } from '@/types/classmate'

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
      <Card className="relative z-10 w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>{children}</CardContent>
      </Card>
    </div>
  )
}

// Avatar component
function Avatar({
  src,
  size = 'md',
  className = '',
}: {
  src: string | null | undefined
  size?: 'sm' | 'md' | 'lg'
  className?: string
}) {
  const sizeClasses = {
    sm: 'w-20 h-20',
    md: 'w-20 h-20',
    lg: 'w-24 h-24',
  }

  const iconSizes = {
    sm: 'h-10 w-10',
    md: 'h-10 w-10',
    lg: 'h-12 w-12',
  }

  if (src) {
    return (
      <img
        src={src}
        alt="Avatar"
        className={`${sizeClasses[size]} rounded-full object-cover ${className}`}
      />
    )
  }

  return (
    <div
      className={`${sizeClasses[size]} rounded-full bg-primary/10 flex items-center justify-center ${className}`}
    >
      <User className={`${iconSizes[size]} text-primary`} />
    </div>
  )
}

// Default form data
const defaultFormData: ClassmateCreate = {
  full_name: '',
  short_name: null,
  email: null,
  phone: null,
  telegram: null,
  vk: null,
  photo_url: null,
  group_name: null,
  subgroup: null,
  notes: null,
}

export function ClassmatesPage() {
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [editingClassmate, setEditingClassmate] = useState<Classmate | null>(null)
  const [viewingClassmate, setViewingClassmate] = useState<Classmate | null>(null)
  const [deleteConfirmClassmate, setDeleteConfirmClassmate] = useState<Classmate | null>(null)
  const [formData, setFormData] = useState<ClassmateCreate>(defaultFormData)
  const [isUploading, setIsUploading] = useState(false)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)

  // Fetch classmates
  const {
    data: classmates = [],
    isLoading,
    error,
    refetch,
  } = useQuery<Classmate[]>({
    queryKey: ['classmates'],
    queryFn: () => classmateService.getClassmates(),
  })

  // Group classmates by subgroup
  const groupedClassmates = useMemo(() => {
    const groups: Record<string, Classmate[]> = {}

    classmates.forEach((classmate) => {
      const key = classmate.subgroup ? String(classmate.subgroup) : 'none'
      if (!groups[key]) {
        groups[key] = []
      }
      groups[key].push(classmate)
    })

    // Sort groups: numbered first, then "none"
    const sortedKeys = Object.keys(groups).sort((a, b) => {
      if (a === 'none') return 1
      if (b === 'none') return -1
      return Number(a) - Number(b)
    })

    return sortedKeys.map((key) => ({
      subgroup: key,
      label: key === 'none' ? 'Без подгруппы' : `${key} подгруппа`,
      classmates: groups[key],
    }))
  }, [classmates])

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: ClassmateCreate) => classmateService.createClassmate(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['classmates'] })
      closeFormModal()
    },
  })

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<ClassmateCreate> }) =>
      classmateService.updateClassmate(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['classmates'] })
      closeFormModal()
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => classmateService.deleteClassmate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['classmates'] })
      setDeleteConfirmClassmate(null)
      setViewingClassmate(null)
    },
  })

  // Handle file selection
  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      alert('Допустимые форматы: JPEG, PNG, WebP')
      return
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('Максимальный размер файла: 5MB')
      return
    }

    // Show preview
    const reader = new FileReader()
    reader.onload = (e) => {
      setPreviewUrl(e.target?.result as string)
    }
    reader.readAsDataURL(file)

    // Upload file
    setIsUploading(true)
    try {
      const response = await uploadService.uploadAvatar(file)
      setFormData((prev) => ({ ...prev, photo_url: response.url }))
    } catch {
      alert('Ошибка загрузки файла')
      setPreviewUrl(null)
    } finally {
      setIsUploading(false)
    }
  }

  // Modal handlers
  const openAddModal = () => {
    setFormData(defaultFormData)
    setEditingClassmate(null)
    setPreviewUrl(null)
    setIsAddModalOpen(true)
  }

  const openEditModal = (classmate: Classmate) => {
    setFormData({
      full_name: classmate.full_name,
      short_name: classmate.short_name,
      email: classmate.email,
      phone: classmate.phone,
      telegram: classmate.telegram,
      vk: classmate.vk,
      photo_url: classmate.photo_url,
      group_name: classmate.group_name,
      subgroup: classmate.subgroup,
      notes: classmate.notes,
    })
    setEditingClassmate(classmate)
    setPreviewUrl(classmate.photo_url)
    setViewingClassmate(null)
    setIsAddModalOpen(true)
  }

  const closeFormModal = () => {
    setIsAddModalOpen(false)
    setEditingClassmate(null)
    setFormData(defaultFormData)
    setPreviewUrl(null)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Clean up empty strings to null
    const cleanedData: ClassmateCreate = {
      full_name: formData.full_name.trim(),
      short_name: formData.short_name?.trim() || null,
      email: formData.email?.trim() || null,
      phone: formData.phone?.trim() || null,
      telegram: formData.telegram?.trim() || null,
      vk: formData.vk?.trim() || null,
      photo_url: formData.photo_url || null,
      group_name: formData.group_name?.trim() || null,
      subgroup: formData.subgroup,
      notes: formData.notes?.trim() || null,
    }

    if (editingClassmate) {
      updateMutation.mutate({ id: editingClassmate.id, data: cleanedData })
    } else {
      createMutation.mutate(cleanedData)
    }
  }

  const handleInputChange = (field: keyof ClassmateCreate, value: string | number | null) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const removeAvatar = () => {
    setFormData((prev) => ({ ...prev, photo_url: null }))
    setPreviewUrl(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const isMutating =
    createMutation.isPending || updateMutation.isPending || deleteMutation.isPending

  // Get display name (short_name or first name from full_name)
  const getDisplayName = (classmate: Classmate): string => {
    if (classmate.short_name) return classmate.short_name
    // Get first name from full_name (e.g., "Иванов Иван Иванович" -> "Иван")
    const parts = classmate.full_name.split(' ')
    return parts.length > 1 ? parts[1] : parts[0]
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container max-w-2xl mx-auto px-4 py-6">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-muted rounded w-1/3" />
            <div className="grid grid-cols-4 gap-3">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div key={i} className="aspect-square bg-muted rounded" />
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
              <p className="text-destructive mb-4">Ошибка загрузки одногруппников</p>
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
          <h1 className="text-2xl font-bold flex-1">Одногруппники</h1>
          <Button size="icon" onClick={openAddModal}>
            <Plus className="h-5 w-5" />
          </Button>
        </div>

        {/* Grouped classmates */}
        {groupedClassmates.map((group) => (
          <div key={group.subgroup} className="mb-6">
            <h2 className="text-lg font-semibold mb-3 text-muted-foreground">{group.label}</h2>
            <div className="grid grid-cols-4 gap-3">
              {group.classmates.map((classmate) => (
                <button
                  key={classmate.id}
                  onClick={() => setViewingClassmate(classmate)}
                  className="aspect-square rounded-lg border bg-card hover:bg-accent hover:border-primary transition-colors flex flex-col items-center justify-center p-2 text-center cursor-pointer"
                >
                  <Avatar src={classmate.photo_url} size="sm" className="mb-1" />
                  <span className="text-sm font-medium truncate w-full">
                    {getDisplayName(classmate)}
                  </span>
                </button>
              ))}
            </div>
          </div>
        ))}

        {/* Empty state */}
        {classmates.length === 0 && (
          <Card>
            <CardContent className="py-10 text-center text-muted-foreground">
              <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Нет одногруппников</p>
              <p className="text-sm mt-1">Добавьте первого одногруппника</p>
              <Button className="mt-4" onClick={openAddModal}>
                <Plus className="h-4 w-4 mr-2" />
                Добавить
              </Button>
            </CardContent>
          </Card>
        )}

        {/* View classmate modal */}
        <Modal
          open={viewingClassmate !== null}
          onClose={() => setViewingClassmate(null)}
          title={viewingClassmate?.full_name || ''}
        >
          {viewingClassmate && (
            <div className="space-y-4">
              {/* Avatar and info */}
              <div className="flex items-center gap-4">
                <Avatar src={viewingClassmate.photo_url} size="md" />
                <div>
                  {viewingClassmate.short_name && (
                    <p className="text-sm text-muted-foreground">{viewingClassmate.short_name}</p>
                  )}
                  {viewingClassmate.subgroup && (
                    <p className="text-sm text-muted-foreground">
                      {viewingClassmate.subgroup} подгруппа
                    </p>
                  )}
                </div>
              </div>

              {/* Contacts */}
              <div className="space-y-2">
                {viewingClassmate.phone && (
                  <a
                    href={`tel:${viewingClassmate.phone}`}
                    className="flex items-center gap-3 p-3 rounded-lg bg-muted hover:bg-accent transition-colors"
                  >
                    <Phone className="h-5 w-5 text-green-500" />
                    <span>{viewingClassmate.phone}</span>
                  </a>
                )}
                {viewingClassmate.email && (
                  <a
                    href={`mailto:${viewingClassmate.email}`}
                    className="flex items-center gap-3 p-3 rounded-lg bg-muted hover:bg-accent transition-colors"
                  >
                    <Mail className="h-5 w-5 text-blue-500" />
                    <span>{viewingClassmate.email}</span>
                  </a>
                )}
                {viewingClassmate.telegram && (
                  <a
                    href={`https://t.me/${viewingClassmate.telegram.replace('@', '')}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-3 p-3 rounded-lg bg-muted hover:bg-accent transition-colors"
                  >
                    <Send className="h-5 w-5 text-sky-500" />
                    <span>{viewingClassmate.telegram}</span>
                  </a>
                )}
                {viewingClassmate.vk && (
                  <a
                    href={viewingClassmate.vk}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-3 p-3 rounded-lg bg-muted hover:bg-accent transition-colors"
                  >
                    <span className="w-5 h-5 flex items-center justify-center text-blue-600 font-bold text-sm">
                      VK
                    </span>
                    <span className="truncate">{viewingClassmate.vk}</span>
                  </a>
                )}
              </div>

              {/* No contacts message */}
              {!viewingClassmate.phone &&
                !viewingClassmate.email &&
                !viewingClassmate.telegram &&
                !viewingClassmate.vk && (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    Контакты не указаны
                  </p>
                )}

              {/* Notes */}
              {viewingClassmate.notes && (
                <div className="p-3 rounded-lg bg-muted">
                  <p className="text-sm text-muted-foreground">{viewingClassmate.notes}</p>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-2 pt-2">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => openEditModal(viewingClassmate)}
                >
                  <Pencil className="h-4 w-4 mr-2" />
                  Редактировать
                </Button>
                <Button
                  variant="destructive"
                  size="icon"
                  onClick={() => setDeleteConfirmClassmate(viewingClassmate)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </Modal>

        {/* Add/Edit Modal */}
        <Modal
          open={isAddModalOpen}
          onClose={closeFormModal}
          title={editingClassmate ? 'Редактировать' : 'Новый одногруппник'}
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Avatar upload */}
            <div className="flex flex-col items-center gap-2">
              <div className="relative">
                {previewUrl || formData.photo_url ? (
                  <img
                    src={previewUrl || formData.photo_url || ''}
                    alt="Avatar preview"
                    className="w-24 h-24 rounded-full object-cover"
                  />
                ) : (
                  <div className="w-24 h-24 rounded-full bg-primary/10 flex items-center justify-center">
                    <User className="h-12 w-12 text-primary" />
                  </div>
                )}
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                  className="absolute bottom-0 right-0 w-9 h-9 rounded-full bg-primary text-primary-foreground flex items-center justify-center hover:bg-primary/90 transition-colors disabled:opacity-50"
                >
                  {isUploading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Camera className="h-4 w-4" />
                  )}
                </button>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={handleFileSelect}
                className="hidden"
              />
              {(previewUrl || formData.photo_url) && (
                <button
                  type="button"
                  onClick={removeAvatar}
                  className="text-xs text-destructive hover:underline"
                >
                  Удалить фото
                </button>
              )}
            </div>

            <div>
              <Label htmlFor="full_name">Полное имя *</Label>
              <Input
                id="full_name"
                value={formData.full_name}
                onChange={(e) => handleInputChange('full_name', e.target.value)}
                placeholder="Иванов Иван Иванович"
                required
              />
            </div>

            <div>
              <Label htmlFor="short_name">Краткое имя</Label>
              <Input
                id="short_name"
                value={formData.short_name || ''}
                onChange={(e) => handleInputChange('short_name', e.target.value)}
                placeholder="Ваня"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="group_name">Группа</Label>
                <Input
                  id="group_name"
                  value={formData.group_name || ''}
                  onChange={(e) => handleInputChange('group_name', e.target.value)}
                  placeholder="ИВТ-101"
                />
              </div>
              <div>
                <Label htmlFor="subgroup">Подгруппа</Label>
                <Input
                  id="subgroup"
                  type="number"
                  min={1}
                  max={10}
                  value={formData.subgroup || ''}
                  onChange={(e) =>
                    handleInputChange('subgroup', e.target.value ? Number(e.target.value) : null)
                  }
                  placeholder="1"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="phone">Телефон</Label>
              <Input
                id="phone"
                type="tel"
                value={formData.phone || ''}
                onChange={(e) => handleInputChange('phone', e.target.value)}
                placeholder="+7 (999) 123-45-67"
              />
            </div>

            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={formData.email || ''}
                onChange={(e) => handleInputChange('email', e.target.value)}
                placeholder="email@example.com"
              />
            </div>

            <div>
              <Label htmlFor="telegram">Telegram</Label>
              <Input
                id="telegram"
                value={formData.telegram || ''}
                onChange={(e) => handleInputChange('telegram', e.target.value)}
                placeholder="@username"
              />
            </div>

            <div>
              <Label htmlFor="vk">VK (ссылка)</Label>
              <Input
                id="vk"
                type="url"
                value={formData.vk || ''}
                onChange={(e) => handleInputChange('vk', e.target.value)}
                placeholder="https://vk.com/username"
              />
            </div>

            <div>
              <Label htmlFor="notes">Заметки</Label>
              <textarea
                id="notes"
                value={formData.notes || ''}
                onChange={(e) => handleInputChange('notes', e.target.value)}
                placeholder="Дополнительная информация..."
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              />
            </div>

            <div className="flex gap-2 pt-2">
              <Button type="button" variant="outline" className="flex-1" onClick={closeFormModal}>
                Отмена
              </Button>
              <Button type="submit" className="flex-1" disabled={isMutating || isUploading}>
                {editingClassmate ? 'Сохранить' : 'Создать'}
              </Button>
            </div>
          </form>
        </Modal>

        {/* Delete confirmation modal */}
        <Modal
          open={deleteConfirmClassmate !== null}
          onClose={() => setDeleteConfirmClassmate(null)}
          title="Удалить одногруппника?"
        >
          <p className="text-muted-foreground mb-4">
            Вы уверены, что хотите удалить {deleteConfirmClassmate?.full_name}? Это действие нельзя
            отменить.
          </p>
          <div className="flex gap-2">
            <Button
              type="button"
              variant="outline"
              className="flex-1"
              onClick={() => setDeleteConfirmClassmate(null)}
            >
              Отмена
            </Button>
            <Button
              type="button"
              variant="destructive"
              className="flex-1"
              disabled={isMutating}
              onClick={() =>
                deleteConfirmClassmate && deleteMutation.mutate(deleteConfirmClassmate.id)
              }
            >
              Удалить
            </Button>
          </div>
        </Modal>
      </div>
    </div>
  )
}

export default ClassmatesPage
