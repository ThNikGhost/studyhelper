import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNetworkStatus } from '@/hooks/useNetworkStatus'
import { ArrowLeft, RefreshCw, Loader2, CheckCircle2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { toast } from 'sonner'
import { AttendanceStatsCard } from '@/components/attendance/AttendanceStatsCard'
import { SubjectAttendanceList } from '@/components/attendance/SubjectAttendanceList'
import { AttendanceTable } from '@/components/attendance/AttendanceTable'
import attendanceService from '@/services/attendanceService'

export function AttendancePage() {
  const isOnline = useNetworkStatus()
  const queryClient = useQueryClient()

  const [filterSubjectId, setFilterSubjectId] = useState<number | null>(null)
  const [togglingId, setTogglingId] = useState<number | null>(null)

  // Fetch stats
  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError,
  } = useQuery({
    queryKey: ['attendance-stats'],
    queryFn: ({ signal }) => attendanceService.getStats(signal),
  })

  // Fetch entries
  const {
    data: entries = [],
    isLoading: entriesLoading,
    error: entriesError,
    refetch,
  } = useQuery({
    queryKey: ['attendance-entries', filterSubjectId],
    queryFn: ({ signal }) =>
      attendanceService.getEntries(filterSubjectId, null, null, signal),
  })

  // Mark absent mutation
  const markAbsentMutation = useMutation({
    mutationFn: (entryId: number) => attendanceService.markAbsent(entryId),
    onSuccess: () => {
      toast.success('Пропуск отмечен')
      queryClient.invalidateQueries({ queryKey: ['attendance-entries'] })
      queryClient.invalidateQueries({ queryKey: ['attendance-stats'] })
    },
    onError: () => {
      toast.error('Ошибка при отметке пропуска')
    },
    onSettled: () => setTogglingId(null),
  })

  // Mark present mutation
  const markPresentMutation = useMutation({
    mutationFn: (entryId: number) => attendanceService.markPresent(entryId),
    onSuccess: () => {
      toast.success('Присутствие отмечено')
      queryClient.invalidateQueries({ queryKey: ['attendance-entries'] })
      queryClient.invalidateQueries({ queryKey: ['attendance-stats'] })
    },
    onError: () => {
      toast.error('Ошибка при отметке присутствия')
    },
    onSettled: () => setTogglingId(null),
  })

  const handleToggle = (entryId: number, isCurrentlyAbsent: boolean) => {
    setTogglingId(entryId)
    if (isCurrentlyAbsent) {
      markPresentMutation.mutate(entryId)
    } else {
      markAbsentMutation.mutate(entryId)
    }
  }

  const isLoading = statsLoading || entriesLoading
  const error = statsError || entriesError

  return (
    <div className="container mx-auto px-4 py-6 max-w-4xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Link to="/">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-6 w-6 text-teal-500" />
            <h1 className="text-2xl font-bold">Посещаемость</h1>
          </div>
        </div>
        <Button
          variant="outline"
          size="icon"
          onClick={() => refetch()}
          disabled={!isOnline}
          aria-label="Обновить"
        >
          <RefreshCw className="h-4 w-4" />
        </Button>
      </div>

      {/* Loading */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : error ? (
        <div className="text-center py-12 text-destructive">
          <p className="text-sm">Ошибка загрузки данных о посещаемости</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Stats card */}
          {stats && <AttendanceStatsCard stats={stats} />}

          {/* Subject list */}
          {stats && stats.by_subject.length > 0 && (
            <SubjectAttendanceList
              subjects={stats.by_subject}
              selectedSubjectId={filterSubjectId}
              onSelectSubject={setFilterSubjectId}
            />
          )}

          {/* Entries table */}
          <div>
            <h2 className="text-lg font-semibold mb-3">
              Журнал занятий
              {filterSubjectId !== null && (
                <Button
                  variant="ghost"
                  size="sm"
                  className="ml-2 text-xs"
                  onClick={() => setFilterSubjectId(null)}
                >
                  Сбросить фильтр
                </Button>
              )}
            </h2>
            <AttendanceTable
              entries={entries}
              onToggle={handleToggle}
              isToggling={togglingId}
              disabled={!isOnline}
            />
          </div>
        </div>
      )}
    </div>
  )
}

export default AttendancePage
