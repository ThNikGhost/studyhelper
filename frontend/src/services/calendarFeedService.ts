import api from '@/lib/api'
import type { CalendarFeedStatus, CalendarFeedCreateResponse } from '@/types/calendar'

export const calendarFeedService = {
  /** Get calendar feed subscription status. */
  async getStatus(signal?: AbortSignal): Promise<CalendarFeedStatus> {
    const response = await api.get<CalendarFeedStatus>('/calendar/status', { signal })
    return response.data
  },

  /** Enable or regenerate calendar feed URL. */
  async enable(signal?: AbortSignal): Promise<CalendarFeedCreateResponse> {
    const response = await api.post<CalendarFeedCreateResponse>(
      '/calendar/enable',
      null,
      { signal },
    )
    return response.data
  },

  /** Disable calendar feed subscription. */
  async disable(signal?: AbortSignal): Promise<void> {
    await api.delete('/calendar/disable', { signal })
  },
}

export default calendarFeedService
