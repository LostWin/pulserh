import { CalendarCheck, UserPlus, Clock4 } from 'lucide-react';
import PageHeader from '../../components/PageHeader';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';

const DEMO_ENTRETIENS = [
  { collaborator: 'Noah Petit', date: '28 juin 2026', time: '10:30', status: 'Planifié' },
  { collaborator: 'Lucas Bernard', date: '02 juillet 2026', time: '14:00', status: 'À planifier' },
  { collaborator: 'Chloé Martin', date: '07 juillet 2026', time: '09:30', status: 'Planifié' },
];

export default function ManagerEntretiens() {
  return (
    <div className="animate-fade-in-up space-y-6">
      <PageHeader title="Entretiens" subtitle="Interface de démonstration pour planifier et suivre les entretiens" />

      <Card className="rounded-4xl p-8 text-center">
        <div className="mx-auto grid h-16 w-16 place-items-center rounded-2xl bg-brand-secondary text-white shadow-sm">
          <CalendarCheck size={28} />
        </div>
        <Badge variant="neutral" className="mt-5 bg-brand-secondary text-white ring-brand-secondary/20">
          Démo activée
        </Badge>
        <h2 className="mt-4 text-2xl font-bold text-brand-dark">Entretiens manager</h2>
        <p className="mx-auto mt-3 max-w-xl text-sm leading-relaxed text-brand-secondary/80">
          Cette vue montre un scénario fonctionnel de suivi des entretiens avec vos collaborateurs. Vous pouvez lancer la préparation ou consulter les entretiens à venir.
        </p>
      </Card>

      <Card className="space-y-4 p-6">
        {DEMO_ENTRETIENS.map((item) => (
          <div key={item.collaborator} className="flex flex-col gap-4 rounded-3xl border border-brand-secondary/10 bg-white p-5 shadow-sm sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div className="flex items-center gap-2 text-xs uppercase tracking-[0.24em] text-brand-secondary/70">{item.collaborator}</div>
              <p className="mt-2 text-lg font-semibold text-brand-dark">{item.date} · {item.time}</p>
              <p className="text-sm text-brand-secondary/80">Statut : {item.status}</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <button className="rounded-2xl bg-orange-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-orange-700">
                Préparer
              </button>
              <button className="rounded-2xl border border-brand-secondary/20 px-4 py-2 text-sm font-semibold text-brand-secondary transition hover:bg-brand-light">
                Voir le dossier
              </button>
            </div>
          </div>
        ))}
      </Card>

      <Card className="grid gap-4 p-6 sm:grid-cols-2">
        <div className="rounded-3xl border border-brand-secondary/10 bg-brand-light p-5">
          <div className="flex items-center gap-3 text-brand-secondary/80">
            <UserPlus size={18} />
            <span>Entretiens planifiés</span>
          </div>
          <p className="mt-3 text-3xl font-semibold text-brand-dark">2</p>
        </div>
        <div className="rounded-3xl border border-brand-secondary/10 bg-brand-light p-5">
          <div className="flex items-center gap-3 text-brand-secondary/80">
            <Clock4 size={18} />
            <span>Temps moyen</span>
          </div>
          <p className="mt-3 text-3xl font-semibold text-brand-dark">45 min</p>
        </div>
      </Card>
    </div>
  );
}
