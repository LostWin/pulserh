import { useEffect, useMemo, useState } from 'react';
import {
  Activity, Server, AlertCircle, Users, Cpu, Shield, Download, User, Database,
  ExternalLink, RefreshCw,
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
  operational: { variant: 'success', label: 'Operationnel' },
  degraded: { variant: 'warning', label: 'Degrade' },
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

function MetricBar({ label, value, max, unit, color }) {
  const pct = Math.min((value / max) * 100, 100);
  const barColor = pct > 80 ? 'bg-red-400' : pct > 60 ? 'bg-yellow-400' : (color || 'bg-brand-secondary');
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-brand-secondary/70">
        <span>{label}</span>
        <span className="font-medium text-brand-dark">{value}{unit}</span>
      </div>
      <div className="h-2 w-full rounded-full bg-slate-100">
        <div className={cn('h-2 rounded-full transition-all', barColor)} style={{ width: pct + '%' }} />
      </div>
    </div>
  );
}

export default function Monitoring() {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState(null);

  const load = async () => {
    setLoading(true);
    try {
      const response = await api.get('/admin/monitoring-summary');
      setData(response);
      setLastRefresh(new Date());
      setError('');
    } catch (err) {
      setError('Impossible de charger le monitoring.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    const interval = setInterval(load, 30000);
    return () => clearInterval(interval);
  }, []);

  const allUp = useMemo(() => (data?.services || []).every((s) => s.status === 'operational'), [data]);
  const stats = data?.stats || {};
  const system = data?.system || {};
  const grafanaUrl = data ? data['grafana_url'] : null;

  return (
    <div className="animate-fade-in-up space-y-6">
      <PageHeader title="Monitoring systeme" subtitle="Sante de la plateforme en temps reel">
        <div className="flex items-center gap-3">
          {lastRefresh && (
            <span className="text-xs text-brand-secondary/60">
              Mis a jour {lastRefresh.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={load}
            className="flex items-center gap-1.5 rounded-xl border border-slate-200 px-3 py-1.5 text-xs text-brand-secondary hover:bg-slate-50"
          >
            <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
            Actualiser
          </button>
          {grafanaUrl && (
            <button
              onClick={() => window.open(grafanaUrl, '_blank')}
              className="flex items-center gap-1.5 rounded-xl bg-brand-secondary px-3 py-1.5 text-xs text-white hover:opacity-90"
            >
              <ExternalLink size={12} />
              Ouvrir Grafana
            </button>
          )}
          <Badge variant={allUp ? 'success' : 'warning'} dot>
            {allUp ? 'Tous les systemes operationnels' : 'Incident en cours'}
          </Badge>
        </div>
      </PageHeader>

      {error && (
        <div className="rounded-2xl border border-brand-danger/20 bg-brand-danger/5 px-4 py-3 text-sm text-brand-danger">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={Activity} label="Disponibilite (30j)" value={stats.availability_30d || 0} suffix="%" accent="emerald" />
        <StatCard icon={Server} label="Requetes / min" value={stats.requests_per_min || 0} accent="blue" />
        <StatCard icon={AlertCircle} label="Taux d erreur" value={stats.error_rate || 0} suffix="%" invertDelta accent="rose" />
        <StatCard icon={Users} label="Utilisateurs actifs" value={stats.active_users || 0} accent="purple" />
      </div>

      {(system.cpu_pct > 0 || system.memory_mb > 0) && (
        <Card>
          <CardHeader title="Ressources systeme" subtitle="Metriques temps reel via Prometheus" icon={Cpu} />
          <div className="grid grid-cols-1 gap-6 p-5 sm:grid-cols-3">
            <MetricBar label="CPU" value={system.cpu_pct} max={100} unit="%" color="bg-blue-400" />
            <MetricBar label="Memoire RAM" value={Math.round(system.memory_mb)} max={8192} unit=" MB" color="bg-purple-400" />
            <MetricBar label="Disque libre" value={Math.round(system.disk_free_gb)} max={100} unit=" GB" color="bg-emerald-400" />
          </div>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader title="Trafic et erreurs" subtitle="Requetes par heure sur la journee" icon={Activity} />
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
                <Area type="monotone" dataKey="req" name="Requetes" stroke="#1F524B" strokeWidth={2.5} fill="url(#req)" />
                <Area type="monotone" dataKey="err" name="Erreurs" stroke="#DF4931" strokeWidth={2} fill="transparent" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card>
          <CardHeader title="Services" subtitle="Etat des composants" icon={Server} />
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
          {grafanaUrl && (
            <div className="border-t border-slate-100 p-4">
              <button
                onClick={() => window.open(grafanaUrl, '_blank')}
                className="flex w-full items-center justify-center gap-2 rounded-xl border border-slate-200 py-2 text-xs text-brand-secondary hover:bg-slate-50"
              >
                <ExternalLink size={12} />
                Visualisation avancee sur Grafana
              </button>
            </div>
          )}
        </Card>
      </div>

      <Card>
        <CardHeader title="Journal d audit" subtitle="Dernieres actions sur la plateforme" icon={Shield} />
        <ul className="divide-y divide-slate-100">
          {(data?.audit_events || []).map((ev, i) => {
            const Icon = EVENT_ICON[ev.type] || Activity;
            return (
              <li key={ev.user + i} className="flex items-center gap-4 px-5 py-3">
                <div className={cn('grid h-9 w-9 shrink-0 place-items-center rounded-xl',
                  ev.type === 'security' ? 'bg-brand-danger/10 text-brand-danger' : 'bg-brand-light text-brand-secondary/80')}>
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
