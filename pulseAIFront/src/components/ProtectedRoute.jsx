import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ROLE_META } from '../config/roles';

/**
 * Guards a section of the app. Redirects anonymous users to /login and
 * sends authenticated users who wander into another role's section back
 * to their own home — so the URL bar can't bypass role separation.
 */
export default function ProtectedRoute({ section }) {
  const { user, role } = useAuth();
  const location = useLocation();

  if (!user || !role) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (section && ROLE_META[role]?.section !== section) {
    return <Navigate to={ROLE_META[role]?.home || '/login'} replace />;
  }

  return <Outlet />;
}
