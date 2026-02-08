import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { AppLayout } from '../AppLayout'

// Mock child components
vi.mock('@/components/NetworkStatusBar', () => ({
  NetworkStatusBar: () => <div data-testid="network-status-bar" />,
}))

vi.mock('@/components/UpdatePrompt', () => ({
  UpdatePrompt: () => <div data-testid="update-prompt" />,
}))

vi.mock('@/components/ThemeToggle', () => ({
  ThemeToggle: () => <div data-testid="theme-toggle" />,
}))

describe('AppLayout', () => {
  it('renders children', () => {
    render(
      <AppLayout>
        <div data-testid="child-content">Hello</div>
      </AppLayout>,
    )
    expect(screen.getByTestId('child-content')).toBeInTheDocument()
  })

  it('renders NetworkStatusBar', () => {
    render(
      <AppLayout>
        <div>Content</div>
      </AppLayout>,
    )
    expect(screen.getByTestId('network-status-bar')).toBeInTheDocument()
  })

  it('renders UpdatePrompt', () => {
    render(
      <AppLayout>
        <div>Content</div>
      </AppLayout>,
    )
    expect(screen.getByTestId('update-prompt')).toBeInTheDocument()
  })

  it('renders ThemeToggle', () => {
    render(
      <AppLayout>
        <div>Content</div>
      </AppLayout>,
    )
    expect(screen.getByTestId('theme-toggle')).toBeInTheDocument()
  })
})
