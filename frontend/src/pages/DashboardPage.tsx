import { useAuthStore } from '@/stores/authStore'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  LogOut,
  Calendar,
  BookOpen,
  ClipboardList,
  Users,
  GraduationCap,
  Clock,
  MapPin,
  User,
  AlertCircle,
  CheckCircle2,
  Loader2,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { scheduleService } from '@/services/scheduleService'
import { workService } from '@/services/workService'
import { formatDeadline, getDeadlineColor } from '@/lib/dateUtils'
import {
  lessonTypeLabels,
  type ScheduleEntry,
  type CurrentLesson,
} from '@/types/schedule'
import {
  workTypeLabels,
  workStatusLabels,
  workStatusColors,
  WorkStatus,
  type UpcomingWork,
} from '@/types/work'

function formatTime(timeStr: string): string {
  // timeStr is in HH:MM:SS format
  return timeStr.slice(0, 5)
}

function formatTimeUntil(seconds: number): string {
  if (seconds < 60) {
    return 'менее минуты'
  }
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) {
    return `${minutes} мин`
  }
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  if (remainingMinutes === 0) {
    return `${hours} ч`
  }
  return `${hours} ч ${remainingMinutes} мин`
}

interface LessonCardProps {
  entry: ScheduleEntry
  label: string
  timeUntil?: number | null
}

function LessonCard({ entry, label, timeUntil }: LessonCardProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-muted-foreground">{label}</span>
        {timeUntil !== null && timeUntil !== undefined && (
          <span className="text-xs bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 px-2 py-0.5 rounded">
            через {formatTimeUntil(timeUntil)}
          </span>
        )}
      </div>

      <div className="space-y-2">
        <div className="font-semibold text-lg">{entry.subject_name}</div>
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <span className="inline-flex items-center gap-1">
            <Clock className="h-4 w-4" />
            {formatTime(entry.start_time)} – {formatTime(entry.end_time)}
          </span>
          <span className="bg-secondary px-2 py-0.5 rounded text-xs">
            {lessonTypeLabels[entry.lesson_type]}
          </span>
        </div>
        {(entry.room || entry.building) && (
          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <MapPin className="h-4 w-4" />
            {[entry.room, entry.building].filter(Boolean).join(', ')}
          </div>
        )}
        {entry.teacher_name && (
          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <User className="h-4 w-4" />
            {entry.teacher_name}
          </div>
        )}
      </div>
    </div>
  )
}

interface CurrentLessonWidgetProps {
  data: CurrentLesson | undefined
  isLoading: boolean
  isError: boolean
}

function CurrentLessonWidget({ data, isLoading, isError }: CurrentLessonWidgetProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calendar className="h-5 w-5 text-blue-500" />
          Текущая пара
        </CardTitle>
        <CardDescription>Сейчас или следующая</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading && (
          <div className="flex items-center justify-center py-4">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        )}

        {isError && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground py-2">
            <AlertCircle className="h-4 w-4" />
            Не удалось загрузить расписание
          </div>
        )}

        {!isLoading && !isError && data && (
          <div className="space-y-4">
            {data.current ? (
              <LessonCard entry={data.current} label="Сейчас" />
            ) : data.next ? (
              <LessonCard
                entry={data.next}
                label="Следующая"
                timeUntil={data.time_until_next}
              />
            ) : (
              <p className="text-muted-foreground text-sm py-2">
                На сегодня занятий больше нет
              </p>
            )}

            {data.current && data.next && (
              <>
                <hr className="border-border" />
                <LessonCard
                  entry={data.next}
                  label="Следующая"
                  timeUntil={data.time_until_next}
                />
              </>
            )}
          </div>
        )}

        {!isLoading && !isError && !data && (
          <p className="text-muted-foreground text-sm py-2">
            Загрузите расписание для отображения
          </p>
        )}
      </CardContent>
    </Card>
  )
}

interface DeadlinesWidgetProps {
  data: UpcomingWork[] | undefined
  isLoading: boolean
  isError: boolean
}

function DeadlinesWidget({ data, isLoading, isError }: DeadlinesWidgetProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ClipboardList className="h-5 w-5 text-orange-500" />
          Ближайшие дедлайны
        </CardTitle>
        <CardDescription>На этой неделе</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading && (
          <div className="flex items-center justify-center py-4">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        )}

        {isError && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground py-2">
            <AlertCircle className="h-4 w-4" />
            Не удалось загрузить дедлайны
          </div>
        )}

        {!isLoading && !isError && data && data.length > 0 && (
          <div className="space-y-3">
            {data.slice(0, 5).map((work) => (
              <Link
                key={work.id}
                to="/works"
                className="block p-3 -mx-3 rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0 flex-1">
                    <div className="font-medium truncate">{work.title}</div>
                    <div className="text-sm text-muted-foreground truncate">
                      {work.subject_name}
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs bg-secondary px-2 py-0.5 rounded">
                        {workTypeLabels[work.work_type]}
                      </span>
                      {work.my_status && (
                        <span
                          className={`text-xs px-2 py-0.5 rounded ${workStatusColors[work.my_status]}`}
                        >
                          {workStatusLabels[work.my_status]}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <div className={`text-sm font-medium ${getDeadlineColor(work.deadline)}`}>
                      {formatDeadline(work.deadline)}
                    </div>
                    {work.my_status === WorkStatus.COMPLETED ||
                    work.my_status === WorkStatus.SUBMITTED ||
                    work.my_status === WorkStatus.GRADED ? (
                      <CheckCircle2 className="h-4 w-4 text-green-500 ml-auto mt-1" />
                    ) : null}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}

        {!isLoading && !isError && (!data || data.length === 0) && (
          <p className="text-muted-foreground text-sm py-2">
            Нет ближайших дедлайнов
          </p>
        )}

        {!isLoading && !isError && data && data.length > 5 && (
          <Link
            to="/works"
            className="block text-center text-sm text-primary hover:underline mt-3 pt-3 border-t"
          >
            Показать все ({data.length})
          </Link>
        )}
      </CardContent>
    </Card>
  )
}

export default function DashboardPage() {
  const { user, logout } = useAuthStore()

  const handleLogout = async () => {
    if (!confirm('Вы уверены, что хотите выйти?')) return
    await logout()
  }

  const { data: currentLesson, isLoading: lessonLoading, isError: lessonError } = useQuery({
    queryKey: ['currentLesson'],
    queryFn: ({ signal }) => scheduleService.getCurrentLesson(signal),
    refetchInterval: 60000, // Refetch every minute
    staleTime: 30000,
  })

  const { data: upcomingWorks, isLoading: worksLoading, isError: worksError } = useQuery({
    queryKey: ['upcomingWorks'],
    queryFn: ({ signal }) => workService.getUpcomingWorks(10, signal),
    staleTime: 60000,
  })

  const menuItems = [
    {
      title: 'Расписание',
      description: 'Просмотр расписания занятий',
      icon: Calendar,
      href: '/schedule',
      color: 'text-blue-500',
    },
    {
      title: 'Предметы',
      description: 'Список предметов семестра',
      icon: BookOpen,
      href: '/subjects',
      color: 'text-green-500',
    },
    {
      title: 'Работы',
      description: 'Задания и дедлайны',
      icon: ClipboardList,
      href: '/works',
      color: 'text-orange-500',
    },
    {
      title: 'Одногруппники',
      description: 'Контакты группы',
      icon: Users,
      href: '/classmates',
      color: 'text-purple-500',
    },
    {
      title: 'Семестры',
      description: 'Управление семестрами',
      icon: GraduationCap,
      href: '/semesters',
      color: 'text-cyan-500',
    },
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold">StudyHelper</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">
              {user?.name}
            </span>
            <Button variant="ghost" size="icon" onClick={handleLogout}>
              <LogOut className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-2">
            Привет, {user?.name}!
          </h2>
          <p className="text-muted-foreground">
            Что будем делать сегодня?
          </p>
        </div>

        {/* Widgets */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <CurrentLessonWidget
            data={currentLesson}
            isLoading={lessonLoading}
            isError={lessonError}
          />
          <DeadlinesWidget
            data={upcomingWorks}
            isLoading={worksLoading}
            isError={worksError}
          />
        </div>

        {/* Quick actions grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {menuItems.map((item) => (
            <Link key={item.href} to={item.href}>
              <Card className="hover:shadow-md transition-shadow cursor-pointer h-full">
                <CardHeader className="pb-2">
                  <item.icon className={`h-8 w-8 ${item.color}`} />
                </CardHeader>
                <CardContent>
                  <CardTitle className="text-lg">{item.title}</CardTitle>
                  <CardDescription>{item.description}</CardDescription>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </main>
    </div>
  )
}
