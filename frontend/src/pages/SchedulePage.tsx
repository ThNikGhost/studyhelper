import { useState, useMemo, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNetworkStatus } from '@/hooks/useNetworkStatus'
import { ChevronLeft, ChevronRight, RefreshCw, ArrowLeft, Loader2, CalendarDays } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Calendar } from '@/components/ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { ScheduleGrid } from '@/components/schedule/ScheduleGrid'
import { PeTeacherSelect } from '@/components/schedule/PeTeacherSelect'
import { LessonDetailModal } from '@/components/schedule/LessonDetailModal'
import { formatDateLocal, getToday, formatTimeUntil } from '@/lib/dateUtils'
import { filterWeekSchedule, getPeTeachersFromWeek } from '@/lib/peTeacherFilter'
import { filterWeekBySubgroup } from '@/lib/subgroupFilter'
import { useSettingsStore } from '@/stores/settingsStore'
import { toast } from 'sonner'
import scheduleService from '@/services/scheduleService'
import { noteService } from '@/services/noteService'
import type { WeekSchedule, CurrentLesson, ScheduleEntry } from '@/types/schedule'

// Add/subtract days from date string (local timezone)
function addDays(dateStr: string, days: number): string {
  const date = new Date(dateStr + 'T12:00:00') // Use noon to avoid timezone edge cases
  date.setDate(date.getDate() + days)
  return formatDateLocal(date)
}

export function SchedulePage() {
  const isOnline = useNetworkStatus()
  const [targetDate, setTargetDate] = useState<string | undefined>(undefined)
  const [calendarOpen, setCalendarOpen] = useState(false)
  const [selectedEntry, setSelectedEntry] = useState<ScheduleEntry | null>(null)
  const { subgroup, peTeacher, setPeTeacher } = useSettingsStore()
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
    queryFn: ({ signal }) => scheduleService.getWeekSchedule(targetDate, signal),
  })

  // Fetch current lesson (updates every minute)
  const { data: currentLesson } = useQuery<CurrentLesson>({
    queryKey: ['schedule', 'current'],
    queryFn: ({ signal }) => scheduleService.getCurrentLesson(signal),
    refetchInterval: 60000, // 1 minute
  })

  // Fetch all notes to show note icons (notes are per-subject, not per-entry)
  const { data: allNotes } = useQuery({
    queryKey: ['notes'],
    queryFn: ({ signal }) => noteService.getNotes(undefined, signal),
  })

  // Set of subject names that have notes
  const noteSubjectNames = useMemo(() => {
    if (!allNotes) return new Set<string>()
    return new Set(allNotes.map((n) => n.subject_name))
  }, [allNotes])

  // PE teacher filter
  const peTeachers = useMemo(
    () => (weekSchedule ? getPeTeachersFromWeek(weekSchedule) : []),
    [weekSchedule],
  )

  // All entries before filtering (for alternate entry detection)
  const allEntries = useMemo(() => {
    if (!weekSchedule) return []
    return weekSchedule.days.flatMap((d) => d.entries)
  }, [weekSchedule])

  // Apply filters: PE teacher first, then subgroup
  const filteredWeekSchedule = useMemo(() => {
    if (!weekSchedule) return undefined
    let filtered = filterWeekSchedule(weekSchedule, peTeacher)
    filtered = filterWeekBySubgroup(filtered, subgroup)
    return filtered
  }, [weekSchedule, peTeacher, subgroup])

  const handlePeTeacherChange = useCallback((teacher: string | null) => {
    setPeTeacher(teacher)
  }, [setPeTeacher])

  // Mutation for refreshing schedule from OmGU
  const refreshMutation = useMutation({
    mutationFn: () => scheduleService.refreshSchedule(false),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['schedule'] })
      if (data.changed) {
        toast.success(`Расписание обновлено (${data.entries_count} записей)`)
      } else {
        toast.info('Расписание не изменилось')
      }
    },
    onError: () => {
      toast.error('Не удалось обновить расписание')
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
  const timeRemaining = (() => {
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
  })()

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
    <div className="h-screen bg-background flex flex-col overflow-hidden">
      <div className="container mx-auto px-2 py-2 flex flex-col flex-1 overflow-hidden">
        {/* Header */}
        <div className="flex items-center gap-2 mb-2">
          <Link to="/">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <h1 className="text-2xl font-bold flex-1">Расписание</h1>
          {peTeachers.length > 1 && (
            <PeTeacherSelect teachers={peTeachers} onChange={handlePeTeacherChange} />
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={handleRefresh}
            disabled={refreshMutation.isPending || !isOnline}
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
        <Card className="mb-2">
          <CardContent className="py-2 px-3">
            <div className="flex items-center justify-between">
              {/* Week info - left */}
              <div>
                <span className="font-medium">Неделя {weekSchedule?.week_number}</span>
                <span className="text-sm text-muted-foreground ml-2">
                  ({weekSchedule?.is_odd_week ? 'нечётная' : 'чётная'})
                </span>
              </div>

              {/* Navigation buttons - right */}
              <div className="flex items-center gap-1">
                {/* Date picker */}
                <Popover open={calendarOpen} onOpenChange={setCalendarOpen}>
                  <PopoverTrigger asChild>
                    <Button variant="ghost" size="icon">
                      <CalendarDays className="h-4 w-4" />
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="end">
                    <Calendar
                      mode="single"
                      selected={targetDate ? new Date(targetDate) : new Date(today)}
                      onSelect={(date) => {
                        if (date) {
                          setTargetDate(formatDateLocal(date))
                        }
                        setCalendarOpen(false)
                      }}
                      onTodayClick={() => {
                        setTargetDate(undefined)
                        setCalendarOpen(false)
                      }}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>

                {/* To current week */}
                {!isCurrentWeek && (
                  <Button variant="ghost" size="sm" onClick={goToCurrentWeek}>
                    Сегодня
                  </Button>
                )}

                {/* Previous/Next week */}
                <Button variant="ghost" size="icon" onClick={goToPreviousWeek}>
                  <ChevronLeft className="h-5 w-5" />
                </Button>
                <Button variant="ghost" size="icon" onClick={goToNextWeek}>
                  <ChevronRight className="h-5 w-5" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Current lesson indicator */}
        {currentLesson?.current && isCurrentWeek && timeRemaining && (
          <Card className="mb-2 border-primary">
            <CardContent className="py-2 px-3">
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
          <Card className="mb-2">
            <CardContent className="py-2 px-3">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-muted-foreground">Следующая:</div>
                  <div className="font-medium">{currentLesson.next.subject_name}</div>
                </div>
                {currentLesson.time_until_next !== null && (
                  <div className="text-right">
                    <div className="text-xs text-muted-foreground">Через:</div>
                    <div className="font-medium">
                      {formatTimeUntil(currentLesson.time_until_next)}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Schedule grid */}
        <div className="flex-1 overflow-auto">
          {filteredWeekSchedule && (
            <ScheduleGrid
              weekSchedule={filteredWeekSchedule}
              currentEntryId={currentLesson?.current?.id}
              noteSubjectNames={noteSubjectNames}
              onEntryClick={setSelectedEntry}
              allEntries={allEntries}
              userSubgroup={subgroup}
            />
          )}

          {/* Empty state */}
          {filteredWeekSchedule?.days.every((d) => d.entries.length === 0) && (
            <Card className="mt-2">
              <CardContent className="py-6 text-center text-muted-foreground">
                <p>На этой неделе нет занятий</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      <LessonDetailModal
        entry={selectedEntry}
        open={!!selectedEntry}
        onClose={() => setSelectedEntry(null)}
      />
    </div>
  )
}

export default SchedulePage
