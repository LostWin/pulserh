import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, Heart, TrendingDown, ShieldAlert, ArrowRight, Download } from 'lucide-react';
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Cell,
  PieChart, Pie,
} from 'recharts';
import { engagementBar } from '../../lib/utils';
import { api } from '../../lib/api';
import PageHeader from '../../components/PageHeader';
import Card, { CardHeader } from '../../components/ui/Card';
import StatCard from '../../components/ui/StatCard';
import Badge from '../../components/ui/Badge';
import ProgressBar from '../../components/ui/ProgressBar';

const DEPT_COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#f43f5e', '#64748b'];

function barColor(v) {
  if (v >= 75) return '#10b981';
  if (v >= 60) return '#f59e0b';
  return '#f43f5e';
}

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-xl border border-brand-secondary/20 bg-white px-3 py-2 text-xs shadow-lg">
      <div className="font-semibold text-brand-dark">{label}</div>
      <div className="text-brand-secondary/80">Engagement : <span className="font-semibold text-brand-dark">{payload[0].value}/100</span></div>
    </div>
  );
}

export default function RhDashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;

    const loadDashboard = async () => {
      try {
        setLoading(true);
        setError('');
        const data = await api.get('/dashboard/rh-summary');
        if (mounted) setDashboard(data);
      } catch (err) {
        console.error(err);
        if (mounted) setError(err.message || "Impossible de charger le dashboard RH.");
      } finally {
        if (mounted) setLoading(false);
      }
    };

    loadDashboard();
    return () => {
      mounted = false;
    };
  }, []);

  const departments = useMemo(() => dashboard?.departments || [], [dashboard]);
  const headcount = dashboard?.summary?.headcount || 0;
  const globalEngagement = dashboard?.summary?.global_engagement || 0;
  const activeRisks = dashboard?.summary?.active_risks || 0;
  const turnoverPredicted = dashboard?.summary?.turnover_predicted || 0;

  return (
    <div className="animate-fade-in-up space-y-6">
      <PageHeader title="Pilotage RH" subtitle="Vue consolidée de l'engagement à l'échelle de l'entreprise">
        <button className="inline-flex items-center gap-2 rounded-xl border border-brand-secondary/20 bg-white px-3 py-2 text-sm font-medium text-brand-dark shadow-sm transition-colors hover:bg-brand-light">
          <Download size={16} /> Exporter
        </button>
      </PageHeader>

      {error && (
        <div className="rounded-2xl border border-brand-warning/20 bg-brand-warning/10 px-4 py-3 text-sm font-medium text-brand-warning">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={Users} label="Effectif total" value={headcount} delta={2} accent="blue" />
        <StatCard icon={Heart} label="Engagement global" value={globalEngagement} suffix="/100" delta={4} accent="emerald" />
        <StatCard icon={TrendingDown} label="Turnover prédit" value={turnoverPredicted} suffix="%" delta={1} invertDelta accent="amber" />
        <StatCard icon={ShieldAlert} label="Risques actifs" value={activeRisks} delta={3} invertDelta accent="rose" />
      </div>

      {loading && (
        <div className="rounded-2xl border border-brand-secondary/15 bg-white px-4 py-3 text-sm text-brand-secondary/70 shadow-sm">
          Chargement des indicateurs RH...
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Engagement by department */}
        <Card className="lg:col-span-2">
          <CardHeader title="Engagement par département" subtitle="Score moyen sur 100" icon={Heart} />
          <div className="h-72 p-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={departments} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <YAxis domain={[0, 100]} tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <Tooltip cursor={{ fill: '#f8fafc' }} content={<ChartTooltip />} />
                <Bar dataKey="engagement" radius={[6, 6, 0, 0]} maxBarSize={48}>
                  {departments.map((d) => <Cell key={d.name} fill={barColor(d.engagement)} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Headcount distribution */}
        <Card>
          <CardHeader title="Répartition de l'effectif" subtitle="Par département" icon={Users} />
          <div className="relative h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={departments} dataKey="headcount" nameKey="name" innerRadius={50} outerRadius={75} paddingAngle={2}>
                  {departments.map((d, i) => <Cell key={d.name} fill={DEPT_COLORS[i % DEPT_COLORS.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-3xl font-bold text-brand-dark">{headcount}</span>
              <span className="text-xs text-brand-secondary/80">employés</span>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2 px-5 pb-5 text-sm">
            {departments.map((d, i) => (
              <div key={d.name} className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ background: DEPT_COLORS[i % DEPT_COLORS.length] }} />
                <span className="truncate text-brand-secondary">{d.name}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Department detail */}
      <Card>
        <CardHeader
          title="Détail par département"
          subtitle="Effectif, engagement et niveau de risque"
          icon={Users}
          action={(
            <Link to="/rh/employes" className="inline-flex items-center gap-1 text-sm font-medium text-brand-secondary hover:underline">
              Voir les employés <ArrowRight size={15} />
            </Link>
          )}
        />
        <div className="divide-y divide-slate-100">
          {departments.map((d) => (
            <div key={d.name} className="grid grid-cols-12 items-center gap-4 px-5 py-3.5">
              <div className="col-span-4 sm:col-span-3">
                <div className="font-medium text-brand-dark">{d.name}</div>
                <div className="text-xs text-brand-secondary/70">{d.headcount} personnes</div>
              </div>
              <div className="col-span-5 sm:col-span-6">
                <ProgressBar value={d.engagement} barClassName={engagementBar(d.engagement)} showLabel />
              </div>
              <div className="col-span-3 flex justify-end">
                <Badge variant={d.risk > 20 ? 'danger' : d.risk > 12 ? 'warning' : 'success'} dot>
                  {d.risk}% risque
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
