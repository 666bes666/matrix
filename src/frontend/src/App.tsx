import { Route, Routes } from 'react-router-dom';

import { ProtectedRoute } from './components/layout/ProtectedRoute';
import { AppLayout } from './components/layout/AppLayout';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { UsersPage } from './pages/UsersPage';
import { UserProfilePage } from './pages/UserProfilePage';
import { CompetenciesPage } from './pages/CompetenciesPage';
import { TargetProfilesPage } from './pages/TargetProfilesPage';
import { AssessmentFormPage } from './pages/AssessmentFormPage';
import { MatrixPage } from './pages/MatrixPage';

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/users" element={<UsersPage />} />
          <Route path="/users/:id" element={<UserProfilePage />} />
          <Route path="/competencies" element={<CompetenciesPage />} />
          <Route path="/target-profiles" element={<TargetProfilesPage />} />
          <Route path="/assessments/:id" element={<AssessmentFormPage />} />
          <Route path="/matrix" element={<MatrixPage />} />
        </Route>
      </Route>
    </Routes>
  );
}
