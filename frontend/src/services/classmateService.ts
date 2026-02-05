import api from '@/lib/api'
import type { Classmate, ClassmateCreate, ClassmateUpdate } from '@/types/classmate'

export const classmateService = {
  async getClassmates(): Promise<Classmate[]> {
    const response = await api.get<Classmate[]>('/classmates')
    return response.data
  },

  async getClassmate(id: number): Promise<Classmate> {
    const response = await api.get<Classmate>(`/classmates/${id}`)
    return response.data
  },

  async createClassmate(data: ClassmateCreate): Promise<Classmate> {
    const response = await api.post<Classmate>('/classmates', data)
    return response.data
  },

  async updateClassmate(id: number, data: ClassmateUpdate): Promise<Classmate> {
    const response = await api.put<Classmate>(`/classmates/${id}`, data)
    return response.data
  },

  async deleteClassmate(id: number): Promise<void> {
    await api.delete(`/classmates/${id}`)
  },
}

export default classmateService
