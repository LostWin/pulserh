import { useState } from 'react';
import { AlertTriangle, Info, CheckCircle, XCircle, Filter, Bell, Archive } from 'lucide-react';
import { cn } from '../../lib/utils';

const INITIAL_ALERTS = [
  { id: 1, level: 'critical', title: 'Risque de départ élevé — Noah Petit', dept: 'Ventes', time: 'Il y a 30 min', read: false, detail: 'Score d\'engagement tombé à 48/100. Baisse de 15 pts en 30 jours. Action recommandée : entretien RH urgent.' },
  { id: 2, level: 'critical', title: 'Absence non justifiée — Adam Faure', dept: 'Support', time: 'Il y a 2 h', read: false, detail: '3ème absence non justifiée ce mois. Risque disciplinaire si non réglé sous 48h.' },
  { id: 3, level: 'warning', title: '3 entretiens annuels non planifiés', dept: 'Marketing', time: 'Il y a 4 h', read: false, detail: 'Les entretiens annuels de Sofia Nguyen, Chloé Martin et Lucas Bernard n\'ont pas été planifiés. Échéance : 30 juin.' },
  { id: 4, level: 'warning', title: 'Budget formation Q3 à 87% d\'utilisation', dept: 'Tous', time: 'Hier', read: true, detail: 'Le budget formation global atteint 87% d\'utilisation à 3 mois de la fin du trimestre.' },
  { id: 5, level: 'info', title: 'Rapport d\'engagement mensuel disponible', dept: 'Tous', time: 'Il y a 2 j', read: true, detail: 'Le rapport d\'engagement de mai 2026 est disponible. Score global : 78/100, +3 pts vs avril.' },
  { id: 6, level: 'info', title: 'Mise à jour convention collective', dept: 'Engineering', time: 'Il y a 3 j', read: true, detail: 'La convention collective SYNTEC a été mise à jour. Vérifiez la conformité des contrats en cours.' },
];

const LEVEL_CONFIG = {
  critical: { label: 'Critique', bg: 'bg-brand-warning/10', border: 'border-brand-warning/30', icon: XCircle, iconColor: 'text-brand-warning', badge: { bg: '#fee2e2', color: '#b91c1c' } },
  warning: { label: 'Attention', bg: 'bg-yellow-50', border: 'border-yellow-200', icon: AlertTriangle, iconColor: 'text-yellow-600', badge: { bg: '#fef9c3', color: '#854d0e' } },
  info: { label: 'Info', bg: 'bg-brand-light/50', border: 'border-brand-secondary/10', icon: Info, iconColor: 'text-brand-secondary', badge: { bg: '#dbeafe', color: '#1d4ed8' } },
};

export default function AlertesGlobales() {
  const [alerts, setAlerts] = useState(INITIAL_ALERTS);
  const [filter, setFilter] = useState('Tous');
  const [expandedId, setExpandedId] = useState(null);

  const markRead = (id) => setAlerts((p) => p.map((a) => a.id === id ? { ...a, read: true } : a));
  const archive = (id) => setAlerts((p) => p.filter((a) => a.id !== id));
  const markAllRead = () => setAlerts((p) => p.map((a) => ({ ...a, read: true })));

  const filtered = alerts.filter((a) => filter === 'Tous' || a.level === filter.toLowerCase());
  const unread = alerts.filter((a) => !a.read).length;

  return (
    <div className="animate-fade-in-up space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-brand-dark flex items-center gap-2">
            Alertes globales
            {unread > 0 && <span className="rounded-full bg-brand-warning text-white text-xs font-bold px-2 py-0.5">{unread}</span>}
          </h1>
          <p className="mt-1 text-sm text-brand-secondary/70">Suivez les signaux critiques à traiter en priorité.</p>
        </div>
        <button onClick={markAllRead} className="flex items-center gap-2 rounded-xl border border-brand-secondary/20 px-4 py-2.5 text-sm font-medium text-brand-secondary hover:bg-brand-light transition-colors">
          <CheckCircle size={15} />Tout marquer lu
        </button>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Critiques', count: alerts.filter((a) => a.level === 'critical').length, color: 'text-brand-warning', bg: 'bg-brand-warning/10' },
          { label: 'Attention', count: alerts.filter((a) => a.level === 'warning').length, color: 'text-yellow-600', bg: 'bg-yellow-50' },
          { label: 'Info', count: alerts.filter((a) => a.level === 'info').length, color: 'text-brand-secondary', bg: 'bg-brand-secondary/10' },
        ].map((k) => (
          <div key={k.label} className={cn('rounded-2xl p-4 border border-brand-secondary/10', k.bg)}>
            <div className={cn('text-2xl font-bold', k.color)}>{k.count}</div>
            <div className="text-xs text-brand-dark/70 mt-0.5">{k.label}</div>
          </div>
        ))}
      </div>

      {/* Filter tabs */}
      <div className="flex gap-1.5">
        {['Tous', 'Critical', 'Warning', 'Info'].map((f) => (
          <button key={f} onClick={() => setFilter(f)}
            className={cn('rounded-xl px-3 py-2 text-xs font-medium transition-colors',
              filter === f ? 'bg-brand-secondary text-white' : 'bg-white border border-brand-secondary/20 text-brand-secondary/70 hover:border-brand-secondary/40')}>
            {f}
          </button>
        ))}
      </div>

      {/* Alert list */}
      <div className="space-y-3">
        {filtered.map((alert) => {
          const cfg = LEVEL_CONFIG[alert.level];
          const Icon = cfg.icon;
          const isExpanded = expandedId === alert.id;
          return (
            <div key={alert.id} className={cn('rounded-2xl border shadow-sm overflow-hidden transition-colors', cfg.bg, cfg.border, !alert.read && 'ring-1 ring-brand-secondary/20')}>
              <div className="flex items-start gap-4 px-5 py-4">
                <Icon size={18} className={cn('shrink-0 mt-0.5', cfg.iconColor)} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <p className={cn('text-sm font-semibold', alert.read ? 'text-brand-dark/70' : 'text-brand-dark')}>{alert.title}</p>
                        {!alert.read && <span className="h-2 w-2 rounded-full bg-brand-secondary shrink-0" />}
                      </div>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="rounded-full px-2 py-0.5 text-[10px] font-semibold" style={{ backgroundColor: cfg.badge.bg, color: cfg.badge.color }}>{cfg.label}</span>
                        <span className="text-[11px] text-brand-secondary/50">{alert.dept} · {alert.time}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-1 shrink-0">
                      <button onClick={() => setExpandedId(isExpanded ? null : alert.id)}
                        className="rounded-lg px-2.5 py-1 text-xs font-medium text-brand-secondary border border-brand-secondary/20 hover:bg-white transition-colors">
                        {isExpanded ? 'Réduire' : 'Détail'}
                      </button>
                      <button onClick={() => markRead(alert.id)} className="grid h-7 w-7 place-items-center rounded-lg hover:bg-white text-brand-secondary/50 hover:text-brand-secondary transition-colors" title="Marquer lu"><CheckCircle size={14} /></button>
                      <button onClick={() => archive(alert.id)} className="grid h-7 w-7 place-items-center rounded-lg hover:bg-white text-brand-secondary/50 hover:text-brand-secondary transition-colors" title="Archiver"><Archive size={14} /></button>
                    </div>
                  </div>
                  {isExpanded && (
                    <div className="mt-3 rounded-xl bg-white/70 border border-brand-secondary/10 px-4 py-3 text-sm text-brand-dark/80 leading-relaxed">
                      {alert.detail}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
        {filtered.length === 0 && (
          <div className="rounded-2xl bg-white border border-brand-secondary/10 py-16 text-center">
            <Bell size={32} className="mx-auto text-brand-secondary/20 mb-3" />
            <p className="text-sm text-brand-secondary/50">Aucune alerte dans cette catégorie.</p>
          </div>
        )}
      </div>
    </div>
  );
}
