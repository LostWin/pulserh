import { useEffect, useMemo, useState } from 'react';
import { Cpu, RefreshCw, AlertTriangle, CheckCircle, Activity } from 'lucide-react';
import { cn } from '../../lib/utils';
import { api } from '../../lib/api';

export default function SupervisionIA() {
  const [metrics, setMetrics] = useState(null);
  const [logs, setLogs] = useState([]);
  const [recalculating, setRecalculating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [recalcDone, setRecalcDone] = useState(false);
  const [period, setPeriod] = useState('7d');

  const load = async () => {
    const [metricsResponse, logsResponse] = await Promise.all([
      api.get(`/admin/metrics/ai?period=${period}`),
      api.get(`/admin/logs?period=${period}`),
    ]);
    setMetrics(metricsResponse);
    setLogs(logsResponse || []);
  };

  useEffect(() => {
    load().catch(() => {});
  }, [period]);

  const forceRecalc = async () => {
    if (recalculating) return;
    setRecalculating(true);
    setRecalcDone(false);
    setProgress(15);
    try {
      await api.post('/admin/ai/recompute');
      setProgress(100);
      setRecalcDone(true);
      await load();
    } finally {
      setRecalculating(false);
    }
  };

  const models = metrics?.models || [];
  const biasAlerts = useMemo(() => models.filter((m) => m.status === 'warning'), [models]);

  return (
    <div className="animate-fade-in-up space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-brand-dark">Supervision IA</h1>
          <p className="mt-1 text-sm text-brand-secondary/70">Monitorer les modèles prédictifs et leurs décisions en temps réel.</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="rounded-xl border border-brand-secondary/20 bg-white px-3 py-2.5 text-sm text-brand-secondary outline-none focus:border-brand-secondary"
          >
            <option value="1d">Dernières 24h</option>
            <option value="7d">Derniers 7 jours</option>
            <option value="30d">Derniers 30 jours</option>
          </select>
          <button onClick={forceRecalc} disabled={recalculating}
            className="flex items-center gap-2 rounded-xl bg-brand-secondary px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-brand-dark transition-colors disabled:opacity-70">
            <RefreshCw size={15} className={recalculating ? 'animate-spin' : ''} />
            {recalculating ? 'Recalcul…' : 'Forcer recalcul'}
          </button>
        </div>
      </div>

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

      {biasAlerts.length > 0 && (
        <div className="rounded-2xl border border-yellow-200 bg-yellow-50 px-5 py-4 flex items-start gap-3">
          <AlertTriangle size={18} className="text-yellow-600 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-yellow-800">Biais détecté au-dessus du seuil</p>
            <p className="text-xs text-yellow-700 mt-0.5">Le modèle <strong>{biasAlerts[0].name}</strong> affiche un biais de <strong>{biasAlerts[0].bias}%</strong>. Vérification recommandée.</p>
          </div>
        </div>
      )}

      {metrics && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {[
            { label: 'Total Appels', val: metrics.total_calls || 0 },
            { label: 'Taux Échec', val: `${metrics.failure_rate || 0}%` },
            { label: 'Taux Fallback', val: `${metrics.fallback_rate || 0}%` },
            { label: 'Tool Calling', val: `${metrics.tool_calling_rate || 0}%` },
            { label: 'Latence Moy.', val: `${metrics.avg_latency_ms || 0} ms` },
          ].map((k) => (
            <div key={k.label} className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm px-5 py-4">
              <div className="text-2xl font-bold text-brand-dark">{k.val}</div>
              <div className="text-xs text-brand-secondary/60 uppercase tracking-wider font-semibold mt-0.5">{k.label}</div>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {models.map((m) => (
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
            {logs.map((log, i) => (
              <tr key={`${log.employee}-${i}`} className={cn('hover:bg-brand-light/40 transition-colors', log.flagged && 'bg-brand-warning/5')}>
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
