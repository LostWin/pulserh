import { lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { NotificationProvider } from './contexts/NotificationContext';
import Layout from './layouts/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import NotFound from './pages/NotFound';

// ── Collaborateur ──────────────────────────────────────────────────────────
const CollaborateurDashboard = lazy(() => import('./pages/collaborateur/Dashboard'));
const Assistant = lazy(() => import('./pages/shared/Assistant'));
const Conges = lazy(() => import('./pages/collaborateur/Conges'));
const Documents = lazy(() => import('./pages/collaborateur/Documents'));
const Profil = lazy(() => import('./pages/collaborateur/Profil'));
const EditProfile = lazy(() => import('./pages/collaborateur/EditProfile'));
const Onboarding = lazy(() => import('./pages/collaborateur/Onboarding'));
const UserSettings = lazy(() => import('./pages/Settings'));

// ── Manager ────────────────────────────────────────────────────────────────
const ManagerDashboard = lazy(() => import('./pages/manager/Dashboard'));
const Equipe = lazy(() => import('./pages/manager/Equipe'));
const Predictions = lazy(() => import('./pages/manager/Predictions'));
const ManagerAlertes = lazy(() => import('./pages/manager/Alertes'));
const ManagerEntretiens = lazy(() => import('./pages/manager/Entretiens'));
const EmployeeProfileView = lazy(() => import('./pages/EmployeeProfileView'));

// ── RH ─────────────────────────────────────────────────────────────────────
const RhDashboard = lazy(() => import('./pages/rh/Dashboard'));
const Employes = lazy(() => import('./pages/rh/Employes'));
const CarrieresRH = lazy(() => import('./pages/rh/Carrieres'));
const Departements = lazy(() => import('./pages/rh/Departements'));
const ImportDonnees = lazy(() => import('./pages/rh/Import'));
const DocumentsRH = lazy(() => import('./pages/rh/DocumentsRH'));
const Workflows = lazy(() => import('./pages/rh/Workflows'));
const AlertesRH = lazy(() => import('./pages/rh/AlertesRH'));
const SupervisionIA = lazy(() => import('./pages/rh/SupervisionIA'));
const EmployeeCarriereView = lazy(() => import('./pages/rh/EmployeeCarriereView'));

// ── Direction ──────────────────────────────────────────────────────────────
const DirectionDashboard = lazy(() => import('./pages/direction/Dashboard'));
const Simulations = lazy(() => import('./pages/direction/Simulations'));
const Rapports = lazy(() => import('./pages/direction/Rapports'));
const AlertesCritiques = lazy(() => import('./pages/direction/AlertesCritiques'));

// ── Admin ──────────────────────────────────────────────────────────────────
const Monitoring = lazy(() => import('./pages/admin/Monitoring'));
const Keycloak = lazy(() => import('./pages/admin/Keycloak'));
const Securite = lazy(() => import('./pages/admin/Securite'));
const ConfigIA = lazy(() => import('./pages/admin/ConfigIA'));
const Audit = lazy(() => import('./pages/admin/Audit'));
const DataAccess = lazy(() => import('./pages/admin/DataAccess'));
const MoteurDocumentaire = lazy(() => import('./pages/admin/MoteurDocumentaire'));

export default function App() {
  return (
    <Router>
      <AuthProvider>
        <NotificationProvider>
          <Routes>
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="/login" element={<Login />} />

            <Route element={<Layout />}>
              {/* ── Collaborateur ── */}
              <Route element={<ProtectedRoute section="collaborateur" />}>
                <Route path="/collaborateur/dashboard" element={<CollaborateurDashboard />} />
                <Route path="/collaborateur/assistant" element={<Assistant />} />
                <Route path="/collaborateur/documents" element={<Documents />} />
                <Route path="/collaborateur/profil" element={<Profil />} />
                <Route path="/collaborateur/profil/modifier" element={<EditProfile />} />
                <Route path="/collaborateur/conges" element={<Conges />} />
                <Route path="/collaborateur/onboarding" element={<Onboarding />} />
              </Route>

              <Route element={<ProtectedRoute />}>
                <Route path="/settings" element={<UserSettings />} />
              </Route>

              {/* ── Manager ── */}
              <Route element={<ProtectedRoute section="manager" />}>
                <Route path="/manager/dashboard" element={<ManagerDashboard />} />
                <Route path="/manager/equipe" element={<Equipe />} />
                <Route path="/manager/equipe/:id" element={<EmployeeProfileView />} />
                <Route path="/manager/predictions" element={<Predictions />} />
                <Route path="/manager/alertes" element={<ManagerAlertes />} />
                <Route path="/manager/entretiens" element={<ManagerEntretiens />} />
                <Route path="/manager/assistant" element={<Assistant />} />
              </Route>

              {/* ── RH ── */}
              <Route element={<ProtectedRoute section="rh" />}>
                <Route path="/rh/dashboard" element={<RhDashboard />} />
                <Route path="/rh/import" element={<ImportDonnees />} />
                <Route path="/rh/employes" element={<Employes />} />
                <Route path="/rh/employes/:id" element={<EmployeeProfileView />} />
                <Route path="/rh/employees/:id/carriere" element={<EmployeeCarriereView />} />
                <Route path="/rh/carrieres" element={<CarrieresRH />} />
                <Route path="/rh/departements" element={<Departements />} />
                <Route path="/rh/documents" element={<DocumentsRH />} />
                <Route path="/rh/workflows" element={<Workflows />} />
                <Route path="/rh/alertes" element={<AlertesRH />} />
                <Route path="/rh/supervision-ia" element={<SupervisionIA />} />
                <Route path="/rh/assistant" element={<Assistant />} />
              </Route>

              {/* ── Direction ── */}
              <Route element={<ProtectedRoute section="direction" />}>
                <Route path="/direction/dashboard" element={<DirectionDashboard />} />
                <Route path="/direction/simulations" element={<Simulations />} />
                <Route path="/direction/rapports" element={<Rapports />} />
                <Route path="/direction/alertes" element={<AlertesCritiques />} />
                <Route path="/direction/assistant" element={<Assistant />} />
              </Route>

              {/* ── Admin ── */}
              <Route element={<ProtectedRoute section="admin" />}>
                <Route path="/admin/dashboard" element={<Navigate to="/admin/monitoring" replace />} />
                <Route path="/admin/monitoring" element={<Monitoring />} />
                <Route path="/admin/keycloak" element={<Keycloak />} />
                <Route path="/admin/securite" element={<Securite />} />
                <Route path="/admin/config-ia" element={<ConfigIA />} />
                <Route path="/admin/data-access" element={<DataAccess />} />
                <Route path="/admin/documents" element={<MoteurDocumentaire />} />
                <Route path="/admin/audit" element={<Audit />} />
                <Route path="/admin/assistant" element={<Assistant />} />
              </Route>
            </Route>

            <Route path="*" element={<NotFound />} />
          </Routes>
        </NotificationProvider>
      </AuthProvider>
    </Router>
  );
}
