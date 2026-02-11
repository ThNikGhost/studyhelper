import { useState, useRef, useCallback, useEffect } from 'react'
import { Loader2, Check, AlertCircle } from 'lucide-react'
import { useNetworkStatus } from '@/hooks/useNetworkStatus'
import { noteService } from '@/services/noteService'
import type { LessonNote } from '@/types/note'

type SaveStatus = 'idle' | 'saving' | 'saved' | 'error'

interface NoteEditorProps {
  /** Existing note (null if no note yet) */
  note: LessonNote | null
  /** Schedule entry ID to link the note to */
  scheduleEntryId: number
  /** Subject name for new notes */
  subjectName: string
  /** Lesson date for new notes */
  lessonDate?: string | null
  /** Callback after successful save */
  onSaved?: (note: LessonNote) => void
  /** Disable editing */
  disabled?: boolean
}

const MAX_LENGTH = 2000
const DEBOUNCE_MS = 500

export function NoteEditor({
  note,
  scheduleEntryId,
  subjectName,
  lessonDate,
  onSaved,
  disabled = false,
}: NoteEditorProps) {
  const isOnline = useNetworkStatus()
  const [content, setContent] = useState(note?.content ?? '')
  const [status, setStatus] = useState<SaveStatus>('idle')
  const noteIdRef = useRef<number | null>(note?.id ?? null)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current)
      if (abortRef.current) abortRef.current.abort()
    }
  }, [])

  const save = useCallback(
    async (text: string) => {
      if (!text.trim()) return

      // Cancel any in-flight request
      if (abortRef.current) abortRef.current.abort()
      abortRef.current = new AbortController()

      setStatus('saving')
      try {
        const signal = abortRef.current.signal
        let saved: LessonNote
        if (noteIdRef.current) {
          // Update existing note
          saved = await noteService.updateNote(
            noteIdRef.current,
            { content: text },
            signal,
          )
        } else {
          // Create new note
          saved = await noteService.createNote(
            {
              schedule_entry_id: scheduleEntryId,
              subject_name: subjectName,
              lesson_date: lessonDate,
              content: text,
            },
            signal,
          )
          noteIdRef.current = saved.id
        }
        setStatus('saved')
        onSaved?.(saved)
      } catch (err) {
        // Don't show error for aborted requests
        if (err instanceof Error && err.name === 'CanceledError') return
        setStatus('error')
      }
    },
    [scheduleEntryId, subjectName, lessonDate, onSaved],
  )

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value
    if (newValue.length > MAX_LENGTH) return

    setContent(newValue)
    setStatus('idle')

    // Debounced autosave
    if (timerRef.current) clearTimeout(timerRef.current)
    if (newValue.trim()) {
      timerRef.current = setTimeout(() => {
        save(newValue)
      }, DEBOUNCE_MS)
    }
  }

  const isDisabled = disabled || !isOnline

  return (
    <div>
      <h3 className="text-sm font-semibold mb-2">Заметки</h3>
      <textarea
        className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
        rows={3}
        placeholder="Добавить заметку к занятию..."
        value={content}
        onChange={handleChange}
        disabled={isDisabled}
        maxLength={MAX_LENGTH}
        aria-label="Заметка к занятию"
      />
      <div className="flex items-center justify-between mt-1">
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          {status === 'saving' && (
            <>
              <Loader2 className="h-3 w-3 animate-spin" />
              <span data-testid="save-status">Сохранение...</span>
            </>
          )}
          {status === 'saved' && (
            <>
              <Check className="h-3 w-3 text-green-500" />
              <span data-testid="save-status">Сохранено</span>
            </>
          )}
          {status === 'error' && (
            <>
              <AlertCircle className="h-3 w-3 text-destructive" />
              <span data-testid="save-status">Ошибка сохранения</span>
            </>
          )}
        </div>
        <span className="text-xs text-muted-foreground" data-testid="char-counter">
          {content.length}/{MAX_LENGTH}
        </span>
      </div>
    </div>
  )
}

export default NoteEditor
