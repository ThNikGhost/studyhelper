import { describe, it, expect } from 'vitest'
import {
  calculateSemesterProgress,
  getProgressColor,
  getProgressBarColor,
} from '../progressUtils'
import type { WorkWithStatus } from '@/types/work'
import type { Subject } from '@/types/subject'

function makeSubject(id: number, name: string): Subject {
  return {
    id,
    name,
    short_name: null,
    description: null,
    semester_id: 1,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  }
}

function makeWork(
  id: number,
  subjectId: number,
  status: string | null,
): WorkWithStatus {
  return {
    id,
    title: `Work ${id}`,
    description: null,
    work_type: 'homework',
    deadline: null,
    max_grade: null,
    subject_id: subjectId,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    my_status: status
      ? {
          id,
          work_id: id,
          user_id: 1,
          status: status as WorkWithStatus['my_status'] extends infer T
            ? T extends { status: infer S }
              ? S
              : never
            : never,
          grade: null,
          notes: null,
          created_at: '2026-01-01T00:00:00Z',
          updated_at: '2026-01-01T00:00:00Z',
        }
      : null,
  }
}

describe('calculateSemesterProgress', () => {
  const subjects = [makeSubject(1, 'Math'), makeSubject(2, 'Physics')]

  it('returns zero progress when there are no works', () => {
    const result = calculateSemesterProgress([], subjects)

    expect(result.total).toBe(0)
    expect(result.completed).toBe(0)
    expect(result.percentage).toBe(0)
    expect(result.subjects).toHaveLength(2)
    expect(result.subjects[0].percentage).toBe(0)
  })

  it('counts completed statuses correctly', () => {
    const works = [
      makeWork(1, 1, 'completed'),
      makeWork(2, 1, 'submitted'),
      makeWork(3, 1, 'graded'),
    ]
    const result = calculateSemesterProgress(works, subjects)

    expect(result.total).toBe(3)
    expect(result.completed).toBe(3)
    expect(result.percentage).toBe(100)
  })

  it('counts in_progress status correctly', () => {
    const works = [
      makeWork(1, 1, 'completed'),
      makeWork(2, 1, 'in_progress'),
    ]
    const result = calculateSemesterProgress(works, subjects)

    expect(result.completed).toBe(1)
    expect(result.inProgress).toBe(1)
    expect(result.percentage).toBe(50)
  })

  it('counts null status (no status) as not started', () => {
    const works = [makeWork(1, 1, null)]
    const result = calculateSemesterProgress(works, subjects)

    expect(result.notStarted).toBe(1)
    expect(result.completed).toBe(0)
    expect(result.percentage).toBe(0)
  })

  it('counts not_started status as not started', () => {
    const works = [makeWork(1, 1, 'not_started')]
    const result = calculateSemesterProgress(works, subjects)

    expect(result.notStarted).toBe(1)
    expect(result.percentage).toBe(0)
  })

  it('groups works by subject correctly', () => {
    const works = [
      makeWork(1, 1, 'completed'),
      makeWork(2, 1, 'in_progress'),
      makeWork(3, 2, 'completed'),
    ]
    const result = calculateSemesterProgress(works, subjects)

    const math = result.subjects.find((s) => s.subjectId === 1)!
    const physics = result.subjects.find((s) => s.subjectId === 2)!

    expect(math.total).toBe(2)
    expect(math.completed).toBe(1)
    expect(math.percentage).toBe(50)

    expect(physics.total).toBe(1)
    expect(physics.completed).toBe(1)
    expect(physics.percentage).toBe(100)
  })

  it('includes subjects without works as 0%', () => {
    const works = [makeWork(1, 1, 'completed')]
    const result = calculateSemesterProgress(works, subjects)

    const physics = result.subjects.find((s) => s.subjectId === 2)!
    expect(physics.total).toBe(0)
    expect(physics.percentage).toBe(0)
  })

  it('handles works for unknown subjects gracefully', () => {
    const works = [makeWork(1, 999, 'completed')]
    const result = calculateSemesterProgress(works, subjects)

    const unknown = result.subjects.find((s) => s.subjectId === 999)!
    expect(unknown.subjectName).toBe('Subject #999')
    expect(unknown.completed).toBe(1)
  })

  it('rounds percentage correctly', () => {
    const works = [
      makeWork(1, 1, 'completed'),
      makeWork(2, 1, 'in_progress'),
      makeWork(3, 1, null),
    ]
    const result = calculateSemesterProgress(works, subjects)

    // 1 out of 3 = 33.33... -> rounds to 33
    expect(result.percentage).toBe(33)
  })
})

describe('getProgressColor', () => {
  it('returns green for >= 75%', () => {
    expect(getProgressColor(75)).toContain('green')
    expect(getProgressColor(100)).toContain('green')
  })

  it('returns yellow for >= 40% and < 75%', () => {
    expect(getProgressColor(40)).toContain('yellow')
    expect(getProgressColor(74)).toContain('yellow')
  })

  it('returns red for < 40%', () => {
    expect(getProgressColor(0)).toContain('red')
    expect(getProgressColor(39)).toContain('red')
  })
})

describe('getProgressBarColor', () => {
  it('returns green bg for >= 75%', () => {
    expect(getProgressBarColor(75)).toBe('bg-green-500')
    expect(getProgressBarColor(100)).toBe('bg-green-500')
  })

  it('returns yellow bg for >= 40% and < 75%', () => {
    expect(getProgressBarColor(40)).toBe('bg-yellow-500')
    expect(getProgressBarColor(74)).toBe('bg-yellow-500')
  })

  it('returns red bg for < 40%', () => {
    expect(getProgressBarColor(0)).toBe('bg-red-500')
    expect(getProgressBarColor(39)).toBe('bg-red-500')
  })
})
