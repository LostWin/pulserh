import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Sparkles } from 'lucide-react';
import Card from './ui/Card';
import Badge from './ui/Badge';

/** Friendly placeholder for modules that aren't built yet. */
export default function ComingSoon({ title, description }) {
  const navigate = useNavigate();
  return (
    <Card className="mx-auto max-w-xl p-10 text-center">
      <div className="mx-auto grid h-16 w-16 place-items-center rounded-xl bg-brand-secondary text-white shadow-sm">
        <Sparkles size={28} />
      </div>
      <Badge variant="neutral" className="mt-5 bg-brand-secondary text-white ring-brand-secondary/20">Bientôt disponible</Badge>
      <h2 className="mt-3 text-xl font-bold text-brand-dark">{title}</h2>
      <p className="mt-2 text-sm leading-relaxed text-brand-secondary/80">
        {description || "Ce module est en cours de développement et rejoindra bientôt la plateforme. Les écrans clés de chaque espace sont déjà accessibles."}
      </p>
      <button
        onClick={() => navigate(-1)}
        className="mt-6 inline-flex items-center gap-2 rounded-xl bg-brand-dark px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-brand-secondary"
      >
        <ArrowLeft size={16} /> Retour
      </button>
    </Card>
  );
}
