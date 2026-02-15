/**
 * Widget API key types for phone widgets.
 */

/** Widget API key status. */
export interface WidgetApiKeyStatus {
  is_active: boolean
  api_key: string | null
  widget_url: string | null
  last_used_at: string | null
  created_at: string | null
}

/** Response after enabling widget API key. */
export interface WidgetApiKeyCreateResponse {
  api_key: string
  widget_url: string
}
