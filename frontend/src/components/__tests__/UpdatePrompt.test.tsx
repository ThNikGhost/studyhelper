import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { UpdatePrompt } from '../UpdatePrompt'

// Mock virtual:pwa-register/react
const mockUpdateServiceWorker = vi.fn()
const mockSetNeedRefresh = vi.fn()
const mockSetOfflineReady = vi.fn()

let mockNeedRefresh = false
let mockOfflineReady = false

vi.mock('virtual:pwa-register/react', () => ({
  useRegisterSW: () => ({
    needRefresh: [mockNeedRefresh, mockSetNeedRefresh],
    offlineReady: [mockOfflineReady, mockSetOfflineReady],
    updateServiceWorker: mockUpdateServiceWorker,
  }),
}))

describe('UpdatePrompt', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockNeedRefresh = false
    mockOfflineReady = false
  })

  it('renders nothing when no update and not offline ready', () => {
    const { container } = render(<UpdatePrompt />)
    expect(container.firstChild).toBeNull()
  })

  it('shows offline ready message', () => {
    mockOfflineReady = true
    render(<UpdatePrompt />)
    expect(screen.getByText('Приложение готово к работе офлайн')).toBeInTheDocument()
  })

  it('shows update available message with refresh button', () => {
    mockNeedRefresh = true
    render(<UpdatePrompt />)
    expect(screen.getByText('Доступна новая версия')).toBeInTheDocument()
    expect(screen.getByText('Обновить')).toBeInTheDocument()
  })

  it('calls updateServiceWorker on refresh button click', async () => {
    mockNeedRefresh = true
    render(<UpdatePrompt />)
    const user = userEvent.setup()
    await user.click(screen.getByText('Обновить'))
    expect(mockUpdateServiceWorker).toHaveBeenCalledWith(true)
  })

  it('closes offline ready message on dismiss', async () => {
    mockOfflineReady = true
    render(<UpdatePrompt />)
    const user = userEvent.setup()
    await user.click(screen.getByLabelText('Закрыть'))
    expect(mockSetOfflineReady).toHaveBeenCalledWith(false)
    expect(mockSetNeedRefresh).toHaveBeenCalledWith(false)
  })

  it('closes update message on dismiss', async () => {
    mockNeedRefresh = true
    render(<UpdatePrompt />)
    const user = userEvent.setup()
    await user.click(screen.getByLabelText('Закрыть'))
    expect(mockSetNeedRefresh).toHaveBeenCalledWith(false)
  })
})
