import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, beforeEach } from 'vitest'
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
})
