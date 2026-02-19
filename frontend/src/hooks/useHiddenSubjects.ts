/**
 * Hook to resolve hidden subject config for filtering.
 *
 * Returns two views of the hidden config:
 * - `hiddenEntries`: Map<subject_name, Set<lesson_type> | null> for schedule filtering
 * - `fullyHiddenIds`: Set<subject_id> for works/subjects/attendance filtering
 *
 * Schedule entries from OmSU parser have subject_id=NULL,
 * so we resolve hidden IDs to names via the subjects query.
 */

import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useUserSettings } from '@/hooks/useUserSettings'
import subjectService from '@/services/subjectService'

export interface HiddenSubjectsConfig {
  /** For schedule filtering: subject_name → hidden lesson types (null = all). */
  hiddenEntries: Map<string, Set<string> | null>
  /** For works/subjects/attendance: subject IDs where ALL types are hidden. */
  fullyHiddenIds: Set<number>
}

const EMPTY_CONFIG: HiddenSubjectsConfig = {
  hiddenEntries: new Map(),
  fullyHiddenIds: new Set(),
}

/**
 * Resolve hidden subject config for both schedule and non-schedule filtering.
 *
 * @returns HiddenSubjectsConfig with two views of hidden subjects.
 */
export function useHiddenSubjects(): HiddenSubjectsConfig {
  const { settings } = useUserSettings()
  const hiddenSubjects = settings.hiddenSubjects

  const hasAny = Object.keys(hiddenSubjects).length > 0

  const { data: subjects } = useQuery({
    queryKey: ['subjects'],
    queryFn: ({ signal }) => subjectService.getSubjects(undefined, signal),
    staleTime: 5 * 60 * 1000,
    enabled: hasAny,
  })

  return useMemo(() => {
    if (!hasAny || !subjects) return EMPTY_CONFIG

    // Build id → name map
    const idToName = new Map(subjects.map((s) => [s.id, s.name]))

    const hiddenEntries = new Map<string, Set<string> | null>()
    const fullyHiddenIds = new Set<number>()

    for (const [idStr, types] of Object.entries(hiddenSubjects)) {
      const id = Number(idStr)
      const name = idToName.get(id)
      if (!name) continue

      if (types === null) {
        hiddenEntries.set(name, null)
        fullyHiddenIds.add(id)
      } else {
        hiddenEntries.set(name, new Set(types))
      }
    }

    return { hiddenEntries, fullyHiddenIds }
  }, [subjects, hiddenSubjects, hasAny])
}
