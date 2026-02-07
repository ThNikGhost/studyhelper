import { useRegisterSW } from 'virtual:pwa-register/react'
import { RefreshCw, CheckCircle, X } from 'lucide-react'
import { Button } from '@/components/ui/button'

/**
 * Prompt banner for PWA updates and offline-ready notifications.
 */
export function UpdatePrompt() {
  const {
    needRefresh: [needRefresh, setNeedRefresh],
    offlineReady: [offlineReady, setOfflineReady],
    updateServiceWorker,
  } = useRegisterSW()

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
          <button onClick={close} className="p-1 hover:bg-blue-700 rounded" aria-label="Закрыть">
            <X className="h-4 w-4" />
          </button>
        </>
      ) : (
        <>
          <RefreshCw className="h-4 w-4 shrink-0" />
          <span className="flex-1">Доступна новая версия</span>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => updateServiceWorker(true)}
            className="h-7 text-xs"
          >
            Обновить
          </Button>
          <button onClick={close} className="p-1 hover:bg-blue-700 rounded" aria-label="Закрыть">
            <X className="h-4 w-4" />
          </button>
        </>
      )}
    </div>
  )
}
