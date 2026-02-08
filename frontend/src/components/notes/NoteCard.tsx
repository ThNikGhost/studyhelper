import { useState } from 'react'
import { Calendar, BookOpen, ChevronDown, ChevronUp, Trash2 } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import type { LessonNote } from '@/types/note'

interface NoteCardProps {
  note: LessonNote
  onDelete: (noteId: number) => void
}

const PREVIEW_LENGTH = 150

export function NoteCard({ note, onDelete }: NoteCardProps) {
  const [expanded, setExpanded] = useState(false)
  const needsTruncation = note.content.length > PREVIEW_LENGTH
  const displayContent = expanded || !needsTruncation
    ? note.content
    : note.content.slice(0, PREVIEW_LENGTH) + '...'

  const formattedDate = note.lesson_date
    ? new Date(note.lesson_date + 'T12:00:00').toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
      })
    : null

  return (
    <Card>
      <CardContent className="p-4">
        {/* Header: subject + date */}
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-1.5 text-sm font-semibold">
              <BookOpen className="h-4 w-4 text-primary flex-shrink-0" />
              <span className="truncate">{note.subject_name}</span>
            </div>
            {formattedDate && (
              <div className="flex items-center gap-1.5 text-xs text-muted-foreground mt-1">
                <Calendar className="h-3 w-3 flex-shrink-0" />
                <span>{formattedDate}</span>
              </div>
            )}
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-muted-foreground hover:text-destructive"
            onClick={() => onDelete(note.id)}
            aria-label="Удалить заметку"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>

        {/* Content */}
        <p className="text-sm whitespace-pre-wrap break-words">{displayContent}</p>

        {/* Expand/collapse */}
        {needsTruncation && (
          <Button
            variant="ghost"
            size="sm"
            className="mt-1 h-7 px-2 text-xs text-muted-foreground"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? (
              <>
                <ChevronUp className="h-3 w-3 mr-1" />
                Свернуть
              </>
            ) : (
              <>
                <ChevronDown className="h-3 w-3 mr-1" />
                Развернуть
              </>
            )}
          </Button>
        )}
      </CardContent>
    </Card>
  )
}

export default NoteCard
