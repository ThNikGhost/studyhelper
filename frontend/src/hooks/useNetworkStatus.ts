import { useState, useEffect, useRef } from 'react'

/**
 * Hook to track browser online/offline status.
 *
 * @returns `true` when the browser is online, `false` when offline.
 */
export function useNetworkStatus(): boolean {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const isMounted = useRef(true)

  useEffect(() => {
    isMounted.current = true

    const handleOnline = () => {
      if (isMounted.current) setIsOnline(true)
    }
    const handleOffline = () => {
      if (isMounted.current) setIsOnline(false)
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      isMounted.current = false
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  return isOnline
}
