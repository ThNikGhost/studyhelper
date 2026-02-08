import api from '@/lib/api'
import type { LessonNote, LessonNoteCreate, LessonNoteUpdate } from '@/types/note'

export const noteService = {
  async getNotes(
    params?: {
      date_from?: string
      date_to?: string
      subject_name?: string
      search?: string
    },
    signal?: AbortSignal,
  ): Promise<LessonNote[]> {
    const response = await api.get<LessonNote[]>('/notes/', { params, signal })
    return response.data
  },

  async getNoteForEntry(
    entryId: number,
    signal?: AbortSignal,
  ): Promise<LessonNote | null> {
    try {
      const response = await api.get<LessonNote>(`/notes/entry/${entryId}`, { signal })
      return response.data
    } catch (err: unknown) {
      // 404 means no note exists yet — return null
      if (
        typeof err === 'object' &&
        err !== null &&
        'response' in err &&
        (err as { response?: { status?: number } }).response?.status === 404
      ) {
        return null
      }
      throw err
    }
  },

  async createNote(data: LessonNoteCreate): Promise<LessonNote> {
    const response = await api.post<LessonNote>('/notes/', data)
    return response.data
  },

  async updateNote(noteId: number, data: LessonNoteUpdate): Promise<LessonNote> {
    const response = await api.put<LessonNote>(`/notes/${noteId}`, data)
    return response.data
  },

  async deleteNote(noteId: number): Promise<void> {
    await api.delete(`/notes/${noteId}`)
  },
}

export default noteService
