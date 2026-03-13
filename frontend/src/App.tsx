import { Suspense, lazy } from 'react'
import { Routes, Route, Navigate, Outlet } from 'react-router-dom'
import * as Sentry from '@sentry/react'
import { useAuthStore } from '@/stores/authStore'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { AppLayout } from '@/components/AppLayout'
import { PageSkeleton } from '@/components/PageSkeleton'

const SentryRoutes = Sentry.withSentryReactRouterV7Routing(Routes)

// Eager-load auth pages (needed immediately)
import LoginPage from '@/pages/LoginPage'
import RegisterPage from '@/pages/RegisterPage'

// Lazy-load all other pages for better initial bundle size
const DashboardPage = lazy(() => import('@/pages/DashboardPage'))
const SchedulePage = lazy(() => import('@/pages/SchedulePage'))
const SubjectsPage = lazy(() => import('@/pages/SubjectsPage'))
const SemestersPage = lazy(() => import('@/pages/SemestersPage'))
const WorksPage = lazy(() => import('@/pages/WorksPage'))
const ClassmatesPage = lazy(() => import('@/pages/ClassmatesPage'))
const FilesPage = lazy(() => import('@/pages/FilesPage'))
const AttendancePage = lazy(() => import('@/pages/AttendancePage'))
const TimelinePage = lazy(() => import('@/pages/TimelinePage'))
const SettingsPage = lazy(() => import('@/pages/SettingsPage'))
const GradesPage = lazy(() => import('@/pages/GradesPage'))

function ProtectedLayout() {
  return (
    <ProtectedRoute>
      <AppLayout>
        <Suspense fallback={<PageSkeleton />}>
          <Outlet />
        </Suspense>
      </AppLayout>
    </ProtectedRoute>
  )
}

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <SentryRoutes>
      <Route
        path="/login"
        element={
          isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />
        }
      />
      <Route
        path="/register"
        element={
          isAuthenticated ? <Navigate to="/" replace /> : <RegisterPage />
        }
      />
      <Route element={<ProtectedLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/schedule" element={<SchedulePage />} />
        <Route path="/subjects" element={<SubjectsPage />} />
        <Route path="/semesters" element={<SemestersPage />} />
        <Route path="/works" element={<WorksPage />} />
        <Route path="/classmates" element={<ClassmatesPage />} />
        <Route path="/files" element={<FilesPage />} />
        <Route path="/attendance" element={<AttendancePage />} />
        <Route path="/timeline" element={<TimelinePage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/grades" element={<GradesPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </SentryRoutes>
  )
}

export default App
