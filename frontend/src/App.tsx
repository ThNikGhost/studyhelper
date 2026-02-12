import { Suspense, lazy } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { AppLayout } from '@/components/AppLayout'
import { PageSkeleton } from '@/components/PageSkeleton'

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
const NotesPage = lazy(() => import('@/pages/NotesPage'))
const TimelinePage = lazy(() => import('@/pages/TimelinePage'))
const SettingsPage = lazy(() => import('@/pages/SettingsPage'))
const GradesPage = lazy(() => import('@/pages/GradesPage'))

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <Routes>
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
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Suspense fallback={<PageSkeleton />}>
                <DashboardPage />
              </Suspense>
            </AppLayout>
          </ProtectedRoute>
        }
      />
      {/* Schedule page */}
      <Route
        path="/schedule"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Suspense fallback={<PageSkeleton />}>
                <SchedulePage />
              </Suspense>
            </AppLayout>
          </ProtectedRoute>
        }
      />
      {/* Placeholder routes for future pages */}
      <Route
        path="/subjects"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Suspense fallback={<PageSkeleton />}>
                <SubjectsPage />
              </Suspense>
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/semesters"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Suspense fallback={<PageSkeleton />}>
                <SemestersPage />
              </Suspense>
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/works"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Suspense fallback={<PageSkeleton />}>
                <WorksPage />
              </Suspense>
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/classmates"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Suspense fallback={<PageSkeleton />}>
                <ClassmatesPage />
              </Suspense>
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/files"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Suspense fallback={<PageSkeleton />}>
                <FilesPage />
              </Suspense>
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/attendance"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Suspense fallback={<PageSkeleton />}>
                <AttendancePage />
              </Suspense>
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/notes"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Suspense fallback={<PageSkeleton />}>
                <NotesPage />
              </Suspense>
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/timeline"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Suspense fallback={<PageSkeleton />}>
                <TimelinePage />
              </Suspense>
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Suspense fallback={<PageSkeleton />}>
                <SettingsPage />
              </Suspense>
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/grades"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Suspense fallback={<PageSkeleton />}>
                <GradesPage />
              </Suspense>
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
