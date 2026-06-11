import { useState } from 'react';
import { Shield, CheckCircle, XCircle, AlertTriangle, Lock, Eye, EyeOff } from 'lucide-react';
import { cn } from '../../lib/utils';

const CHECKLIST = [
  { id: 1, label: 'MFA obligatoire pour Admin et RH', done: true, critical: true },
  { id: 2, label: 'Sessions expirées après 8h d\'inactivité', done: true, critical: false },
  { id: 3, label: 'Chiffrement AES-256 des données au repos', done: true, critical: true },
  { id: 4, label: 'Audit log activé sur tous les endpoints', done: true, critical: false },
  { id: 5, label: 'Certificats SSL valides (> 30 jours)', done: true, critical: true },
  { id: 6, label: 'MFA activé pour tous les collaborateurs', done: false, critical: false },
  { id: 7, label: 'Politique de mot de passe forte (12 car. min.)', done: false, critical: true },
  { id: 8, label: 'Backup quotidien des clés de chiffrement', done: false, critical: false },
];

const SUSPICIOUS_LOGS = [
  { user: 'n.petit@pulse-rh.ai', action: 'Tentative de connexion échouée (×5)', ip: '185.234.21.4', time: 'Il y a 2 h', level: 'high' },
  { user: 'inconnu@extern.io', action: 'Accès refusé — route protégée /admin', ip: '92.184.12.77', time: 'Il y a 4 h', level: 'high' },
  { user: 'a.dupont@pulse-rh.ai', action: 'Export de données hors des heures habituelles', ip: '192.168.1.45', time: 'Hier, 23:47', level: 'medium' },
  { user: 'c.laurent@pulse-rh.ai', action: 'Connexion depuis un nouvel appareil', ip: '78.192.34.11', time: 'Il y a 2 j', level: 'low' },
];

const LEVEL_COLORS = {
  high: { bg: '#fee2e2', color: '#b91c1c' },
  medium: { bg: '#fef9c3', color: '#854d0e' },
  low: { bg: '#dbeafe', color: '#1d4ed8' },
};

export default function Securite() {
  const [checklist, setChecklist] = useState(CHECKLIST);
  const [policy, setPolicy] = useState({ minLength: 12, requireUpper: true, requireNumber: true, requireSymbol: false, maxAge: 90 });
  const [showPolicy, setShowPolicy] = useState(false);

  const toggle = (id) => setChecklist((p) => p.map((c) => c.id === id ? { ...c, done: !c.done } : c));
  const done = checklist.filter((c) => c.done).length;
  const score = Math.round((done / checklist.length) * 100);

  return (
    <div className="animate-fade-in-up space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-brand-dark">Sécurité</h1>
        <p className="mt-1 text-sm text-brand-secondary/70">Tableau de bord sécurité de la plateforme Pulse RH.</p>
      </div>

      {/* Score + checklist */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Score gauge */}
        <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-6 flex flex-col items-center justify-center">
          <div className="relative mb-4">
            <svg className="w-32 h-32 -rotate-90" viewBox="0 0 120 120">
              <circle cx="60" cy="60" r="50" fill="none" strokeWidth="12" className="stroke-brand-light" />
              <circle cx="60" cy="60" r="50" fill="none" strokeWidth="12"
                strokeLinecap="round"
                strokeDasharray={`${2 * Math.PI * 50}`}
                strokeDashoffset={`${2 * Math.PI * 50 * (1 - score / 100)}`}
                className={score >= 80 ? 'stroke-brand-secondary' : score >= 60 ? 'stroke-yellow-500' : 'stroke-brand-warning'}
                style={{ transition: 'stroke-dashoffset 0.6s ease' }} />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-3xl font-bold text-brand-dark">{score}%</span>
              <span className="text-[10px] text-brand-secondary/60 uppercase tracking-widest">Score</span>
            </div>
          </div>
          <p className="text-sm font-semibold text-brand-dark">{score >= 80 ? '✅ Bon niveau' : score >= 60 ? '⚠️ À améliorer' : '🔴 Critique'}</p>
          <p className="text-xs text-brand-secondary/60 mt-0.5">{done}/{checklist.length} contrôles validés</p>
        </div>

        {/* Checklist */}
        <div className="lg:col-span-2 rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-5">
          <h2 className="font-semibold text-brand-dark mb-4 flex items-center gap-2"><Shield size={16} className="text-brand-secondary" />Checklist de sécurité</h2>
          <div className="space-y-2">
            {checklist.map((item) => (
              <button key={item.id} onClick={() => toggle(item.id)}
                className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 hover:bg-brand-light/50 transition-colors text-left">
                {item.done
                  ? <CheckCircle size={16} className="text-brand-secondary shrink-0" />
                  : <XCircle size={16} className="text-brand-secondary/25 shrink-0" />}
                <span className={cn('text-sm flex-1', item.done ? 'text-brand-dark/60 line-through' : 'text-brand-dark')}>{item.label}</span>
                {item.critical && !item.done && (
                  <span className="rounded-full bg-brand-warning/10 px-2 py-0.5 text-[10px] font-bold text-brand-warning uppercase shrink-0">Critique</span>
                )}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Password policy */}
      <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm overflow-hidden">
        <button onClick={() => setShowPolicy(!showPolicy)}
          className="flex w-full items-center justify-between px-5 py-4 hover:bg-brand-light/30 transition-colors">
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
                <input type="number" value={policy.minLength} onChange={(e) => setPolicy((p) => ({ ...p, minLength: e.target.value }))}
                  className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2 text-sm outline-none focus:border-brand-secondary" />
              </div>
              <div>
                <label className="block text-[10px] font-semibold uppercase tracking-widest text-brand-secondary/50 mb-1.5">Expiration (jours)</label>
                <input type="number" value={policy.maxAge} onChange={(e) => setPolicy((p) => ({ ...p, maxAge: e.target.value }))}
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
            <button className="mt-4 rounded-xl bg-brand-secondary px-4 py-2 text-sm font-medium text-white hover:bg-brand-dark transition-colors">
              Sauvegarder la politique
            </button>
          </div>
        )}
      </div>

      {/* Suspicious logs */}
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
            {SUSPICIOUS_LOGS.map((log, i) => {
              const lc = LEVEL_COLORS[log.level];
              return (
                <tr key={i} className="hover:bg-brand-light/40 transition-colors">
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
