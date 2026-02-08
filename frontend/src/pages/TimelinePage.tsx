import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { ArrowLeft, BarChart3, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import subjectService from '@/services/subjectService'
import { TimelineBar } from '@/components/timeline/TimelineBar'
import { TimelineLegend } from '@/components/timeline/TimelineLegend'
import { TimelineEventList } from '@/components/timeline/TimelineEventList'
import type { Semester } from '@/types/subject'

export function TimelinePage() {
  const [showDeadlines, setShowDeadlines] = useState(true)
  const [showExams, setShowExams] = useState(true)
  const [subjectFilter, setSubjectFilter] = useState<number | null>(null)

  // Get current semester
  const {
    data: currentSemester,
    isLoading: semesterLoading,
    isError: semesterError,
  } = useQuery<Semester | null>({
    queryKey: ['semesters', 'current'],
    queryFn: ({ signal }) => subjectService.getCurrentSemester(signal),
  })

  // Get timeline data
  const {
    data: timeline,
    isLoading: timelineLoading,
    isError: timelineError,
  } = useQuery({
    queryKey: ['timeline', currentSemester?.id],
    queryFn: ({ signal }) => subjectService.getSemesterTimeline(currentSemester!.id, signal),
    enabled: !!currentSemester?.start_date && !!currentSemester?.end_date,
  })

  // Unique subjects for filter dropdown
  const subjects = useMemo(() => {
    if (!timeline) return []
    const map = new Map<number, string>()
    for (const d of timeline.deadlines) {
      map.set(d.subject_id, d.subject_name)
    }
    return Array.from(map, ([id, name]) => ({ id, name }))
  }, [timeline])

  const isLoading = semesterLoading || timelineLoading

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container max-w-3xl mx-auto px-4 py-6">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-muted rounded w-1/3" />
            <div className="h-16 bg-muted rounded" />
            <div className="h-40 bg-muted rounded" />
          </div>
        </div>
      </div>
    )
  }

  if (semesterError || timelineError) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container max-w-3xl mx-auto px-4 py-6">
          <Card>
            <CardContent className="py-10 text-center">
              <p className="text-destructive mb-4">Ошибка загрузки данных</p>
              <Link to="/">
                <Button>На главную</Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  // No current semester set
  if (!currentSemester) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container max-w-3xl mx-auto px-4 py-6">
          <div className="flex items-center gap-4 mb-6">
            <Link to="/">
              <Button variant="ghost" size="icon">
                <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>
            <h1 className="text-2xl font-bold">Timeline семестра</h1>
          </div>
          <Card>
            <CardContent className="py-10 text-center">
              <AlertCircle className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
              <p className="text-muted-foreground mb-2">Текущий семестр не установлен</p>
              <Link to="/semesters">
                <Button variant="outline">Настроить семестры</Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  // Current semester has no dates
  if (!currentSemester.start_date || !currentSemester.end_date) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container max-w-3xl mx-auto px-4 py-6">
          <div className="flex items-center gap-4 mb-6">
            <Link to="/">
              <Button variant="ghost" size="icon">
                <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>
            <h1 className="text-2xl font-bold">Timeline семестра</h1>
          </div>
          <Card>
            <CardContent className="py-10 text-center">
              <AlertCircle className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
              <p className="text-muted-foreground mb-2">
                Укажите даты начала и окончания семестра
              </p>
              <Link to="/semesters">
                <Button variant="outline">Перейти к семестрам</Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container max-w-3xl mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <Link to="/">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div className="flex-1">
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <BarChart3 className="h-6 w-6 text-indigo-500" />
              Timeline
            </h1>
            <p className="text-sm text-muted-foreground">{currentSemester.name}</p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-4 mb-4">
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input
              type="checkbox"
              checked={showDeadlines}
              onChange={(e) => setShowDeadlines(e.target.checked)}
              className="rounded"
            />
            Дедлайны
          </label>
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input
              type="checkbox"
              checked={showExams}
              onChange={(e) => setShowExams(e.target.checked)}
              className="rounded"
            />
            Экзамены
          </label>
          {subjects.length > 0 && (
            <div className="flex items-center gap-2">
              <Label htmlFor="subject-filter" className="text-sm whitespace-nowrap">
                Предмет:
              </Label>
              <select
                id="subject-filter"
                value={subjectFilter ?? ''}
                onChange={(e) => setSubjectFilter(e.target.value ? Number(e.target.value) : null)}
                className="text-sm border rounded px-2 py-1 bg-background"
              >
                <option value="">Все</option>
                {subjects.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Timeline bar */}
        <div className="mb-4 pt-6">
          <TimelineBar
            startDate={currentSemester.start_date}
            endDate={currentSemester.end_date}
            deadlines={timeline?.deadlines ?? []}
            exams={timeline?.exams ?? []}
            showDeadlines={showDeadlines}
            showExams={showExams}
            subjectFilter={subjectFilter}
          />
        </div>

        {/* Legend */}
        <div className="mb-6">
          <TimelineLegend />
        </div>

        {/* Event list */}
        {timeline && (
          <TimelineEventList
            deadlines={showDeadlines ? (subjectFilter ? timeline.deadlines.filter((d) => d.subject_id === subjectFilter) : timeline.deadlines) : []}
            exams={showExams ? timeline.exams : []}
          />
        )}
      </div>
    </div>
  )
}

export default TimelinePage
