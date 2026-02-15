import api from '@/lib/api'
import type {
  TelegramStatus,
  TelegramLinkCode,
  TelegramNotificationsUpdate,
} from '@/types/telegram'

export const telegramService = {
  /** Get Telegram link status. */
  async getStatus(signal?: AbortSignal): Promise<TelegramStatus> {
    const response = await api.get<TelegramStatus>('/telegram/status', { signal })
    return response.data
  },

  /** Generate a 6-digit link code. */
  async generateLinkCode(signal?: AbortSignal): Promise<TelegramLinkCode> {
    const response = await api.post<TelegramLinkCode>('/telegram/link-code', null, {
      signal,
    })
    return response.data
  },

  /** Unlink Telegram account. */
  async unlink(signal?: AbortSignal): Promise<void> {
    await api.delete('/telegram/link', { signal })
  },

  /** Update notification preferences. */
  async updateNotifications(
    data: TelegramNotificationsUpdate,
    signal?: AbortSignal,
  ): Promise<TelegramStatus> {
    const response = await api.patch<TelegramStatus>(
      '/telegram/notifications',
      data,
      { signal },
    )
    return response.data
  },
}

export default telegramService
