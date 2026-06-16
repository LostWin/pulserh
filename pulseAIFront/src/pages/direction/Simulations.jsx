import { useMemo, useState } from 'react';
import { Sparkles, RotateCcw, Heart, TrendingDown, Wallet, PiggyBank } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';

import { api } from '../../lib/api';
import PageHeader from '../../components/PageHeader';
import Card, { CardHeader } from '../../components/ui/Card';

const DEFAULTS = { raise_pct: 0, training_pct: 0, remote_days: 0, recognition_pct: 0 };

const LEVERS = [
  { key: 'raise_pct', label: 'Augmentation salariale', min: 0, max: 8, step: 0.5, unit: '%' },
  { key: 'training_pct', label: 'Budget formation', min: 0, max: 100, step: 5, unit: '%' },
  { key: 'remote_days', label: 'Jours de télétravail / sem.', min: 0, max: 5, step: 1, unit: ' j' },
  { key: 'recognition_pct', label: 'Programme de reconnaissance', min: 0, max: 100, step: 5, unit: '%' },
];

function ResultTile({ icon: Icon, label, value, sub, accent, subColor }) {
  return (
    <Card className="p-4">
      <div className="flex items-center gap-2 text-brand-secondary/80">
        <Icon size={16} className={accent} />
        <span className="text-xs font-medium">{label}</span>
      </div>
      <div className="mt-2 text-2xl font-bold text-brand-dark">{value}</div>
      {sub && <div className={`text-xs font-medium ${subColor || 'text-brand-secondary/70'}`}>{sub}</div>}
    </Card>
  );
}

export default function Simulations() {
  const [levers, setLevers] = useState(DEFAULTS);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const touched = useMemo(() => Object.keys(DEFAULTS).some((key) => levers[key] !== DEFAULTS[key]), [levers]);

  const runSimulation = async () => {
    try {
      const payload = await api.post('/predict/simulate', {
        scenario_type: 'direction_dashboard',
        parameters: levers,
      });
      setResult({
        engagement: payload.engagement ?? 76,
        engagementGain: payload.engagement_gain ?? 0,
        turnover: payload.turnover ?? 7.4,
        savings: payload.savings ?? 0,
        cost: payload.cost ?? 0,
        net: payload.net ?? 0,
        roi: payload.roi ?? null,
        projection: payload.projection ?? ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin'].map((month) => ({ month, actuel: 76, projeté: 76 })),
      });
      setError('');
    } catch (err) {
      setError(err.message || 'Impossible de lancer la simulation.');
    }
  };

  const projection = result?.projection || ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin'].map((month) => ({ month, actuel: 76, projeté: 76 }));
  const fmt = (n) => `${Math.round(n || 0)} k€`;

  return (
    <div className="animate-fade-in-up space-y-6">
      <PageHeader title="Simulateur de scénarios" subtitle="Projetez l'impact RH et financier de vos décisions">
        <button onClick={() => { setLevers(DEFAULTS); setResult(null); }} disabled={!touched} className="inline-flex items-center gap-2 rounded-xl border border-brand-secondary/20 bg-white px-3 py-2 text-sm font-medium text-brand-dark shadow-sm disabled:opacity-40">
          <RotateCcw size={15} /> Réinitialiser
        </button>
      </PageHeader>
      {error ? <div className="rounded-xl bg-white p-4 text-sm text-brand-warning">{error}</div> : null}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardHeader title="Leviers d'action" subtitle="Ajustez et observez l'impact" icon={Sparkles} />
          <div className="space-y-6 p-5">
            {LEVERS.map((lever) => (
              <div key={lever.key}>
                <div className="mb-2 flex items-center justify-between">
                  <label className="text-sm font-medium text-brand-dark">{lever.label}</label>
                  <span className="rounded-xl bg-brand-light px-2 py-0.5 text-sm font-semibold text-brand-secondary">{levers[lever.key]}{lever.unit}</span>
                </div>
                <input type="range" min={lever.min} max={lever.max} step={lever.step} value={levers[lever.key]} onChange={(event) => setLevers({ ...levers, [lever.key]: Number(event.target.value) })} className="h-2 w-full cursor-pointer appearance-none rounded-full bg-brand-light accent-brand-secondary" />
              </div>
            ))}
            <button onClick={runSimulation} className="w-full rounded-xl bg-brand-secondary py-3 text-sm font-semibold text-white">Lancer la simulation</button>
          </div>
        </Card>

        <div className="space-y-6 lg:col-span-2">
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <ResultTile icon={Heart} accent="text-brand-secondary" label="Engagement projeté" value={`${Math.round(result?.engagement || 76)}/100`} sub={`${(result?.engagementGain || 0).toFixed(1)} pts`} subColor="text-brand-secondary" />
            <ResultTile icon={TrendingDown} accent="text-brand-secondary" label="Turnover projeté" value={`${(result?.turnover || 7.4).toFixed(1)}%`} sub="projection backend" />
            <ResultTile icon={Wallet} accent="text-brand-secondary" label="Coût annuel" value={fmt(result?.cost)} sub="investissement" />
            <ResultTile icon={PiggyBank} accent="text-purple-500" label="Bénéfice net" value={fmt(result?.net)} sub={result?.roi ? `ROI ${result.roi.toFixed(1)}x` : 'sans coût'} subColor={result?.net >= 0 ? 'text-brand-secondary' : 'text-brand-danger'} />
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
                  <Tooltip />
                  <Legend />
                  <Area type="monotone" dataKey="actuel" name="Actuel" stroke="#cbd5e1" strokeWidth={2} strokeDasharray="5 5" fill="transparent" />
                  <Area type="monotone" dataKey="projeté" name="Projeté" stroke="#8b5cf6" strokeWidth={2.5} fill="url(#proj)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
