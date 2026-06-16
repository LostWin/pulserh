import { useState } from 'react';
import { CheckCircle, ArrowUp, X } from 'lucide-react';
import { cn } from '../../lib/utils';
import { useNotifications } from '../../hooks/useNotifications';

const PRIORITY_CONFIG = {
  P1: { label: 'Critique', bg: '#fee2e2', color: '#b91c1c', border: 'border-red-200', row: 'bg-red-50/40' },
  P2: { label: 'Élevé', bg: '#fef9c3', color: '#854d0e', border: 'border-yellow-200', row: 'bg-yellow-50/20' },
  P3: { label: 'Modéré', bg: '#dbeafe', color: '#1d4ed8', border: '', row: '' },
};
const STATUS_CONFIG = {
  open: { label: 'Ouvert', bg: 'bg-brand-warning/10 text-brand-warning' },
  in_progress: { label: 'En cours', bg: 'bg-blue-50 text-blue-700' },
  resolved: { label: 'Résolu', bg: 'bg-brand-secondary/10 text-brand-secondary' },
};

export default function AlertesCritiques() {
  const { notifications, updateNotification, markAsRead } = useNotifications();
  const [selected, setSelected] = useState(null);

  const alerts = notifications;

  const resolve = (id) => {
    updateNotification(id, { status: 'resolved', read: true });
    markAsRead(id);
    if (selected?.id === id) {
      setSelected((current) => current ? { ...current, status: 'resolved', read: true } : current);
    }
  };

  const escalate = (id) => {
    updateNotification(id, { status: 'in_progress', read: true });
    markAsRead(id);
    if (selected?.id === id) {
      setSelected((current) => current ? { ...current, status: 'in_progress', read: true } : current);
    }
  };

  const open = alerts.filter((a) => a.status === 'open').length;
  const inProgress = alerts.filter((a) => a.status === 'in_progress').length;
  const resolved = alerts.filter((a) => a.status === 'resolved').length;

  return (
    <div className="animate-fade-in-up space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-brand-dark flex items-center gap-2">
          Alertes critiques
          {open > 0 && <span className="rounded-full bg-brand-warning text-white text-xs font-bold px-2 py-0.5">{open}</span>}
        </h1>
        <p className="mt-1 text-sm text-brand-secondary/70">Situations nécessitant une décision au niveau Direction.</p>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Alertes ouvertes', val: open, color: 'text-brand-warning', bg: 'bg-brand-warning/10' },
          { label: 'En traitement', val: inProgress, color: 'text-blue-600', bg: 'bg-blue-50' },
          { label: 'Résolues', val: resolved, color: 'text-brand-secondary', bg: 'bg-brand-secondary/10' },
        ].map((k) => (
          <div key={k.label} className={cn('rounded-2xl p-5 border border-brand-secondary/10', k.bg)}>
            <div className={cn('text-3xl font-bold', k.color)}>{k.val}</div>
            <div className="text-xs text-brand-dark/60 mt-1">{k.label}</div>
          </div>
        ))}
      </div>

      {/* Alerts table */}
      <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-brand-light/60">
            <tr>{['Priorité', 'Alerte', 'Département', 'Impact', 'Depuis', 'Statut', 'Actions'].map((h) => (
              <th key={h} className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-widest text-brand-secondary/50">{h}</th>
            ))}</tr>
          </thead>
          <tbody className="divide-y divide-brand-secondary/5">
            {alerts.map((a) => {
              const pc = PRIORITY_CONFIG[a.priority];
              const sc = STATUS_CONFIG[a.status];
              return (
                <tr key={a.id} className={cn('hover:bg-brand-light/30 transition-colors', pc.row)}>
                  <td className="px-4 py-3">
                    <span className="rounded-full px-2.5 py-1 text-xs font-bold" style={{ backgroundColor: pc.bg, color: pc.color }}>{a.priority}</span>
                  </td>
                  <td className="px-4 py-3 font-semibold text-brand-dark max-w-[220px]">
                    <button onClick={() => setSelected(a)} className="hover:underline text-left">{a.title}</button>
                  </td>
                  <td className="px-4 py-3 text-brand-secondary/70">{a.department}</td>
                  <td className="px-4 py-3 text-brand-secondary/70 text-xs">{a.impact}</td>
                  <td className="px-4 py-3 text-brand-secondary/50 text-xs">{a.time}</td>
                  <td className="px-4 py-3">
                    <span className={cn('rounded-full px-2.5 py-1 text-xs font-medium', sc.bg)}>{sc.label}</span>
                  </td>
                  <td className="px-4 py-3">
                    {a.status !== 'resolved' && (
                      <div className="flex items-center gap-1">
                        <button onClick={() => escalate(a.id)} className="flex items-center gap-1 rounded-lg border border-brand-secondary/20 px-2 py-1 text-[11px] font-medium text-brand-secondary hover:bg-brand-light transition-colors">
                          <ArrowUp size={11} />Escalader
                        </button>
                        <button onClick={() => resolve(a.id)} className="flex items-center gap-1 rounded-lg bg-brand-secondary/10 px-2 py-1 text-[11px] font-medium text-brand-secondary hover:bg-brand-secondary hover:text-white transition-colors">
                          <CheckCircle size={11} />Résoudre
                        </button>
                      </div>
                    )}
                    {a.status === 'resolved' && <span className="text-xs text-brand-secondary/40">—</span>}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Detail modal */}
      {selected && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" onClick={() => setSelected(null)}>
          <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl m-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-start justify-between gap-3 mb-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="rounded-full px-2.5 py-0.5 text-xs font-bold"
                    style={{ backgroundColor: PRIORITY_CONFIG[selected.priority].bg, color: PRIORITY_CONFIG[selected.priority].color }}>
                    {selected.priority}
                  </span>
                  <span className={cn('rounded-full px-2.5 py-0.5 text-xs font-medium', STATUS_CONFIG[selected.status].bg)}>
                    {STATUS_CONFIG[selected.status].label}
                  </span>
                </div>
                <h2 className="text-lg font-bold text-brand-dark">{selected.title}</h2>
              </div>
              <button onClick={() => setSelected(null)} className="grid h-8 w-8 place-items-center rounded-lg hover:bg-brand-light text-brand-secondary/60 shrink-0"><X size={16} /></button>
            </div>
            <p className="text-sm text-brand-dark/80 leading-relaxed mb-5">{selected.message}</p>
            <div className="grid grid-cols-2 gap-3 text-xs text-brand-secondary/60 mb-5">
              <div><span className="block font-semibold uppercase tracking-wider text-brand-secondary/40 mb-0.5">Département</span>{selected.department}</div>
              <div><span className="block font-semibold uppercase tracking-wider text-brand-secondary/40 mb-0.5">Impact</span>{selected.impact}</div>
            </div>
            {selected.status !== 'resolved' && (
              <div className="flex gap-3">
                <button onClick={() => { escalate(selected.id); setSelected(null); }}
                  className="flex-1 rounded-xl border border-brand-secondary/20 py-2.5 text-sm font-medium text-brand-secondary hover:bg-brand-light transition-colors flex items-center justify-center gap-2">
                  <ArrowUp size={14} />Escalader
                </button>
                <button onClick={() => { resolve(selected.id); setSelected(null); }}
                  className="flex-1 rounded-xl bg-brand-secondary py-2.5 text-sm font-medium text-white hover:bg-brand-dark transition-colors flex items-center justify-center gap-2">
                  <CheckCircle size={14} />Résoudre
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
