import { cn } from '@/lib/utils'

interface ProgressBarProps {
  /** Progress value from 0 to 100. */
  value: number
  /** Tailwind background class for the filled portion. */
  color?: string
  /** Bar height: sm (1.5) or md (2.5). */
  size?: 'sm' | 'md'
  /** Show percentage label to the right of the bar. */
  showLabel?: boolean
  className?: string
}

const sizeClasses = {
  sm: 'h-1.5',
  md: 'h-2.5',
} as const

export function ProgressBar({
  value,
  color = 'bg-primary',
  size = 'md',
  showLabel = false,
  className,
}: ProgressBarProps) {
  const clamped = Math.max(0, Math.min(100, value))

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div
        className={cn('flex-1 bg-muted rounded-full overflow-hidden', sizeClasses[size])}
      >
        <div
          className={cn('h-full rounded-full transition-all duration-500', color)}
          style={{ width: `${clamped}%` }}
          role="progressbar"
          aria-valuenow={clamped}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
      {showLabel && (
        <span className="text-xs font-medium text-muted-foreground tabular-nums w-8 text-right">
          {clamped}%
        </span>
      )}
    </div>
  )
}
