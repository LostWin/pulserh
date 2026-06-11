import { useState } from 'react';
import { Cpu, RefreshCw, AlertTriangle, CheckCircle, TrendingUp, Activity, Eye } from 'lucide-react';
import { cn } from '../../lib/utils';

const MODELS = [
  { id: 1, name: 'Prédiction de désengagement', accuracy: 91.4, recall: 88.2, bias: 1.2, status: 'ok', lastRun: 'Il y a 1 h' },
  { id: 2, name: 'Estimation risque de départ', accuracy: 87.6, recall: 83.1, bias: 3.8, status: 'warning', lastRun: 'Il y a 3 h' },
  { id: 3, name: 'Recommandation formation', accuracy: 79.2, recall: 75.5, bias: 0.9, status: 'ok', lastRun: 'Il y a 6 h' },
  { id: 4, name: 'Détection anomalie congés', accuracy: 94.1, recall: 91.8, bias: 0.4, status: 'ok', lastRun: 'Il y a 1 j' },
];

const AI_LOGS = [
  { employee: 'Noah Petit', type: 'Risque de départ', result: 'ÉLEVÉ (88%)', date: '11 juin, 09:14', flagged: true },
  { employee: 'Yanis Moreau', type: 'Désengagement', result: 'MODÉRÉ (54%)', date: '11 juin, 08:52', flagged: false },
  { employee: 'Adam Faure', type: 'Anomalie absences', result: 'DÉTECTÉE', date: '11 juin, 08:30', flagged: true },
  { employee: 'Chloé Martin', type: 'Désengagement', result: 'FAIBLE (73%)', date: '10 juin, 17:45', flagged: false },
  { employee: 'Lucas Bernard', type: 'Risque de départ', result: 'MODÉRÉ (61%)', date: '10 juin, 15:20', flagged: false },
  { employee: 'Emma Rossi', type: 'Recommandation', result: 'React Avancé (92%)', date: '10 juin, 14:10', flagged: false },
];

export default function SupervisionIA() {
  const [recalculating, setRecalculating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [recalcDone, setRecalcDone] = useState(false);

  const forceRecalc = () => {
    if (recalculating) return;
    setRecalculating(true); setRecalcDone(false); setProgress(0);
    const iv = setInterval(() => {
      setProgress((p) => {
        if (p >= 100) { clearInterval(iv); setRecalculating(false); setRecalcDone(true); return 100; }
        return Math.min(p + Math.random() * 15, 100);
      });
    }, 250);
  };

  const biasAlerts = MODELS.filter((m) => m.status === 'warning');

  return (
    <div className="animate-fade-in-up space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-brand-dark">Supervision IA</h1>
          <p className="mt-1 text-sm text-brand-secondary/70">Monitorer les modèles prédictifs et leurs décisions en temps réel.</p>
        </div>
        <button onClick={forceRecalc} disabled={recalculating}
          className="flex items-center gap-2 rounded-xl bg-brand-secondary px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-brand-dark transition-colors disabled:opacity-70">
          <RefreshCw size={15} className={recalculating ? 'animate-spin' : ''} />
          {recalculating ? 'Recalcul…' : 'Forcer recalcul'}
        </button>
      </div>

      {/* Recalc progress */}
      {(recalculating || recalcDone) && (
        <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-brand-dark">{recalcDone ? '✅ Recalcul terminé' : 'Recalcul des scores en cours…'}</span>
            <span className="text-sm font-bold text-brand-secondary">{Math.round(progress)}%</span>
          </div>
          <div className="h-2 rounded-full bg-brand-light overflow-hidden">
            <div className="h-full rounded-full bg-brand-secondary transition-all duration-200" style={{ width: `${progress}%` }} />
          </div>
        </div>
      )}

      {/* Bias alert */}
      {biasAlerts.length > 0 && (
        <div className="rounded-2xl border border-yellow-200 bg-yellow-50 px-5 py-4 flex items-start gap-3">
          <AlertTriangle size={18} className="text-yellow-600 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-yellow-800">Biais détecté au-dessus du seuil</p>
            <p className="text-xs text-yellow-700 mt-0.5">Le modèle <strong>"{biasAlerts[0].name}"</strong> affiche un biais de <strong>{biasAlerts[0].bias}%</strong> (seuil : 3%). Vérification recommandée.</p>
          </div>
        </div>
      )}

      {/* Models grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {MODELS.map((m) => (
          <div key={m.id} className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-5">
            <div className="flex items-start justify-between gap-2 mb-4">
              <div className="flex items-center gap-2">
                <div className="grid h-8 w-8 place-items-center rounded-xl bg-brand-secondary/10">
                  <Cpu size={15} className="text-brand-secondary" />
                </div>
                <span className="text-sm font-semibold text-brand-dark">{m.name}</span>
              </div>
              {m.status === 'ok'
                ? <CheckCircle size={16} className="text-brand-secondary shrink-0" />
                : <AlertTriangle size={16} className="text-yellow-500 shrink-0" />}
            </div>
            <div className="grid grid-cols-3 gap-3">
              {[{ label: 'Précision', val: `${m.accuracy}%` }, { label: 'Recall', val: `${m.recall}%` }, { label: 'Biais', val: `${m.bias}%` }].map((s) => (
                <div key={s.label} className="rounded-xl bg-brand-light p-3 text-center">
                  <div className="text-base font-bold text-brand-dark">{s.val}</div>
                  <div className="text-[10px] text-brand-secondary/60 uppercase tracking-wider mt-0.5">{s.label}</div>
                </div>
              ))}
            </div>
            <p className="mt-3 text-[11px] text-brand-secondary/50">Dernier calcul : {m.lastRun}</p>
          </div>
        ))}
      </div>

      {/* Decision logs */}
      <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm overflow-hidden">
        <div className="flex items-center gap-2 px-5 py-4 border-b border-brand-secondary/10">
          <Activity size={16} className="text-brand-secondary" />
          <h2 className="font-semibold text-brand-dark">Journal des décisions IA</h2>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-brand-light/60">
            <tr>{['Collaborateur', 'Type de prédiction', 'Résultat', 'Date', ''].map((h) => (
              <th key={h} className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-widest text-brand-secondary/50">{h}</th>
            ))}</tr>
          </thead>
          <tbody className="divide-y divide-brand-secondary/5">
            {AI_LOGS.map((log, i) => (
              <tr key={i} className={cn('hover:bg-brand-light/40 transition-colors', log.flagged && 'bg-brand-warning/5')}>
                <td className="px-5 py-3 font-medium text-brand-dark">{log.employee}</td>
                <td className="px-5 py-3 text-brand-secondary/70">{log.type}</td>
                <td className="px-5 py-3">
                  <span className={cn('text-sm font-semibold', log.flagged ? 'text-brand-warning' : 'text-brand-secondary')}>{log.result}</span>
                </td>
                <td className="px-5 py-3 text-brand-secondary/50 text-xs">{log.date}</td>
                <td className="px-5 py-3">
                  {log.flagged && <span className="rounded-full bg-brand-warning/15 px-2 py-0.5 text-[10px] font-bold text-brand-warning uppercase">Signalé</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
