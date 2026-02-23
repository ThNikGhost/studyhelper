import api from '@/lib/api'
import type { StudyFile, FileCategory } from '@/types/file'

export interface UploadFileParams {
  file: File
  category: FileCategory
  subject_id?: number | null
  onProgress?: (percent: number) => void
  signal?: AbortSignal
}

export const fileService = {
  async uploadFile({ file, category, subject_id, onProgress, signal }: UploadFileParams): Promise<StudyFile> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('category', category)
    if (subject_id != null) {
      formData.append('subject_id', String(subject_id))
    }

    const response = await api.post<StudyFile>('/files/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      signal,
      onUploadProgress: (event) => {
        if (onProgress && event.total) {
          onProgress(Math.round((event.loaded * 100) / event.total))
        }
      },
    })
    return response.data
  },

  async getFiles(
    subjectId?: number | null,
    category?: string | null,
    signal?: AbortSignal,
  ): Promise<StudyFile[]> {
    const params: Record<string, string | number> = {}
    if (subjectId != null) params.subject_id = subjectId
    if (category) params.category = category

    const response = await api.get<StudyFile[]>('/files/', { params, signal })
    return response.data
  },

  async updateFileCategory(id: number, category: string): Promise<StudyFile> {
    const response = await api.patch<StudyFile>(`/files/${id}`, { category })
    return response.data
  },

  async deleteFile(id: number): Promise<void> {
    await api.delete(`/files/${id}`)
  },

  async downloadFile(id: number, filename: string): Promise<void> {
    const response = await api.get(`/files/${id}/download`, {
      responseType: 'blob',
    })
    const url = URL.createObjectURL(response.data as Blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  },

  async openFile(id: number): Promise<void> {
    const response = await api.get(`/files/${id}/download`, {
      responseType: 'blob',
    })
    const url = URL.createObjectURL(response.data as Blob)
    window.open(url, '_blank')
    setTimeout(() => URL.revokeObjectURL(url), 10000)
  },
}

export default fileService
