import api from '@/lib/api'
import type { WidgetApiKeyStatus, WidgetApiKeyCreateResponse } from '@/types/widget'

export const widgetService = {
  /** Get widget API key status. */
  async getStatus(signal?: AbortSignal): Promise<WidgetApiKeyStatus> {
    const response = await api.get<WidgetApiKeyStatus>('/widget/status', { signal })
    return response.data
  },

  /** Enable or regenerate widget API key. */
  async enable(signal?: AbortSignal): Promise<WidgetApiKeyCreateResponse> {
    const response = await api.post<WidgetApiKeyCreateResponse>(
      '/widget/enable',
      null,
      { signal },
    )
    return response.data
  },

  /** Disable widget API key. */
  async disable(signal?: AbortSignal): Promise<void> {
    await api.delete('/widget/disable', { signal })
  },
}

export default widgetService
