import api from '@/lib/api'
import type { WeekSchedule, DaySchedule, CurrentLesson, ScheduleEntry, ScheduleEntryUpdate } from '@/types/schedule'

export const scheduleService = {
  /**
   * Get schedule for a week
   * @param targetDate - Date within target week (YYYY-MM-DD), defaults to current week
   */
  async getWeekSchedule(targetDate?: string, signal?: AbortSignal): Promise<WeekSchedule> {
    const params = targetDate ? { target_date: targetDate } : {}
    const response = await api.get<WeekSchedule>('/schedule/week', { params, signal })
    return response.data
  },

  /**
   * Get schedule for a specific day
   * @param targetDate - Target date (YYYY-MM-DD), defaults to today
   */
  async getTodaySchedule(targetDate?: string, signal?: AbortSignal): Promise<DaySchedule> {
    const params = targetDate ? { target_date: targetDate } : {}
    const response = await api.get<DaySchedule>('/schedule/today', { params, signal })
    return response.data
  },

  /**
   * Get current and next lesson
   */
  async getCurrentLesson(signal?: AbortSignal): Promise<CurrentLesson> {
    const response = await api.get<CurrentLesson>('/schedule/current', { signal })
    return response.data
  },

  /**
   * Update a schedule entry (e.g. notes).
   */
  async updateEntry(id: number, data: ScheduleEntryUpdate): Promise<ScheduleEntry> {
    const response = await api.put<ScheduleEntry>(`/schedule/entries/${id}`, data)
    return response.data
  },

  /**
   * Refresh schedule from OmGU (sync with parser)
   * @param force - Force refresh even if unchanged
   */
  async refreshSchedule(force = false): Promise<{
    success: boolean
    changed: boolean
    entries_count: number
    content_hash?: string
    message?: string
  }> {
    const response = await api.post('/schedule/refresh', null, {
      params: { force },
    })
    return response.data
  },
}

export default scheduleService
