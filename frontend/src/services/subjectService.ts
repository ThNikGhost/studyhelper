import api from '@/lib/api'
import type { Subject, SubjectCreate, SubjectUpdate, Semester, SemesterCreate } from '@/types/subject'

export const subjectService = {
  // Subjects
  async getSubjects(semesterId?: number): Promise<Subject[]> {
    const params = semesterId ? { semester_id: semesterId } : {}
    const response = await api.get<Subject[]>('/subjects', { params })
    return response.data
  },

  async getSubject(id: number): Promise<Subject> {
    const response = await api.get<Subject>(`/subjects/${id}`)
    return response.data
  },

  async createSubject(data: SubjectCreate): Promise<Subject> {
    const response = await api.post<Subject>('/subjects', data)
    return response.data
  },

  async updateSubject(id: number, data: SubjectUpdate): Promise<Subject> {
    const response = await api.put<Subject>(`/subjects/${id}`, data)
    return response.data
  },

  async deleteSubject(id: number): Promise<void> {
    await api.delete(`/subjects/${id}`)
  },

  // Semesters
  async getSemesters(): Promise<Semester[]> {
    const response = await api.get<Semester[]>('/semesters')
    return response.data
  },

  async getCurrentSemester(): Promise<Semester | null> {
    const response = await api.get<Semester | null>('/semesters/current')
    return response.data
  },

  async createSemester(data: SemesterCreate): Promise<Semester> {
    const response = await api.post<Semester>('/semesters', data)
    return response.data
  },

  async setCurrentSemester(id: number): Promise<Semester> {
    const response = await api.post<Semester>(`/semesters/${id}/set-current`)
    return response.data
  },
}

export default subjectService
