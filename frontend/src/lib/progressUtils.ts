import type { WorkWithStatus } from '@/types/work'
import { WorkStatus } from '@/types/work'
import type { Subject } from '@/types/subject'

export interface SubjectProgress {
  subjectId: number
  subjectName: string
  total: number
  completed: number
  inProgress: number
  notStarted: number
  percentage: number
}

export interface SemesterProgress {
  total: number
  completed: number
  inProgress: number
  notStarted: number
  percentage: number
  subjects: SubjectProgress[]
}

/** Statuses considered "completed" for progress calculation. */
const COMPLETED_STATUSES: ReadonlySet<string> = new Set([
  WorkStatus.COMPLETED,
  WorkStatus.SUBMITTED,
  WorkStatus.GRADED,
])

/**
 * Calculate semester progress by grouping works per subject.
 *
 * Status mapping:
 * - COMPLETED / SUBMITTED / GRADED -> completed
 * - IN_PROGRESS -> inProgress
 * - NOT_STARTED / null (no status) -> notStarted
 */
export function calculateSemesterProgress(
  works: WorkWithStatus[],
  subjects: Subject[],
): SemesterProgress {
  const subjectMap = new Map<number, Subject>()
  for (const s of subjects) {
    subjectMap.set(s.id, s)
  }

  // Group works by subject_id
  const grouped = new Map<number, WorkWithStatus[]>()
  for (const work of works) {
    const list = grouped.get(work.subject_id) ?? []
    list.push(work)
    grouped.set(work.subject_id, list)
  }

  let totalAll = 0
  let completedAll = 0
  let inProgressAll = 0
  let notStartedAll = 0

  const subjectProgresses: SubjectProgress[] = []

  // Build progress for every subject that has works
  for (const [subjectId, subjectWorks] of grouped) {
    const subject = subjectMap.get(subjectId)
    const name = subject?.name ?? `Subject #${subjectId}`

    let completed = 0
    let inProgress = 0
    let notStarted = 0

    for (const work of subjectWorks) {
      const status = work.my_status?.status
      if (status && COMPLETED_STATUSES.has(status)) {
        completed++
      } else if (status === WorkStatus.IN_PROGRESS) {
        inProgress++
      } else {
        notStarted++
      }
    }

    const total = subjectWorks.length
    const percentage = total > 0 ? Math.round((completed / total) * 100) : 0

    subjectProgresses.push({
      subjectId,
      subjectName: name,
      total,
      completed,
      inProgress,
      notStarted,
      percentage,
    })

    totalAll += total
    completedAll += completed
    inProgressAll += inProgress
    notStartedAll += notStarted
  }

  // Include subjects without works (0%)
  for (const subject of subjects) {
    if (!grouped.has(subject.id)) {
      subjectProgresses.push({
        subjectId: subject.id,
        subjectName: subject.name,
        total: 0,
        completed: 0,
        inProgress: 0,
        notStarted: 0,
        percentage: 0,
      })
    }
  }

  const percentageAll = totalAll > 0 ? Math.round((completedAll / totalAll) * 100) : 0

  return {
    total: totalAll,
    completed: completedAll,
    inProgress: inProgressAll,
    notStarted: notStartedAll,
    percentage: percentageAll,
    subjects: subjectProgresses,
  }
}

/** Get text color class based on progress percentage. */
export function getProgressColor(percentage: number): string {
  if (percentage >= 75) return 'text-green-600 dark:text-green-400'
  if (percentage >= 40) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-red-600 dark:text-red-400'
}

/** Get background color class for the progress bar fill. */
export function getProgressBarColor(percentage: number): string {
  if (percentage >= 75) return 'bg-green-500'
  if (percentage >= 40) return 'bg-yellow-500'
  return 'bg-red-500'
}
