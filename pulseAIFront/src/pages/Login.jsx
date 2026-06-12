import { Shield, Sparkles } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { ROLE_META } from '../config/roles';
import { Navigate } from 'react-router-dom';
import logo from '../LOGO 512PX.png';

export default function Login() {
  const { login, isAuthenticated, role } = useAuth();
  
  // Si déjà connecté, on redirige vers l'accueil ou le tableau de bord
  if (isAuthenticated && role) {
    return <Navigate to={ROLE_META[role]?.home || '/'} replace />;
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-brand-light text-brand-dark">
      {/* Background decorations */}
      <div className="pointer-events-none absolute left-[-10%] top-[-10%] h-[40%] w-[40%] rounded-full bg-brand-secondary/20 blur-[120px]" />
      <div className="pointer-events-none absolute bottom-[-10%] right-[-10%] h-[40%] w-[40%] rounded-full bg-brand-secondary/10 blur-[120px]" />

      <div className="z-10 grid w-full max-w-5xl grid-cols-1 items-center gap-8 p-6 md:grid-cols-2 md:p-8">
        {/* Branding */}
        <div className="space-y-6 text-brand-dark">
          <div className="inline-flex items-center gap-2 rounded-full border border-brand-secondary/20 bg-brand-secondary/10 px-3 py-1 text-xs font-medium text-brand-dark">
            <Sparkles size={14} /> IA prédictive RH
          </div>
          <div className="flex items-center gap-4">
            <img src={logo} alt="Pulse RH" className="h-20 w-20 rounded-full object-cover" />
            <div>
              <div className="text-3xl font-bold tracking-tight text-brand-dark">Pulse RH</div>
              <p className="text-sm text-brand-secondary/80">Enterprise Portal</p>
            </div>
          </div>
          <p className="max-w-md text-lg text-brand-secondary/70">
            La solution IA de nouvelle génération pour anticiper le désengagement et optimiser le pilotage de vos ressources humaines.
          </p>
        </div>

        {/* Login Box */}
        <div className="rounded-3xl border border-brand-secondary/15 bg-white p-6 shadow-sm md:p-8 text-center">
          <div className="mb-8">
            <div className="mx-auto grid h-16 w-16 place-items-center rounded-full bg-brand-secondary/10 mb-4">
              <Shield size={32} className="text-brand-secondary" />
            </div>
            <h2 className="mb-2 text-2xl font-bold text-brand-dark">Authentification Sécurisée</h2>
            <p className="text-sm text-brand-secondary/70">
              Veuillez vous connecter avec votre compte d'entreprise via Keycloak.
            </p>
          </div>

          <button
            onClick={() => login()}
            className="w-full rounded-xl bg-brand-secondary px-4 py-3 font-semibold text-white transition hover:bg-brand-secondary/90 shadow-lg shadow-brand-secondary/20"
          >
            Se connecter avec Keycloak
          </button>
        </div>
      </div>
    </div>
  );
}
