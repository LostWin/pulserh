import { useState } from 'react';
import { Brain, Lightbulb, ChevronRight } from 'lucide-react';
import { employees } from '../../data/mockData';
import { cn, riskMeta } from '../../lib/utils';
import PageHeader from '../../components/PageHeader';
import Card, { CardHeader } from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import Avatar from '../../components/ui/Avatar';

const FACTORS = ['Charge de travail', 'Reconnaissance', "Perspectives d'évolution", "Ambiance d'équipe", 'Rémunération', 'Équilibre vie pro/perso'];

const RECO = {
  'Charge de travail': 'Rééquilibrer la charge et envisager de déléguer certaines missions prioritaires.',
  'Reconnaissance': 'Instaurer un feedback régulier et valoriser publiquement les réussites.',
  "Perspectives d'évolution": "Co-construire un plan de développement et de mobilité interne.",
  "Ambiance d'équipe": "Organiser un point d'équipe et renforcer les moments collectifs.",
  'Rémunération': 'Étudier un ajustement salarial ou une prime de performance.',
  'Équilibre vie pro/perso': 'Proposer davantage de flexibilité (télétravail, horaires aménagés).',
};

function predictedRisk(emp) {
  const penalty = emp.delta < 0 ? Math.abs(emp.delta) : 0;
  return Math.round(Math.min(95, Math.max(5, 100 - emp.engagement - penalty * 0.5)));
}

function factorsFor(emp) {
  const risk = predictedRisk(emp);
  return FACTORS.map((label, i) => {
    const seed = (emp.id * 37 + i * 101) % 100;
    const value = Math.round(Math.min(95, Math.max(8, (seed / 100) * risk * 1.3)));
    return { label, value };
  }).sort((a, b) => b.value - a.value);
}

function factorColor(v) {
  if (v >= 60) return 'bg-brand-danger';
  if (v >= 35) return 'bg-brand-danger/10';
  return 'bg-brand-secondary';
}

export default function Predictions() {
  const ranked = [...employees].sort((a, b) => predictedRisk(b) - predictedRisk(a));
  const [selectedId, setSelectedId] = useState(ranked[0].id);
  const selected = ranked.find((e) => e.id === selectedId) || ranked[0];
  const factors = factorsFor(selected);
  const risk = predictedRisk(selected);
  const meta = riskMeta(selected.risk);

  return (
    <div className="animate-fade-in-up space-y-6">
      <PageHeader title="Prédictions IA" subtitle="Risque de départ estimé et facteurs explicatifs par collaborateur" />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Ranked list */}
        <Card className="lg:col-span-1">
          <CardHeader title="Classement par risque" subtitle="Détecté par le modèle prédictif" icon={Brain} />
          <ul className="max-h-[28rem] divide-y divide-slate-100 overflow-y-auto">
            {ranked.map((emp) => {
              const r = predictedRisk(emp);
              const active = emp.id === selectedId;
              return (
                <li key={emp.id}>
                  <button
                    onClick={() => setSelectedId(emp.id)}
                    className={cn('flex w-full items-center gap-3 px-4 py-3 text-left transition-colors', active ? 'bg-brand-light' : 'hover:bg-brand-light')}
                  >
                    <Avatar name={emp.name} size="sm" />
                    <div className="min-w-0 flex-1">
                      <div className="truncate text-sm font-medium text-brand-dark">{emp.name}</div>
                      <div className="truncate text-xs text-brand-secondary/70">{emp.department}</div>
                    </div>
                    <span className={cn('text-sm font-bold', r >= 60 ? 'text-brand-danger' : r >= 35 ? 'text-brand-danger/10' : 'text-brand-secondary')}>{r}%</span>
                    <ChevronRight size={16} className={cn('shrink-0', active ? 'text-brand-secondary' : 'text-brand-secondary/40')} />
                  </button>
                </li>
              );
            })}
          </ul>
        </Card>

        {/* Detail */}
        <Card className="lg:col-span-2">
          <div className="flex flex-col gap-4 border-b border-brand-secondary/10 p-5 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-3">
              <Avatar name={selected.name} size="lg" />
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-brand-dark">{selected.name}</h3>
                  <Badge variant={meta.badge} dot>{meta.label}</Badge>
                </div>
                <p className="text-sm text-brand-secondary/80">{selected.title} · {selected.department} · {selected.tenure}</p>
              </div>
            </div>
            <div className="text-center">
              <div className={cn('text-4xl font-black tracking-tight', risk >= 60 ? 'text-brand-danger' : risk >= 35 ? 'text-brand-danger/10' : 'text-brand-secondary')}>{risk}%</div>
              <div className="text-xs text-brand-secondary/70">risque de départ (12 mois)</div>
            </div>
          </div>

          <div className="p-5">
            <h4 className="mb-4 text-sm font-semibold text-brand-dark">Facteurs contributifs</h4>
            <div className="space-y-3">
              {factors.map((f) => (
                <div key={f.label}>
                  <div className="mb-1 flex items-center justify-between text-sm">
                    <span className="text-brand-secondary">{f.label}</span>
                    <span className="font-semibold text-brand-dark">{f.value}%</span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-brand-light">
                    <div className={cn('h-full rounded-full transition-all duration-500', factorColor(f.value))} style={{ width: `${f.value}%` }} />
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-5 flex gap-3 rounded-xl border border-brand-secondary/20 bg-brand-light/60 p-4">
              <Lightbulb size={20} className="shrink-0 text-brand-secondary" />
              <div>
                <div className="text-sm font-semibold text-brand-dark">Recommandation de l'IA</div>
                <p className="mt-0.5 text-sm text-brand-secondary/80">{RECO[factors[0].label]}</p>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
