import { useEffect, useMemo, useState } from 'react';
import { Shield, CheckCircle, XCircle, AlertTriangle, Lock, Eye, EyeOff } from 'lucide-react';
import { cn } from '../../lib/utils';
import { api } from '../../lib/api';

const LEVEL_COLORS = {
  high: { bg: '#fee2e2', color: '#b91c1c' },
  medium: { bg: '#fef9c3', color: '#854d0e' },
  low: { bg: '#dbeafe', color: '#1d4ed8' },
};

export default function Securite() {
  const [overview, setOverview] = useState(null);
  const [policy, setPolicy] = useState({ minLength: 12, requireUpper: true, requireNumber: true, requireSymbol: false, maxAge: 90 });
  const [showPolicy, setShowPolicy] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const response = await api.get('/admin/security-overview');
        setOverview(response);
        setPolicy(response.policy);
      } catch {
        setMessage("Impossible de charger l'état sécurité.");
      }
    };
    load();
  }, []);

  const checklist = overview?.checklist || [];
  const score = overview?.score || 0;
  const done = overview?.validated || 0;

  const savePolicy = async () => {
    setSaving(true);
    setMessage('');
    try {
      const response = await api.put('/admin/security-policy', policy);
      setPolicy(response);
      setMessage('Politique sauvegardée.');
    } catch {
      setMessage("Impossible d'enregistrer la politique.");
    } finally {
      setSaving(false);
    }
  };

  const scoreLabel = useMemo(() => (
    score >= 80 ? '✅ Bon niveau' : score >= 60 ? '⚠️ À améliorer' : '🔴 Critique'
  ), [score]);

  return (
    <div className="animate-fade-in-up space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-brand-dark">Sécurité</h1>
        <p className="mt-1 text-sm text-brand-secondary/70">Tableau de bord sécurité de la plateforme Pulse RH.</p>
      </div>

      {message && <div className="rounded-2xl border border-brand-secondary/15 bg-white px-4 py-3 text-sm text-brand-dark">{message}</div>}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-6 flex flex-col items-center justify-center">
          <div className="relative mb-4">
            <svg className="w-32 h-32 -rotate-90" viewBox="0 0 120 120">
              <circle cx="60" cy="60" r="50" fill="none" strokeWidth="12" className="stroke-brand-light" />
              <circle
                cx="60"
                cy="60"
                r="50"
                fill="none"
                strokeWidth="12"
                strokeLinecap="round"
                strokeDasharray={`${2 * Math.PI * 50}`}
                strokeDashoffset={`${2 * Math.PI * 50 * (1 - score / 100)}`}
                className={score >= 80 ? 'stroke-brand-secondary' : score >= 60 ? 'stroke-yellow-500' : 'stroke-brand-warning'}
                style={{ transition: 'stroke-dashoffset 0.6s ease' }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-3xl font-bold text-brand-dark">{score}%</span>
              <span className="text-[10px] text-brand-secondary/60 uppercase tracking-widest">Score</span>
            </div>
          </div>
          <p className="text-sm font-semibold text-brand-dark">{scoreLabel}</p>
          <p className="text-xs text-brand-secondary/60 mt-0.5">{done}/{overview?.total || checklist.length || 0} contrôles validés</p>
        </div>

        <div className="lg:col-span-2 rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-5">
          <h2 className="font-semibold text-brand-dark mb-4 flex items-center gap-2"><Shield size={16} className="text-brand-secondary" />Checklist de sécurité</h2>
          <div className="space-y-2">
            {checklist.map((item) => (
              <div key={item.id} className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 hover:bg-brand-light/50 transition-colors text-left">
                {item.done
                  ? <CheckCircle size={16} className="text-brand-secondary shrink-0" />
                  : <XCircle size={16} className="text-brand-secondary/25 shrink-0" />}
                <span className={cn('text-sm flex-1', item.done ? 'text-brand-dark/60 line-through' : 'text-brand-dark')}>{item.label}</span>
                {item.critical && !item.done && (
                  <span className="rounded-full bg-brand-warning/10 px-2 py-0.5 text-[10px] font-bold text-brand-warning uppercase shrink-0">Critique</span>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm overflow-hidden">
        <button onClick={() => setShowPolicy(!showPolicy)} className="flex w-full items-center justify-between px-5 py-4 hover:bg-brand-light/30 transition-colors">
          <div className="flex items-center gap-2">
            <Lock size={16} className="text-brand-secondary" />
            <h2 className="font-semibold text-brand-dark">Politique de mot de passe</h2>
          </div>
          {showPolicy ? <EyeOff size={16} className="text-brand-secondary/50" /> : <Eye size={16} className="text-brand-secondary/50" />}
        </button>
        {showPolicy && (
          <div className="px-5 pb-5 border-t border-brand-secondary/10">
            <div className="grid grid-cols-2 gap-4 mt-4 sm:grid-cols-4">
              <div>
                <label className="block text-[10px] font-semibold uppercase tracking-widest text-brand-secondary/50 mb-1.5">Longueur min.</label>
                <input type="number" value={policy.minLength} onChange={(e) => setPolicy((p) => ({ ...p, minLength: Number(e.target.value) }))}
                  className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2 text-sm outline-none focus:border-brand-secondary" />
              </div>
              <div>
                <label className="block text-[10px] font-semibold uppercase tracking-widest text-brand-secondary/50 mb-1.5">Expiration (jours)</label>
                <input type="number" value={policy.maxAge} onChange={(e) => setPolicy((p) => ({ ...p, maxAge: Number(e.target.value) }))}
                  className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2 text-sm outline-none focus:border-brand-secondary" />
              </div>
              {[{ key: 'requireUpper', label: 'Majuscule requise' }, { key: 'requireNumber', label: 'Chiffre requis' }, { key: 'requireSymbol', label: 'Symbole requis' }].map((opt) => (
                <div key={opt.key} className="flex items-center gap-2 pt-5">
                  <button onClick={() => setPolicy((p) => ({ ...p, [opt.key]: !p[opt.key] }))}
                    className={cn('h-6 w-11 rounded-full transition-colors relative', policy[opt.key] ? 'bg-brand-secondary' : 'bg-brand-secondary/20')}>
                    <span className={cn('absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform', policy[opt.key] ? 'left-5' : 'left-0.5')} />
                  </button>
                  <span className="text-xs text-brand-dark">{opt.label}</span>
                </div>
              ))}
            </div>
            <button onClick={savePolicy} disabled={saving} className="mt-4 rounded-xl bg-brand-secondary px-4 py-2 text-sm font-medium text-white hover:bg-brand-dark transition-colors disabled:opacity-70">
              {saving ? 'Sauvegarde…' : 'Sauvegarder la politique'}
            </button>
          </div>
        )}
      </div>

      <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm overflow-hidden">
        <div className="flex items-center gap-2 px-5 py-4 border-b border-brand-secondary/10">
          <AlertTriangle size={16} className="text-brand-warning" />
          <h2 className="font-semibold text-brand-dark">Connexions suspectes</h2>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-brand-light/60">
            <tr>{['Utilisateur', 'Action', 'IP', 'Heure', 'Niveau'].map((h) => (
              <th key={h} className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-widest text-brand-secondary/50">{h}</th>
            ))}</tr>
          </thead>
          <tbody className="divide-y divide-brand-secondary/5">
            {(overview?.suspicious_logs || []).map((log, i) => {
              const lc = LEVEL_COLORS[log.level] || LEVEL_COLORS.low;
              return (
                <tr key={`${log.user}-${i}`} className="hover:bg-brand-light/40 transition-colors">
                  <td className="px-5 py-3 font-medium text-brand-dark">{log.user}</td>
                  <td className="px-5 py-3 text-brand-secondary/70">{log.action}</td>
                  <td className="px-5 py-3 font-mono text-xs text-brand-secondary/60">{log.ip}</td>
                  <td className="px-5 py-3 text-brand-secondary/50 text-xs">{log.time}</td>
                  <td className="px-5 py-3">
                    <span className="rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize" style={{ backgroundColor: lc.bg, color: lc.color }}>
                      {log.level === 'high' ? 'Élevé' : log.level === 'medium' ? 'Modéré' : 'Faible'}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
