import api from '@/lib/api'
import type { StudyFile, FileCategory } from '@/types/file'

export interface UploadFileParams {
  file: File
  category: FileCategory
  subject_id?: number | null
  onProgress?: (percent: number) => void
}

export const fileService = {
  async uploadFile({ file, category, subject_id, onProgress }: UploadFileParams): Promise<StudyFile> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('category', category)
    if (subject_id != null) {
      formData.append('subject_id', String(subject_id))
    }

    const response = await api.post<StudyFile>('/files/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
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
}

export default fileService
