import { createContext, useContext } from 'react';
import { useKeycloak } from '@react-keycloak/web';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const { keycloak, initialized } = useKeycloak();

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
  let role = null;

  if (keycloak.authenticated) {
    user = {
      name: keycloak.tokenParsed?.preferred_username || keycloak.tokenParsed?.name || "Utilisateur",
      email: keycloak.tokenParsed?.email,
      avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(keycloak.tokenParsed?.preferred_username || 'U')}&background=2563eb&color=fff&bold=true`,
    };

    // Logique pour définir le rôle principal en fonction de roles de Keycloak
    const roles = keycloak.realmAccess?.roles || [];
    if (roles.includes('admin')) role = 'Admin';
    else if (roles.includes('director')) role = 'Direction';
    else if (roles.includes('hr')) role = 'RH'; 
    else if (roles.includes('manager')) role = 'Manager';
    else role = 'Collaborateur'; 
  }

  return (
    <AuthContext.Provider value={{ user, role, login, logout, isAuthenticated: keycloak.authenticated }}>
      {children}
    </AuthContext.Provider>
  );
};
