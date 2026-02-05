import api from '@/lib/api'

export interface UploadResponse {
  url: string
  filename: string
}

export const uploadService = {
  async uploadAvatar(file: File): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post<UploadResponse>('/uploads/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async deleteAvatar(filename: string): Promise<void> {
    await api.delete(`/uploads/avatar/${filename}`)
  },
}

export default uploadService
