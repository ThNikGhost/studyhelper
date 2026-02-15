import { useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNetworkStatus } from '@/hooks/useNetworkStatus'
import {
  ArrowLeft,
  GraduationCap,
  RefreshCw,
  Loader2,
  AlertCircle,
  Settings,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { toast } from 'sonner'
import { lkService } from '@/services/lkService'
import type { SessionGrade } from '@/types/lk'

/** Grade badge color based on result. */
function getGradeColor(result: string): string {
  const lower = result.toLowerCase()
  if (lower.includes('отлично') || lower === '5') {
    return 'bg-green-100 text-green-800 border border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800'
  }
  if (lower.includes('хорошо') || lower === '4') {
    return 'bg-blue-100 text-blue-800 border border-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800'
  }
  if (lower.includes('удовл') || lower === '3') {
    return 'bg-yellow-100 text-yellow-800 border border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-800'
  }
  if (lower.includes('зачтено') || lower.includes('зачёт')) {
    return 'bg-teal-100 text-teal-800 border border-teal-200 dark:bg-teal-900/30 dark:text-teal-400 dark:border-teal-800'
  }
  if (lower.includes('неуд') || lower.includes('незач') || lower === '2') {
    return 'bg-red-100 text-red-800 border border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800'
  }
  return 'bg-gray-100 text-gray-800 border border-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700'
}

/** Convert result to numeric value for average calculation. */
function getNumericGrade(result: string): number | null {
  const lower = result.toLowerCase()
  if (lower.includes('отлично') || lower === '5') return 5
  if (lower.includes('хорошо') || lower === '4') return 4
  if (lower.includes('удовл') || lower === '3') return 3
  if (lower.includes('неуд') || lower === '2') return 2
  return null
}

/** Group grades by session. */
function groupBySession(grades: SessionGrade[]): Map<string, SessionGrade[]> {
  const groups = new Map<string, SessionGrade[]>()
  for (const grade of grades) {
    const existing = groups.get(grade.session_number) || []
    existing.push(grade)
    groups.set(grade.session_number, existing)
  }
  return groups
}

interface GradeStats {
  total: number
  average: number | null
  excellentCount: number
  excellentPercent: number
}

/** Calculate grade statistics. */
function calculateStats(grades: SessionGrade[]): GradeStats {
  const numericGrades = grades
    .map((g) => getNumericGrade(g.result))
    .filter((n): n is number => n !== null)

  const excellentCount = numericGrades.filter((n) => n === 5).length
  const average =
    numericGrades.length > 0
      ? numericGrades.reduce((a, b) => a + b, 0) / numericGrades.length
      : null

  return {
    total: grades.length,
    average,
    excellentCount,
    excellentPercent:
      numericGrades.length > 0
        ? Math.round((excellentCount / numericGrades.length) * 100)
        : 0,
  }
}

export default function GradesPage() {
  const isOnline = useNetworkStatus()
  const queryClient = useQueryClient()

  // Fetch LK status
  const { data: lkStatus, isLoading: lkStatusLoading } = useQuery({
    queryKey: ['lk', 'status'],
    queryFn: ({ signal }) => lkService.getStatus(signal),
    staleTime: 1000 * 60,
  })

  // Fetch grades
  const {
    data: grades = [],
    isLoading: gradesLoading,
    error: gradesError,
    refetch,
  } = useQuery({
    queryKey: ['lk', 'grades'],
    queryFn: ({ signal }) => lkService.getGrades(undefined, signal),
    enabled: lkStatus?.has_credentials === true,
  })

  // Fetch available sessions for filter
  const { data: sessions = [] } = useQuery({
    queryKey: ['lk', 'sessions'],
    queryFn: ({ signal }) => lkService.getSessions(signal),
    enabled: lkStatus?.has_credentials === true,
  })

  // Sync mutation
  const syncMutation = useMutation({
    mutationFn: () => lkService.sync(),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['lk', 'status'] })
      queryClient.invalidateQueries({ queryKey: ['lk', 'grades'] })
      queryClient.invalidateQueries({ queryKey: ['lk', 'sessions'] })
      toast.success(
        `Синхронизировано: ${result.grades_synced} оценок, ${result.disciplines_synced} дисциплин`
      )
    },
    onError: () => {
      toast.error('Ошибка синхронизации')
    },
  })

  // Group grades by session
  const groupedGrades = useMemo(() => groupBySession(grades), [grades])

  // Calculate overall stats
  const stats = useMemo(() => calculateStats(grades), [grades])

  // Sort sessions descending (newest first)
  const sortedSessions = useMemo(
    () => [...sessions].sort((a, b) => b.localeCompare(a)),
    [sessions]
  )

  const isLoading = lkStatusLoading || gradesLoading
  const isSyncing = syncMutation.isPending

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container max-w-2xl mx-auto px-4 py-6">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-muted rounded w-1/3" />
            <div className="h-24 bg-muted rounded" />
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-20 bg-muted rounded" />
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Not connected state
  if (!lkStatus?.has_credentials) {
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
            <h1 className="text-2xl font-bold flex-1">Зачётка</h1>
          </div>

          <Card>
            <CardContent className="py-10 text-center">
              <AlertCircle className="h-12 w-12 mx-auto mb-4 text-amber-500" />
              <p className="text-lg font-medium mb-2">
                Личный кабинет не подключён
              </p>
              <p className="text-muted-foreground mb-4">
                Подключите ЛК ОмГУ в настройках для просмотра оценок
              </p>
              <Link to="/settings">
                <Button className="gap-2">
                  <Settings className="h-4 w-4" />
                  Перейти в настройки
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  // Error state
  if (gradesError) {
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
            <h1 className="text-2xl font-bold flex-1">Зачётка</h1>
          </div>

          <Card>
            <CardContent className="py-10 text-center">
              <p className="text-destructive mb-4">Ошибка загрузки оценок</p>
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
          <h1 className="text-2xl font-bold flex-1">Зачётка</h1>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => syncMutation.mutate()}
            disabled={isSyncing || !isOnline}
            title="Синхронизировать"
          >
            {isSyncing ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <RefreshCw className="h-5 w-5" />
            )}
          </Button>
        </div>

        {/* Stats card */}
        {grades.length > 0 && (
          <Card className="mb-6">
            <CardContent className="py-4 px-4">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold">{stats.total}</p>
                  <p className="text-xs text-muted-foreground">Всего оценок</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    {stats.average !== null ? stats.average.toFixed(2) : '—'}
                  </p>
                  <p className="text-xs text-muted-foreground">Средний балл</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {stats.excellentPercent}%
                  </p>
                  <p className="text-xs text-muted-foreground">Отлично</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Empty state */}
        {grades.length === 0 && (
          <Card>
            <CardContent className="py-10 text-center text-muted-foreground">
              <GraduationCap className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Нет оценок</p>
              <p className="text-sm mt-1">
                Нажмите кнопку синхронизации для загрузки
              </p>
            </CardContent>
          </Card>
        )}

        {/* Grades by session */}
        {sortedSessions.length > 0 && (
          <div className="space-y-4">
            {sortedSessions.map((session) => {
              const sessionGrades = groupedGrades.get(session) || []
              if (sessionGrades.length === 0) return null

              return (
                <Card key={session}>
                  <CardHeader className="py-3 px-4">
                    <CardTitle className="text-base flex items-center gap-2">
                      <GraduationCap className="h-4 w-4 text-violet-500" />
                      Сессия {session}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="py-0 px-4 pb-3">
                    <div className="space-y-2">
                      {sessionGrades.map((grade) => (
                        <div
                          key={grade.id}
                          className="flex items-center justify-between py-2 border-b last:border-0"
                        >
                          <span className="text-sm flex-1 pr-2 truncate">
                            {grade.subject_name}
                          </span>
                          <span
                            className={`text-xs px-2 py-1 rounded font-medium shrink-0 ${getGradeColor(grade.result)}`}
                          >
                            {grade.result}
                          </span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
