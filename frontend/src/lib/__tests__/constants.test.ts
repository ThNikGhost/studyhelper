import { describe, it, expect } from 'vitest'
import { TIME_SLOTS, LESSON_TYPE_COLORS } from '../constants'
import { LessonType } from '@/types/schedule'

describe('TIME_SLOTS', () => {
  it('contains 8 time slots', () => {
    expect(TIME_SLOTS).toHaveLength(8)
  })

  it('has pair numbers from 1 to 8', () => {
    const pairs = TIME_SLOTS.map((s) => s.pair)
    expect(pairs).toEqual([1, 2, 3, 4, 5, 6, 7, 8])
  })

  it('has start and end times in HH:MM format', () => {
    const timeRegex = /^\d{2}:\d{2}$/
    for (const slot of TIME_SLOTS) {
      expect(slot.start).toMatch(timeRegex)
      expect(slot.end).toMatch(timeRegex)
    }
  })

  it('has end times after start times', () => {
    for (const slot of TIME_SLOTS) {
      expect(slot.end > slot.start).toBe(true)
    }
  })
})

describe('LESSON_TYPE_COLORS', () => {
  it('has colors for all LessonType values', () => {
    const allTypes = Object.values(LessonType)
    for (const type of allTypes) {
      expect(LESSON_TYPE_COLORS[type]).toBeDefined()
      expect(typeof LESSON_TYPE_COLORS[type]).toBe('string')
      expect(LESSON_TYPE_COLORS[type].length).toBeGreaterThan(0)
    }
  })

  it('contains Tailwind CSS classes', () => {
    for (const color of Object.values(LESSON_TYPE_COLORS)) {
      expect(color).toMatch(/bg-/)
      expect(color).toMatch(/border-/)
      expect(color).toMatch(/text-/)
    }
  })
})
