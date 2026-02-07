import { WifiOff } from 'lucide-react'
import { useNetworkStatus } from '@/hooks/useNetworkStatus'

/**
 * Amber banner displayed when the browser is offline.
 */
export function NetworkStatusBar() {
  const isOnline = useNetworkStatus()

  if (isOnline) return null

  return (
    <div
      role="alert"
      className="flex items-center gap-2 bg-amber-500 text-white px-4 py-2 text-sm font-medium"
    >
      <WifiOff className="h-4 w-4 shrink-0" />
      <span>Нет подключения к интернету</span>
    </div>
  )
}
