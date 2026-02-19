import { useRegisterSW } from 'virtual:pwa-register/react'
import { RefreshCw, CheckCircle, X } from 'lucide-react'
import { Button } from '@/components/ui/button'

const UPDATE_CHECK_INTERVAL_MS = 60 * 60 * 1000 // 1 hour
const RELOAD_FALLBACK_MS = 2000

/**
 * Prompt banner for PWA updates and offline-ready notifications.
 *
 * Includes periodic SW update checks (hourly) and a fallback reload
 * mechanism to work around vite-pwa#896 (updateServiceWorker not reloading).
 */
export function UpdatePrompt() {
  const {
    needRefresh: [needRefresh, setNeedRefresh],
    offlineReady: [offlineReady, setOfflineReady],
    updateServiceWorker,
  } = useRegisterSW({
    onRegisteredSW(swUrl, registration) {
      if (!registration) return
      // Periodic SW update check (vite-pwa docs recommendation)
      const id = setInterval(async () => {
        if (registration.installing || !navigator) return
        if ('connection' in navigator && !navigator.onLine) return
        try {
          const resp = await fetch(swUrl, {
            cache: 'no-store',
            headers: { 'cache-control': 'no-cache' },
          })
          if (resp?.status === 200) await registration.update()
        } catch {
          // Network error during update check — non-critical, will retry next interval
        }
      }, UPDATE_CHECK_INTERVAL_MS)
      // Fix vite-pwa#583: clear interval to prevent race condition
      registration.addEventListener('updatefound', () => clearInterval(id))
    },
  })

  const handleUpdate = () => {
    updateServiceWorker(true)
    // Fallback (vite-pwa#896): if page didn't reload in 2s, force it
    setTimeout(async () => {
      if ('caches' in window) {
        const names = await caches.keys()
        await Promise.all(names.map((n) => caches.delete(n)))
      }
      window.location.reload()
    }, RELOAD_FALLBACK_MS)
  }

  const close = () => {
    setOfflineReady(false)
    setNeedRefresh(false)
  }

  if (!offlineReady && !needRefresh) return null

  return (
    <div role="alert" className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 text-sm">
      {offlineReady ? (
        <>
          <CheckCircle className="h-4 w-4 shrink-0" />
          <span className="flex-1">Приложение готово к работе офлайн</span>
          <Button
            variant="ghost"
            size="icon"
            onClick={close}
            aria-label="Закрыть"
            className="h-7 w-7 text-white hover:bg-blue-700 hover:text-white"
          >
            <X className="h-4 w-4" />
          </Button>
        </>
      ) : (
        <>
          <RefreshCw className="h-4 w-4 shrink-0" />
          <span className="flex-1">Доступна новая версия</span>
          <Button
            size="sm"
            variant="secondary"
            onClick={handleUpdate}
            className="h-7 text-xs"
          >
            Обновить
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={close}
            aria-label="Закрыть"
            className="h-7 w-7 text-white hover:bg-blue-700 hover:text-white"
          >
            <X className="h-4 w-4" />
          </Button>
        </>
      )}
    </div>
  )
}
