import { Check, X, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { lessonTypeLabels } from '@/lib/attendanceUtils'
import type { AttendanceEntry } from '@/types/attendance'

interface AttendanceTableProps {
  entries: AttendanceEntry[]
  onToggle: (entryId: number, isAbsent: boolean) => void
  isToggling?: number | null
  disabled?: boolean
}

export function AttendanceTable({
  entries,
  onToggle,
  isToggling,
  disabled = false,
}: AttendanceTableProps) {
  if (entries.length === 0) {
    return (
      <p className="text-sm text-muted-foreground py-8 text-center">
        Нет прошедших занятий
      </p>
    )
  }

  return (
    <div className="border rounded-lg overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b bg-muted/50">
            <th className="text-left px-3 py-2 font-medium">Дата</th>
            <th className="text-left px-3 py-2 font-medium">Предмет</th>
            <th className="text-left px-3 py-2 font-medium hidden sm:table-cell">
              Тип
            </th>
            <th className="text-left px-3 py-2 font-medium hidden md:table-cell">
              Время
            </th>
            <th className="text-center px-3 py-2 font-medium w-24">Статус</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry) => {
            const toggling = isToggling === entry.id
            return (
              <tr
                key={entry.id}
                className={`border-b last:border-b-0 ${
                  entry.is_absent ? 'bg-red-50 dark:bg-red-950/30' : ''
                }`}
              >
                <td className="px-3 py-2 whitespace-nowrap tabular-nums">
                  {entry.lesson_date ?? '—'}
                </td>
                <td className="px-3 py-2 truncate max-w-[200px]">
                  {entry.subject_name}
                </td>
                <td className="px-3 py-2 hidden sm:table-cell text-muted-foreground">
                  {lessonTypeLabels[entry.lesson_type] ?? entry.lesson_type}
                </td>
                <td className="px-3 py-2 hidden md:table-cell tabular-nums text-muted-foreground">
                  {entry.start_time?.slice(0, 5)} – {entry.end_time?.slice(0, 5)}
                </td>
                <td className="px-3 py-2 text-center">
                  <Button
                    variant={entry.is_absent ? 'destructive' : 'outline'}
                    size="sm"
                    className="h-7 w-16 text-xs"
                    disabled={disabled || toggling}
                    onClick={() => onToggle(entry.id, entry.is_absent)}
                    aria-label={
                      entry.is_absent
                        ? `Отметить присутствие на ${entry.subject_name}`
                        : `Отметить пропуск на ${entry.subject_name}`
                    }
                  >
                    {toggling ? (
                      <Loader2 className="h-3 w-3 animate-spin" />
                    ) : entry.is_absent ? (
                      <>
                        <X className="h-3 w-3 mr-0.5" />
                        Н/Б
                      </>
                    ) : (
                      <>
                        <Check className="h-3 w-3 mr-0.5" />
                        Был
                      </>
                    )}
                  </Button>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
