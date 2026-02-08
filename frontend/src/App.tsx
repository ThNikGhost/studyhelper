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
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
