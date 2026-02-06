import { LessonType, type LessonType as LessonTypeValue } from '@/types/schedule'

export const TIME_SLOTS = [
  { pair: 1, start: '08:45', end: '10:20' },
  { pair: 2, start: '10:30', end: '12:05' },
  { pair: 3, start: '12:45', end: '14:20' },
  { pair: 4, start: '14:30', end: '16:05' },
  { pair: 5, start: '16:15', end: '17:50' },
  { pair: 6, start: '18:00', end: '19:35' },
  { pair: 7, start: '19:45', end: '21:20' },
  { pair: 8, start: '21:30', end: '23:05' },
]

export const LESSON_TYPE_COLORS: Record<LessonTypeValue, string> = {
  [LessonType.LECTURE]: 'bg-[#6fa8ff] border-[#4a8fef] text-black',
  [LessonType.PRACTICE]: 'bg-[#7dbf99] border-[#5fad7d] text-black',
  [LessonType.LAB]: 'bg-[#e8868f] border-[#d96b75] text-black',
  [LessonType.SEMINAR]: 'bg-[#6fa8ff] border-[#4a8fef] text-black',
  [LessonType.EXAM]: 'bg-[#e8868f] border-[#d96b75] text-black',
  [LessonType.CONSULTATION]: 'bg-gray-300 border-gray-400 text-black',
  [LessonType.OTHER]: 'bg-gray-300 border-gray-400 text-black',
}
