import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { NetworkStatusBar } from '../NetworkStatusBar'

// Mock useNetworkStatus
vi.mock('@/hooks/useNetworkStatus', () => ({
  useNetworkStatus: vi.fn(),
}))

import { useNetworkStatus } from '@/hooks/useNetworkStatus'

const mockUseNetworkStatus = vi.mocked(useNetworkStatus)

describe('NetworkStatusBar', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders nothing when online', () => {
    mockUseNetworkStatus.mockReturnValue(true)
    const { container } = render(<NetworkStatusBar />)
    expect(container.firstChild).toBeNull()
  })

  it('renders offline banner when offline', () => {
    mockUseNetworkStatus.mockReturnValue(false)
    render(<NetworkStatusBar />)
    expect(screen.getByRole('alert')).toBeInTheDocument()
    expect(screen.getByText('Нет подключения к интернету')).toBeInTheDocument()
  })

  it('has amber background styling', () => {
    mockUseNetworkStatus.mockReturnValue(false)
    render(<NetworkStatusBar />)
    const alert = screen.getByRole('alert')
    expect(alert.className).toContain('bg-amber-500')
  })
})
