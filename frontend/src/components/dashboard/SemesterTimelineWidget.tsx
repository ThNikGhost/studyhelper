import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart3, Loader2, AlertTriangle } from 'lucide-react'
import { Link } from 'react-router-dom'
import { TimelineBar } from '@/components/timeline/TimelineBar'
import type { TimelineData } from '@/types/timeline'
import type { Semester } from '@/types/subject'

interface SemesterTimelineWidgetProps {
  semester: Semester | null | undefined
  timeline: TimelineData | undefined
  isLoading: boolean
  isError: boolean
}

export function SemesterTimelineWidget({
  semester,
  timeline,
  isLoading,
  isError,
}: SemesterTimelineWidgetProps) {
  if (isLoading) {
    return (
      <Card className="md:col-span-2">
        <CardHeader className="pb-2">
          <CardTitle className="text-base flex items-center gap-2">
            <BarChart3 className="h-4 w-4 text-indigo-500" />
            Timeline семестра
          </CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center py-6">
          <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    )
  }

  if (isError) {
    return (
      <Card className="md:col-span-2">
        <CardHeader className="pb-2">
          <CardTitle className="text-base flex items-center gap-2">
            <BarChart3 className="h-4 w-4 text-indigo-500" />
            Timeline семестра
          </CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center py-6 text-muted-foreground">
          <AlertTriangle className="h-4 w-4 mr-2" />
          Ошибка загрузки
        </CardContent>
      </Card>
    )
  }

  // No semester or no dates
  if (!semester?.start_date || !semester?.end_date) {
    return null
  }

  return (
    <Card className="md:col-span-2">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <BarChart3 className="h-4 w-4 text-indigo-500" />
            Timeline семестра
          </CardTitle>
          <Link
            to="/timeline"
            className="text-xs text-primary hover:underline"
          >
            Подробнее →
          </Link>
        </div>
      </CardHeader>
      <CardContent className="pt-4">
        <TimelineBar
          startDate={semester.start_date}
          endDate={semester.end_date}
          deadlines={timeline?.deadlines ?? []}
          exams={timeline?.exams ?? []}
        />
      </CardContent>
    </Card>
  )
}
