import { cn } from '@/lib/utils'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'

interface TimelineMarkerProps {
  /** Position as left percentage (0-100). */
  percent: number
  /** Tailwind background color class. */
  color: string
  /** Tooltip label. */
  label: string
  /** Optional secondary line in tooltip. */
  sublabel?: string
  /** Diamond shape for exams, circle for deadlines. */
  variant?: 'circle' | 'diamond'
  onClick?: () => void
}

export function TimelineMarker({
  percent,
  color,
  label,
  sublabel,
  variant = 'circle',
  onClick,
}: TimelineMarkerProps) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <button
          type="button"
          className={cn(
            'absolute top-1/2 -translate-y-1/2 -translate-x-1/2 z-10 cursor-pointer transition-transform hover:scale-150 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-1 rounded-full',
            variant === 'diamond' ? 'w-3 h-3 rotate-45' : 'w-3 h-3 rounded-full',
            color,
          )}
          style={{ left: `${percent}%` }}
          onClick={onClick}
          aria-label={label}
        />
      </PopoverTrigger>
      <PopoverContent className="w-auto max-w-60 p-2 text-sm" side="top">
        <p className="font-medium">{label}</p>
        {sublabel && <p className="text-muted-foreground text-xs">{sublabel}</p>}
      </PopoverContent>
    </Popover>
  )
}
