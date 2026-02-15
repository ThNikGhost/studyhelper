/**
 * Telegram bot integration types.
 */

/** Telegram link status. */
export interface TelegramStatus {
  is_linked: boolean
  telegram_username: string | null
  notify_deadlines: boolean
  morning_summary: boolean
  link_code: string | null
  link_code_expires_at: string | null
}

/** Response from link code generation. */
export interface TelegramLinkCode {
  link_code: string
  expires_at: string
  bot_username: string
}

/** Notification preferences update. */
export interface TelegramNotificationsUpdate {
  notify_deadlines?: boolean
  morning_summary?: boolean
}
