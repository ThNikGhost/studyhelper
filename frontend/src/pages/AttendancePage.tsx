import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNetworkStatus } from '@/hooks/useNetworkStatus'
import { ArrowLeft, RefreshCw, Loader2, CheckCircle2, AlertCircle } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { toast } from 'sonner'
import { AttendanceStatsCard } from '@/components/attendance/AttendanceStatsCard'
import { SubjectAttendanceList } from '@/components/attendance/SubjectAttendanceList'
import { AttendanceTable } from '@/components/attendance/AttendanceTable'
import attendanceService from '@/services/attendanceService'
import subjectService from '@/services/subjectService'
import type { Semester } from '@/types/subject'
import type { AttendanceEntry, AttendanceStats } from '@/types/attendance'

export function AttendancePage() {
  const isOnline = useNetworkStatus()
  const queryClient = useQueryClient()

  const [selectedSemesterId, setSelectedSemesterId] = useState<number | undefined>(undefined)
  const [filterSubjectId, setFilterSubjectId] = useState<number | null>(null)
  const [togglingId, setTogglingId] = useState<number | null>(null)

  // Fetch semesters
  const { data: semesters = [], isLoading: semestersLoading } = useQuery<Semester[]>({
    queryKey: ['semesters'],
    queryFn: ({ signal }) => subjectService.getSemesters(signal),
  })

  // Fetch current semester
  const { data: currentSemester } = useQuery<Semester | null>({
    queryKey: ['semesters', 'current'],
    queryFn: ({ signal }) => subjectService.getCurrentSemester(signal),
  })

  // Auto-select current semester
  const effectiveSemesterId = selectedSemesterId ?? currentSemester?.id

  // Check if selected semester has dates
  const selectedSemester = semesters.find((s) => s.id === effectiveSemesterId)
  const hasDates = !!(selectedSemester?.start_date && selectedSemester?.end_date)

  // Fetch stats
  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError,
  } = useQuery<AttendanceStats>({
    queryKey: ['attendance-stats', effectiveSemesterId],
    queryFn: ({ signal }) => attendanceService.getStats(effectiveSemesterId!, signal),
    enabled: !!effectiveSemesterId && hasDates,
  })

  // Fetch entries
  const {
    data: entries = [],
    isLoading: entriesLoading,
    error: entriesError,
    refetch,
  } = useQuery<AttendanceEntry[]>({
    queryKey: ['attendance-entries', effectiveSemesterId, filterSubjectId],
    queryFn: ({ signal }) =>
      attendanceService.getEntries(effectiveSemesterId!, filterSubjectId, 100, 0, signal),
    enabled: !!effectiveSemesterId && hasDates,
  })

  // Mark absent mutation
  const markAbsentMutation = useMutation({
    mutationFn: (entryId: number) => attendanceService.markAbsent(entryId),
    onSuccess: () => {
      toast.success('Пропуск отмечен')
      queryClient.invalidateQueries({ queryKey: ['attendance-entries', effectiveSemesterId] })
      queryClient.invalidateQueries({ queryKey: ['attendance-stats', effectiveSemesterId] })
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
      queryClient.invalidateQueries({ queryKey: ['attendance-entries', effectiveSemesterId] })
      queryClient.invalidateQueries({ queryKey: ['attendance-stats', effectiveSemesterId] })
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

  const isLoading = semestersLoading || (hasDates && (statsLoading || entriesLoading))
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
          disabled={!isOnline || !hasDates}
          aria-label="Обновить"
        >
          <RefreshCw className="h-4 w-4" />
        </Button>
      </div>

      {/* Semester selector */}
      <Card className="mb-6">
        <CardContent className="py-3 px-4">
          <Label htmlFor="semester-select" className="text-sm text-muted-foreground">
            Семестр
          </Label>
          <select
            id="semester-select"
            className="w-full mt-1 px-3 py-2 bg-background border rounded-md text-sm"
            value={effectiveSemesterId || ''}
            onChange={(e) => {
              setSelectedSemesterId(e.target.value ? Number(e.target.value) : undefined)
              setFilterSubjectId(null)
            }}
          >
            {semesters.map((semester) => (
              <option key={semester.id} value={semester.id}>
                Семестр {semester.number} {semester.is_current && '(текущий)'}
              </option>
            ))}
          </select>
        </CardContent>
      </Card>

      {/* No dates warning */}
      {effectiveSemesterId && !hasDates && (
        <Card className="mb-6 border-amber-200 bg-amber-50 dark:border-amber-900 dark:bg-amber-950/30">
          <CardContent className="py-4 px-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-amber-800 dark:text-amber-200">
                  Даты семестра не указаны
                </p>
                <p className="text-sm text-amber-700 dark:text-amber-300 mt-1">
                  Для отслеживания посещаемости укажите даты начала и окончания семестра в{' '}
                  <Link to="/semesters" className="underline hover:no-underline">
                    настройках семестров
                  </Link>
                  .
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Loading */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : error ? (
        <div className="text-center py-12 text-destructive">
          <p className="text-sm">Ошибка загрузки данных о посещаемости</p>
        </div>
      ) : hasDates ? (
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
            {entries.length > 0 ? (
              <AttendanceTable
                entries={entries}
                onToggle={handleToggle}
                isToggling={togglingId}
                disabled={!isOnline}
              />
            ) : (
              <Card>
                <CardContent className="py-8 text-center text-muted-foreground">
                  <p>Нет завершённых занятий в этом семестре</p>
                  <p className="text-sm mt-1">
                    Занятия появятся здесь после их окончания
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      ) : null}
    </div>
  )
}

export default AttendancePage
