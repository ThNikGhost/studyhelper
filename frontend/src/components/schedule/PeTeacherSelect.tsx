import { useState } from 'react'
import { Dumbbell, Check, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useSettingsStore } from '@/stores/settingsStore'

interface PeTeacherSelectProps {
  /** List of available PE teacher names. */
  teachers: string[]
  /** Called after the user selects or clears a teacher. */
  onChange: (teacher: string | null) => void
}

export function PeTeacherSelect({ teachers, onChange }: PeTeacherSelectProps) {
  const { peTeacher, setPeTeacher } = useSettingsStore()
  const [isOpen, setIsOpen] = useState(false)

  if (teachers.length <= 1) return null

  const handleSelect = (teacher: string) => {
    setPeTeacher(teacher)
    setIsOpen(false)
    onChange(teacher)
  }

  const handleClear = () => {
    setPeTeacher(null)
    setIsOpen(false)
    onChange(null)
  }

  return (
    <div className="relative">
      <Button
        variant="outline"
        size="sm"
        className="gap-1.5 text-xs"
        onClick={() => setIsOpen(!isOpen)}
        title={peTeacher ? `Физра: ${peTeacher}` : 'Выбрать преподавателя физры'}
      >
        <Dumbbell className="h-3.5 w-3.5" />
        {peTeacher ? peTeacher.split(' ').slice(0, 2).join(' ') : 'Физра'}
      </Button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />

          {/* Dropdown */}
          <div className="absolute right-0 top-full mt-1 z-50 w-72 rounded-md border bg-popover shadow-md">
            <div className="p-2 border-b">
              <p className="text-xs text-muted-foreground">Выберите преподавателя физры</p>
            </div>
            <div className="max-h-60 overflow-y-auto p-1">
              {teachers.map((teacher) => (
                <button
                  key={teacher}
                  onClick={() => handleSelect(teacher)}
                  className="flex items-center gap-2 w-full rounded px-2 py-1.5 text-sm hover:bg-accent text-left"
                >
                  {peTeacher === teacher ? (
                    <Check className="h-3.5 w-3.5 text-primary flex-shrink-0" />
                  ) : (
                    <span className="w-3.5 flex-shrink-0" />
                  )}
                  <span className="truncate">{teacher}</span>
                </button>
              ))}
            </div>
            {peTeacher && (
              <div className="p-1 border-t">
                <button
                  onClick={handleClear}
                  className="flex items-center gap-2 w-full rounded px-2 py-1.5 text-sm hover:bg-accent text-muted-foreground"
                >
                  <X className="h-3.5 w-3.5 flex-shrink-0" />
                  Показать всех преподавателей
                </button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
