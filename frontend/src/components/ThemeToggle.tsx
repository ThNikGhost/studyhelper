import { Sun, Moon, Monitor } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useTheme } from '@/hooks/useTheme'
import type { ThemeMode } from '@/lib/theme'

const CYCLE: ThemeMode[] = ['light', 'dark', 'system']

const LABELS: Record<ThemeMode, string> = {
  light: 'Светлая тема',
  dark: 'Тёмная тема',
  system: 'Системная тема',
}

const ICONS: Record<ThemeMode, typeof Sun> = {
  light: Sun,
  dark: Moon,
  system: Monitor,
}

/**
 * Cycling theme toggle button: light → dark → system → light.
 *
 * Uses ghost variant, icon-only, with aria-label for accessibility.
 */
export function ThemeToggle() {
  const { mode, setTheme } = useTheme()

  const nextMode = CYCLE[(CYCLE.indexOf(mode) + 1) % CYCLE.length]
  const Icon = ICONS[mode]

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(nextMode)}
      aria-label={LABELS[mode]}
      title={LABELS[mode]}
    >
      <Icon className="h-5 w-5" />
    </Button>
  )
}
