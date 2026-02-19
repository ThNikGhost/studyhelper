/**
 * Hook to resolve hidden subject IDs to subject names.
 *
 * Schedule entries from OmSU parser have subject_id=NULL,
 * so we resolve hidden IDs to names via the subjects query
 * and filter by subject_name instead.
 */

import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useUserSettings } from '@/hooks/useUserSettings'
import subjectService from '@/services/subjectService'

const EMPTY_SET = new Set<string>()

/**
 * Resolve hidden subject IDs to subject names for schedule filtering.
 *
 * @returns Set of subject names that should be hidden.
 */
export function useHiddenSubjectNames(): Set<string> {
  const { settings } = useUserSettings()
  const hiddenIds = settings.hiddenSubjects

  const { data: subjects } = useQuery({
    queryKey: ['subjects'],
    queryFn: ({ signal }) => subjectService.getSubjects(undefined, signal),
    staleTime: 5 * 60 * 1000,
    enabled: hiddenIds.length > 0,
  })

  return useMemo(() => {
    if (hiddenIds.length === 0 || !subjects) return EMPTY_SET
    const hidden = new Set(hiddenIds)
    return new Set(subjects.filter((s) => hidden.has(s.id)).map((s) => s.name))
  }, [subjects, hiddenIds])
}
