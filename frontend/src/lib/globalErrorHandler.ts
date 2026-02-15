import * as Sentry from '@sentry/react'
import { toast } from 'sonner'

/**
 * Setup global error handlers for unhandled promise rejections.
 *
 * React ErrorBoundary only catches errors during rendering,
 * not async errors in event handlers or useEffect callbacks.
 * This handler catches those unhandled promise rejections.
 */
export function setupGlobalErrorHandlers(): void {
  // Handle unhandled promise rejections (async errors)
  window.addEventListener('unhandledrejection', (event: PromiseRejectionEvent) => {
    // Log for debugging
    console.error('Unhandled promise rejection:', event.reason)

    // Prevent default browser error logging (we handle it ourselves)
    event.preventDefault()

    // Extract error message
    const message =
      event.reason instanceof Error
        ? event.reason.message
        : typeof event.reason === 'string'
          ? event.reason
          : 'An unexpected error occurred'

    Sentry.captureException(
      event.reason instanceof Error ? event.reason : new Error(message),
    )

    // Show user-friendly toast
    toast.error('Something went wrong', {
      description: message,
      duration: 5000,
    })
  })

  // Handle global errors (synchronous errors not caught by React)
  window.addEventListener('error', (event: ErrorEvent) => {
    // Don't handle if already handled by ErrorBoundary
    if (event.defaultPrevented) return

    console.error('Global error:', event.error)

    Sentry.captureException(event.error || new Error(event.message))

    toast.error('An error occurred', {
      description: event.message || 'Please try refreshing the page',
      duration: 5000,
    })
  })
}
