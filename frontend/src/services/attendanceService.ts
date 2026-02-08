import api from '@/lib/api'
import type {
  AbsenceRecord,
  AttendanceEntry,
  AttendanceStats,
  SubjectAttendanceStats,
} from '@/types/attendance'

export const attendanceService = {
  async getEntries(
    subjectId?: number | null,
    dateFrom?: string | null,
    dateTo?: string | null,
    signal?: AbortSignal,
  ): Promise<AttendanceEntry[]> {
    const params: Record<string, string | number> = {}
    if (subjectId != null) params.subject_id = subjectId
    if (dateFrom) params.date_from = dateFrom
    if (dateTo) params.date_to = dateTo

    const response = await api.get<AttendanceEntry[]>('/attendance/', { params, signal })
    return response.data
  },

  async markAbsent(scheduleEntryId: number): Promise<AbsenceRecord> {
    const response = await api.post<AbsenceRecord>('/attendance/mark-absent', {
      schedule_entry_id: scheduleEntryId,
    })
    return response.data
  },

  async markPresent(scheduleEntryId: number): Promise<void> {
    await api.post('/attendance/mark-present', {
      schedule_entry_id: scheduleEntryId,
    })
  },

  async getStats(signal?: AbortSignal): Promise<AttendanceStats> {
    const response = await api.get<AttendanceStats>('/attendance/stats', { signal })
    return response.data
  },

  async getSubjectStats(
    subjectId: number,
    signal?: AbortSignal,
  ): Promise<SubjectAttendanceStats> {
    const response = await api.get<SubjectAttendanceStats>(
      `/attendance/stats/${subjectId}`,
      { signal },
    )
    return response.data
  },
}

export default attendanceService
