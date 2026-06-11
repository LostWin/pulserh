import { createContext, useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ROLE_META } from '../config/roles';

const AuthContext = createContext();

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => useContext(AuthContext);

/** Read a persisted session from localStorage (synchronous, runs once on mount). */
function readStoredSession() {
  try {
    const storedUser = localStorage.getItem('yuser');
    const storedRole = localStorage.getItem('yrole');
    if (storedUser && storedRole && ROLE_META[storedRole]) {
      return { user: JSON.parse(storedUser), role: storedRole };
    }
  } catch {
    localStorage.removeItem('yuser');
    localStorage.removeItem('yrole');
  }
  return { user: null, role: null };
}

export const AuthProvider = ({ children }) => {
  const [session, setSession] = useState(readStoredSession);
  const navigate = useNavigate();
  const { user, role } = session;

  const login = (selectedRole) => {
    const meta = ROLE_META[selectedRole];
    if (!meta) return;

    const dummyUser = {
      name: `${selectedRole} Démo`,
      email: `${selectedRole.toLowerCase()}@ydays.com`,
      avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(selectedRole)}&background=2563eb&color=fff&bold=true`,
    };

    setSession({ user: dummyUser, role: selectedRole });
    localStorage.setItem('yuser', JSON.stringify(dummyUser));
    localStorage.setItem('yrole', selectedRole);
    navigate(meta.home);
  };

  const logout = () => {
    setSession({ user: null, role: null });
    localStorage.removeItem('yuser');
    localStorage.removeItem('yrole');
    navigate('/login');
  };

  return (
    <AuthContext.Provider value={{ user, role, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
