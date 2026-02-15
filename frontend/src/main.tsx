import { StrictMode, useEffect } from 'react'
import { createRoot } from 'react-dom/client'
import {
  BrowserRouter,
  useLocation,
  useNavigationType,
  createRoutesFromChildren,
  matchRoutes,
} from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import * as Sentry from '@sentry/react'
import { Toaster } from 'sonner'
import { ErrorBoundary } from './components/ErrorBoundary'
import { setupGlobalErrorHandlers } from './lib/globalErrorHandler'
import './index.css'
import App from './App.tsx'

// Initialize Sentry before error handlers
if (import.meta.env.VITE_SENTRY_DSN) {
  Sentry.init({
    dsn: import.meta.env.VITE_SENTRY_DSN,
    integrations: [
      Sentry.reactRouterV7BrowserTracingIntegration({
        useEffect,
        useLocation,
        useNavigationType,
        createRoutesFromChildren,
        matchRoutes,
      }),
    ],
    tracesSampleRate: 0.1,
    environment: import.meta.env.MODE,
    release: 'studyhelper-frontend@0.1.0',
  })
}

// Setup global error handlers for unhandled promise rejections
setupGlobalErrorHandlers()

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
})

createRoot(document.getElementById('root')!, {
  onUncaughtError: Sentry.reactErrorHandler((error, errorInfo) => {
    console.warn('Uncaught error', error, errorInfo.componentStack)
  }),
  onCaughtError: Sentry.reactErrorHandler((error, errorInfo) => {
    console.warn('Caught error', error, errorInfo.componentStack)
  }),
}).render(
  <StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
          <Toaster position="top-right" richColors closeButton theme="system" />
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  </StrictMode>
)
