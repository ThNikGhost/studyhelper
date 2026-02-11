import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { AppLayout } from '@/components/AppLayout'
import LoginPage from '@/pages/LoginPage'
import RegisterPage from '@/pages/RegisterPage'
import DashboardPage from '@/pages/DashboardPage'
import SchedulePage from '@/pages/SchedulePage'
import SubjectsPage from '@/pages/SubjectsPage'
import SemestersPage from '@/pages/SemestersPage'
import WorksPage from '@/pages/WorksPage'
import ClassmatesPage from '@/pages/ClassmatesPage'
import FilesPage from '@/pages/FilesPage'
import AttendancePage from '@/pages/AttendancePage'
import NotesPage from '@/pages/NotesPage'
import TimelinePage from '@/pages/TimelinePage'
import SettingsPage from '@/pages/SettingsPage'
import GradesPage from '@/pages/GradesPage'

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
              <DashboardPage />
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
              <SchedulePage />
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
              <SubjectsPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/semesters"
        element={
          <ProtectedRoute>
            <AppLayout>
              <SemestersPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/works"
        element={
          <ProtectedRoute>
            <AppLayout>
              <WorksPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/classmates"
        element={
          <ProtectedRoute>
            <AppLayout>
              <ClassmatesPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/files"
        element={
          <ProtectedRoute>
            <AppLayout>
              <FilesPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/attendance"
        element={
          <ProtectedRoute>
            <AppLayout>
              <AttendancePage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/notes"
        element={
          <ProtectedRoute>
            <AppLayout>
              <NotesPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/timeline"
        element={
          <ProtectedRoute>
            <AppLayout>
              <TimelinePage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <AppLayout>
              <SettingsPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/grades"
        element={
          <ProtectedRoute>
            <AppLayout>
              <GradesPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
