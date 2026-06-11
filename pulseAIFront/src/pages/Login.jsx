import { Shield, Users, ArrowRight, Sparkles } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { ROLES, ROLE_META } from '../config/roles';
import logo from '../LOGO 512PX.png';

export default function Login() {
  const { login } = useAuth();

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
          <div className="space-y-4 pt-6">
            <div className="flex items-center gap-3 text-brand-secondary/80">
              <div className="grid h-10 w-10 place-items-center rounded-full border border-brand-secondary/20 bg-brand-light">
                <Shield size={20} className="text-brand-secondary" />
              </div>
              <span>Connexion sécurisée via Keycloak (simulée)</span>
            </div>
            <div className="flex items-center gap-3 text-brand-secondary/80">
              <div className="grid h-10 w-10 place-items-center rounded-full border border-brand-secondary/20 bg-brand-light">
                <Users size={20} className="text-brand-secondary" />
              </div>
              <span>Espaces adaptés à chaque profil</span>
            </div>
          </div>
        </div>

        {/* Role picker */}
        <div className="rounded-3xl border border-brand-secondary/15 bg-white p-6 shadow-sm md:p-8">
          <div className="mb-8">
            <h2 className="mb-2 text-2xl font-bold text-brand-dark">Simulateur d'accès</h2>
            <p className="text-sm text-brand-secondary/70">
              Pour ce prototype, sélectionnez le rôle que vous souhaitez tester.
            </p>
          </div>

          <div className="space-y-3">
            {ROLES.map((name) => {
              const meta = ROLE_META[name];
              const Icon = meta.icon;
              return (
                <button
                  key={name}
                  onClick={() => login(name)}
                  className="group flex w-full items-center justify-between rounded-xl border border-brand-secondary/20 bg-brand-light p-4 transition-all duration-300 hover:border-brand-secondary/30 hover:bg-white"
                >
                  <div className="flex items-center gap-4">
                    <div className="grid h-12 w-12 place-items-center rounded-xl bg-brand-secondary text-white shadow-sm">
                      <Icon size={24} />
                    </div>
                    <div className="text-left">
                      <div className="text-lg font-semibold text-brand-dark transition-colors group-hover:text-brand-secondary">{name}</div>
                      <div className="text-xs text-brand-secondary/70">{meta.desc}</div>
                    </div>
                  </div>
                  <ArrowRight size={20} className="text-brand-secondary/80 transition-all group-hover:translate-x-1 group-hover:text-brand-dark" />
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
