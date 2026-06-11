import { useState } from 'react';
import { ShieldAlert, CheckCircle, Clock, ArrowUp, X } from 'lucide-react';
import { cn } from '../../lib/utils';

const INITIAL_ALERTS = [
  { id: 1, priority: 'P1', title: 'Risque de départ massif — Ventes', dept: 'Ventes', impact: '3 commerciaux clés', time: '1 h', status: 'open', detail: '3 Account Executives affichent un score d\'engagement sous 55%. Coût de remplacement estimé : 180 k€. Action immédiate recommandée.' },
  { id: 2, priority: 'P1', title: 'Non-conformité RGPD détectée', dept: 'IT', impact: 'Données de 42 employés', time: '3 h', status: 'open', detail: 'Des données personnelles non chiffrées ont été détectées dans un bucket S3 non sécurisé. Mesure corrective urgente requise.' },
  { id: 3, priority: 'P2', title: 'Dépassement budget formation', dept: 'Engineering', impact: '120% du budget Q2', time: '1 j', status: 'in_progress', detail: 'Le département Engineering a dépassé son budget formation de 20%. Validation exceptionnelle requise de la Direction.' },
  { id: 4, priority: 'P2', title: 'Turnover Ventes > 15%', dept: 'Ventes', impact: '4 départs en 60 jours', time: '2 j', status: 'in_progress', detail: 'Le taux de turnover du département Ventes atteint 15.3% sur les 60 derniers jours, soit le double de la moyenne secteur.' },
  { id: 5, priority: 'P3', title: 'Charge de travail anormale détectée', dept: 'Support', impact: '3 collaborateurs', time: '3 j', status: 'resolved', detail: 'L\'IA a détecté des patterns d\'heures supplémentaires anormaux sur 3 agents du Support. Entretiens planifiés.' },
];

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
  const [alerts, setAlerts] = useState(INITIAL_ALERTS);
  const [selected, setSelected] = useState(null);

  const resolve = (id) => setAlerts((p) => p.map((a) => a.id === id ? { ...a, status: 'resolved' } : a));
  const escalate = (id) => setAlerts((p) => p.map((a) => a.id === id ? { ...a, status: 'in_progress' } : a));

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
                  <td className="px-4 py-3 text-brand-secondary/70">{a.dept}</td>
                  <td className="px-4 py-3 text-brand-secondary/70 text-xs">{a.impact}</td>
                  <td className="px-4 py-3 text-brand-secondary/50 text-xs">Il y a {a.time}</td>
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
            <p className="text-sm text-brand-dark/80 leading-relaxed mb-5">{selected.detail}</p>
            <div className="grid grid-cols-2 gap-3 text-xs text-brand-secondary/60 mb-5">
              <div><span className="block font-semibold uppercase tracking-wider text-brand-secondary/40 mb-0.5">Département</span>{selected.dept}</div>
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
