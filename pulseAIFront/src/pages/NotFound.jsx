import { useNavigate } from 'react-router-dom';
import { Home, Compass } from 'lucide-react';

export default function NotFound() {
  const navigate = useNavigate();
  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center bg-brand-light px-6 text-center text-brand-dark">
      <div className="absolute top-[-10%] left-[-10%] h-[40%] w-[40%] rounded-full bg-brand-secondary/20 blur-[120px]" />
      <div className="absolute bottom-[-10%] right-[-10%] h-[40%] w-[40%] rounded-full bg-brand-secondary/10 blur-[120px]" />
      <div className="z-10">
        <div className="mx-auto grid h-16 w-16 place-items-center rounded-xl border border-brand-secondary/20 bg-brand-light text-brand-secondary">
          <Compass size={30} />
        </div>
        <p className="mt-6 text-7xl font-black tracking-tighter text-brand-dark">404</p>
        <h1 className="mt-2 text-xl font-semibold text-brand-dark">Page introuvable</h1>
        <p className="mt-2 max-w-sm text-brand-secondary/70">
          La page que vous cherchez a été déplacée ou n'existe pas.
        </p>
        <button
          onClick={() => navigate('/login')}
          className="mt-8 inline-flex items-center gap-2 rounded-xl bg-brand-secondary px-5 py-2.5 font-medium text-white shadow-sm transition-transform hover:bg-brand-dark hover:scale-[1.02]"
        >
          <Home size={18} /> Retour à l'accueil
        </button>
      </div>
    </div>
  );
}
