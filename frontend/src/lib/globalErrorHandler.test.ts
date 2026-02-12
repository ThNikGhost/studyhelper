import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { toast } from 'sonner'
import { setupGlobalErrorHandlers } from './globalErrorHandler'

// Mock sonner toast
vi.mock('sonner', () => ({
  toast: {
    error: vi.fn(),
  },
}))

describe('globalErrorHandler', () => {
  let unhandledRejectionHandler: (event: PromiseRejectionEvent) => void
  let errorHandler: (event: ErrorEvent) => void
  const originalAddEventListener = window.addEventListener

  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(console, 'error').mockImplementation(() => {})

    // Capture event listeners
    window.addEventListener = vi.fn((event, handler) => {
      if (event === 'unhandledrejection') {
        unhandledRejectionHandler = handler as (event: PromiseRejectionEvent) => void
      } else if (event === 'error') {
        errorHandler = handler as (event: ErrorEvent) => void
      }
    })

    setupGlobalErrorHandlers()
  })

  afterEach(() => {
    window.addEventListener = originalAddEventListener
  })

  describe('unhandledrejection handler', () => {
    it('handles Error objects', () => {
      const error = new Error('Test error message')
      const event = {
        reason: error,
        preventDefault: vi.fn(),
      } as unknown as PromiseRejectionEvent

      unhandledRejectionHandler(event)

      expect(event.preventDefault).toHaveBeenCalled()
      expect(console.error).toHaveBeenCalledWith('Unhandled promise rejection:', error)
      expect(toast.error).toHaveBeenCalledWith('Something went wrong', {
        description: 'Test error message',
        duration: 5000,
      })
    })

    it('handles string rejection reasons', () => {
      const event = {
        reason: 'String error',
        preventDefault: vi.fn(),
      } as unknown as PromiseRejectionEvent

      unhandledRejectionHandler(event)

      expect(toast.error).toHaveBeenCalledWith('Something went wrong', {
        description: 'String error',
        duration: 5000,
      })
    })

    it('handles unknown rejection reasons', () => {
      const event = {
        reason: { some: 'object' },
        preventDefault: vi.fn(),
      } as unknown as PromiseRejectionEvent

      unhandledRejectionHandler(event)

      expect(toast.error).toHaveBeenCalledWith('Something went wrong', {
        description: 'An unexpected error occurred',
        duration: 5000,
      })
    })

    it('handles null rejection reason', () => {
      const event = {
        reason: null,
        preventDefault: vi.fn(),
      } as unknown as PromiseRejectionEvent

      unhandledRejectionHandler(event)

      expect(toast.error).toHaveBeenCalledWith('Something went wrong', {
        description: 'An unexpected error occurred',
        duration: 5000,
      })
    })
  })

  describe('error handler', () => {
    it('shows toast for global errors', () => {
      const event = {
        error: new Error('Global error'),
        message: 'Global error message',
        defaultPrevented: false,
      } as unknown as ErrorEvent

      errorHandler(event)

      expect(console.error).toHaveBeenCalledWith('Global error:', event.error)
      expect(toast.error).toHaveBeenCalledWith('An error occurred', {
        description: 'Global error message',
        duration: 5000,
      })
    })

    it('skips already handled errors', () => {
      const event = {
        error: new Error('Already handled'),
        message: 'Error message',
        defaultPrevented: true,
      } as unknown as ErrorEvent

      errorHandler(event)

      expect(toast.error).not.toHaveBeenCalled()
    })

    it('shows fallback message when no error message', () => {
      const event = {
        error: new Error('Error'),
        message: '',
        defaultPrevented: false,
      } as unknown as ErrorEvent

      errorHandler(event)

      expect(toast.error).toHaveBeenCalledWith('An error occurred', {
        description: 'Please try refreshing the page',
        duration: 5000,
      })
    })
  })
})
