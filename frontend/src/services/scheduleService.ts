import api from '@/lib/api'
import type { WeekSchedule, DaySchedule, CurrentLesson } from '@/types/schedule'

export const scheduleService = {
  /**
   * Get schedule for a week
   * @param targetDate - Date within target week (YYYY-MM-DD), defaults to current week
   */
  async getWeekSchedule(targetDate?: string): Promise<WeekSchedule> {
    const params = targetDate ? { target_date: targetDate } : {}
    const response = await api.get<WeekSchedule>('/schedule/week', { params })
    return response.data
  },

  /**
   * Get schedule for a specific day
   * @param targetDate - Target date (YYYY-MM-DD), defaults to today
   */
  async getTodaySchedule(targetDate?: string): Promise<DaySchedule> {
    const params = targetDate ? { target_date: targetDate } : {}
    const response = await api.get<DaySchedule>('/schedule/today', { params })
    return response.data
  },

  /**
   * Get current and next lesson
   */
  async getCurrentLesson(): Promise<CurrentLesson> {
    const response = await api.get<CurrentLesson>('/schedule/current')
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
