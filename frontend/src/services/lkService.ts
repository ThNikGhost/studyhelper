import api from '@/lib/api'
import type {
  LkStatus,
  LkCredentials,
  SessionGrade,
  SemesterDiscipline,
  LkSyncResult,
  LkImportResult,
} from '@/types/lk'

export const lkService = {
  /** Get LK connection status. */
  async getStatus(signal?: AbortSignal): Promise<LkStatus> {
    const response = await api.get<LkStatus>('/lk/status', { signal })
    return response.data
  },

  /** Save LK credentials (encrypted). */
  async saveCredentials(
    data: LkCredentials,
    signal?: AbortSignal,
  ): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/lk/credentials', data, {
      signal,
    })
    return response.data
  },

  /** Delete stored LK credentials. */
  async deleteCredentials(signal?: AbortSignal): Promise<void> {
    await api.delete('/lk/credentials', { signal })
  },

  /** Verify credentials without saving. */
  async verifyCredentials(
    data: LkCredentials,
    signal?: AbortSignal,
  ): Promise<{ valid: boolean; message: string }> {
    const response = await api.post<{ valid: boolean; message: string }>(
      '/lk/verify',
      data,
      { signal },
    )
    return response.data
  },

  /** Sync grades and disciplines from LK. */
  async sync(signal?: AbortSignal): Promise<LkSyncResult> {
    const response = await api.post<LkSyncResult>('/lk/sync', null, { signal })
    return response.data
  },

  /** Get session grades. */
  async getGrades(session?: string, signal?: AbortSignal): Promise<SessionGrade[]> {
    const params = session ? { session } : undefined
    const response = await api.get<SessionGrade[]>('/lk/grades', { params, signal })
    return response.data
  },

  /** Get list of available sessions. */
  async getSessions(signal?: AbortSignal): Promise<string[]> {
    const response = await api.get<string[]>('/lk/grades/sessions', { signal })
    return response.data
  },

  /** Get semester disciplines. */
  async getDisciplines(
    semester?: number,
    signal?: AbortSignal,
  ): Promise<SemesterDiscipline[]> {
    const params = semester ? { semester } : undefined
    const response = await api.get<SemesterDiscipline[]>('/lk/disciplines', {
      params,
      signal,
    })
    return response.data
  },

  /** Get list of available semesters. */
  async getSemesters(signal?: AbortSignal): Promise<number[]> {
    const response = await api.get<number[]>('/lk/disciplines/semesters', { signal })
    return response.data
  },

  /** Import semesters and subjects from LK to app. */
  async importToApp(signal?: AbortSignal): Promise<LkImportResult> {
    const response = await api.post<LkImportResult>('/lk/import', null, { signal })
    return response.data
  },
}

export default lkService
