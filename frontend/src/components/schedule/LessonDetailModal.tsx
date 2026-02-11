import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Clock, MapPin, User, Users, BookOpen, ExternalLink, Loader2 } from 'lucide-react'
import { Modal } from '@/components/ui/modal'
import { useNetworkStatus } from '@/hooks/useNetworkStatus'
import { workService } from '@/services/workService'
import { noteService } from '@/services/noteService'
import { NoteEditor } from '@/components/notes/NoteEditor'
import { formatTime } from '@/lib/dateUtils'
import { cn } from '@/lib/utils'
import { lessonTypeLabels } from '@/types/schedule'
import type { ScheduleEntry } from '@/types/schedule'
import { workTypeLabels, workStatusLabels, workStatusColors } from '@/types/work'

interface LessonDetailModalProps {
  entry: ScheduleEntry | null
  open: boolean
  onClose: () => void
}

/**
 * Outer wrapper that remounts the inner content when the entry changes,
 * so that local state (notes) resets cleanly without useEffect.
 */
export function LessonDetailModal({ entry, open, onClose }: LessonDetailModalProps) {
  if (!entry) return null

  return (
    <Modal open={open} onClose={onClose} title={entry.subject_name}>
      <LessonDetailContent key={entry.subject_name} entry={entry} onClose={onClose} />
    </Modal>
  )
}

interface LessonDetailContentProps {
  entry: ScheduleEntry
  onClose: () => void
}

function LessonDetailContent({ entry, onClose }: LessonDetailContentProps) {
  const isOnline = useNetworkStatus()
  const queryClient = useQueryClient()

  // Fetch works for the subject
  const { data: works, isLoading: worksLoading } = useQuery({
    queryKey: ['works', { subject_id: entry.subject_id }],
    queryFn: ({ signal }) =>
      workService.getWorks({ subject_id: entry.subject_id! }, signal),
    enabled: entry.subject_id != null,
  })

  // Fetch existing note for this subject
  const { data: existingNote, isLoading: noteLoading } = useQuery({
    queryKey: ['note-for-subject', entry.subject_name],
    queryFn: ({ signal }) => noteService.getNoteForSubject(entry.subject_name, signal),
  })

  const handleNoteSaved = () => {
    queryClient.invalidateQueries({ queryKey: ['note-for-subject', entry.subject_name] })
    queryClient.invalidateQueries({ queryKey: ['notes'] })
  }

  const location = entry.building && entry.room
    ? `${entry.building}-${entry.room}`
    : entry.room || entry.building || null

  return (
    <>
      {/* Info section */}
      <div className="space-y-2 mb-4">
        <div className="flex items-center gap-2 text-sm">
          <Clock className="h-4 w-4 text-muted-foreground flex-shrink-0" />
          <span>{formatTime(entry.start_time)} – {formatTime(entry.end_time)}</span>
          <span
            className={cn(
              'text-xs px-2 py-0.5 rounded-full font-medium',
              'bg-secondary text-secondary-foreground'
            )}
          >
            {lessonTypeLabels[entry.lesson_type]}
          </span>
        </div>

        {location && (
          <div className="flex items-center gap-2 text-sm">
            <MapPin className="h-4 w-4 text-muted-foreground flex-shrink-0" />
            <span>{location}</span>
          </div>
        )}

        {entry.teacher_name && (
          <div className="flex items-center gap-2 text-sm">
            <User className="h-4 w-4 text-muted-foreground flex-shrink-0" />
            <span>{entry.teacher_name}</span>
          </div>
        )}

        {entry.subgroup && (
          <div className="flex items-center gap-2 text-sm">
            <Users className="h-4 w-4 text-muted-foreground flex-shrink-0" />
            <span>Подгруппа {entry.subgroup}</span>
          </div>
        )}

        {entry.group_name && (
          <div className="flex items-center gap-2 text-sm">
            <Users className="h-4 w-4 text-muted-foreground flex-shrink-0" />
            <span>{entry.group_name}</span>
          </div>
        )}
      </div>

      {/* Subject link */}
      {entry.subject_id && (
        <div className="mb-4">
          <Link
            to="/subjects"
            className="text-sm text-primary hover:underline inline-flex items-center gap-1"
            onClick={onClose}
          >
            <BookOpen className="h-3.5 w-3.5" />
            Перейти к предмету
            <ExternalLink className="h-3 w-3" />
          </Link>
        </div>
      )}

      {/* Works section */}
      {entry.subject_id != null && (
        <div className="mb-4">
          <h3 className="text-sm font-semibold mb-2">Работы по предмету</h3>
          {worksLoading && (
            <div className="flex items-center justify-center py-3">
              <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
            </div>
          )}
          {!worksLoading && works && works.length > 0 && (
            <div className="space-y-2">
              {works.slice(0, 5).map((work) => (
                <div
                  key={work.id}
                  className="flex items-center justify-between text-sm p-2 rounded bg-muted/50"
                >
                  <div className="min-w-0 flex-1">
                    <div className="font-medium truncate">{work.title}</div>
                    <div className="text-xs text-muted-foreground">
                      {workTypeLabels[work.work_type]}
                      {work.deadline && (
                        <span className="ml-2">
                          {new Date(work.deadline).toLocaleDateString('ru-RU', {
                            day: 'numeric',
                            month: 'short',
                          })}
                        </span>
                      )}
                    </div>
                  </div>
                  {work.my_status && (
                    <span
                      className={cn(
                        'text-xs px-2 py-0.5 rounded-full whitespace-nowrap ml-2',
                        workStatusColors[work.my_status.status]
                      )}
                    >
                      {workStatusLabels[work.my_status.status]}
                    </span>
                  )}
                </div>
              ))}
              {works.length > 5 && (
                <Link
                  to="/works"
                  className="text-xs text-primary hover:underline"
                  onClick={onClose}
                >
                  Все работы ({works.length})
                </Link>
              )}
            </div>
          )}
          {!worksLoading && works && works.length === 0 && (
            <p className="text-sm text-muted-foreground">Нет работ по этому предмету</p>
          )}
        </div>
      )}

      {/* Notes section — NoteEditor with autosave */}
      {noteLoading ? (
        <div className="flex items-center justify-center py-3">
          <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
        </div>
      ) : (
        <NoteEditor
          note={existingNote ?? null}
          scheduleEntryId={entry.id}
          subjectName={entry.subject_name}
          lessonDate={entry.lesson_date}
          disabled={!isOnline}
          onSaved={handleNoteSaved}
        />
      )}
    </>
  )
}
