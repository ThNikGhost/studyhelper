import { useState, useMemo, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNetworkStatus } from '@/hooks/useNetworkStatus'
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
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Modal } from '@/components/ui/modal'
import { toast } from 'sonner'
import classmateService from '@/services/classmateService'
import uploadService from '@/services/uploadService'
import type {
  Classmate,
  ClassmateBase,
  ClassmateCreate,
  ClassmateDetailUpsert,
  ClassmateUpdate,
} from '@/types/classmate'

// Sanitize Telegram username for safe URL construction
function sanitizeTelegram(value: string): string {
  return value.replace('@', '').replace(/[^a-zA-Z0-9_]/g, '')
}

// Sanitize URL to only allow http/https protocols (prevent javascript: injection)
function sanitizeUrl(url: string): string {
  try {
    const parsed = new URL(url)
    if (parsed.protocol === 'http:' || parsed.protocol === 'https:') {
      return url
    }
  } catch {
    // If URL is relative (e.g. "vk.com/user"), prepend https://
    if (/^[a-zA-Z0-9]/.test(url) && !url.includes(':')) {
      return `https://${url}`
    }
  }
  return '#'
}

// Avatar component
function Avatar({
  src,
  initials,
  size = 'md',
  className = '',
}: {
  src?: string | null
  initials?: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}) {
  const sizeClasses = {
    sm: 'w-16 h-16 sm:w-20 sm:h-20',
    md: 'w-16 h-16 sm:w-20 sm:h-20',
    lg: 'w-24 h-24',
  }

  const iconSizes = {
    sm: 'h-8 w-8 sm:h-10 sm:w-10',
    md: 'h-8 w-8 sm:h-10 sm:w-10',
    lg: 'h-12 w-12',
  }

  const textSizes = {
    sm: 'text-lg',
    md: 'text-lg',
    lg: 'text-2xl',
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
      {initials ? (
        <span className={`${textSizes[size]} font-semibold text-primary`}>{initials}</span>
      ) : (
        <User className={`${iconSizes[size]} text-primary`} />
      )}
    </div>
  )
}

// Get initials from full name (first letters of first two words)
function getInitials(fullName: string): string {
  const parts = fullName.trim().split(/\s+/)
  if (parts.length === 1) return parts[0][0]?.toUpperCase() ?? ''
  return (parts[0][0] + parts[1][0]).toUpperCase()
}

// Get display name from full_name (first name = second word, e.g. "Иванов Иван Иванович" -> "Иван")
function getDisplayName(fullName: string): string {
  const parts = fullName.split(' ')
  return parts.length > 1 ? parts[1] : parts[0]
}

// Default form data
const defaultBaseData: ClassmateCreate = {
  full_name: '',
  group_name: null,
  subgroup: null,
}

const defaultDetailsData: ClassmateDetailUpsert = {
  short_name: null,
  email: null,
  phone: null,
  telegram: null,
  vk: null,
  photo_url: null,
  notes: null,
}

export function ClassmatesPage() {
  const isOnline = useNetworkStatus()
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [editingClassmate, setEditingClassmate] = useState<Classmate | null>(null)
  const [viewingClassmate, setViewingClassmate] = useState<Classmate | null>(null)
  const [isLoadingDetails, setIsLoadingDetails] = useState(false)
  const [deleteConfirmClassmate, setDeleteConfirmClassmate] = useState<ClassmateBase | null>(null)
  const [baseFormData, setBaseFormData] = useState<ClassmateCreate>(defaultBaseData)
  const [detailsFormData, setDetailsFormData] = useState<ClassmateDetailUpsert>(defaultDetailsData)
  const [isUploading, setIsUploading] = useState(false)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)

  // Fetch classmates list (base fields only)
  const {
    data: classmates = [],
    isLoading,
    error,
    refetch,
  } = useQuery<ClassmateBase[]>({
    queryKey: ['classmates'],
    queryFn: ({ signal }) => classmateService.getClassmates(signal),
  })

  // Group classmates by subgroup
  const groupedClassmates = useMemo(() => {
    const groups: Record<string, ClassmateBase[]> = {}

    classmates.forEach((classmate) => {
      const key = classmate.subgroup ? String(classmate.subgroup) : 'none'
      if (!groups[key]) {
        groups[key] = []
      }
      groups[key].push(classmate)
    })

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

  // Create mutation (base fields)
  const createMutation = useMutation({
    mutationFn: (data: ClassmateCreate) => classmateService.createClassmate(data),
    onSuccess: async (classmate) => {
      // If any details fields filled, upsert them
      const hasDetails = Object.values(detailsFormData).some((v) => v !== null && v !== '')
      if (hasDetails) {
        try {
          await classmateService.upsertDetails(classmate.id, detailsFormData)
        } catch {
          toast.error('Одногруппник добавлен, но контакты не сохранились')
        }
      }
      queryClient.invalidateQueries({ queryKey: ['classmates'] })
      toast.success('Одногруппник добавлен')
      closeFormModal()
    },
    onError: () => {
      toast.error('Не удалось добавить одногруппника')
    },
  })

  // Update base fields mutation
  const updateBaseMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: ClassmateUpdate }) =>
      classmateService.updateClassmate(id, data),
    onSuccess: async (classmate) => {
      // Always upsert details on edit (to allow clearing fields)
      try {
        await classmateService.upsertDetails(classmate.id, detailsFormData)
      } catch {
        toast.error('Данные обновлены, но контакты не сохранились')
      }
      queryClient.invalidateQueries({ queryKey: ['classmates'] })
      toast.success('Одногруппник обновлён')
      closeFormModal()
    },
    onError: () => {
      toast.error('Не удалось обновить одногруппника')
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => classmateService.deleteClassmate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['classmates'] })
      toast.success('Одногруппник удалён')
      setDeleteConfirmClassmate(null)
      setViewingClassmate(null)
    },
    onError: () => {
      toast.error('Не удалось удалить одногруппника')
    },
  })

  // Open view modal — fetch full classmate with details
  const openViewModal = async (classmate: ClassmateBase) => {
    setIsLoadingDetails(true)
    setViewingClassmate({ ...classmate, details: null })
    try {
      const full = await classmateService.getClassmate(classmate.id)
      setViewingClassmate(full)
    } catch {
      toast.error('Не удалось загрузить данные')
    } finally {
      setIsLoadingDetails(false)
    }
  }

  // Handle file selection
  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      toast.error('Допустимые форматы: JPEG, PNG, WebP')
      return
    }

    if (file.size > 5 * 1024 * 1024) {
      toast.error('Максимальный размер файла: 5MB')
      return
    }

    const reader = new FileReader()
    reader.onload = (e) => {
      setPreviewUrl(e.target?.result as string)
    }
    reader.readAsDataURL(file)

    setIsUploading(true)
    try {
      const response = await uploadService.uploadAvatar(file)
      setDetailsFormData((prev) => ({ ...prev, photo_url: response.url }))
    } catch {
      toast.error('Ошибка загрузки файла')
      setPreviewUrl(null)
    } finally {
      setIsUploading(false)
    }
  }

  // Modal handlers
  const openAddModal = () => {
    setBaseFormData(defaultBaseData)
    setDetailsFormData(defaultDetailsData)
    setEditingClassmate(null)
    setPreviewUrl(null)
    setIsAddModalOpen(true)
  }

  const openEditModal = (classmate: Classmate) => {
    setBaseFormData({
      full_name: classmate.full_name,
      group_name: classmate.group_name,
      subgroup: classmate.subgroup,
    })
    setDetailsFormData({
      short_name: classmate.details?.short_name ?? null,
      email: classmate.details?.email ?? null,
      phone: classmate.details?.phone ?? null,
      telegram: classmate.details?.telegram ?? null,
      vk: classmate.details?.vk ?? null,
      photo_url: classmate.details?.photo_url ?? null,
      notes: classmate.details?.notes ?? null,
    })
    setEditingClassmate(classmate)
    setPreviewUrl(classmate.details?.photo_url ?? null)
    setViewingClassmate(null)
    setIsAddModalOpen(true)
  }

  const closeFormModal = () => {
    setIsAddModalOpen(false)
    setEditingClassmate(null)
    setBaseFormData(defaultBaseData)
    setDetailsFormData(defaultDetailsData)
    setPreviewUrl(null)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const cleanedBase: ClassmateCreate = {
      full_name: baseFormData.full_name.trim(),
      group_name: baseFormData.group_name?.trim() || null,
      subgroup: baseFormData.subgroup,
    }

    const cleanedDetails: ClassmateDetailUpsert = {
      short_name: detailsFormData.short_name?.trim() || null,
      email: detailsFormData.email?.trim() || null,
      phone: detailsFormData.phone?.trim() || null,
      telegram: detailsFormData.telegram?.trim() || null,
      vk: detailsFormData.vk?.trim() || null,
      photo_url: detailsFormData.photo_url || null,
      notes: detailsFormData.notes?.trim() || null,
    }
    setDetailsFormData(cleanedDetails)

    if (editingClassmate) {
      updateBaseMutation.mutate({ id: editingClassmate.id, data: cleanedBase })
    } else {
      createMutation.mutate(cleanedBase)
    }
  }

  const removeAvatar = () => {
    setDetailsFormData((prev) => ({ ...prev, photo_url: null }))
    setPreviewUrl(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const isMutating =
    createMutation.isPending || updateBaseMutation.isPending || deleteMutation.isPending

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container max-w-2xl mx-auto px-4 py-6">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-muted rounded w-1/3" />
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
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
          <h1 className="text-xl sm:text-2xl font-bold">Одногруппники</h1>
          <span className="text-sm text-muted-foreground">{classmates.length}</span>
          <Button size="icon" onClick={openAddModal} disabled={!isOnline} className="shrink-0">
            <Plus className="h-5 w-5" />
          </Button>
        </div>

        {/* Grouped classmates */}
        {groupedClassmates.map((group) => (
          <div key={group.subgroup} className="mb-6">
            <h2 className="text-lg font-semibold mb-3 text-muted-foreground">
              {group.label}
              <span className="ml-2 text-sm font-normal">({group.classmates.length})</span>
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              {group.classmates.map((classmate) => (
                <button
                  key={classmate.id}
                  onClick={() => openViewModal(classmate)}
                  className="aspect-square rounded-lg border bg-card hover:bg-accent hover:border-primary transition-colors flex flex-col items-center justify-center p-2 text-center cursor-pointer"
                >
                  {/* Cards show initials only — photo is in details (not in list response) */}
                  <Avatar
                    initials={getInitials(classmate.full_name)}
                    size="sm"
                    className="mb-1"
                  />
                  <span className="text-sm font-medium truncate w-full">
                    {getDisplayName(classmate.full_name)}
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
              {isLoadingDetails ? (
                <div className="flex justify-center py-6">
                  <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                </div>
              ) : (
                <>
                  {/* Avatar and info */}
                  <div className="flex items-center gap-4">
                    <Avatar
                      src={viewingClassmate.details?.photo_url}
                      initials={getInitials(viewingClassmate.full_name)}
                      size="md"
                    />
                    <div>
                      {viewingClassmate.details?.short_name && (
                        <p className="text-sm text-muted-foreground">
                          {viewingClassmate.details.short_name}
                        </p>
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
                    {viewingClassmate.details?.phone && (
                      <a
                        href={`tel:${viewingClassmate.details.phone}`}
                        className="flex items-center gap-3 p-3 rounded-lg bg-muted hover:bg-accent transition-colors"
                      >
                        <Phone className="h-5 w-5 text-green-500" />
                        <span>{viewingClassmate.details.phone}</span>
                      </a>
                    )}
                    {viewingClassmate.details?.email && (
                      <a
                        href={`mailto:${viewingClassmate.details.email}`}
                        className="flex items-center gap-3 p-3 rounded-lg bg-muted hover:bg-accent transition-colors"
                      >
                        <Mail className="h-5 w-5 text-blue-500" />
                        <span>{viewingClassmate.details.email}</span>
                      </a>
                    )}
                    {viewingClassmate.details?.telegram && (
                      <a
                        href={`https://t.me/${sanitizeTelegram(viewingClassmate.details.telegram)}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-3 p-3 rounded-lg bg-muted hover:bg-accent transition-colors"
                      >
                        <Send className="h-5 w-5 text-sky-500" />
                        <span>{viewingClassmate.details.telegram}</span>
                      </a>
                    )}
                    {viewingClassmate.details?.vk && (
                      <a
                        href={sanitizeUrl(viewingClassmate.details.vk)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-3 p-3 rounded-lg bg-muted hover:bg-accent transition-colors"
                      >
                        <span className="w-5 h-5 flex items-center justify-center text-blue-600 font-bold text-sm">
                          VK
                        </span>
                        <span className="truncate">{viewingClassmate.details.vk}</span>
                      </a>
                    )}
                  </div>

                  {/* No contacts message */}
                  {!viewingClassmate.details?.phone &&
                    !viewingClassmate.details?.email &&
                    !viewingClassmate.details?.telegram &&
                    !viewingClassmate.details?.vk && (
                      <p className="text-sm text-muted-foreground text-center py-4">
                        Контакты не указаны
                      </p>
                    )}

                  {/* Notes */}
                  {viewingClassmate.details?.notes && (
                    <div className="p-3 rounded-lg bg-muted">
                      <p className="text-sm text-muted-foreground">{viewingClassmate.details.notes}</p>
                    </div>
                  )}
                </>
              )}

              {/* Actions */}
              <div className="flex gap-2 pt-2">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => openEditModal(viewingClassmate)}
                  disabled={!isOnline || isLoadingDetails}
                >
                  <Pencil className="h-4 w-4 mr-2" />
                  Редактировать
                </Button>
                <Button
                  variant="destructive"
                  size="icon"
                  onClick={() => setDeleteConfirmClassmate(viewingClassmate)}
                  disabled={!isOnline}
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
            {/* Base fields */}
            <div>
              <Label htmlFor="full_name">Полное имя *</Label>
              <Input
                id="full_name"
                value={baseFormData.full_name}
                onChange={(e) => setBaseFormData((prev) => ({ ...prev, full_name: e.target.value }))}
                placeholder="Иванов Иван Иванович"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="group_name">Группа</Label>
                <Input
                  id="group_name"
                  value={baseFormData.group_name || ''}
                  onChange={(e) =>
                    setBaseFormData((prev) => ({ ...prev, group_name: e.target.value }))
                  }
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
                  value={baseFormData.subgroup || ''}
                  onChange={(e) =>
                    setBaseFormData((prev) => ({
                      ...prev,
                      subgroup: e.target.value ? Number(e.target.value) : null,
                    }))
                  }
                  placeholder="1"
                />
              </div>
            </div>

            {/* Divider */}
            <div className="border-t pt-3">
              <p className="text-sm font-medium text-muted-foreground mb-3">
                Мои контакты (видны только вам)
              </p>

              {/* Avatar upload */}
              <div className="flex flex-col items-center gap-2 mb-4">
                <div className="relative">
                  {previewUrl || detailsFormData.photo_url ? (
                    <img
                      src={previewUrl || detailsFormData.photo_url || ''}
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
                {(previewUrl || detailsFormData.photo_url) && (
                  <button
                    type="button"
                    onClick={removeAvatar}
                    className="text-xs text-destructive hover:underline"
                  >
                    Удалить фото
                  </button>
                )}
              </div>

              <div className="space-y-4">
                <div>
                  <Label htmlFor="short_name">Краткое имя</Label>
                  <Input
                    id="short_name"
                    value={detailsFormData.short_name || ''}
                    onChange={(e) =>
                      setDetailsFormData((prev) => ({ ...prev, short_name: e.target.value }))
                    }
                    placeholder="Ваня"
                  />
                </div>

                <div>
                  <Label htmlFor="phone">Телефон</Label>
                  <Input
                    id="phone"
                    type="tel"
                    value={detailsFormData.phone || ''}
                    onChange={(e) =>
                      setDetailsFormData((prev) => ({ ...prev, phone: e.target.value }))
                    }
                    placeholder="+7 (999) 123-45-67"
                  />
                </div>

                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={detailsFormData.email || ''}
                    onChange={(e) =>
                      setDetailsFormData((prev) => ({ ...prev, email: e.target.value }))
                    }
                    placeholder="email@example.com"
                  />
                </div>

                <div>
                  <Label htmlFor="telegram">Telegram</Label>
                  <Input
                    id="telegram"
                    value={detailsFormData.telegram || ''}
                    onChange={(e) =>
                      setDetailsFormData((prev) => ({ ...prev, telegram: e.target.value }))
                    }
                    placeholder="@username"
                  />
                </div>

                <div>
                  <Label htmlFor="vk">VK (ссылка)</Label>
                  <Input
                    id="vk"
                    type="url"
                    value={detailsFormData.vk || ''}
                    onChange={(e) =>
                      setDetailsFormData((prev) => ({ ...prev, vk: e.target.value }))
                    }
                    placeholder="https://vk.com/username"
                  />
                </div>

                <div>
                  <Label htmlFor="notes">Заметки</Label>
                  <textarea
                    id="notes"
                    value={detailsFormData.notes || ''}
                    onChange={(e) =>
                      setDetailsFormData((prev) => ({ ...prev, notes: e.target.value }))
                    }
                    placeholder="Дополнительная информация..."
                    className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  />
                </div>
              </div>
            </div>

            <div className="flex gap-2 pt-2">
              <Button type="button" variant="outline" className="flex-1" onClick={closeFormModal}>
                Отмена
              </Button>
              <Button type="submit" className="flex-1" disabled={isMutating || isUploading}>
                {isMutating ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : editingClassmate ? (
                  'Сохранить'
                ) : (
                  'Создать'
                )}
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
              disabled={deleteMutation.isPending}
              onClick={() =>
                deleteConfirmClassmate && deleteMutation.mutate(deleteConfirmClassmate.id)
              }
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

export default ClassmatesPage
