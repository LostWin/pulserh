import { useState, useEffect } from 'react';
import { Search, Download, Filter, Shield, User, Database, LogIn, Upload, AlertTriangle, Eye } from 'lucide-react';
import { cn } from '../../lib/utils';
import { api } from '../../lib/api';

const AUDIT_TYPES = ['Tous', 'auth', 'export', 'security', 'ai', 'system', 'access'];

const TYPE_ICONS = { auth: LogIn, export: Upload, security: Shield, ai: Database, system: Database, access: Eye };
const TYPE_COLORS = {
  auth: { bg: '#dbeafe', color: '#1d4ed8' },
  export: { bg: '#dcfce7', color: '#15803d' },
  security: { bg: '#fee2e2', color: '#b91c1c' },
  ai: { bg: '#ede9fe', color: '#7c3aed' },
  system: { bg: '#f3f4f6', color: '#374151' },
  access: { bg: '#ffedd5', color: '#c2410c' }
};

export default function Audit() {
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('Tous');
  const [onlyCritical, setOnlyCritical] = useState(false);
  const [period, setPeriod] = useState('7d');
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const data = await api.get(`/audit?period=${period}`);
        setLogs(data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchLogs();
  }, [period]);

  const filtered = logs.filter((l) =>
    (typeFilter === 'Tous' || l.log_type === typeFilter) &&
    (!onlyCritical || l.critical) &&
    (l.user_email.toLowerCase().includes(search.toLowerCase()) || l.action.toLowerCase().includes(search.toLowerCase()))
  );

  const exportCSV = () => {
    const header = 'Utilisateur,Action,Type,IP,Date\n';
    const rows = filtered.map((l) => `"${l.user_email}","${l.action}","${l.log_type}","${l.ip_address}","${new Date(l.timestamp).toLocaleString()}"`).join('\n');
    const blob = new Blob([header + rows], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'audit_log.csv'; a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="animate-fade-in-up space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-brand-dark">Journal d'audit</h1>
          <p className="mt-1 text-sm text-brand-secondary/70">Traçabilité complète de toutes les actions effectuées sur la plateforme.</p>
        </div>
        <button onClick={exportCSV}
          className="flex items-center gap-2 rounded-xl border border-brand-secondary/20 px-4 py-2.5 text-sm font-medium text-brand-secondary hover:bg-brand-light transition-colors">
          <Download size={15} />Exporter CSV
        </button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[
          { label: 'Total', val: logs.length },
          { label: 'Critiques', val: logs.filter((l) => l.critical).length },
          { label: 'Sécurité', val: logs.filter((l) => l.log_type === 'security').length },
          { label: 'Accès', val: logs.filter((l) => l.log_type === 'access').length },
        ].map((k) => (
          <div key={k.label} className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm px-5 py-4">
            <div className="text-2xl font-bold text-brand-dark">{k.val}</div>
            <div className="text-xs text-brand-secondary/60 uppercase tracking-wider font-semibold mt-0.5">{k.label}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-secondary/50" />
          <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Rechercher utilisateur ou action…"
            className="w-full rounded-xl border border-brand-secondary/20 bg-white pl-9 pr-4 py-2.5 text-sm outline-none focus:border-brand-secondary" />
        </div>
        <div className="flex gap-1.5 flex-wrap">
          {AUDIT_TYPES.map((t) => (
            <button key={t} onClick={() => setTypeFilter(t)}
              className={cn('rounded-xl px-3 py-2 text-xs font-medium capitalize transition-colors',
                typeFilter === t ? 'bg-brand-secondary text-white' : 'bg-white border border-brand-secondary/20 text-brand-secondary/70 hover:border-brand-secondary/40')}>
              {t}
            </button>
          ))}
        </div>
        <select
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
          className="rounded-xl border border-brand-secondary/20 bg-white px-3 py-2 text-xs text-brand-secondary outline-none focus:border-brand-secondary"
        >
          <option value="1d">Dernières 24h</option>
          <option value="7d">Derniers 7 jours</option>
          <option value="30d">Derniers 30 jours</option>
        </select>
        <button onClick={() => setOnlyCritical(!onlyCritical)}
          className={cn('flex items-center gap-1.5 rounded-xl px-3 py-2 text-xs font-medium transition-colors',
            onlyCritical ? 'bg-brand-warning text-white' : 'bg-white border border-brand-secondary/20 text-brand-secondary/70 hover:border-brand-secondary/40')}>
          <AlertTriangle size={13} />Critiques seulement
        </button>
      </div>

      {/* Audit table */}
      <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-brand-light/60">
            <tr>{['Utilisateur', 'Action', 'Type', 'IP', 'Horodatage'].map((h) => (
              <th key={h} className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-widest text-brand-secondary/50">{h}</th>
            ))}</tr>
          </thead>
          <tbody className="divide-y divide-brand-secondary/5">
            {filtered.map((log) => {
              const tc = TYPE_COLORS[log.log_type] || { bg: '#f3f4f6', color: '#374151' };
              const Icon = TYPE_ICONS[log.log_type] || Database;
              return (
                <tr key={log.id} className={cn('hover:bg-brand-light/40 transition-colors', log.critical && 'bg-red-50/30')}>
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-2">
                      <div className="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-brand-secondary/10">
                        <User size={12} className="text-brand-secondary" />
                      </div>
                      <span className="font-medium text-brand-dark">{log.user_email}</span>
                      {log.critical && <AlertTriangle size={13} className="text-brand-warning shrink-0" />}
                    </div>
                  </td>
                  <td className="px-5 py-3 text-brand-secondary/70 max-w-[280px]">{log.action}</td>
                  <td className="px-5 py-3">
                    <span className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold" style={{ backgroundColor: tc.bg, color: tc.color }}>
                      <Icon size={10} />{log.log_type}
                    </span>
                  </td>
                  <td className="px-5 py-3 font-mono text-xs text-brand-secondary/60">{log.ip_address}</td>
                  <td className="px-5 py-3 text-brand-secondary/50 text-xs">{new Date(log.timestamp).toLocaleString()}</td>
                </tr>
              );
            })}
            {filtered.length === 0 && (
              <tr><td colSpan={5} className="px-5 py-12 text-center text-sm text-brand-secondary/50">Aucun événement trouvé.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
