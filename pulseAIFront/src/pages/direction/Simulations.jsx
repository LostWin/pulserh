import { useMemo, useState } from 'react';
import { Sparkles, RotateCcw, Heart, TrendingDown, Wallet, PiggyBank } from 'lucide-react';
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, Legend,
} from 'recharts';
import { cn } from '../../lib/utils';
import PageHeader from '../../components/PageHeader';
import Card, { CardHeader } from '../../components/ui/Card';

const BASE = { engagement: 76, turnover: 7.4, headcount: 127, payroll: 4200, replacement: 22 };
const MONTHS = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin'];
const DEFAULTS = { raise: 0, training: 0, remote: 0, recognition: 0 };

const LEVERS = [
  { key: 'raise', label: 'Augmentation salariale', min: 0, max: 8, step: 0.5, unit: '%' },
  { key: 'training', label: 'Budget formation', min: 0, max: 100, step: 5, unit: '%' },
  { key: 'remote', label: 'Jours de télétravail / sem.', min: 0, max: 5, step: 1, unit: ' j' },
  { key: 'recognition', label: 'Programme de reconnaissance', min: 0, max: 100, step: 5, unit: '%' },
];

function simulate({ raise, training, remote, recognition }) {
  const gain = raise * 1.4 + (training / 100) * 5 + remote * 1.3 + (recognition / 100) * 7;
  const engagement = Math.min(100, BASE.engagement + gain);
  const engagementGain = engagement - BASE.engagement;
  const turnover = Math.max(1.5, BASE.turnover - engagementGain * 0.4);
  const departsAvoided = ((BASE.turnover - turnover) / 100) * BASE.headcount;
  const savings = departsAvoided * BASE.replacement; // k€
  const cost = (raise / 100) * BASE.payroll + (training / 100) * 80 + (recognition / 100) * 30; // k€
  const net = savings - cost;
  const roi = cost > 0 ? savings / cost : null;
  return { engagement, engagementGain, turnover, savings, cost, net, roi };
}

function ResultTile({ icon: Icon, label, value, sub, accent, subColor }) {
  return (
    <Card className="p-4">
      <div className="flex items-center gap-2 text-brand-secondary/80">
        <Icon size={16} className={accent} />
        <span className="text-xs font-medium">{label}</span>
      </div>
      <div className="mt-2 text-2xl font-bold text-brand-dark">{value}</div>
      {sub && <div className={cn('text-xs font-medium', subColor || 'text-brand-secondary/70')}>{sub}</div>}
    </Card>
  );
}

export default function Simulations() {
  const [levers, setLevers] = useState(DEFAULTS);
  const r = useMemo(() => simulate(levers), [levers]);
  const touched = useMemo(() => Object.keys(DEFAULTS).some((k) => levers[k] !== DEFAULTS[k]), [levers]);

  const projection = MONTHS.map((month, i) => {
    const t = i / (MONTHS.length - 1);
    return {
      month,
      actuel: BASE.engagement,
      projeté: Math.round((BASE.engagement + r.engagementGain * t) * 10) / 10,
    };
  });

  const fmt = (n) => `${Math.round(n)} k€`;

  return (
    <div className="animate-fade-in-up space-y-6">
      <PageHeader title="Simulateur de scénarios" subtitle="Projetez l'impact RH et financier de vos décisions">
        <button
          onClick={() => setLevers(DEFAULTS)}
          disabled={!touched}
          className="inline-flex items-center gap-2 rounded-xl border border-brand-secondary/20 bg-white px-3 py-2 text-sm font-medium text-brand-dark shadow-sm transition-colors hover:bg-brand-light disabled:opacity-40"
        >
          <RotateCcw size={15} /> Réinitialiser
        </button>
      </PageHeader>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Levers */}
        <Card className="lg:col-span-1">
          <CardHeader title="Leviers d'action" subtitle="Ajustez et observez l'impact" icon={Sparkles} />
          <div className="space-y-6 p-5">
            {LEVERS.map((lever) => (
              <div key={lever.key}>
                <div className="mb-2 flex items-center justify-between">
                  <label className="text-sm font-medium text-brand-dark">{lever.label}</label>
                  <span className="rounded-xl bg-brand-light px-2 py-0.5 text-sm font-semibold text-brand-secondary">
                    {levers[lever.key]}{lever.unit}
                  </span>
                </div>
                <input
                  type="range"
                  min={lever.min} max={lever.max} step={lever.step}
                  value={levers[lever.key]}
                  onChange={(e) => setLevers({ ...levers, [lever.key]: Number(e.target.value) })}
                  className="h-2 w-full cursor-pointer appearance-none rounded-full bg-brand-light accent-brand-secondary"
                />
              </div>
            ))}
          </div>
        </Card>

        {/* Results */}
        <div className="space-y-6 lg:col-span-2">
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <ResultTile
              icon={Heart} accent="text-brand-secondary" label="Engagement projeté"
              value={`${r.engagement.toFixed(0)}/100`}
              sub={`${r.engagementGain >= 0 ? '+' : ''}${r.engagementGain.toFixed(1)} pts`}
              subColor={r.engagementGain > 0 ? 'text-brand-secondary' : 'text-brand-secondary/70'}
            />
            <ResultTile
              icon={TrendingDown} accent="text-brand-secondary" label="Turnover projeté"
              value={`${r.turnover.toFixed(1)}%`}
              sub={`${(r.turnover - BASE.turnover).toFixed(1)} pts`}
              subColor={r.turnover < BASE.turnover ? 'text-brand-secondary' : 'text-brand-secondary/70'}
            />
            <ResultTile
              icon={Wallet} accent="text-brand-secondary" label="Coût annuel"
              value={fmt(r.cost)} sub="investissement"
            />
            <ResultTile
              icon={PiggyBank} accent="text-purple-500" label="Bénéfice net"
              value={fmt(r.net)}
              sub={r.roi ? `ROI ${r.roi.toFixed(1)}x` : 'sans coût'}
              subColor={r.net >= 0 ? 'text-brand-secondary' : 'text-brand-danger'}
            />
          </div>

          <Card>
            <CardHeader title="Trajectoire d'engagement projetée" subtitle="Scénario vs situation actuelle" icon={Heart} />
            <div className="h-64 p-4">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={projection} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="proj" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.3} />
                      <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                  <XAxis dataKey="month" tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                  <YAxis domain={[60, 100]} tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                  <Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #e2e8f0', fontSize: 12 }} />
                  <Legend wrapperStyle={{ fontSize: 12 }} />
                  <Area type="monotone" dataKey="actuel" name="Actuel" stroke="#cbd5e1" strokeWidth={2} strokeDasharray="5 5" fill="transparent" />
                  <Area type="monotone" dataKey="projeté" name="Projeté" stroke="#8b5cf6" strokeWidth={2.5} fill="url(#proj)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <p className="px-1 text-xs text-brand-secondary/70">
            * Modèle illustratif à des fins de démonstration. Base : {BASE.headcount} collaborateurs, turnover {BASE.turnover}%, coût de remplacement moyen {BASE.replacement} k€.
          </p>
        </div>
      </div>
    </div>
  );
}
