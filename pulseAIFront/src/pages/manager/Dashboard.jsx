import {
  Users, Heart, AlertTriangle, CalendarClock, Bell, ArrowRight,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid,
  PieChart, Pie, Cell,
} from 'recharts';
import { employees, engagementTrend, managerAlerts } from '../../data/mockData';
import { cn, riskMeta } from '../../lib/utils';
import PageHeader from '../../components/PageHeader';
import Card, { CardHeader } from '../../components/ui/Card';
import StatCard from '../../components/ui/StatCard';
import Badge from '../../components/ui/Badge';
import Avatar from '../../components/ui/Avatar';

const ALERT_STYLES = {
  high: 'border-l-brand-danger bg-brand-danger/10',
  medium: 'border-l-brand-danger/20 bg-brand-danger/10',
  low: 'border-l-brand-secondary bg-brand-light/60',
};

const RISK_COLORS = { low: '#1F524B', medium: '#DF4931', high: '#DF4931' };

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-xl border border-brand-secondary/20 bg-white px-3 py-2 text-xs shadow-lg">
      <div className="mb-1 font-semibold text-brand-dark">{label}</div>
      {payload.map((p) => (
        <div key={p.dataKey} className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full" style={{ background: p.color }} />
          <span className="capitalize text-brand-secondary/80">{p.dataKey}</span>
          <span className="ml-auto font-semibold text-brand-dark">{p.value}%</span>
        </div>
      ))}
    </div>
  );
}

export default function ManagerDashboard() {
  const team = employees; // in a real app this would be filtered to the manager's reports
  const avgEngagement = Math.round(team.reduce((s, e) => s + e.engagement, 0) / team.length);
  const atRisk = team.filter((e) => e.risk !== 'low');
  const watchlist = [...atRisk].sort((a, b) => a.engagement - b.engagement).slice(0, 5);

  const riskCounts = team.reduce(
    (acc, e) => ({ ...acc, [e.risk]: (acc[e.risk] || 0) + 1 }), {},
  );
  const riskPie = [
    { name: 'Engagés', value: riskCounts.low || 0, key: 'low' },
    { name: 'À surveiller', value: riskCounts.medium || 0, key: 'medium' },
    { name: 'À risque', value: riskCounts.high || 0, key: 'high' },
  ];

  return (
    <div className="animate-fade-in-up space-y-6">
      <PageHeader title="Tableau de bord équipe" subtitle="Vue d'ensemble de l'engagement et des signaux faibles" />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={Users} label="Taille de l'équipe" value={team.length} accent="purple" />
        <StatCard icon={Heart} label="Engagement moyen" value={avgEngagement} suffix="/100" delta={3} accent="emerald" />
        <StatCard icon={AlertTriangle} label="Collaborateurs à risque" value={atRisk.length} delta={2} invertDelta accent="rose" />
        <StatCard icon={CalendarClock} label="Entretiens à planifier" value={3} accent="blue" />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Engagement vs risk trend */}
        <Card className="lg:col-span-2">
          <CardHeader title="Engagement & risque" subtitle="Tendance de l'équipe sur 6 mois" icon={Heart} />
          <div className="h-64 p-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={engagementTrend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="eng" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="risk" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#f43f5e" stopOpacity={0.25} />
                    <stop offset="100%" stopColor="#f43f5e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="month" tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <YAxis tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <Tooltip content={<ChartTooltip />} />
                <Area type="monotone" dataKey="engagement" stroke="#10b981" strokeWidth={2.5} fill="url(#eng)" />
                <Area type="monotone" dataKey="risque" stroke="#f43f5e" strokeWidth={2.5} fill="url(#risk)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Risk distribution */}
        <Card>
          <CardHeader title="Répartition des risques" subtitle="Effectif par niveau" icon={AlertTriangle} />
          <div className="relative h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={riskPie} dataKey="value" innerRadius={55} outerRadius={75} paddingAngle={3} startAngle={90} endAngle={-270}>
                  {riskPie.map((d) => <Cell key={d.key} fill={RISK_COLORS[d.key]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-3xl font-bold text-brand-dark">{team.length}</span>
              <span className="text-xs text-brand-secondary/80">collaborateurs</span>
            </div>
          </div>
          <div className="space-y-2 px-5 pb-5">
            {riskPie.map((d) => (
              <div key={d.key} className="flex items-center gap-2 text-sm">
                <span className="h-2.5 w-2.5 rounded-full" style={{ background: RISK_COLORS[d.key] }} />
                <span className="text-brand-secondary">{d.name}</span>
                <span className="ml-auto font-semibold text-brand-dark">{d.value}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* AI watchlist */}
        <Card className="lg:col-span-2">
          <CardHeader
            title="Collaborateurs à surveiller"
            subtitle="Signaux détectés par l'IA prédictive"
            icon={AlertTriangle}
            action={<Badge variant="danger" dot>{atRisk.length} signalés</Badge>}
          />
          <ul className="divide-y divide-slate-100">
            {watchlist.map((emp) => {
              const meta = riskMeta(emp.risk);
              return (
                <li key={emp.id} className="flex items-center gap-4 px-5 py-3.5">
                  <Avatar name={emp.name} size="md" />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="truncate font-medium text-brand-dark">{emp.name}</span>
                      <Badge variant={meta.badge}>{meta.label}</Badge>
                    </div>
                    <p className="truncate text-xs text-brand-secondary/80">{emp.signal}</p>
                  </div>
                  <div className="hidden text-right sm:block">
                    <div className={cn('text-lg font-bold', meta.text)}>{emp.engagement}</div>
                    <div className="text-xs text-brand-secondary/70">{emp.delta > 0 ? '+' : ''}{emp.delta} pts</div>
                  </div>
                  <Link
                    to="/manager/entretiens"
                    className="shrink-0 rounded-xl border border-brand-secondary/20 px-3 py-1.5 text-xs font-medium text-brand-secondary transition-colors hover:border-brand-secondary/30 hover:bg-brand-light hover:text-brand-secondary"
                  >
                    Entretien
                  </Link>
                </li>
              );
            })}
          </ul>
        </Card>

        {/* Alerts */}
        <Card>
          <CardHeader title="Alertes" subtitle="Notifications récentes" icon={Bell} />
          <div className="space-y-3 p-4">
            {managerAlerts.map((alert, i) => (
              <div key={i} className={cn('rounded-xl border-l-4 p-3', ALERT_STYLES[alert.level])}>
                <p className="text-sm font-medium text-brand-dark">{alert.text}</p>
                <p className="mt-1 text-xs text-brand-secondary/70">{alert.time}</p>
              </div>
            ))}
            <Link to="/manager/alertes" className="flex w-full items-center justify-center gap-1.5 rounded-xl py-2 text-sm font-medium text-brand-secondary transition hover:bg-brand-light">
              Voir toutes les alertes <ArrowRight size={15} />
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
