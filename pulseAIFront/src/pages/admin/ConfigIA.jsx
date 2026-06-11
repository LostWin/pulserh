import { useState } from 'react';
import { Cpu, RefreshCw, Save, History, CheckCircle } from 'lucide-react';
import { cn } from '../../lib/utils';

const MODULES = [
  { id: 'engagement', label: 'Prédiction d\'engagement', desc: 'Analyse les patterns comportementaux pour prédire l\'engagement.', enabled: true },
  { id: 'turnover', label: 'Estimation risque de départ', desc: 'Modèle de scoring du risque de départ à 90 jours.', enabled: true },
  { id: 'formation', label: 'Recommandation formation', desc: 'Suggère des formations basées sur les lacunes détectées.', enabled: true },
  { id: 'anomaly', label: 'Détection anomalie absences', desc: 'Identifie les patterns d\'absences anormaux.', enabled: false },
  { id: 'bias', label: 'Détecteur de biais algorithmique', desc: 'Surveille et signale les biais dans les prédictions IA.', enabled: true },
  { id: 'nlp', label: 'Analyse NLP des feedbacks', desc: 'Sentiment analysis sur les retours de collaborateurs.', enabled: false },
];

const HISTORY = [
  { action: 'Seuil d\'alerte modifié', old: '65%', new: '70%', user: 'admin@pulse-rh.ai', date: '11 juin, 09:30' },
  { action: 'Module "anomaly" désactivé', old: 'Actif', new: 'Inactif', user: 'admin@pulse-rh.ai', date: '10 juin, 14:15' },
  { action: 'Recalibration forcée', old: '—', new: 'Succès', user: 'admin@pulse-rh.ai', date: '8 juin, 11:02' },
  { action: 'Poids du facteur "absences" ajusté', old: '0.3', new: '0.45', user: 'i.garcia@pulse-rh.ai', date: '5 juin, 16:48' },
];

export default function ConfigIA() {
  const [modules, setModules] = useState(MODULES);
  const [config, setConfig] = useState({ alertThreshold: 70, absenceWeight: 0.45, strictMode: false });
  const [calibrating, setCalibrating] = useState(false);
  const [calibProgress, setCalibProgress] = useState(0);
  const [saved, setSaved] = useState(false);

  const toggleModule = (id) => setModules((p) => p.map((m) => m.id === id ? { ...m, enabled: !m.enabled } : m));

  const calibrate = () => {
    setCalibrating(true); setCalibProgress(0);
    const iv = setInterval(() => {
      setCalibProgress((p) => {
        if (p >= 100) { clearInterval(iv); setCalibrating(false); return 100; }
        return Math.min(p + Math.random() * 14, 100);
      });
    }, 220);
  };

  const save = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="animate-fade-in-up space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-brand-dark">Configuration IA</h1>
          <p className="mt-1 text-sm text-brand-secondary/70">Paramétrez les modèles prédictifs et ajustez les seuils d'alerte.</p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={calibrate} disabled={calibrating}
            className="flex items-center gap-2 rounded-xl border border-brand-secondary/20 px-4 py-2.5 text-sm font-medium text-brand-secondary hover:bg-brand-light transition-colors disabled:opacity-60">
            <RefreshCw size={14} className={calibrating ? 'animate-spin' : ''} />
            Recalibrer
          </button>
          <button onClick={save}
            className="flex items-center gap-2 rounded-xl bg-brand-secondary px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-brand-dark transition-colors">
            {saved ? <CheckCircle size={14} /> : <Save size={14} />}
            {saved ? 'Sauvegardé !' : 'Sauvegarder'}
          </button>
        </div>
      </div>

      {/* Calibration progress */}
      {calibrating && (
        <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-4">
          <div className="flex justify-between mb-2">
            <span className="text-sm font-medium text-brand-dark">Recalibration des modèles…</span>
            <span className="text-sm font-bold text-brand-secondary">{Math.round(calibProgress)}%</span>
          </div>
          <div className="h-2 rounded-full bg-brand-light overflow-hidden">
            <div className="h-full rounded-full bg-brand-secondary transition-all" style={{ width: `${calibProgress}%` }} />
          </div>
        </div>
      )}

      {/* Parameters */}
      <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-5">
        <h2 className="font-semibold text-brand-dark mb-5 flex items-center gap-2"><Cpu size={16} className="text-brand-secondary" />Paramètres globaux</h2>
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-widest text-brand-secondary/50 mb-2">Seuil d'alerte (%)</label>
            <input type="range" min="50" max="95" step="5" value={config.alertThreshold}
              onChange={(e) => setConfig((p) => ({ ...p, alertThreshold: Number(e.target.value) }))}
              className="w-full accent-brand-secondary" />
            <div className="flex justify-between mt-1 text-xs text-brand-secondary/50">
              <span>50%</span>
              <span className="font-bold text-brand-secondary">{config.alertThreshold}%</span>
              <span>95%</span>
            </div>
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-widest text-brand-secondary/50 mb-2">Poids absences</label>
            <input type="range" min="0.1" max="1" step="0.05" value={config.absenceWeight}
              onChange={(e) => setConfig((p) => ({ ...p, absenceWeight: Number(e.target.value) }))}
              className="w-full accent-brand-secondary" />
            <div className="flex justify-between mt-1 text-xs text-brand-secondary/50">
              <span>0.1</span>
              <span className="font-bold text-brand-secondary">{config.absenceWeight.toFixed(2)}</span>
              <span>1.0</span>
            </div>
          </div>
          <div className="flex flex-col justify-between">
            <label className="block text-xs font-semibold uppercase tracking-widest text-brand-secondary/50 mb-2">Mode strict</label>
            <div className="flex items-center gap-3">
              <button onClick={() => setConfig((p) => ({ ...p, strictMode: !p.strictMode }))}
                className={cn('h-7 w-14 rounded-full transition-colors relative', config.strictMode ? 'bg-brand-secondary' : 'bg-brand-secondary/20')}>
                <span className={cn('absolute top-0.5 h-6 w-6 rounded-full bg-white shadow transition-transform', config.strictMode ? 'left-7' : 'left-0.5')} />
              </button>
              <span className="text-sm text-brand-dark">{config.strictMode ? 'Activé' : 'Désactivé'}</span>
            </div>
            <p className="text-xs text-brand-secondary/50 mt-2">En mode strict, toute décision IA est soumise à validation humaine.</p>
          </div>
        </div>
      </div>

      {/* Module toggles */}
      <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-5">
        <h2 className="font-semibold text-brand-dark mb-4">Modules actifs</h2>
        <div className="space-y-3">
          {modules.map((m) => (
            <div key={m.id} className={cn('flex items-center gap-4 rounded-xl px-4 py-3 transition-colors', m.enabled ? 'bg-brand-light/50' : 'bg-white border border-brand-secondary/10')}>
              <button onClick={() => toggleModule(m.id)}
                className={cn('h-6 w-11 rounded-full transition-colors relative shrink-0', m.enabled ? 'bg-brand-secondary' : 'bg-brand-secondary/20')}>
                <span className={cn('absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform', m.enabled ? 'left-5' : 'left-0.5')} />
              </button>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-brand-dark">{m.label}</p>
                <p className="text-xs text-brand-secondary/60">{m.desc}</p>
              </div>
              <span className={cn('text-xs font-semibold rounded-full px-2.5 py-0.5 shrink-0',
                m.enabled ? 'bg-brand-secondary/10 text-brand-secondary' : 'bg-brand-dark/10 text-brand-dark/50')}>
                {m.enabled ? 'Actif' : 'Inactif'}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* History */}
      <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm overflow-hidden">
        <div className="flex items-center gap-2 px-5 py-4 border-b border-brand-secondary/10">
          <History size={16} className="text-brand-secondary" />
          <h2 className="font-semibold text-brand-dark">Historique des modifications</h2>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-brand-light/60">
            <tr>{['Action', 'Avant', 'Après', 'Par', 'Date'].map((h) => (
              <th key={h} className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-widest text-brand-secondary/50">{h}</th>
            ))}</tr>
          </thead>
          <tbody className="divide-y divide-brand-secondary/5">
            {HISTORY.map((h, i) => (
              <tr key={i} className="hover:bg-brand-light/40 transition-colors">
                <td className="px-5 py-3 font-medium text-brand-dark">{h.action}</td>
                <td className="px-5 py-3 font-mono text-xs text-brand-secondary/60">{h.old}</td>
                <td className="px-5 py-3 font-mono text-xs text-brand-secondary font-semibold">{h.new}</td>
                <td className="px-5 py-3 text-brand-secondary/70">{h.user}</td>
                <td className="px-5 py-3 text-brand-secondary/50 text-xs">{h.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
