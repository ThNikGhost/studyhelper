import type { ReactNode } from 'react'
import { NetworkStatusBar } from '@/components/NetworkStatusBar'
import { UpdatePrompt } from '@/components/UpdatePrompt'

interface AppLayoutProps {
  children: ReactNode
}

/**
 * Layout wrapper for authenticated pages.
 * Renders network status bar, update prompt, and children.
 */
export function AppLayout({ children }: AppLayoutProps) {
  return (
    <>
      <NetworkStatusBar />
      <UpdatePrompt />
      {children}
    </>
  )
}
