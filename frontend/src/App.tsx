import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import RoleRoute from './components/RoleRoute';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import EmployeesPage from './pages/EmployeesPage';
import EmployeeDetailPage from './pages/EmployeeDetailPage';
import AlertsPage from './pages/AlertsPage';
import IncidentsPage from './pages/IncidentsPage';
import IncidentDetailPage from './pages/IncidentDetailPage';
import SettingsPage from './pages/SettingsPage';
import AIInsightsPage from './pages/AIInsightsPage';
import ForbiddenPage from './pages/ForbiddenPage';
import CompliancePage from './pages/CompliancePage';
import UserManagementPage from './pages/UserManagementPage';
import ReportsPage from './pages/ReportsPage';
import { getStoredRole, getRoleHome } from './lib/roles';

const queryClient = new QueryClient();

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('sentinelai_token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

function RoleHomeRedirect() {
  const role = getStoredRole();
  const home = getRoleHome(role);
  return <Navigate to={home} replace />;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/403" element={<ForbiddenPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<RoleHomeRedirect />} />

            {/* Dashboard - all roles */}
            <Route path="dashboard" element={
              <RoleRoute>
                <DashboardPage />
              </RoleRoute>
            } />

            {/* AI Insights - admin & analyst only */}
            <Route path="ai-insights" element={
              <RoleRoute roles={['admin', 'analyst']}>
                <AIInsightsPage />
              </RoleRoute>
            } />

            {/* Employees - admin, analyst, compliance */}
            <Route path="employees" element={
              <RoleRoute roles={['admin', 'analyst', 'compliance']}>
                <EmployeesPage />
              </RoleRoute>
            } />
            <Route path="employees/:id" element={
              <RoleRoute roles={['admin', 'analyst', 'compliance']}>
                <EmployeeDetailPage />
              </RoleRoute>
            } />

            {/* Alerts - admin, analyst, compliance */}
            <Route path="alerts" element={
              <RoleRoute roles={['admin', 'analyst', 'compliance']}>
                <AlertsPage />
              </RoleRoute>
            } />

            {/* Incidents - admin & analyst only */}
            <Route path="incidents" element={
              <RoleRoute roles={['admin', 'analyst']}>
                <IncidentsPage />
              </RoleRoute>
            } />
            <Route path="incidents/:id" element={
              <RoleRoute roles={['admin', 'analyst']}>
                <IncidentDetailPage />
              </RoleRoute>
            } />

            {/* Compliance - admin & compliance */}
            <Route path="compliance" element={
              <RoleRoute roles={['admin', 'compliance']}>
                <CompliancePage />
              </RoleRoute>
            } />

            {/* Reports - admin & compliance */}
            <Route path="reports" element={
              <RoleRoute roles={['admin', 'compliance']}>
                <ReportsPage />
              </RoleRoute>
            } />

            {/* User Management - admin only */}
            <Route path="user-management" element={
              <RoleRoute roles={['admin']}>
                <UserManagementPage />
              </RoleRoute>
            } />

            {/* Settings - admin only */}
            <Route path="settings" element={
              <RoleRoute roles={['admin']}>
                <SettingsPage />
              </RoleRoute>
            } />
          </Route>

          {/* Catch-all -> role home or login */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
