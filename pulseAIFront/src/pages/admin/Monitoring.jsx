import { useEffect, useMemo, useState } from 'react';
import {
  Activity, Server, AlertCircle, Users, Cpu, Shield, Download, User, Database,
} from 'lucide-react';
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid,
} from 'recharts';
import { cn } from '../../lib/utils';
import { api } from '../../lib/api';
import PageHeader from '../../components/PageHeader';
import Card, { CardHeader } from '../../components/ui/Card';
import StatCard from '../../components/ui/StatCard';
import Badge from '../../components/ui/Badge';

const STATUS = {
  operational: { variant: 'success', label: 'Opérationnel' },
  degraded: { variant: 'warning', label: 'Dégradé' },
  down: { variant: 'danger', label: 'Hors ligne' },
};

const EVENT_ICON = {
  export: Download,
  security: Shield,
  ai: Cpu,
  auth: User,
  system: Database,
};

function latencyColor(ms) {
  if (ms < 100) return 'text-brand-secondary';
  if (ms < 250) return 'text-brand-warning';
  return 'text-brand-danger';
}

export default function Monitoring() {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const response = await api.get('/admin/monitoring-summary');
        setData(response);
      } catch (err) {
        setError("Impossible de charger le monitoring.");
      }
    };
    load();
  }, []);

  const allUp = useMemo(() => (data?.services || []).every((s) => s.status === 'operational'), [data]);
  const stats = data?.stats || {};

  return (
    <div className="animate-fade-in-up space-y-6">
      <PageHeader title="Monitoring système" subtitle="Santé de la plateforme en temps réel">
        <Badge variant={allUp ? 'success' : 'warning'} dot>
          {allUp ? 'Tous les systèmes opérationnels' : 'Incident en cours'}
        </Badge>
      </PageHeader>

      {error && <div className="rounded-2xl border border-brand-danger/20 bg-brand-danger/5 px-4 py-3 text-sm text-brand-danger">{error}</div>}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={Activity} label="Disponibilité (30j)" value={stats.availability_30d || 0} suffix="%" accent="emerald" />
        <StatCard icon={Server} label="Requêtes / min" value={stats.requests_per_min || 0} accent="blue" />
        <StatCard icon={AlertCircle} label="Taux d'erreur" value={stats.error_rate || 0} suffix="%" invertDelta accent="rose" />
        <StatCard icon={Users} label="Utilisateurs actifs" value={stats.active_users || 0} accent="purple" />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader title="Trafic & erreurs" subtitle="Requêtes par heure sur la journée" icon={Activity} />
          <div className="h-64 p-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data?.traffic || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="req" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#1F524B" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#1F524B" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="time" tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <YAxis tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #e2e8f0', fontSize: 12 }} />
                <Area type="monotone" dataKey="req" name="Requêtes" stroke="#1F524B" strokeWidth={2.5} fill="url(#req)" />
                <Area type="monotone" dataKey="err" name="Erreurs" stroke="#DF4931" strokeWidth={2} fill="transparent" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <CardHeader title="Services" subtitle="État des composants" icon={Server} />
          <ul className="divide-y divide-slate-100">
            {(data?.services || []).map((svc) => {
              const st = STATUS[svc.status] || STATUS.degraded;
              return (
                <li key={svc.name} className="flex items-center justify-between gap-3 px-5 py-3">
                  <div className="min-w-0">
                    <div className="truncate text-sm font-medium text-brand-dark">{svc.name}</div>
                    <div className="text-xs text-brand-secondary/70">
                      <span className={latencyColor(svc.latency)}>{svc.latency} ms</span> · uptime {svc.uptime}
                    </div>
                  </div>
                  <Badge variant={st.variant} dot>{st.label}</Badge>
                </li>
              );
            })}
          </ul>
        </Card>
      </div>

      <Card>
        <CardHeader title="Journal d'audit" subtitle="Dernières actions sur la plateforme" icon={Shield} />
        <ul className="divide-y divide-slate-100">
          {(data?.audit_events || []).map((ev, i) => {
            const Icon = EVENT_ICON[ev.type] || Activity;
            return (
              <li key={`${ev.user}-${i}`} className="flex items-center gap-4 px-5 py-3">
                <div className={cn('grid h-9 w-9 shrink-0 place-items-center rounded-xl', ev.type === 'security' ? 'bg-brand-danger/10 text-brand-danger' : 'bg-brand-light text-brand-secondary/80')}>
                  <Icon size={16} />
                </div>
                <p className="flex-1 text-sm text-brand-dark">
                  <span className="font-medium text-brand-dark">{ev.user}</span> {ev.action}
                </p>
                <span className="shrink-0 text-xs text-brand-secondary/70">{ev.time}</span>
              </li>
            );
          })}
        </ul>
      </Card>
    </div>
  );
}
