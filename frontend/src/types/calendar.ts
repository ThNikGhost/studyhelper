/**
 * Calendar feed (iCal subscription) types.
 */

/** Calendar feed subscription status. */
export interface CalendarFeedStatus {
  is_active: boolean
  feed_url: string | null
  last_accessed_at: string | null
  created_at: string | null
}

/** Response after enabling calendar feed. */
export interface CalendarFeedCreateResponse {
  feed_url: string
}
