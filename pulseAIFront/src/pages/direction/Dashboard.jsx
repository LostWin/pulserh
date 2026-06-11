import { Link } from 'react-router-dom';
import {
  Heart, PiggyBank, Sparkles, Users, ShieldAlert, ArrowRight, BarChart4,
} from 'lucide-react';
import {
  ResponsiveContainer, ComposedChart, Bar, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend,
  BarChart, Cell,
} from 'recharts';
import { turnoverSaved, departments } from '../../data/mockData';
import { cn } from '../../lib/utils';
import PageHeader from '../../components/PageHeader';
import Card, { CardHeader } from '../../components/ui/Card';
import StatCard from '../../components/ui/StatCard';

const STRATEGIC_ALERTS = [
  { level: 'high', text: 'Département Ventes sous le seuil critique d\'engagement (66/100)', impact: '≈ 120 k€ de risque turnover' },
  { level: 'medium', text: 'Pic de désengagement détecté au Support', impact: '21 collaborateurs concernés' },
  { level: 'low', text: 'Objectif d\'engagement Q2 atteint (+4 pts)', impact: 'Tendance positive confirmée' },
];

const ALERT_DOT = { high: 'bg-brand-danger', medium: 'bg-brand-danger/10', low: 'bg-brand-secondary' };

function barColor(v) {
  if (v >= 75) return '#1F524B';
  if (v >= 60) return '#DF4931';
  return '#DF4931';
}

export default function DirectionDashboard() {
  const headcount = departments.reduce((s, d) => s + d.headcount, 0);
  const totalSaved = turnoverSaved.reduce((s, d) => s + d.economie, 0);

  return (
    <div className="animate-fade-in-up space-y-6">
      <PageHeader title="Vue stratégique" subtitle="Impact business du pilotage RH augmenté par l'IA" />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={Heart} label="Engagement global" value={76} suffix="/100" delta={4} accent="emerald" />
        <StatCard icon={PiggyBank} label="Turnover évité (cumul.)" value={`${totalSaved}`} suffix=" k€" delta={12} accent="blue" />
        <StatCard icon={Sparkles} label="ROI de l'IA RH" value="3.2" suffix="x" delta={8} accent="purple" />
        <StatCard icon={Users} label="Effectif total" value={headcount} delta={2} accent="amber" />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Savings */}
        <Card className="lg:col-span-2">
          <CardHeader title="Économies générées par l'IA" subtitle="Coût de turnover évité vs départs réels" icon={PiggyBank} />
          <div className="h-72 p-4">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={turnoverSaved} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="month" tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <YAxis yAxisId="left" tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <YAxis yAxisId="right" orientation="right" tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <Tooltip
                  contentStyle={{ borderRadius: 12, border: '1px solid #e2e8f0', fontSize: 12, boxShadow: '0 10px 25px -5px rgb(0 0 0 / 0.1)' }}
                  formatter={(value, name) => name === 'economie' ? [`${value} k€`, 'Économie'] : [value, 'Départs']}
                />
                <Legend formatter={(v) => v === 'economie' ? 'Économie (k€)' : 'Départs réels'} wrapperStyle={{ fontSize: 12 }} />
                <Bar yAxisId="left" dataKey="economie" fill="#3b82f6" radius={[6, 6, 0, 0]} maxBarSize={40} />
                <Line yAxisId="right" type="monotone" dataKey="depart" stroke="#f43f5e" strokeWidth={2.5} dot={{ r: 4 }} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Strategic alerts */}
        <Card>
          <CardHeader title="Alertes critiques" subtitle="Points d'attention direction" icon={ShieldAlert} />
          <div className="space-y-4 p-5">
            {STRATEGIC_ALERTS.map((a, i) => (
              <div key={i} className="flex gap-3">
                <span className={cn('mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full', ALERT_DOT[a.level])} />
                <div>
                  <p className="text-sm font-medium leading-snug text-brand-dark">{a.text}</p>
                  <p className="mt-0.5 text-xs text-brand-secondary/70">{a.impact}</p>
                </div>
              </div>
            ))}
            <Link to="/direction/alertes" className="flex items-center justify-center gap-1.5 rounded-xl py-2 text-sm font-medium text-brand-secondary hover:bg-brand-light">
              Toutes les alertes <ArrowRight size={15} />
            </Link>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Department comparison */}
        <Card className="lg:col-span-2">
          <CardHeader title="Engagement par département" subtitle="Comparatif des entités" icon={BarChart4} />
          <div className="h-72 p-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart layout="vertical" data={departments} margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
                <XAxis type="number" domain={[0, 100]} tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <YAxis type="category" dataKey="name" width={80} tickLine={false} axisLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
                <Tooltip cursor={{ fill: '#f8fafc' }} contentStyle={{ borderRadius: 12, border: '1px solid #e2e8f0', fontSize: 12 }} formatter={(v) => [`${v}/100`, 'Engagement']} />
                <Bar dataKey="engagement" radius={[0, 6, 6, 0]} maxBarSize={26}>
                  {departments.map((d) => <Cell key={d.name} fill={barColor(d.engagement)} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Simulation teaser */}
        <Link
          to="/direction/simulations"
          className="group flex flex-col justify-between rounded-xl bg-brand-secondary/90 p-6 text-white shadow-lg transition-transform hover:scale-[1.02]"
        >
          <div>
            <div className="grid h-12 w-12 place-items-center rounded-xl bg-white/10">
              <Sparkles size={24} className="text-brand-light" />
            </div>
            <h3 className="mt-4 text-lg font-bold">Simulateur de scénarios</h3>
            <p className="mt-2 text-sm text-brand-light/80">
              Projetez l'impact d'une augmentation salariale, d'un plan de formation ou d'une réorganisation sur l'engagement et le turnover.
            </p>
          </div>
          <span className="mt-6 inline-flex items-center gap-1.5 text-sm font-medium text-brand-light">
            Lancer une simulation <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" />
          </span>
        </Link>
      </div>
    </div>
  );
}
