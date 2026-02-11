import api from '@/lib/api'
import type {
  AbsenceRecord,
  AttendanceEntry,
  AttendanceStats,
  SubjectAttendanceStats,
} from '@/types/attendance'

export const attendanceService = {
  async getEntries(
    semesterId: number,
    subjectId?: number | null,
    limit?: number,
    offset?: number,
    signal?: AbortSignal,
  ): Promise<AttendanceEntry[]> {
    const params: Record<string, string | number> = {
      semester_id: semesterId,
    }
    if (subjectId != null) params.subject_id = subjectId
    if (limit != null) params.limit = limit
    if (offset != null) params.offset = offset

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

  async getStats(semesterId: number, signal?: AbortSignal): Promise<AttendanceStats> {
    const response = await api.get<AttendanceStats>('/attendance/stats', {
      params: { semester_id: semesterId },
      signal,
    })
    return response.data
  },

  async getSubjectStats(
    subjectId: number,
    semesterId: number,
    signal?: AbortSignal,
  ): Promise<SubjectAttendanceStats> {
    const response = await api.get<SubjectAttendanceStats>(
      `/attendance/stats/${subjectId}`,
      {
        params: { semester_id: semesterId },
        signal,
      },
    )
    return response.data
  },
}

export default attendanceService
