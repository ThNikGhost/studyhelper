import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Settings, Dumbbell, Users, Building2, Check, Loader2, RefreshCw, LogOut, Eye, EyeOff, Sun, Moon, Monitor, MessageCircle, Copy, Bell, BellOff, LinkIcon, Unlink } from 'lucide-react'
import { Link } from 'react-router-dom'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Modal } from '@/components/ui/modal'
import { toast } from 'sonner'
import { useUserSettings } from '@/hooks/useUserSettings'
import { useTheme } from '@/hooks/useTheme'
import { scheduleService } from '@/services/scheduleService'
import { lkService } from '@/services/lkService'
import { telegramService } from '@/services/telegramService'
import { getPeTeachersFromWeek } from '@/lib/peTeacherFilter'
import { formatDistanceToNow } from '@/lib/dateUtils'
import type { LkCredentials } from '@/types/lk'

export default function SettingsPage() {
  const queryClient = useQueryClient()
  const { settings, updateSettings, isUpdating } = useUserSettings()
  const { subgroup, peTeacher } = settings
  const { mode, setTheme } = useTheme()

  // LK form state
  const [lkEmail, setLkEmail] = useState('')
  const [lkPassword, setLkPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [disconnectModalOpen, setDisconnectModalOpen] = useState(false)

  // Telegram state
  const [tgUnlinkModalOpen, setTgUnlinkModalOpen] = useState(false)
  const [tgCodeCountdown, setTgCodeCountdown] = useState(0)

  // Fetch schedule to get available subgroups and PE teachers
  const { data: weekSchedule } = useQuery({
    queryKey: ['schedule', 'week'],
    queryFn: () => scheduleService.getWeekSchedule(),
    staleTime: 1000 * 60 * 5,
  })

  // Fetch LK status
  const { data: lkStatus, isLoading: lkStatusLoading } = useQuery({
    queryKey: ['lk', 'status'],
    queryFn: ({ signal }) => lkService.getStatus(signal),
    staleTime: 1000 * 60,
  })

  // Verify credentials mutation
  const verifyMutation = useMutation({
    mutationFn: (data: LkCredentials) => lkService.verifyCredentials(data),
    onSuccess: (result) => {
      if (result.valid) {
        toast.success('Учётные данные верны')
      } else {
        toast.error('Неверные учётные данные')
      }
    },
    onError: () => {
      toast.error('Ошибка проверки учётных данных')
    },
  })

  // Save credentials mutation
  const saveMutation = useMutation({
    mutationFn: (data: LkCredentials) => lkService.saveCredentials(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lk', 'status'] })
      toast.success('Учётные данные сохранены')
      setLkEmail('')
      setLkPassword('')
    },
    onError: () => {
      toast.error('Не удалось сохранить учётные данные')
    },
  })

  // Sync mutation
  const syncMutation = useMutation({
    mutationFn: () => lkService.sync(),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['lk', 'status'] })
      queryClient.invalidateQueries({ queryKey: ['lk', 'grades'] })
      queryClient.invalidateQueries({ queryKey: ['lk', 'disciplines'] })
      toast.success(`Синхронизировано: ${result.grades_synced} оценок, ${result.disciplines_synced} дисциплин`)
    },
    onError: () => {
      toast.error('Ошибка синхронизации')
    },
  })

  // Delete credentials mutation
  const deleteMutation = useMutation({
    mutationFn: () => lkService.deleteCredentials(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lk', 'status'] })
      setDisconnectModalOpen(false)
      toast.success('Подключение отключено')
    },
    onError: () => {
      toast.error('Не удалось отключить подключение')
    },
  })

  // Telegram status
  const { data: tgStatus, isLoading: tgStatusLoading } = useQuery({
    queryKey: ['telegram', 'status'],
    queryFn: ({ signal }) => telegramService.getStatus(signal),
    staleTime: 1000 * 60,
  })

  // Telegram generate link code
  const tgGenerateCodeMutation = useMutation({
    mutationFn: () => telegramService.generateLinkCode(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['telegram', 'status'] })
      toast.success('Код привязки сгенерирован')
    },
    onError: () => {
      toast.error('Не удалось сгенерировать код')
    },
  })

  // Telegram unlink
  const tgUnlinkMutation = useMutation({
    mutationFn: () => telegramService.unlink(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['telegram', 'status'] })
      setTgUnlinkModalOpen(false)
      toast.success('Telegram отвязан')
    },
    onError: () => {
      toast.error('Не удалось отвязать Telegram')
    },
  })

  // Telegram notification toggles
  const tgNotifyMutation = useMutation({
    mutationFn: (data: { notify_deadlines?: boolean; morning_summary?: boolean }) =>
      telegramService.updateNotifications(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['telegram', 'status'] })
    },
    onError: () => {
      toast.error('Не удалось обновить настройки уведомлений')
    },
  })

  // Countdown timer for link code
  const expiresAt = tgStatus?.link_code_expires_at
  useEffect(() => {
    if (!expiresAt) {
      return
    }
    const updateCountdown = () => {
      const remaining = Math.max(
        0,
        Math.floor((new Date(expiresAt).getTime() - Date.now()) / 1000)
      )
      setTgCodeCountdown(remaining)
    }
    updateCountdown()
    const interval = setInterval(updateCountdown, 1000)
    return () => clearInterval(interval)
  }, [expiresAt])

  const copyLinkCode = () => {
    if (tgStatus?.link_code) {
      navigator.clipboard.writeText(tgStatus.link_code)
      toast.success('Код скопирован')
    }
  }

  const isTgMutating = tgGenerateCodeMutation.isPending || tgUnlinkMutation.isPending || tgNotifyMutation.isPending

  const availablePeTeachers = weekSchedule ? getPeTeachersFromWeek(weekSchedule) : []

  const handleVerify = () => {
    if (!lkEmail || !lkPassword) {
      toast.error('Введите email и пароль')
      return
    }
    verifyMutation.mutate({ email: lkEmail, password: lkPassword })
  }

  const handleSave = () => {
    if (!lkEmail || !lkPassword) {
      toast.error('Введите email и пароль')
      return
    }
    saveMutation.mutate({ email: lkEmail, password: lkPassword })
  }

  const isLkMutating = verifyMutation.isPending || saveMutation.isPending || syncMutation.isPending || deleteMutation.isPending

  return (
    <div className="min-h-screen bg-background">
      <div className="container max-w-2xl mx-auto px-4 py-6 space-y-6">
        {/* Header */}
        <div className="flex items-center gap-3">
          <Settings className="h-8 w-8 text-gray-500" />
          <div>
            <h1 className="text-2xl font-bold">Настройки</h1>
            <p className="text-muted-foreground">Персональные настройки приложения</p>
          </div>
        </div>

        {/* Subgroup Section */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-blue-500" />
              <CardTitle>Подгруппа</CardTitle>
            </div>
            <CardDescription>
              Фильтрует расписание по вашей подгруппе. Общие занятия (без подгруппы) отображаются всегда.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              <Button
                variant={subgroup === null ? 'default' : 'outline'}
                onClick={() => updateSettings({ preferred_subgroup: null })}
                disabled={isUpdating}
                className="gap-2"
              >
                {subgroup === null && <Check className="h-4 w-4" />}
                Все подгруппы
              </Button>
              <Button
                variant={subgroup === 1 ? 'default' : 'outline'}
                onClick={() => updateSettings({ preferred_subgroup: 1 })}
                disabled={isUpdating}
                className="gap-2"
              >
                {subgroup === 1 && <Check className="h-4 w-4" />}
                1 подгруппа
              </Button>
              <Button
                variant={subgroup === 2 ? 'default' : 'outline'}
                onClick={() => updateSettings({ preferred_subgroup: 2 })}
                disabled={isUpdating}
                className="gap-2"
              >
                {subgroup === 2 && <Check className="h-4 w-4" />}
                2 подгруппа
              </Button>
            </div>
            {subgroup !== null && (
              <p className="mt-3 text-sm text-muted-foreground">
                Выбрана {subgroup} подгруппа. Занятия для других подгрупп будут помечены значком "!".
              </p>
            )}
          </CardContent>
        </Card>

        {/* PE Teacher Section */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Dumbbell className="h-5 w-5 text-green-500" />
              <CardTitle>Физкультура</CardTitle>
            </div>
            <CardDescription>
              Выберите вашего преподавателя для занятий по физкультуре.
              В расписании несколько преподавателей на одно время — выберите своего.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {availablePeTeachers.length > 0 ? (
              <div className="space-y-2">
                <Button
                  variant={peTeacher === null ? 'default' : 'outline'}
                  onClick={() => updateSettings({ preferred_pe_teacher: null })}
                  disabled={isUpdating}
                  className="w-full justify-start gap-2"
                >
                  {peTeacher === null && <Check className="h-4 w-4" />}
                  Показать всех преподавателей
                </Button>
                {availablePeTeachers.map((teacher) => (
                  <Button
                    key={teacher}
                    variant={peTeacher === teacher ? 'default' : 'outline'}
                    onClick={() => updateSettings({ preferred_pe_teacher: teacher })}
                    disabled={isUpdating}
                    className="w-full justify-start gap-2"
                  >
                    {peTeacher === teacher && <Check className="h-4 w-4" />}
                    <span className="truncate">{teacher}</span>
                  </Button>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                Преподаватели физкультуры будут доступны после загрузки расписания.
              </p>
            )}
            {peTeacher && (
              <p className="mt-3 text-sm text-muted-foreground">
                Выбран: {peTeacher}
              </p>
            )}
          </CardContent>
        </Card>

        {/* Theme Section */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Sun className="h-5 w-5 text-amber-500" />
              <CardTitle>Тема</CardTitle>
            </div>
            <CardDescription>
              Выберите тему оформления приложения.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              <Button
                variant={mode === 'light' ? 'default' : 'outline'}
                onClick={() => setTheme('light')}
                aria-pressed={mode === 'light'}
                className="gap-2"
              >
                <Sun className="h-4 w-4" />
                Светлая
              </Button>
              <Button
                variant={mode === 'dark' ? 'default' : 'outline'}
                onClick={() => setTheme('dark')}
                aria-pressed={mode === 'dark'}
                className="gap-2"
              >
                <Moon className="h-4 w-4" />
                Тёмная
              </Button>
              <Button
                variant={mode === 'system' ? 'default' : 'outline'}
                onClick={() => setTheme('system')}
                aria-pressed={mode === 'system'}
                className="gap-2"
              >
                <Monitor className="h-4 w-4" />
                Системная
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Telegram Section */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <MessageCircle className="h-5 w-5 text-sky-500" />
              <CardTitle>Telegram</CardTitle>
            </div>
            <CardDescription>
              Привяжите Telegram для получения уведомлений о расписании и дедлайнах.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {tgStatusLoading ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              </div>
            ) : tgStatus?.is_linked ? (
              // State 3: Linked
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-green-600 dark:text-green-400">
                  <Check className="h-5 w-5" />
                  <span className="font-medium">
                    Привязан{tgStatus.telegram_username ? ` (@${tgStatus.telegram_username})` : ''}
                  </span>
                </div>

                <div className="space-y-3">
                  <p className="text-sm font-medium">Уведомления:</p>
                  <div className="flex flex-wrap gap-2">
                    <Button
                      variant={tgStatus.notify_deadlines ? 'default' : 'outline'}
                      size="sm"
                      onClick={() =>
                        tgNotifyMutation.mutate({
                          notify_deadlines: !tgStatus.notify_deadlines,
                        })
                      }
                      disabled={isTgMutating}
                      className="gap-2"
                    >
                      {tgStatus.notify_deadlines ? (
                        <Bell className="h-4 w-4" />
                      ) : (
                        <BellOff className="h-4 w-4" />
                      )}
                      Дедлайны
                    </Button>
                    <Button
                      variant={tgStatus.morning_summary ? 'default' : 'outline'}
                      size="sm"
                      onClick={() =>
                        tgNotifyMutation.mutate({
                          morning_summary: !tgStatus.morning_summary,
                        })
                      }
                      disabled={isTgMutating}
                      className="gap-2"
                    >
                      {tgStatus.morning_summary ? (
                        <Bell className="h-4 w-4" />
                      ) : (
                        <BellOff className="h-4 w-4" />
                      )}
                      Утренняя сводка
                    </Button>
                  </div>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setTgUnlinkModalOpen(true)}
                  disabled={isTgMutating}
                  className="gap-2 text-destructive hover:text-destructive"
                >
                  <Unlink className="h-4 w-4" />
                  Отвязать
                </Button>
              </div>
            ) : tgStatus?.link_code && tgCodeCountdown > 0 ? (
              // State 2: Code generated
              <div className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  Отправьте эту команду боту в Telegram:
                </p>
                <div className="flex items-center gap-2">
                  <code className="bg-muted px-3 py-2 rounded text-lg font-mono tracking-wider">
                    /link {tgStatus.link_code}
                  </code>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={copyLinkCode}
                    title="Скопировать код"
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
                <p className="text-sm text-muted-foreground">
                  Код действует ещё {Math.floor(tgCodeCountdown / 60)}:{String(tgCodeCountdown % 60).padStart(2, '0')}
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => tgGenerateCodeMutation.mutate()}
                  disabled={isTgMutating}
                  className="gap-2"
                >
                  <RefreshCw className="h-4 w-4" />
                  Новый код
                </Button>
              </div>
            ) : (
              // State 1: Not linked
              <div className="space-y-4">
                <Button
                  onClick={() => tgGenerateCodeMutation.mutate()}
                  disabled={isTgMutating}
                  className="gap-2"
                >
                  {tgGenerateCodeMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <LinkIcon className="h-4 w-4" />
                  )}
                  Сгенерировать код привязки
                </Button>
                <p className="text-xs text-muted-foreground">
                  После генерации кода отправьте его боту в Telegram для привязки аккаунта.
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* OmSU LK Integration Section */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Building2 className="h-5 w-5 text-purple-500" />
              <CardTitle>Личный кабинет ОмГУ</CardTitle>
            </div>
            <CardDescription>
              Интеграция с личным кабинетом ОмГУ для автоматического импорта оценок и дисциплин.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {lkStatusLoading ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              </div>
            ) : lkStatus?.has_credentials ? (
              // Connected state
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-green-600 dark:text-green-400">
                  <Check className="h-5 w-5" />
                  <span className="font-medium">Подключено</span>
                </div>

                {lkStatus.last_sync_at && (
                  <p className="text-sm text-muted-foreground">
                    Последняя синхронизация: {formatDistanceToNow(new Date(lkStatus.last_sync_at))}
                  </p>
                )}

                <div className="flex flex-wrap gap-2">
                  <Button
                    variant="outline"
                    onClick={() => syncMutation.mutate()}
                    disabled={isLkMutating}
                    className="gap-2"
                  >
                    {syncMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <RefreshCw className="h-4 w-4" />
                    )}
                    Синхронизировать
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setDisconnectModalOpen(true)}
                    disabled={isLkMutating}
                    className="gap-2 text-destructive hover:text-destructive"
                  >
                    <LogOut className="h-4 w-4" />
                    Отключить
                  </Button>
                </div>

                <p className="text-xs text-muted-foreground">
                  После синхронизации вы можете импортировать семестры и предметы на странице "Семестры".
                </p>
              </div>
            ) : (
              // Not connected state - show form
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="lk-email">Email</Label>
                  <Input
                    id="lk-email"
                    type="email"
                    placeholder="your.email@omsu.ru"
                    value={lkEmail}
                    onChange={(e) => setLkEmail(e.target.value)}
                    className="max-w-sm"
                    disabled={isLkMutating}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="lk-password">Пароль</Label>
                  <div className="relative max-w-sm">
                    <Input
                      id="lk-password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="••••••••"
                      value={lkPassword}
                      onChange={(e) => setLkPassword(e.target.value)}
                      className="pr-10"
                      disabled={isLkMutating}
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? (
                        <EyeOff className="h-4 w-4 text-muted-foreground" />
                      ) : (
                        <Eye className="h-4 w-4 text-muted-foreground" />
                      )}
                    </Button>
                  </div>
                </div>

                <div className="flex flex-wrap gap-2">
                  <Button
                    variant="outline"
                    onClick={handleVerify}
                    disabled={isLkMutating || !lkEmail || !lkPassword}
                  >
                    {verifyMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    ) : null}
                    Проверить
                  </Button>
                  <Button
                    onClick={handleSave}
                    disabled={isLkMutating || !lkEmail || !lkPassword}
                  >
                    {saveMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    ) : null}
                    Сохранить
                  </Button>
                </div>

                <p className="text-xs text-muted-foreground">
                  Учётные данные хранятся в зашифрованном виде. Используются для доступа к вашим оценкам и учебному плану.
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Navigation back */}
        <div className="pt-4">
          <Link to="/">
            <Button variant="outline">← На главную</Button>
          </Link>
        </div>

        {/* Telegram unlink confirmation modal */}
        <Modal
          open={tgUnlinkModalOpen}
          onClose={() => setTgUnlinkModalOpen(false)}
          title="Отвязать Telegram?"
        >
          <p className="text-muted-foreground mb-4">
            Уведомления будут отключены. Вы сможете привязать аккаунт повторно.
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => setTgUnlinkModalOpen(false)}
            >
              Отмена
            </Button>
            <Button
              variant="destructive"
              className="flex-1"
              onClick={() => tgUnlinkMutation.mutate()}
              disabled={tgUnlinkMutation.isPending}
            >
              {tgUnlinkMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                'Отвязать'
              )}
            </Button>
          </div>
        </Modal>

        {/* Disconnect confirmation modal */}
        <Modal
          open={disconnectModalOpen}
          onClose={() => setDisconnectModalOpen(false)}
          title="Отключить личный кабинет?"
        >
          <p className="text-muted-foreground mb-4">
            Учётные данные будут удалены. Синхронизированные данные (оценки, дисциплины) останутся в приложении.
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => setDisconnectModalOpen(false)}
            >
              Отмена
            </Button>
            <Button
              variant="destructive"
              className="flex-1"
              onClick={() => deleteMutation.mutate()}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                'Отключить'
              )}
            </Button>
          </div>
        </Modal>
      </div>
    </div>
  )
}
