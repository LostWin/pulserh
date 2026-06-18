import { createContext, useContext, useState, useEffect } from 'react';
import { useKeycloak } from '@react-keycloak/web';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const { keycloak, initialized } = useKeycloak();
  const [currentRole, setCurrentRole] = useState(null);

  useEffect(() => {
    if (keycloak.authenticated && !currentRole) {
      const roles = keycloak.realmAccess?.roles || [];
      const available = [];
      if (roles.includes('admin')) available.push('Admin');
      if (roles.includes('director')) available.push('Direction');
      if (roles.includes('hr')) available.push('RH'); 
      if (roles.includes('manager')) available.push('Manager');
      available.push('Collaborateur'); 
      
      if (available.length > 0) {
        setCurrentRole(available[0]);
      }
    }
  }, [keycloak.authenticated, keycloak.realmAccess, currentRole]);

  if (!initialized) {
    return (
      <div className="flex h-screen items-center justify-center bg-brand-light">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-brand-secondary/20 border-t-brand-secondary" />
      </div>
    );
  }

  const login = () => keycloak.login();
  const logout = () => keycloak.logout({ redirectUri: window.location.origin });

  let user = null;
  let availableRoles = [];

  if (keycloak.authenticated) {
    user = {
      name: keycloak.tokenParsed?.preferred_username || keycloak.tokenParsed?.name || "Utilisateur",
      email: keycloak.tokenParsed?.email,
      avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(keycloak.tokenParsed?.preferred_username || 'U')}&background=2563eb&color=fff&bold=true`,
    };

    const roles = keycloak.realmAccess?.roles || [];
    if (roles.includes('admin')) availableRoles.push('Admin');
    if (roles.includes('director')) availableRoles.push('Direction');
    if (roles.includes('hr')) availableRoles.push('RH'); 
    if (roles.includes('manager')) availableRoles.push('Manager');
    availableRoles.push('Collaborateur'); 
  }

  const switchRole = (newRole) => {
    if (availableRoles.includes(newRole)) {
      setCurrentRole(newRole);
    }
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      role: currentRole, 
      availableRoles, 
      switchRole, 
      login, 
      logout, 
      isAuthenticated: keycloak.authenticated 
    }}>
      {children}
    </AuthContext.Provider>
  );
};
