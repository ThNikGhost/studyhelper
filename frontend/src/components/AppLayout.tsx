import type { ReactNode } from 'react'
import { NetworkStatusBar } from '@/components/NetworkStatusBar'
import { UpdatePrompt } from '@/components/UpdatePrompt'
import { ThemeToggle } from '@/components/ThemeToggle'

interface AppLayoutProps {
  children: ReactNode
}

/**
 * Layout wrapper for authenticated pages.
 * Renders network status bar, update prompt, theme toggle, and children.
 */
export function AppLayout({ children }: AppLayoutProps) {
  return (
    <>
      <NetworkStatusBar />
      <UpdatePrompt />
      {children}
      <div className="fixed bottom-4 right-4 z-50">
        <ThemeToggle />
      </div>
    </>
  )
}
