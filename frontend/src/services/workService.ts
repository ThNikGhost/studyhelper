import api from '@/lib/api'
import type {
  WorkWithStatus,
  WorkCreate,
  WorkUpdate,
  WorkStatusData,
  WorkStatusUpdate,
  UpcomingWork,
  WorkStatus,
} from '@/types/work'

export interface WorkFilters {
  subject_id?: number
  status?: WorkStatus
  has_deadline?: boolean
}

export const workService = {
  /**
   * Get all works with optional filters.
   */
  async getWorks(filters?: WorkFilters, signal?: AbortSignal): Promise<WorkWithStatus[]> {
    const params: Record<string, string | number | boolean> = {}
    if (filters?.subject_id) params.subject_id = filters.subject_id
    if (filters?.status) params.status = filters.status
    if (filters?.has_deadline !== undefined) params.has_deadline = filters.has_deadline

    const response = await api.get<WorkWithStatus[]>('/works', { params, signal })
    return response.data
  },

  /**
   * Get a single work by ID.
   */
  async getWork(id: number, signal?: AbortSignal): Promise<WorkWithStatus> {
    const response = await api.get<WorkWithStatus>(`/works/${id}`, { signal })
    return response.data
  },

  /**
   * Create a new work.
   */
  async createWork(data: WorkCreate): Promise<WorkWithStatus> {
    const response = await api.post<WorkWithStatus>('/works', data)
    return response.data
  },

  /**
   * Update a work.
   */
  async updateWork(id: number, data: WorkUpdate): Promise<WorkWithStatus> {
    const response = await api.put<WorkWithStatus>(`/works/${id}`, data)
    return response.data
  },

  /**
   * Delete a work.
   */
  async deleteWork(id: number): Promise<void> {
    await api.delete(`/works/${id}`)
  },

  /**
   * Update work status for current user.
   */
  async updateWorkStatus(workId: number, data: WorkStatusUpdate): Promise<WorkStatusData> {
    const response = await api.put<WorkStatusData>(`/works/${workId}/status`, data)
    return response.data
  },

  /**
   * Get upcoming works with deadlines.
   */
  async getUpcomingWorks(limit: number = 10, signal?: AbortSignal): Promise<UpcomingWork[]> {
    const response = await api.get<UpcomingWork[]>('/works/upcoming', {
      params: { limit },
      signal,
    })
    return response.data
  },
}

export default workService
