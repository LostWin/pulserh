import { useState, useEffect, useRef } from 'react';
import {
  ToggleLeft, ToggleRight, Save, RefreshCw, Play, CheckCircle,
  AlertTriangle, Cpu, Brain, TrendingDown, Shield, BookOpen,
  ChevronDown, ChevronUp, Info
} from 'lucide-react';
import { cn } from '../lib/utils';
import { api } from '../lib/api';

// ─── Icône par module ───────────────────────────────────────────────────────
const MODULE_ICONS = {
  CHURN_RISK:       <TrendingDown size={20} className="text-red-500" />,
  ABSENTEEISM:      <Brain size={20} className="text-amber-500" />,
  SENTIMENT:        <Cpu size={20} className="text-blue-500" />,
  TRAINING_RECO:    <BookOpen size={20} className="text-emerald-500" />,
  SECURITY_ANOMALY: <Shield size={20} className="text-purple-500" />,
};

// ─── Config des champs heuristiques par module ───────────────────────────────
const HEURISTIC_FIELDS = {
  CHURN_RISK: [
    { key: 'absence_weight',     label: 'Poids Absences',               type: 'slider', min: 0, max: 1, step: 0.05 },
    { key: 'sick_leave_weight',  label: 'Poids Congés Maladie',          type: 'slider', min: 0, max: 1, step: 0.05 },
    { key: 'task_score_weight',  label: 'Poids Performance Tâches',      type: 'slider', min: 0, max: 1, step: 0.05 },
  ],
  ABSENTEEISM: [
    { key: 'rolling_window_days', label: 'Fenêtre glissante (jours)', type: 'number', min: 30, max: 180 },
    { key: 'threshold_absences', label: "Seuil d'absences (alerte)",   type: 'number', min: 1, max: 20 },
  ],
  SENTIMENT: [
    { key: 'negative_keywords', label: 'Mots-clés négatifs', type: 'tags' },
    { key: 'positive_keywords', label: 'Mots-clés positifs', type: 'tags' },
  ],
  TRAINING_RECO: [
    { key: 'max_recommendations', label: 'Nb de recommandations max',           type: 'number', min: 1, max: 10 },
    { key: 'mandatory_first',     label: 'Formations obligatoires en priorité', type: 'toggle' },
  ],
  SECURITY_ANOMALY: [
    { key: 'max_tokens_per_hour',    label: 'Tokens max / heure',          type: 'number', min: 1000, max: 500000 },
    { key: 'max_requests_per_hour',  label: 'Requêtes max / heure',        type: 'number', min: 10, max: 5000 },
    { key: 'suspicious_hours_start', label: 'Début plage suspecte (h)',     type: 'number', min: 0, max: 23 },
    { key: 'suspicious_hours_end',   label: 'Fin plage suspecte (h)',       type: 'number', min: 0, max: 23 },
  ],
};

// ─── Config des champs ML par module ─────────────────────────────────────────
const ML_FIELDS = {
  CHURN_RISK: [
    { key: 'n_estimators',  label: "Nombre d'arbres (XGBoost)", type: 'number', min: 50, max: 1000 },
    { key: 'max_depth',     label: 'Profondeur max',            type: 'number', min: 3, max: 15 },
    { key: 'class_weight',  label: 'Équilibrage des classes',   type: 'select',
      options: [{ value: 'balanced', label: 'Automatique (SMOTE)' }, { value: 'none', label: 'Non' }] },
    { key: 'shap_enabled',  label: 'Explications SHAP (XAI)',   type: 'toggle' },
  ],
  ABSENTEEISM: [
    { key: 'model_type',           label: 'Algorithme', type: 'select',
      options: [{ value: 'prophet', label: 'Prophet (Meta)' }, { value: 'poisson', label: 'Régression Poisson' }] },
    { key: 'forecast_horizon_days', label: 'Horizon de prévision (jours)', type: 'number', min: 7, max: 90 },
    { key: 'aggregate_level',      label: "Niveau d'agrégation (RGPD)", type: 'select',
      options: [{ value: 'department', label: 'Département' }, { value: 'company', label: 'Entreprise' }] },
  ],
  SENTIMENT: [
    { key: 'model_name', label: 'Modèle NLP', type: 'select',
      options: [
        { value: 'cmarkea/distilcamembert-base-sentiment', label: 'DistilCamemBERT (Rapide, FR)' },
        { value: 'nlptown/bert-base-multilingual-uncased-sentiment', label: 'BERT Multilingue' },
      ]},
    { key: 'anonymize_before_inference', label: 'Anonymisation PII obligatoire', type: 'toggle' },
    { key: 'aggregate_results',          label: 'Résultats agrégés uniquement',  type: 'toggle' },
  ],
  TRAINING_RECO: [
    { key: 'top_k',                 label: 'Top-K recommandations',         type: 'number', min: 1, max: 20 },
    { key: 'collaborative_weight',  label: 'Poids Filtrage Collaboratif',   type: 'slider', min: 0, max: 1, step: 0.1 },
    { key: 'content_weight',        label: 'Poids Contenu (Compétences)',   type: 'slider', min: 0, max: 1, step: 0.1 },
    { key: 'cold_start_strategy',   label: 'Stratégie Cold Start', type: 'select',
      options: [{ value: 'job_rules', label: 'Règles par Poste' }, { value: 'department_average', label: 'Moyenne Département' }] },
  ],
  SECURITY_ANOMALY: [
    { key: 'model_type',             label: 'Algorithme', type: 'select',
      options: [{ value: 'isolation_forest', label: 'Isolation Forest' }, { value: 'one_class_svm', label: 'One-Class SVM' }] },
    { key: 'contamination',          label: 'Taux de contamination estimé', type: 'slider', min: 0.01, max: 0.20, step: 0.01 },
    { key: 'n_estimators',           label: "Nombre d'estimateurs",          type: 'number', min: 50, max: 500 },
    { key: 'batch_interval_minutes', label: 'Intervalle batch (minutes)',    type: 'number', min: 15, max: 1440 },
  ],
};

// ─── Badge de statut d'entraînement ──────────────────────────────────────────
function TrainingBadge({ status }) {
  const map = {
    untrained: { label: 'Non entraîné', cls: 'bg-slate-100 text-slate-600 border-slate-200' },
    training:  { label: 'En cours...', cls: 'bg-amber-50 text-amber-700 border-amber-200 animate-pulse' },
    ready:     { label: 'Prêt',       cls: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
    error:     { label: 'Erreur',     cls: 'bg-red-50 text-red-700 border-red-200' },
  };
  const { label, cls } = map[status] || map.untrained;
  return (
    <span className={cn('text-xxs font-bold px-2 py-0.5 rounded-full border', cls)}>{label}</span>
  );
}

// ─── Rendu d'un champ selon son type ────────────────────────────────────────
function ParamField({ field, value, onChange }) {
  if (field.type === 'slider') {
    return (
      <div className="space-y-1">
        <div className="flex justify-between items-center">
          <label className="text-xs font-semibold text-brand-secondary/70">{field.label}</label>
          <span className="text-xs font-bold text-brand-secondary">{Number(value).toFixed(2)}</span>
        </div>
        <input
          type="range" min={field.min} max={field.max} step={field.step}
          value={value ?? field.min}
          onChange={e => onChange(parseFloat(e.target.value))}
          className="w-full accent-brand-secondary h-1.5 bg-brand-light rounded-lg appearance-none cursor-pointer"
        />
        <div className="flex justify-between text-xxs text-brand-secondary/40">
          <span>{field.min}</span><span>{field.max}</span>
        </div>
      </div>
    );
  }
  if (field.type === 'number') {
    return (
      <div className="space-y-1">
        <label className="text-xs font-semibold text-brand-secondary/70">{field.label}</label>
        <input
          type="number" min={field.min} max={field.max}
          value={value ?? field.min}
          onChange={e => onChange(parseFloat(e.target.value))}
          className="w-full bg-brand-light/50 border border-brand-secondary/15 rounded-lg px-3 py-2 text-sm text-brand-dark focus:outline-none focus:ring-1 focus:ring-brand-secondary"
        />
      </div>
    );
  }
  if (field.type === 'select') {
    return (
      <div className="space-y-1">
        <label className="text-xs font-semibold text-brand-secondary/70">{field.label}</label>
        <select
          value={value ?? field.options[0].value}
          onChange={e => onChange(e.target.value)}
          className="w-full bg-brand-light/50 border border-brand-secondary/15 rounded-lg px-3 py-2 text-sm text-brand-dark focus:outline-none focus:ring-1 focus:ring-brand-secondary"
        >
          {field.options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
      </div>
    );
  }
  if (field.type === 'toggle') {
    return (
      <div className="flex items-center justify-between py-1">
        <label className="text-xs font-semibold text-brand-secondary/70">{field.label}</label>
        <button
          onClick={() => onChange(!value)}
          className="focus:outline-none"
        >
          {value
            ? <ToggleRight size={28} className="text-brand-secondary" />
            : <ToggleLeft size={28} className="text-brand-secondary/30" />}
        </button>
      </div>
    );
  }
  if (field.type === 'tags') {
    const tags = Array.isArray(value) ? value : [];
    const [draft, setDraft] = useState('');
    return (
      <div className="space-y-1">
        <label className="text-xs font-semibold text-brand-secondary/70">{field.label}</label>
        <div className="flex flex-wrap gap-1 min-h-8 bg-brand-light/50 border border-brand-secondary/15 rounded-lg p-2">
          {tags.map((t, i) => (
            <span key={i} className="flex items-center gap-1 text-xxs bg-brand-secondary/10 text-brand-secondary px-2 py-0.5 rounded-full">
              {t}
              <button onClick={() => onChange(tags.filter((_, idx) => idx !== i))} className="hover:text-red-500">×</button>
            </span>
          ))}
          <input
            value={draft}
            onChange={e => setDraft(e.target.value)}
            onKeyDown={e => { if ((e.key === 'Enter' || e.key === ',') && draft.trim()) { onChange([...tags, draft.trim()]); setDraft(''); e.preventDefault(); }}}
            placeholder="Ajouter + Entrée"
            className="text-xs outline-none bg-transparent flex-1 min-w-16 text-brand-dark"
          />
        </div>
      </div>
    );
  }
  return null;
}

// ─── Composant principal MLModuleCard ────────────────────────────────────────
export default function MLModuleCard({ module: initialModule, onSave, onTrain }) {
  const [module, setModule] = useState(initialModule);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [training, setTraining] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const pollRef = useRef(null);

  // Sync when parent data changes (e.g. after polling)
  useEffect(() => { setModule(initialModule); }, [initialModule]);

  // Poll training status when training is in progress
  useEffect(() => {
    if (module.training_status === 'training') {
      pollRef.current = setInterval(async () => {
        try {
          const updated = await api.get(`/admin/ml/modules/${module.module_id}`);
          if (updated.training_status !== 'training') {
            setModule(updated);
            clearInterval(pollRef.current);
          }
        } catch {}
      }, 3000);
    }
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [module.training_status, module.module_id]);

  const update = (key, val) => setModule(m => ({ ...m, [key]: val }));
  const updateHeuristic = (key, val) => setModule(m => ({ ...m, heuristic_params: { ...m.heuristic_params, [key]: val } }));
  const updateML = (key, val) => setModule(m => ({ ...m, ml_params: { ...m.ml_params, [key]: val } }));

  const handleSave = async () => {
    setSaving(true);
    try {
      const saved = await api.put(`/admin/ml/modules/${module.module_id}`, {
        is_enabled: module.is_enabled,
        mode: module.mode,
        alert_threshold: module.alert_threshold,
        strict_mode: module.strict_mode,
        heuristic_params: module.heuristic_params,
        ml_params: module.ml_params,
      });
      setModule(saved);
      onSave?.(saved);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  const handleTrain = async () => {
    setTraining(true);
    try {
      await api.post(`/admin/ml/modules/${module.module_id}/train`);
      setModule(m => ({ ...m, training_status: 'training', training_error: null }));
      onTrain?.(module.module_id);
    } catch (e) {
      console.error(e);
      setModule(m => ({
        ...m,
        training_status: 'error',
        training_error: e.response?.data?.detail || e.message || 'Erreur inconnue'
      }));
    } finally {
      setTraining(false);
    }
  };

  const hFields = HEURISTIC_FIELDS[module.module_id] || [];
  const mFields = ML_FIELDS[module.module_id] || [];

  return (
    <div className={cn(
      'bg-white rounded-2xl border shadow-sm transition-all duration-200',
      module.is_enabled ? 'border-brand-secondary/15' : 'border-brand-secondary/5 opacity-60'
    )}>
      {/* ── Header ── */}
      <div className="flex items-center gap-3 p-5 cursor-pointer" onClick={() => setExpanded(e => !e)}>
        <div className="p-2 bg-brand-light/50 rounded-xl">
          {MODULE_ICONS[module.module_id] ?? <Cpu size={20} />}
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-bold text-brand-dark text-sm">{module.module_name}</p>
          <div className="flex items-center gap-2 mt-0.5 flex-wrap">
            <span className={cn(
              'text-xxs font-bold px-2 py-0.5 rounded-full border',
              module.mode === 'ml'
                ? 'bg-indigo-50 text-indigo-700 border-indigo-200'
                : 'bg-amber-50 text-amber-700 border-amber-200'
            )}>
              {module.mode === 'ml' ? 'ML' : 'Heuristique'}
            </span>
            {module.mode === 'ml' && module.module_id !== 'TRAINING_RECO' && module.module_id !== 'SENTIMENT' && <TrainingBadge status={module.training_status} />}
            {module.last_trained_at && module.mode === 'ml' && (
              <span className="text-xxs text-brand-secondary/40">
                v{module.model_version || '—'} · {new Date(module.last_trained_at).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2" onClick={e => e.stopPropagation()}>
          <button
            onClick={() => update('is_enabled', !module.is_enabled)}
            className="focus:outline-none"
            title={module.is_enabled ? 'Désactiver' : 'Activer'}
          >
            {module.is_enabled
              ? <ToggleRight size={30} className="text-brand-secondary" />
              : <ToggleLeft size={30} className="text-brand-secondary/30" />}
          </button>
          {expanded ? <ChevronUp size={16} className="text-brand-secondary/40" /> : <ChevronDown size={16} className="text-brand-secondary/40" />}
        </div>
      </div>

      {/* ── Expanded content ── */}
      {expanded && (
        <div className="px-5 pb-5 space-y-5 border-t border-brand-secondary/5 pt-4">

          {/* Mode selector */}
          <div className="space-y-1.5">
            <label className="text-xxs font-bold uppercase tracking-wider text-brand-secondary/60">Mode d'analyse</label>
            <div className="flex gap-1.5 bg-brand-light/40 rounded-xl p-1">
              {['heuristic', 'ml'].map(m => (
                <button
                  key={m}
                  onClick={() => update('mode', m)}
                  className={cn(
                    'flex-1 py-2 px-3 rounded-lg text-xs font-bold transition-all',
                    module.mode === m
                      ? 'bg-white text-brand-secondary shadow-sm'
                      : 'text-brand-secondary/50 hover:text-brand-secondary'
                  )}
                >
                  {m === 'heuristic' ? 'Heuristique' : 'Machine Learning'}
                </button>
              ))}
            </div>
          </div>

          {/* Mode-specific params */}
          {module.mode === 'heuristic' ? (
            hFields.length > 0 && (
              <div className="space-y-3 bg-amber-50/50 border border-amber-100 rounded-xl p-4">
                <p className="text-xxs font-bold uppercase tracking-wider text-amber-700/70">Paramètres heuristiques</p>
                {hFields.map(f => (
                  <ParamField
                    key={f.key} field={f}
                    value={module.heuristic_params?.[f.key]}
                    onChange={v => updateHeuristic(f.key, v)}
                  />
                ))}
              </div>
            )
          ) : (
            <div className="space-y-4">
              {/* ML Params */}
              {mFields.length > 0 && (
                <div className="space-y-3 bg-indigo-50/50 border border-indigo-100 rounded-xl p-4">
                  <p className="text-xxs font-bold uppercase tracking-wider text-indigo-700/70">Paramètres du modèle</p>
                  {mFields.map(f => (
                    <ParamField
                      key={f.key} field={f}
                      value={module.ml_params?.[f.key]}
                      onChange={v => updateML(f.key, v)}
                    />
                  ))}
                </div>
              )}

              {/* Training status + button */}
              <div className="flex items-center justify-between bg-brand-light/40 rounded-xl p-3 border border-brand-secondary/10">
                <div className="flex items-center gap-2 flex-1 min-w-0 mr-4">
                  {module.module_id !== 'TRAINING_RECO' && module.module_id !== 'SENTIMENT' && (
                    <>
                      <TrainingBadge status={module.training_status} />
                      {module.training_error && module.training_status === 'error' && (
                        <span className="text-xxs text-red-500 leading-tight whitespace-normal">{module.training_error}</span>
                      )}
                    </>
                  )}
                </div>
                {module.module_id !== 'TRAINING_RECO' && module.module_id !== 'SENTIMENT' ? (
                  <button
                    onClick={handleTrain}
                    disabled={training || module.training_status === 'training'}
                    className="flex items-center gap-1.5 text-xs font-bold bg-indigo-600 text-white hover:bg-indigo-700 px-3 py-1.5 rounded-lg transition-all disabled:opacity-50 focus:outline-none"
                  >
                    {(training || module.training_status === 'training')
                      ? <><RefreshCw size={12} className="animate-spin" />En cours...</>
                      : <><Play size={12} />Entraîner</>}
                  </button>
                ) : (
                  <span className="text-xxs text-brand-secondary/50 italic px-2">Modèle sans entraînement custom</span>
                )}
              </div>

              {module.mode === 'ml' && module.training_status !== 'ready' && module.module_id !== 'TRAINING_RECO' && module.module_id !== 'SENTIMENT' && (
                <div className="flex items-start gap-2 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-xl p-3">
                  <Info size={14} className="shrink-0 mt-0.5" />
                  <p>Le mode ML est sélectionné mais le modèle n'est pas encore entraîné. Le système utilisera le mode heuristique comme fallback jusqu'à la fin de l'entraînement.</p>
                </div>
              )}
            </div>
          )}

          {/* Common params: alert threshold + strict mode */}
          <div className="space-y-3 border-t border-brand-secondary/5 pt-4">
            <p className="text-xxs font-bold uppercase tracking-wider text-brand-secondary/60">Paramètres communs</p>
            <div className="space-y-1">
              <div className="flex justify-between">
                <label className="text-xs font-semibold text-brand-secondary/70">Seuil d'alerte</label>
                <span className="text-xs font-bold text-brand-secondary">{Math.round(module.alert_threshold * 100)}%</span>
              </div>
              <input
                type="range" min="0.3" max="0.95" step="0.05"
                value={module.alert_threshold}
                onChange={e => update('alert_threshold', parseFloat(e.target.value))}
                className="w-full accent-brand-secondary h-1.5 bg-brand-light rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xxs text-brand-secondary/40"><span>30%</span><span>95%</span></div>
            </div>
            <div className="flex items-center justify-between py-1">
              <div>
                <p className="text-xs font-semibold text-brand-dark">Mode strict</p>
                <p className="text-xxs text-brand-secondary/50">Toute décision IA nécessite une validation humaine</p>
              </div>
              <button onClick={() => update('strict_mode', !module.strict_mode)} className="focus:outline-none">
                {module.strict_mode
                  ? <ToggleRight size={28} className="text-brand-secondary" />
                  : <ToggleLeft size={28} className="text-brand-secondary/30" />}
              </button>
            </div>
          </div>

          {/* Save button */}
          <div className="flex justify-end">
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex items-center gap-2 bg-brand-secondary text-white hover:bg-brand-dark rounded-xl px-4 py-2 text-xs font-bold transition-all focus:outline-none disabled:opacity-60"
            >
              {saving ? <><RefreshCw size={12} className="animate-spin" />Sauvegarde...</> :
               saved  ? <><CheckCircle size={12} />Sauvegardé !</> :
                        <><Save size={12} />Sauvegarder</>}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
