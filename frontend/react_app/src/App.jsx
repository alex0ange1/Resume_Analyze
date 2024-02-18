import { Route, Routes, Navigate } from 'react-router-dom'
import Authorization from './pages/Authorization'
import Analyse from './pages/Analyse'
import CompetencesPage from './pages/CompetencesPage'
import ProfessionsPage from './pages/ProfessionsPage'
import MainLayout from './layouts/MainLayout'
import PrivateRoute from './layouts/PrivateRoute'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Authorization />} />

      <Route
        path="/"
        element={
          <PrivateRoute>
            <MainLayout />
          </PrivateRoute>
        }
      >
        <Route index element={<Navigate to="/competences" />} />
        <Route path="analyse" element={<Analyse />} />
        <Route path="competences" element={<CompetencesPage />} />
        <Route path="professions" element={<ProfessionsPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/login" />} />
    </Routes>
  )
}