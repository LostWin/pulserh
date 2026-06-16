import { Link } from 'react-router-dom';
import { ArrowRight, BarChart4, Heart, PiggyBank, ShieldAlert, Sparkles, Users } from 'lucide-react';
import { ResponsiveContainer, ComposedChart, Bar, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend, BarChart, Cell } from 'recharts';

import PageHeader from '../../components/PageHeader';
import Card, { CardHeader } from '../../components/ui/Card';
import StatCard from '../../components/ui/StatCard';
import { api } from '../../lib/api';
import { useEffect, useState } from 'react';

const ALERT_DOT = { high: 'bg-brand-danger', medium: 'bg-brand-warning', low: 'bg-brand-secondary' };
const COLORS = ['#1F524B', '#DF4931', '#D97706', '#2563EB', '#7C3AED', '#0F766E'];

export default function DirectionDashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/dashboard/direction-summary')
      .then(setDashboard)
      .catch((err) => setError(err.message || 'Impossible de charger la vue direction.'));
  }, []);

  const summary = dashboard?.summary || {};
  const turnoverSaved = dashboard?.turnover_saved || [];
  const departments = dashboard?.departments || [];
  const alerts = dashboard?.alerts || [];

  return (
    <div className="animate-fade-in-up space-y-6">
      <PageHeader title="Vue stratégique" subtitle="Impact business du pilotage RH augmenté par l'IA" />
      {error ? <div className="rounded-xl bg-white p-4 text-sm text-brand-warning">{error}</div> : null}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={Heart} label="Engagement global" value={summary.global_engagement || 0} suffix="/100" accent="emerald" />
        <StatCard icon={PiggyBank} label="Turnover évité" value={summary.turnover_saved_total || 0} suffix=" k€" accent="blue" />
        <StatCard icon={Sparkles} label="ROI IA RH" value={summary.roi_ia || 0} suffix="x" accent="purple" />
        <StatCard icon={Users} label="Effectif total" value={summary.headcount || 0} accent="amber" />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader title="Économies générées par l'IA" subtitle="Coût de turnover évité vs départs réels" icon={PiggyBank} />
          <div className="h-72 p-4">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={turnoverSaved} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="month" tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <YAxis yAxisId="left" tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <YAxis yAxisId="right" orientation="right" tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <Tooltip formatter={(value, name) => name === 'economie' ? [`${value} k€`, 'Économie'] : [value, 'Départs']} />
                <Legend formatter={(value) => value === 'economie' ? 'Économie (k€)' : 'Départs réels'} />
                <Bar yAxisId="left" dataKey="economie" fill="#2563EB" radius={[6, 6, 0, 0]} maxBarSize={40} />
                <Line yAxisId="right" type="monotone" dataKey="depart" stroke="#DF4931" strokeWidth={2.5} dot={{ r: 4 }} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <CardHeader title="Alertes critiques" subtitle="Points d'attention direction" icon={ShieldAlert} />
          <div className="space-y-4 p-5">
            {alerts.map((alert, index) => (
              <div key={`${alert.text}-${index}`} className="flex gap-3">
                <span className={`mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full ${ALERT_DOT[alert.level] || ALERT_DOT.low}`} />
                <div>
                  <p className="text-sm font-medium leading-snug text-brand-dark">{alert.text}</p>
                  <p className="mt-0.5 text-xs text-brand-secondary/70">{alert.impact}</p>
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
        <Card className="lg:col-span-2">
          <CardHeader title="Engagement par département" subtitle="Comparatif des entités" icon={BarChart4} />
          <div className="h-72 p-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart layout="vertical" data={departments} margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
                <XAxis type="number" domain={[0, 100]} tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <YAxis type="category" dataKey="name" width={120} tickLine={false} axisLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
                <Tooltip formatter={(value) => [`${value}/100`, 'Engagement']} />
                <Bar dataKey="engagement" radius={[0, 6, 6, 0]} maxBarSize={26}>
                  {departments.map((department, index) => <Cell key={department.id} fill={COLORS[index % COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Link to="/direction/simulations" className="group flex flex-col justify-between rounded-xl bg-brand-secondary/90 p-6 text-white shadow-lg transition-transform hover:scale-[1.02]">
          <div>
            <div className="grid h-12 w-12 place-items-center rounded-xl bg-white/10">
              <Sparkles size={24} className="text-brand-light" />
            </div>
            <h3 className="mt-4 text-lg font-bold">Simulateur de scénarios</h3>
            <p className="mt-2 text-sm text-brand-light/80">Projetez l'impact d'une augmentation salariale, d'un plan de formation ou d'une réorganisation.</p>
          </div>
          <span className="mt-6 inline-flex items-center gap-1.5 text-sm font-medium text-brand-light">
            Lancer une simulation <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" />
          </span>
        </Link>
      </div>
    </div>
  );
}
