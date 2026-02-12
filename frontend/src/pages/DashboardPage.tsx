import { useState, useMemo } from 'react'
import { useAuthStore } from '@/stores/authStore'
import { useUserSettings } from '@/hooks/useUserSettings'
import { Button } from '@/components/ui/button'
import { LogOut } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { scheduleService } from '@/services/scheduleService'
import { workService } from '@/services/workService'
import subjectService from '@/services/subjectService'
import { calculateSemesterProgress } from '@/lib/progressUtils'
import { filterDaySchedule } from '@/lib/peTeacherFilter'
import { filterDayBySubgroup } from '@/lib/subgroupFilter'
import { TodayScheduleWidget } from '@/components/dashboard/TodayScheduleWidget'
import { DeadlinesWidget } from '@/components/dashboard/DeadlinesWidget'
import { SemesterProgressWidget } from '@/components/dashboard/SemesterProgressWidget'
import { SemesterTimelineWidget } from '@/components/dashboard/SemesterTimelineWidget'
import { QuickActions } from '@/components/dashboard/QuickActions'
import { LessonDetailModal } from '@/components/schedule/LessonDetailModal'
import type { ScheduleEntry } from '@/types/schedule'
import type { Semester } from '@/types/subject'

export default function DashboardPage() {
  const { user, logout } = useAuthStore()
  const { settings } = useUserSettings()
  const { peTeacher, subgroup } = settings
  const [selectedEntry, setSelectedEntry] = useState<ScheduleEntry | null>(null)

  const handleLogout = async () => {
    if (!confirm('Вы уверены, что хотите выйти?')) return
    await logout()
  }

  // Schedule data - refreshes frequently
  const {
    data: todaySchedule,
    isLoading: todayLoading,
    isError: todayError,
  } = useQuery({
    queryKey: ['schedule', 'today'],
    queryFn: ({ signal }) => scheduleService.getTodaySchedule(undefined, signal),
    staleTime: 60 * 1000, // 1 min
  })

  const {
    data: currentLesson,
    isLoading: currentLoading,
  } = useQuery({
    queryKey: ['currentLesson'],
    queryFn: ({ signal }) => scheduleService.getCurrentLesson(signal),
    refetchInterval: 60 * 1000, // 1 min
    staleTime: 30 * 1000, // 30 sec
  })

  // Works data - moderate refresh
  const {
    data: upcomingWorks,
    isLoading: upcomingWorksLoading,
    isError: upcomingWorksError,
  } = useQuery({
    queryKey: ['upcomingWorks'],
    queryFn: ({ signal }) => workService.getUpcomingWorks(10, signal),
    staleTime: 2 * 60 * 1000, // 2 min
    gcTime: 10 * 60 * 1000, // 10 min cache
  })

  const {
    data: allWorks = [],
    isLoading: allWorksLoading,
    isError: allWorksError,
  } = useQuery({
    queryKey: ['works'],
    queryFn: ({ signal }) => workService.getWorks(undefined, signal),
    staleTime: 2 * 60 * 1000, // 2 min
    gcTime: 10 * 60 * 1000, // 10 min cache
  })

  // Reference data - rarely changes, longer cache
  const {
    data: subjects = [],
    isLoading: subjectsLoading,
    isError: subjectsError,
  } = useQuery({
    queryKey: ['subjects'],
    queryFn: ({ signal }) => subjectService.getSubjects(undefined, signal),
    staleTime: 5 * 60 * 1000, // 5 min
    gcTime: 30 * 60 * 1000, // 30 min cache
  })

  const {
    data: currentSemester,
    isLoading: currentSemesterLoading,
    isError: currentSemesterError,
  } = useQuery<Semester | null>({
    queryKey: ['semesters', 'current'],
    queryFn: ({ signal }) => subjectService.getCurrentSemester(signal),
    staleTime: 10 * 60 * 1000, // 10 min - semester rarely changes
    gcTime: 60 * 60 * 1000, // 1 hour cache
  })

  const {
    data: timeline,
    isLoading: timelineLoading,
    isError: timelineError,
  } = useQuery({
    queryKey: ['timeline', currentSemester?.id],
    queryFn: ({ signal }) => subjectService.getSemesterTimeline(currentSemester!.id, signal),
    enabled: !!currentSemester?.start_date && !!currentSemester?.end_date,
    staleTime: 5 * 60 * 1000, // 5 min
    gcTime: 30 * 60 * 1000, // 30 min cache
  })

  const filteredTodaySchedule = useMemo(() => {
    if (!todaySchedule) return undefined
    let filtered = filterDaySchedule(todaySchedule, peTeacher)
    filtered = filterDayBySubgroup(filtered, subgroup)
    return filtered
  }, [todaySchedule, peTeacher, subgroup])

  const semesterProgress = useMemo(
    () => calculateSemesterProgress(allWorks, subjects),
    [allWorks, subjects],
  )

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
          <h2 className="text-2xl font-bold">
            Привет, {user?.name}!
          </h2>
        </div>

        {/* Widgets */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <TodayScheduleWidget
            todaySchedule={filteredTodaySchedule}
            currentLesson={currentLesson}
            isLoading={todayLoading || currentLoading}
            isError={todayError}
            onEntryClick={setSelectedEntry}
          />
          <DeadlinesWidget
            data={upcomingWorks}
            isLoading={upcomingWorksLoading}
            isError={upcomingWorksError}
          />
          <SemesterProgressWidget
            progress={semesterProgress}
            isLoading={subjectsLoading || allWorksLoading}
            isError={subjectsError || allWorksError}
          />
          <SemesterTimelineWidget
            semester={currentSemester}
            timeline={timeline}
            isLoading={currentSemesterLoading || timelineLoading}
            isError={currentSemesterError || timelineError}
          />
        </div>

        {/* Quick actions grid */}
        <QuickActions />
      </main>

      <LessonDetailModal
        entry={selectedEntry}
        open={!!selectedEntry}
        onClose={() => setSelectedEntry(null)}
      />
    </div>
  )
}
