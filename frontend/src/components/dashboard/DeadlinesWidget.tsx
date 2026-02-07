import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  ClipboardList,
  AlertCircle,
  CheckCircle2,
  Loader2,
  ArrowRight,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { formatDeadline, getDeadlineColor } from '@/lib/dateUtils'
import {
  workTypeLabels,
  workStatusLabels,
  workStatusColors,
  WorkStatus,
  type UpcomingWork,
} from '@/types/work'

type UrgencyGroup = 'overdue' | 'soon' | 'week'

interface GroupedWork {
  urgency: UrgencyGroup
  work: UpcomingWork
}

/** Classify a work item by deadline urgency. */
function getUrgency(deadline: string): UrgencyGroup {
  const date = new Date(deadline)
  const now = new Date()
  const diffMs = date.getTime() - now.getTime()
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays < 0) return 'overdue'
  if (diffDays <= 1) return 'soon'
  return 'week'
}

const urgencyOrder: Record<UrgencyGroup, number> = {
  overdue: 0,
  soon: 1,
  week: 2,
}

const urgencyLabels: Record<UrgencyGroup, string> = {
  overdue: 'Просрочено',
  soon: 'Сегодня / Завтра',
  week: 'На неделе',
}

const urgencyStyles: Record<UrgencyGroup, string> = {
  overdue: 'text-red-600 dark:text-red-400',
  soon: 'text-orange-600 dark:text-orange-400',
  week: 'text-muted-foreground',
}

const MAX_VISIBLE = 8

interface DeadlinesWidgetProps {
  data: UpcomingWork[] | undefined
  isLoading: boolean
  isError: boolean
}

export function DeadlinesWidget({ data, isLoading, isError }: DeadlinesWidgetProps) {
  // Group and sort works by urgency
  const grouped: GroupedWork[] = (data ?? [])
    .map((work) => ({ urgency: getUrgency(work.deadline), work }))
    .sort((a, b) => urgencyOrder[a.urgency] - urgencyOrder[b.urgency])

  const overdueCount = grouped.filter((g) => g.urgency === 'overdue').length

  // Determine which urgency groups are present in visible items
  const visible = grouped.slice(0, MAX_VISIBLE)
  const groupBreaks = new Set<number>()
  visible.forEach((item, idx) => {
    if (idx === 0 || item.urgency !== visible[idx - 1].urgency) {
      groupBreaks.add(idx)
    }
  })

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ClipboardList className="h-5 w-5 text-orange-500" />
          Ближайшие дедлайны
          {overdueCount > 0 && (
            <span className="ml-auto text-xs bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300 px-2 py-0.5 rounded-full">
              {overdueCount} просроч.
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading && (
          <div className="flex items-center justify-center py-4">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        )}

        {isError && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground py-2">
            <AlertCircle className="h-4 w-4" />
            Не удалось загрузить дедлайны
          </div>
        )}

        {!isLoading && !isError && visible.length > 0 && (
          <div className="space-y-1">
            {visible.map(({ urgency, work }, idx) => (
              <div key={work.id}>
                {groupBreaks.has(idx) && (
                  <div
                    className={`text-xs font-semibold uppercase tracking-wide ${urgencyStyles[urgency]} ${idx > 0 ? 'mt-3 pt-2 border-t' : ''} mb-1`}
                  >
                    {urgencyLabels[urgency]}
                  </div>
                )}
                <Link
                  to="/works"
                  className="block p-2 -mx-2 rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0 flex-1">
                      <div className="font-medium truncate text-sm">{work.title}</div>
                      <div className="text-xs text-muted-foreground truncate">
                        {work.subject_name}
                      </div>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-xs bg-secondary px-1.5 py-0.5 rounded">
                          {workTypeLabels[work.work_type]}
                        </span>
                        {work.my_status && (
                          <span
                            className={`text-xs px-1.5 py-0.5 rounded ${workStatusColors[work.my_status]}`}
                          >
                            {workStatusLabels[work.my_status]}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <div
                        className={`text-xs font-medium ${getDeadlineColor(work.deadline)}`}
                      >
                        {formatDeadline(work.deadline)}
                      </div>
                      {work.my_status === WorkStatus.COMPLETED ||
                      work.my_status === WorkStatus.SUBMITTED ||
                      work.my_status === WorkStatus.GRADED ? (
                        <CheckCircle2 className="h-3.5 w-3.5 text-green-500 ml-auto mt-0.5" />
                      ) : null}
                    </div>
                  </div>
                </Link>
              </div>
            ))}
          </div>
        )}

        {!isLoading && !isError && (!data || data.length === 0) && (
          <p className="text-muted-foreground text-sm py-2">
            Нет ближайших дедлайнов
          </p>
        )}

        {!isLoading && !isError && data && data.length > 0 && (
          <Link
            to="/works"
            className="flex items-center justify-center gap-1 text-sm text-primary hover:underline mt-3 pt-3 border-t"
          >
            Все работы
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        )}
      </CardContent>
    </Card>
  )
}
