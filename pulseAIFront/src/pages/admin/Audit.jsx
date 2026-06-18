import { useState, useEffect } from 'react';
import { Search, Download, Filter, Shield, User, Database, LogIn, Upload, AlertTriangle, Eye, Workflow, FileText, GitMerge, ChevronDown, ChevronRight } from 'lucide-react';
import { cn } from '../../lib/utils';
import { api } from '../../lib/api';

const AUDIT_TYPES = ['Tous', 'auth', 'access', 'import', 'document', 'workflow', 'hr_action', 'export', 'security', 'ai', 'system'];

const TYPE_META = {
  auth:      { bg: '#dbeafe', color: '#1d4ed8', icon: LogIn,     label: 'Auth' },
  access:    { bg: '#ffedd5', color: '#c2410c', icon: Eye,        label: 'Accès' },
  import:    { bg: '#dcfce7', color: '#15803d', icon: Upload,     label: 'Import' },
  document:  { bg: '#fce7f3', color: '#be185d', icon: FileText,  label: 'Document' },
  workflow:  { bg: '#ede9fe', color: '#7c3aed', icon: GitMerge,  label: 'Workflow' },
  hr_action: { bg: '#fef9c3', color: '#a16207', icon: User,       label: 'RH Action' },
  export:    { bg: '#cffafe', color: '#0e7490', icon: Download,   label: 'Export' },
  security:  { bg: '#fee2e2', color: '#b91c1c', icon: Shield,     label: 'Sécurité' },
  ai:        { bg: '#f3e8ff', color: '#9333ea', icon: Database,   label: 'IA' },
  system:    { bg: '#f3f4f6', color: '#374151', icon: Database,   label: 'Système' },
};

function DetailsCell({ details }) {
  const [open, setOpen] = useState(false);
  if (!details || Object.keys(details).length === 0) return <span className="text-brand-secondary/30 text-xs">—</span>;
  return (
    <div>
      <button
        onClick={() => setOpen(v => !v)}
        className="flex items-center gap-1 text-xs text-brand-secondary/60 hover:text-brand-secondary transition-colors"
      >
        {open ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
        Détails
      </button>
      {open && (
        <pre className="mt-1 max-w-xs overflow-auto rounded-lg bg-brand-light/80 p-2 text-[10px] text-brand-dark/70 font-mono leading-relaxed">
          {JSON.stringify(details, null, 2)}
        </pre>
      )}
    </div>
  );
}

export default function Audit() {
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('Tous');
  const [onlyCritical, setOnlyCritical] = useState(false);
  const [period, setPeriod] = useState('7d');
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const fetchLogs = async () => {
      try {
        const data = await api.get(`/audit?period=${period}`);
        setLogs(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, [period]);

  const filtered = logs.filter((l) =>
    (typeFilter === 'Tous' || l.log_type === typeFilter) &&
    (!onlyCritical || l.critical) &&
    ((l.user_email || '').toLowerCase().includes(search.toLowerCase()) ||
     (l.action || '').toLowerCase().includes(search.toLowerCase()))
  );

  const exportCSV = () => {
    const header = 'Utilisateur,Action,Type,IP,Date\n';
    const rows = filtered.map((l) => `"${l.user_email}","${l.action}","${l.log_type}","${l.ip_address}","${new Date(l.timestamp).toLocaleString()}"`).join('\n');
    const blob = new Blob([header + rows], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'audit_log.csv'; a.click();
    URL.revokeObjectURL(url);
  };

  // Count by type for KPIs
  const kpis = [
    { label: 'Total', val: logs.length },
    { label: 'Critiques', val: logs.filter((l) => l.critical).length },
    { label: 'Imports', val: logs.filter((l) => l.log_type === 'import').length },
    { label: 'Documents', val: logs.filter((l) => l.log_type === 'document').length },
    { label: 'Workflows', val: logs.filter((l) => l.log_type === 'workflow').length },
    { label: 'RH Actions', val: logs.filter((l) => l.log_type === 'hr_action').length },
    { label: 'Sécurité', val: logs.filter((l) => l.log_type === 'security').length },
    { label: 'Accès', val: logs.filter((l) => l.log_type === 'access').length },
  ];

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
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-8">
        {kpis.map((k) => (
          <div key={k.label} className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm px-4 py-3 text-center">
            <div className="text-xl font-bold text-brand-dark">{k.val}</div>
            <div className="text-[10px] text-brand-secondary/60 uppercase tracking-wider font-semibold mt-0.5">{k.label}</div>
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
          {AUDIT_TYPES.map((t) => {
            const meta = TYPE_META[t];
            return (
              <button key={t} onClick={() => setTypeFilter(t)}
                className={cn('rounded-xl px-3 py-2 text-xs font-medium capitalize transition-colors',
                  typeFilter === t ? 'bg-brand-secondary text-white' : 'bg-white border border-brand-secondary/20 text-brand-secondary/70 hover:border-brand-secondary/40')}>
                {meta ? meta.label : t}
              </button>
            );
          })}
        </div>
        <select
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
          className="rounded-xl border border-brand-secondary/20 bg-white px-3 py-2 text-xs text-brand-secondary outline-none focus:border-brand-secondary"
        >
          <option value="1d">Dernières 24h</option>
          <option value="7d">Derniers 7 jours</option>
          <option value="30d">Derniers 30 jours</option>
          <option value="90d">Derniers 90 jours</option>
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
            <tr>{['Utilisateur', 'Action', 'Type', 'Détails', 'IP', 'Horodatage'].map((h) => (
              <th key={h} className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-widest text-brand-secondary/50">{h}</th>
            ))}</tr>
          </thead>
          <tbody className="divide-y divide-brand-secondary/5">
            {loading && (
              <tr><td colSpan={6} className="px-5 py-12 text-center text-sm text-brand-secondary/50">Chargement…</td></tr>
            )}
            {!loading && filtered.map((log) => {
              const meta = TYPE_META[log.log_type] || { bg: '#f3f4f6', color: '#374151', icon: Database, label: log.log_type };
              const Icon = meta.icon;
              return (
                <tr key={log.id} className={cn('hover:bg-brand-light/40 transition-colors', log.critical && 'bg-red-50/30')}>
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-2">
                      <div className="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-brand-secondary/10">
                        <User size={12} className="text-brand-secondary" />
                      </div>
                      <span className="font-medium text-brand-dark text-xs">{log.user_email}</span>
                      {log.critical && <AlertTriangle size={13} className="text-brand-warning shrink-0" />}
                    </div>
                  </td>
                  <td className="px-5 py-3 text-brand-secondary/70 max-w-[240px] text-xs">{log.action}</td>
                  <td className="px-5 py-3">
                    <span className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-semibold" style={{ backgroundColor: meta.bg, color: meta.color }}>
                      <Icon size={10} />{meta.label}
                    </span>
                  </td>
                  <td className="px-5 py-3"><DetailsCell details={log.details} /></td>
                  <td className="px-5 py-3 font-mono text-xs text-brand-secondary/60">{log.ip_address}</td>
                  <td className="px-5 py-3 text-brand-secondary/50 text-xs">{new Date(log.timestamp).toLocaleString()}</td>
                </tr>
              );
            })}
            {!loading && filtered.length === 0 && (
              <tr><td colSpan={6} className="px-5 py-12 text-center text-sm text-brand-secondary/50">Aucun événement trouvé.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
