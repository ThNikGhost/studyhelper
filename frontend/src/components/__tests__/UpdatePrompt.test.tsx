import { render, screen, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { pwaRegisterMock } from '@/test/pwa-mock'
import { UpdatePrompt } from '../UpdatePrompt'

describe('UpdatePrompt', () => {
  beforeEach(() => {
    pwaRegisterMock.needRefresh = false
    pwaRegisterMock.offlineReady = false
  })

  it('renders nothing when no update and not offline ready', () => {
    const { container } = render(<UpdatePrompt />)
    expect(container.firstChild).toBeNull()
  })

  it('shows offline ready message', () => {
    pwaRegisterMock.offlineReady = true
    render(<UpdatePrompt />)
    expect(screen.getByText('Приложение готово к работе офлайн')).toBeInTheDocument()
  })

  it('shows update available message with refresh button', () => {
    pwaRegisterMock.needRefresh = true
    render(<UpdatePrompt />)
    expect(screen.getByText('Доступна новая версия')).toBeInTheDocument()
    expect(screen.getByText('Обновить')).toBeInTheDocument()
  })

  it('calls updateServiceWorker on refresh button click', async () => {
    pwaRegisterMock.needRefresh = true
    render(<UpdatePrompt />)
    const user = userEvent.setup()
    await user.click(screen.getByText('Обновить'))
    expect(pwaRegisterMock.updateServiceWorker).toHaveBeenCalledWith(true)
  })

  it('closes offline ready message on dismiss', async () => {
    pwaRegisterMock.offlineReady = true
    render(<UpdatePrompt />)
    const user = userEvent.setup()
    await user.click(screen.getByLabelText('Закрыть'))
    expect(pwaRegisterMock.setOfflineReady).toHaveBeenCalledWith(false)
    expect(pwaRegisterMock.setNeedRefresh).toHaveBeenCalledWith(false)
  })

  it('closes update message on dismiss', async () => {
    pwaRegisterMock.needRefresh = true
    render(<UpdatePrompt />)
    const user = userEvent.setup()
    await user.click(screen.getByLabelText('Закрыть'))
    expect(pwaRegisterMock.setNeedRefresh).toHaveBeenCalledWith(false)
  })

  it('passes onRegisteredSW callback to useRegisterSW', () => {
    render(<UpdatePrompt />)
    expect(pwaRegisterMock.onRegisteredSW).toBeTypeOf('function')
  })

  describe('fallback reload on update button click', () => {
    let reloadMock: ReturnType<typeof vi.fn>
    let cachesDeleteMock: ReturnType<typeof vi.fn>
    let cachesKeysMock: ReturnType<typeof vi.fn>

    beforeEach(() => {
      vi.useFakeTimers()
      reloadMock = vi.fn()
      Object.defineProperty(window, 'location', {
        value: { reload: reloadMock },
        writable: true,
        configurable: true,
      })
      cachesDeleteMock = vi.fn().mockResolvedValue(true)
      cachesKeysMock = vi.fn().mockResolvedValue(['workbox-precache-v2', 'api-cache'])
      Object.defineProperty(window, 'caches', {
        value: { keys: cachesKeysMock, delete: cachesDeleteMock },
        writable: true,
        configurable: true,
      })
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('force reloads after 2s fallback timeout', async () => {
      pwaRegisterMock.needRefresh = true
      render(<UpdatePrompt />)

      // Click update button (with fake timers, use act for event handling)
      await act(async () => {
        screen.getByText('Обновить').click()
      })

      expect(pwaRegisterMock.updateServiceWorker).toHaveBeenCalledWith(true)
      expect(reloadMock).not.toHaveBeenCalled()

      // Advance past fallback timeout and flush microtasks
      await act(async () => {
        vi.advanceTimersByTime(2000)
      })

      expect(cachesKeysMock).toHaveBeenCalled()
      expect(cachesDeleteMock).toHaveBeenCalledWith('workbox-precache-v2')
      expect(cachesDeleteMock).toHaveBeenCalledWith('api-cache')
      expect(reloadMock).toHaveBeenCalled()
    })
  })
})
