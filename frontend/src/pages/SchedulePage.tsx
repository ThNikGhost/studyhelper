import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ChevronLeft, ChevronRight, RefreshCw, Calendar } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { DayScheduleCard } from '@/components/schedule/DayScheduleCard'
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

// Check if two date strings are the same day
function isSameDay(date1: string, date2: string): boolean {
  return date1.split('T')[0] === date2.split('T')[0]
}

export function SchedulePage() {
  const [targetDate, setTargetDate] = useState<string | undefined>(undefined)
  const today = getToday()

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
              <p className="text-destructive mb-4">
                Ошибка загрузки расписания
              </p>
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
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold">Расписание</h1>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => refetch()}
            title="Обновить"
          >
            <RefreshCw className="h-5 w-5" />
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
                <div className="font-medium">
                  Неделя {weekSchedule?.week_number}
                </div>
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
                <Calendar className="h-4 w-4 mr-2" />
                К текущей неделе
              </Button>
            )}
          </CardContent>
        </Card>

        {/* Current lesson indicator */}
        {currentLesson?.current && isCurrentWeek && (
          <Card className="mb-6 border-primary">
            <CardContent className="py-3 px-4">
              <div className="text-sm text-primary font-medium mb-1">
                Сейчас идёт:
              </div>
              <div className="font-medium">
                {currentLesson.current.subject_name}
              </div>
              {currentLesson.time_until_next !== null && (
                <div className="text-xs text-muted-foreground mt-1">
                  До конца: {Math.floor(currentLesson.time_until_next / 60)}ч{' '}
                  {currentLesson.time_until_next % 60}мин
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Days list */}
        <div className="space-y-6">
          {weekSchedule?.days.map((day) => (
            <DayScheduleCard
              key={day.date}
              day={day}
              isToday={isSameDay(day.date, today)}
              currentEntryId={currentLesson?.current?.id}
            />
          ))}
        </div>

        {/* Empty state */}
        {weekSchedule?.days.every((d) => d.entries.length === 0) && (
          <Card>
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
