import { useEffect } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ROLE_META } from '../config/roles';

export default function ProtectedRoute({ section }) {
  const { user, role, login, isAuthenticated } = useAuth();
  const location = useLocation();

  useEffect(() => {
    if (isAuthenticated === false) {
      // Pour forcer une redirection Keycloak si vraiment déconnecté (sinon Login s'en charge)
      // Mais ici, on va juste rediriger vers /login, où le bouton SSO est présent.
    }
  }, [isAuthenticated, login]);

  if (!isAuthenticated || !user || !role) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (section && ROLE_META[role]?.section !== section) {
    return <Navigate to={ROLE_META[role]?.home || '/'} replace />;
  }

  return <Outlet />;
}
