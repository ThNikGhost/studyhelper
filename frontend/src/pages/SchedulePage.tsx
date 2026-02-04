import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ChevronLeft, ChevronRight, RefreshCw, Calendar, ArrowLeft, Loader2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { ScheduleGrid } from '@/components/schedule/ScheduleGrid'
import scheduleService from '@/services/scheduleService'
import type { WeekSchedule, CurrentLesson } from '@/types/schedule'

// Add/subtract days from date string
function addDays(dateStr: string, days: number): string {
  const date = new Date(dateStr)
  date.setDate(date.getDate() + days)
  return date.toISOString().split('T')[0]
}

// Get today's date string
function getToday(): string {
  return new Date().toISOString().split('T')[0]
}

export function SchedulePage() {
  const [targetDate, setTargetDate] = useState<string | undefined>(undefined)
  const today = getToday()
  const queryClient = useQueryClient()

  // Fetch week schedule
  const {
    data: weekSchedule,
    isLoading,
    error,
    refetch,
  } = useQuery<WeekSchedule>({
    queryKey: ['schedule', 'week', targetDate],
    queryFn: () => scheduleService.getWeekSchedule(targetDate),
  })

  // Fetch current lesson (updates every minute)
  const { data: currentLesson } = useQuery<CurrentLesson>({
    queryKey: ['schedule', 'current'],
    queryFn: () => scheduleService.getCurrentLesson(),
    refetchInterval: 60000, // 1 minute
  })

  // Mutation for refreshing schedule from OmGU
  const refreshMutation = useMutation({
    mutationFn: () => scheduleService.refreshSchedule(false),
    onSuccess: () => {
      // Invalidate all schedule queries to refetch fresh data
      queryClient.invalidateQueries({ queryKey: ['schedule'] })
    },
  })

  // Handle refresh button click
  const handleRefresh = () => {
    refreshMutation.mutate()
  }

  // Navigation handlers
  const goToPreviousWeek = () => {
    const baseDate = weekSchedule?.week_start || today
    setTargetDate(addDays(baseDate, -7))
  }

  const goToNextWeek = () => {
    const baseDate = weekSchedule?.week_start || today
    setTargetDate(addDays(baseDate, 7))
  }

  const goToCurrentWeek = () => {
    setTargetDate(undefined)
  }

  // Check if viewing current week
  const isCurrentWeek = useMemo(() => {
    if (!weekSchedule) return true
    const todayDate = new Date(today)
    const weekStart = new Date(weekSchedule.week_start)
    const weekEnd = new Date(weekSchedule.week_end)
    return todayDate >= weekStart && todayDate <= weekEnd
  }, [weekSchedule, today])

  // Calculate time remaining for current lesson
  const timeRemaining = useMemo(() => {
    if (!currentLesson?.current) return null
    const now = new Date()
    const [endHours, endMinutes] = currentLesson.current.end_time.split(':').map(Number)
    const endTime = new Date()
    endTime.setHours(endHours, endMinutes, 0, 0)
    const diff = endTime.getTime() - now.getTime()
    if (diff <= 0) return null
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return { hours, minutes: mins }
  }, [currentLesson])

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-6">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-muted rounded w-1/3" />
            <div className="h-12 bg-muted rounded" />
            <div className="h-96 bg-muted rounded" />
          </div>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-6">
          <Card>
            <CardContent className="py-10 text-center">
              <p className="text-destructive mb-4">Ошибка загрузки расписания</p>
              <Button onClick={() => refetch()}>Попробовать снова</Button>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <Link to="/">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <h1 className="text-2xl font-bold flex-1">Расписание</h1>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleRefresh}
            disabled={refreshMutation.isPending}
            title="Обновить с сайта ОмГУ"
          >
            {refreshMutation.isPending ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <RefreshCw className="h-5 w-5" />
            )}
          </Button>
        </div>

        {/* Week navigation */}
        <Card className="mb-6">
          <CardContent className="py-3 px-4">
            <div className="flex items-center justify-between">
              <Button variant="ghost" size="icon" onClick={goToPreviousWeek}>
                <ChevronLeft className="h-5 w-5" />
              </Button>

              <div className="text-center">
                <div className="font-medium">Неделя {weekSchedule?.week_number}</div>
                <div className="text-sm text-muted-foreground">
                  {weekSchedule?.is_odd_week ? 'Нечётная' : 'Чётная'}
                </div>
              </div>

              <Button variant="ghost" size="icon" onClick={goToNextWeek}>
                <ChevronRight className="h-5 w-5" />
              </Button>
            </div>

            {/* Go to current week button */}
            {!isCurrentWeek && (
              <Button
                variant="outline"
                size="sm"
                className="w-full mt-2"
                onClick={goToCurrentWeek}
              >
                <Calendar className="h-4 w-4 mr-2" />К текущей неделе
              </Button>
            )}
          </CardContent>
        </Card>

        {/* Current lesson indicator */}
        {currentLesson?.current && isCurrentWeek && timeRemaining && (
          <Card className="mb-6 border-primary">
            <CardContent className="py-3 px-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-primary font-medium">Сейчас идёт:</div>
                  <div className="font-medium">{currentLesson.current.subject_name}</div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-muted-foreground">До конца:</div>
                  <div className="font-medium">
                    {timeRemaining.hours}ч {timeRemaining.minutes}мин
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Next lesson (when no current) */}
        {!currentLesson?.current && currentLesson?.next && isCurrentWeek && (
          <Card className="mb-6">
            <CardContent className="py-3 px-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-muted-foreground">Следующая:</div>
                  <div className="font-medium">{currentLesson.next.subject_name}</div>
                </div>
                {currentLesson.time_until_next !== null && (
                  <div className="text-right">
                    <div className="text-xs text-muted-foreground">Через:</div>
                    <div className="font-medium">
                      {Math.floor(currentLesson.time_until_next / 60)}ч{' '}
                      {currentLesson.time_until_next % 60}мин
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Schedule grid */}
        {weekSchedule && (
          <ScheduleGrid
            weekSchedule={weekSchedule}
            currentEntryId={currentLesson?.current?.id}
          />
        )}

        {/* Empty state */}
        {weekSchedule?.days.every((d) => d.entries.length === 0) && (
          <Card className="mt-6">
            <CardContent className="py-10 text-center text-muted-foreground">
              <p>На этой неделе нет занятий</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

export default SchedulePage
