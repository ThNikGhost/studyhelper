import { useState } from 'react'
import { useAuthStore } from '@/stores/authStore'
import { Button } from '@/components/ui/button'
import { LogOut } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { scheduleService } from '@/services/scheduleService'
import { workService } from '@/services/workService'
import { TodayScheduleWidget } from '@/components/dashboard/TodayScheduleWidget'
import { DeadlinesWidget } from '@/components/dashboard/DeadlinesWidget'
import { QuickActions } from '@/components/dashboard/QuickActions'
import { LessonDetailModal } from '@/components/schedule/LessonDetailModal'
import type { ScheduleEntry } from '@/types/schedule'

export default function DashboardPage() {
  const { user, logout } = useAuthStore()
  const [selectedEntry, setSelectedEntry] = useState<ScheduleEntry | null>(null)

  const handleLogout = async () => {
    if (!confirm('Вы уверены, что хотите выйти?')) return
    await logout()
  }

  const {
    data: todaySchedule,
    isLoading: todayLoading,
    isError: todayError,
  } = useQuery({
    queryKey: ['schedule', 'today'],
    queryFn: ({ signal }) => scheduleService.getTodaySchedule(undefined, signal),
    staleTime: 60000,
  })

  const {
    data: currentLesson,
    isLoading: currentLoading,
  } = useQuery({
    queryKey: ['currentLesson'],
    queryFn: ({ signal }) => scheduleService.getCurrentLesson(signal),
    refetchInterval: 60000,
    staleTime: 30000,
  })

  const {
    data: upcomingWorks,
    isLoading: worksLoading,
    isError: worksError,
  } = useQuery({
    queryKey: ['upcomingWorks'],
    queryFn: ({ signal }) => workService.getUpcomingWorks(10, signal),
    staleTime: 60000,
  })

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
          <TodayScheduleWidget
            todaySchedule={todaySchedule}
            currentLesson={currentLesson}
            isLoading={todayLoading || currentLoading}
            isError={todayError}
            onEntryClick={setSelectedEntry}
          />
          <DeadlinesWidget
            data={upcomingWorks}
            isLoading={worksLoading}
            isError={worksError}
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
