import { useState, useMemo, useCallback, useRef, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNetworkStatus } from '@/hooks/useNetworkStatus'
import { ArrowLeft, StickyNote, Search, Loader2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { Modal } from '@/components/ui/modal'
import { toast } from 'sonner'
import { NoteCard } from '@/components/notes/NoteCard'
import { noteService } from '@/services/noteService'
import type { LessonNote } from '@/types/note'

const SEARCH_DEBOUNCE_MS = 300

export function NotesPage() {
  const isOnline = useNetworkStatus()
  const queryClient = useQueryClient()

  const [searchInput, setSearchInput] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [filterSubject, setFilterSubject] = useState<string | ''>('')
  const [deleteTarget, setDeleteTarget] = useState<number | null>(null)

  const searchTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Cleanup debounce timer
  useEffect(() => {
    return () => {
      if (searchTimerRef.current) clearTimeout(searchTimerRef.current)
    }
  }, [])

  const handleSearchChange = (value: string) => {
    setSearchInput(value)
    if (searchTimerRef.current) clearTimeout(searchTimerRef.current)
    searchTimerRef.current = setTimeout(() => {
      setSearchQuery(value)
    }, SEARCH_DEBOUNCE_MS)
  }

  // Fetch all notes
  const {
    data: notes = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: [
      'notes',
      { subject_name: filterSubject || undefined, search: searchQuery || undefined },
    ],
    queryFn: ({ signal }) =>
      noteService.getNotes(
        {
          subject_name: filterSubject || undefined,
          search: searchQuery || undefined,
        },
        signal,
      ),
  })

  // Unique subject names for the filter
  const subjectNames = useMemo(() => {
    const names = new Set(notes.map((n: LessonNote) => n.subject_name))
    return Array.from(names).sort()
  }, [notes])

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (noteId: number) => noteService.deleteNote(noteId),
    onSuccess: () => {
      toast.success('Заметка удалена')
      queryClient.invalidateQueries({ queryKey: ['notes'] })
      setDeleteTarget(null)
    },
    onError: () => {
      toast.error('Ошибка при удалении заметки')
    },
  })

  const handleDeleteRequest = useCallback((noteId: number) => {
    setDeleteTarget(noteId)
  }, [])

  const handleDeleteConfirm = () => {
    if (deleteTarget != null) {
      deleteMutation.mutate(deleteTarget)
    }
  }

  // Loading
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-6">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-muted rounded w-1/3" />
            <div className="h-10 bg-muted rounded" />
            <div className="h-32 bg-muted rounded" />
            <div className="h-32 bg-muted rounded" />
          </div>
        </div>
      </div>
    )
  }

  // Error
  if (error) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-6">
          <Card>
            <CardContent className="py-10 text-center">
              <p className="text-destructive mb-4">Ошибка загрузки заметок</p>
              <Button onClick={() => queryClient.invalidateQueries({ queryKey: ['notes'] })}>
                Попробовать снова
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-6 max-w-2xl">
        {/* Header */}
        <div className="flex items-center gap-2 mb-4">
          <Link to="/">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <StickyNote className="h-6 w-6 text-amber-500" />
          <h1 className="text-2xl font-bold">Заметки</h1>
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-2 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Поиск в заметках..."
              value={searchInput}
              onChange={(e) => handleSearchChange(e.target.value)}
              className="pl-9"
              disabled={!isOnline}
            />
          </div>
          <select
            className="h-10 rounded-md border border-input bg-background px-3 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            value={filterSubject}
            onChange={(e) => setFilterSubject(e.target.value)}
            disabled={!isOnline}
          >
            <option value="">Все предметы</option>
            {subjectNames.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </div>

        {/* Notes list */}
        {notes.length > 0 ? (
          <div className="space-y-3">
            {notes.map((note: LessonNote) => (
              <NoteCard key={note.id} note={note} onDelete={handleDeleteRequest} />
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="py-10 text-center text-muted-foreground">
              <StickyNote className="h-12 w-12 mx-auto mb-3 opacity-30" />
              <p>Нет заметок</p>
              <p className="text-sm mt-1">
                Добавляйте заметки из карточки занятия в расписании
              </p>
            </CardContent>
          </Card>
        )}

        {/* Delete confirmation modal */}
        <Modal
          open={deleteTarget != null}
          onClose={() => setDeleteTarget(null)}
          title="Удалить заметку?"
        >
          <p className="text-sm text-muted-foreground mb-4">
            Это действие нельзя отменить.
          </p>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setDeleteTarget(null)}>
              Отмена
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteConfirm}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin mr-1" />
              ) : null}
              Удалить
            </Button>
          </div>
        </Modal>
      </div>
    </div>
  )
}

export default NotesPage
