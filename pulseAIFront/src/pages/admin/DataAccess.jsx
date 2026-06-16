import { useEffect, useMemo, useState } from 'react';
import {
  Eye, EyeOff, ShieldCheck, SlidersHorizontal, Sparkles, Save, Trash2, Plus,
} from 'lucide-react';

import PageHeader from '../../components/PageHeader';
import Card, { CardHeader } from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import { cn } from '../../lib/utils';
import { dataAccessApi } from '../../lib/dataAccessApi';

const ROLE_ORDER = ['collaborator', 'manager', 'hr', 'director', 'admin'];
const VISIBILITY_OPTIONS = [
  { value: 'visible', label: 'Visible' },
  { value: 'masked', label: 'Masqué' },
  { value: 'hidden', label: 'Caché' },
  { value: 'readonly', label: 'Lecture seule' },
];
const MASK_TYPES = [
  { value: '', label: 'Aucun' },
  { value: 'phone', label: 'Téléphone' },
  { value: 'email', label: 'Email' },
  { value: 'full', label: 'Masquage total' },
];

const SAMPLE_PAYLOADS = {
  employee: {
    id: 'emp-demo-1',
    first_name: 'Amina',
    last_name: 'Benjelloun',
    email: 'amina.benjelloun@pulse.ma',
    department: 'Finance',
    job_title: 'HR Business Partner',
    status: 'actif',
    contract_type: 'CDI',
    manager_id: 'mgr-42',
    salary: 58000,
    phone: '+212 6 12 34 56 78',
    hire_date: '03 mars 2024',
    manager_name: 'Fatima Alaoui',
    leave_balance: '24 / 30 jours',
  },
  document: {
    name: 'Contrat cadre dirigeant.pdf',
    type: 'Contrat',
    size: '1.8 Mo',
    file_path: 'minio://pulse-documents-uploaded/enc-object',
    uploaded_by: 'karim.tazi@pulse.ma',
    created_at: '2026-06-15T09:30:00Z',
    allowed_roles: ['hr', 'admin'],
    rag_enabled: true,
    rag_status: 'ready',
    rag_last_synced_at: '2026-06-15T09:35:00Z',
    rag_error: null,
    can_preview: true,
  },
  leave: {
    leave_type: 'Congés Payés',
    start_date: '2026-08-05',
    end_date: '2026-08-12',
    status: 'Approuvé',
    reason: 'Vacances familiales',
    message: 'Planifier tôt les congés aide à lisser la charge de l’équipe.',
    primary_action: 'Planifier mes congés',
    secondary_action: 'Me rappeler plus tard',
  },
  prediction: {
    employee_name: 'Amina Benjelloun',
    department: 'Finance',
    title: 'HR Business Partner',
    tenure: '18 mois',
    score: 72,
    level: 'red',
    recommendation: 'Prévoir un échange manager et revoir la charge de travail.',
    factors: [
      { label: 'Charge de travail', value: 78 },
      { label: 'Assiduité', value: 55 },
    ],
    months: [
      { month: '2026-07', projected_departures: 4, confidence: 0.88 },
      { month: '2026-08', projected_departures: 3, confidence: 0.84 },
    ],
    summary: 'Projection consolidée sur 6 mois.',
    impact_description: 'Une hausse de 5% du variable réduirait le turnover estimé.',
    projected_turnover_change: -1.5,
  },
};

const DEFAULT_CONTEXT = {
  is_self: false,
  is_manager_of_target: true,
  same_department: true,
};

const VISIBILITY_STYLES = {
  visible: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  masked: 'bg-amber-50 text-amber-700 border-amber-200',
  hidden: 'bg-rose-50 text-rose-700 border-rose-200',
  readonly: 'bg-slate-100 text-slate-700 border-slate-200',
};

function emptyDraft(resource, scope, fieldKey, role) {
  return {
    resource,
    scope,
    field_key: fieldKey || '',
    role: role || 'manager',
    visibility: 'visible',
    mask_type: '',
    description: '',
    conditions_json: null,
  };
}

function normalizeDraft(policy) {
  return {
    resource: policy.resource,
    scope: policy.scope,
    field_key: policy.field_key,
    role: policy.role,
    visibility: policy.visibility,
    mask_type: policy.mask_type || '',
    description: policy.description || '',
    conditions_json: policy.conditions_json || null,
  };
}

export default function DataAccess() {
  const [resources, setResources] = useState([]);
  const [selectedResource, setSelectedResource] = useState('employee');
  const [selectedScope, setSelectedScope] = useState('detail');
  const [policies, setPolicies] = useState([]);
  const [selectedCell, setSelectedCell] = useState(null);
  const [draft, setDraft] = useState(emptyDraft('employee', 'detail'));
  const [previewRole, setPreviewRole] = useState('manager');
  const [previewResult, setPreviewResult] = useState(null);
  const [previewContext, setPreviewContext] = useState(DEFAULT_CONTEXT);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const selectedResourceMeta = useMemo(
    () => resources.find((resource) => resource.resource === selectedResource),
    [resources, selectedResource],
  );

  const samplePayload = useMemo(() => {
    const base = SAMPLE_PAYLOADS[selectedResource] || {};
    const fields = selectedResourceMeta?.fields || [];
    return Object.fromEntries(fields.map((field) => [field, base[field] ?? null]));
  }, [selectedResource, selectedResourceMeta]);

  const customPoliciesCount = useMemo(
    () => policies.filter((policy) => policy.source === 'custom').length,
    [policies],
  );

  const coverageRate = useMemo(() => {
    if (!selectedResourceMeta?.fields?.length) return 0;
    const totalCells = selectedResourceMeta.fields.length * ROLE_ORDER.length;
    return Math.round((policies.length / totalCells) * 100);
  }, [policies, selectedResourceMeta]);

  const loadResources = async () => {
    const data = await dataAccessApi.listResources();
    setResources(data || []);
  };

  const loadPolicies = async (resource, scope) => {
    const data = await dataAccessApi.listPolicies({ resource, scope });
    setPolicies(data || []);
  };

  const loadPreview = async (resource = selectedResource, scope = selectedScope, role = previewRole, context = previewContext) => {
    const data = await dataAccessApi.preview({
      resource,
      scope,
      role,
      payload: samplePayload,
      context,
    });
    setPreviewResult(data);
  };

  useEffect(() => {
    const bootstrap = async () => {
      setLoading(true);
      setError('');
      try {
        await loadResources();
      } catch (err) {
        setError(err.message || "Impossible de charger le catalogue DAC.");
      } finally {
        setLoading(false);
      }
    };
    bootstrap();
  }, []);

  useEffect(() => {
    if (!resources.length) return;
    const current = resources.find((resource) => resource.resource === selectedResource) || resources[0];
    const scope = current.scopes.includes(selectedScope) ? selectedScope : current.scopes[0];
    setSelectedResource(current.resource);
    setSelectedScope(scope);
  }, [resources]);

  useEffect(() => {
    if (!selectedResource || !selectedScope) return;
    const run = async () => {
      setError('');
      try {
        await loadPolicies(selectedResource, selectedScope);
      } catch (err) {
        setError(err.message || "Impossible de charger les politiques DAC.");
      }
    };
    run();
  }, [selectedResource, selectedScope]);

  useEffect(() => {
    if (!selectedResourceMeta) return;
    loadPreview().catch((err) => setError(err.message || "Impossible de générer l'aperçu DAC."));
  }, [policies, previewRole, previewContext, selectedResourceMeta, selectedScope]);

  const policyByCell = useMemo(() => {
    const map = new Map();
    policies.forEach((policy) => {
      map.set(`${policy.field_key}:${policy.role}`, policy);
    });
    return map;
  }, [policies]);

  const handleSelectCell = (fieldKey, role) => {
    const policy = policyByCell.get(`${fieldKey}:${role}`);
    setSelectedCell({ fieldKey, role, policyId: policy?.source === 'custom' ? policy.id : null });
    setDraft(policy ? normalizeDraft(policy) : emptyDraft(selectedResource, selectedScope, fieldKey, role));
    setMessage('');
    setError('');
  };

  const savePolicy = async () => {
    setSaving(true);
    setError('');
    setMessage('');
    try {
      const payload = {
        ...draft,
        mask_type: draft.visibility === 'masked' ? (draft.mask_type || 'full') : null,
      };
      if (selectedCell?.policyId) {
        await dataAccessApi.updatePolicy(selectedCell.policyId, {
          visibility: payload.visibility,
          mask_type: payload.mask_type,
          description: payload.description || null,
          conditions_json: payload.conditions_json,
        });
        setMessage('Politique mise à jour.');
      } else {
        await dataAccessApi.createPolicy({
          ...payload,
          description: payload.description || null,
        });
        setMessage('Politique créée.');
      }
      await loadPolicies(selectedResource, selectedScope);
    } catch (err) {
      setError(err.message || "Impossible d'enregistrer la politique.");
    } finally {
      setSaving(false);
    }
  };

  const deletePolicy = async () => {
    if (!selectedCell?.policyId) return;
    setSaving(true);
    setError('');
    setMessage('');
    try {
      await dataAccessApi.deletePolicy(selectedCell.policyId);
      setSelectedCell(null);
      setDraft(emptyDraft(selectedResource, selectedScope));
      setMessage('Surcharge supprimée, le fallback par défaut reprend la main.');
      await loadPolicies(selectedResource, selectedScope);
    } catch (err) {
      setError(err.message || "Impossible de supprimer la politique.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="animate-fade-in-up space-y-6">
      <PageHeader title="Data Access Control" subtitle="Masquez ou exposez finement les champs visibles par rôle, même quand l’accès fonctionnel à la page est autorisé.">
        <Badge variant="success" dot>
          Backend-enforced
        </Badge>
      </PageHeader>

      {error && <div className="rounded-2xl border border-brand-danger/20 bg-brand-danger/5 px-4 py-3 text-sm text-brand-danger">{error}</div>}
      {message && <div className="rounded-2xl border border-brand-secondary/15 bg-brand-secondary/5 px-4 py-3 text-sm text-brand-secondary">{message}</div>}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="rounded-2xl border border-brand-secondary/10 bg-white p-4 shadow-sm">
          <div className="mb-1 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em] text-brand-secondary/60">
            <ShieldCheck size={14} />
            Ressource
          </div>
          <div className="text-2xl font-bold text-brand-dark">{selectedResourceMeta?.resource || '—'}</div>
        </div>
        <div className="rounded-2xl border border-brand-secondary/10 bg-white p-4 shadow-sm">
          <div className="mb-1 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em] text-brand-secondary/60">
            <SlidersHorizontal size={14} />
            Couverture
          </div>
          <div className="text-2xl font-bold text-brand-dark">{coverageRate}%</div>
          <p className="mt-1 text-xs text-brand-secondary/70">Matrice actuelle pour le scope sélectionné</p>
        </div>
        <div className="rounded-2xl border border-brand-secondary/10 bg-white p-4 shadow-sm">
          <div className="mb-1 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em] text-brand-secondary/60">
            <Sparkles size={14} />
            Overrides
          </div>
          <div className="text-2xl font-bold text-brand-dark">{customPoliciesCount}</div>
          <p className="mt-1 text-xs text-brand-secondary/70">Surcharges custom enregistrées en base</p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.5fr_1fr]">
        <Card className="overflow-hidden">
          <CardHeader
            title="Matrice de visibilité"
            subtitle="Cliquez sur une cellule pour créer ou éditer la règle du champ pour un rôle."
            icon={Eye}
            action={(
              <div className="flex flex-wrap items-center gap-2">
                <select value={selectedResource} onChange={(event) => setSelectedResource(event.target.value)} className="rounded-xl border border-brand-secondary/20 bg-white px-3 py-2 text-sm text-brand-dark outline-none focus:border-brand-secondary">
                  {resources.map((resource) => (
                    <option key={resource.resource} value={resource.resource}>{resource.resource}</option>
                  ))}
                </select>
                <select value={selectedScope} onChange={(event) => setSelectedScope(event.target.value)} className="rounded-xl border border-brand-secondary/20 bg-white px-3 py-2 text-sm text-brand-dark outline-none focus:border-brand-secondary">
                  {(selectedResourceMeta?.scopes || []).map((scope) => (
                    <option key={scope} value={scope}>{scope}</option>
                  ))}
                </select>
              </div>
            )}
          />

          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-brand-light/60">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.18em] text-brand-secondary/50">Champ</th>
                  {ROLE_ORDER.map((role) => (
                    <th key={role} className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.18em] text-brand-secondary/50">{role}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-brand-secondary/5">
                {(selectedResourceMeta?.fields || []).map((fieldKey) => (
                  <tr key={fieldKey} className="hover:bg-brand-light/30">
                    <td className="px-4 py-3 font-medium text-brand-dark">{fieldKey}</td>
                    {ROLE_ORDER.map((role) => {
                      const policy = policyByCell.get(`${fieldKey}:${role}`);
                      const visibility = policy?.visibility || 'visible';
                      const isActive = selectedCell?.fieldKey === fieldKey && selectedCell?.role === role;
                      return (
                        <td key={`${fieldKey}-${role}`} className="px-4 py-3">
                          <button
                            type="button"
                            onClick={() => handleSelectCell(fieldKey, role)}
                            className={cn(
                              'inline-flex w-full items-center justify-between rounded-xl border px-3 py-2 text-left transition-all',
                              VISIBILITY_STYLES[visibility],
                              isActive && 'ring-2 ring-brand-secondary/25',
                            )}
                          >
                            <span className="text-xs font-semibold uppercase tracking-wide">{visibility}</span>
                            <span className="text-[11px] opacity-70">{policy?.source === 'custom' ? 'custom' : 'default'}</span>
                          </button>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader
              title="Éditeur de règle"
              subtitle={selectedCell ? `${selectedCell.fieldKey} · ${selectedCell.role}` : 'Sélectionnez une cellule'}
              icon={selectedCell?.policyId ? Save : Plus}
            />
            <div className="space-y-4 p-5">
              <div className="grid grid-cols-2 gap-3">
                <label className="space-y-1 text-sm">
                  <span className="text-brand-secondary/70">Champ</span>
                  <select value={draft.field_key} onChange={(event) => setDraft((current) => ({ ...current, field_key: event.target.value }))} className="w-full rounded-xl border border-brand-secondary/20 bg-white px-3 py-2.5 outline-none focus:border-brand-secondary">
                    <option value="">Choisir…</option>
                    {(selectedResourceMeta?.fields || []).map((field) => <option key={field} value={field}>{field}</option>)}
                  </select>
                </label>
                <label className="space-y-1 text-sm">
                  <span className="text-brand-secondary/70">Rôle</span>
                  <select value={draft.role} onChange={(event) => setDraft((current) => ({ ...current, role: event.target.value }))} className="w-full rounded-xl border border-brand-secondary/20 bg-white px-3 py-2.5 outline-none focus:border-brand-secondary">
                    {ROLE_ORDER.map((role) => <option key={role} value={role}>{role}</option>)}
                  </select>
                </label>
              </div>

              <label className="space-y-1 text-sm">
                <span className="text-brand-secondary/70">Visibilité</span>
                <select value={draft.visibility} onChange={(event) => setDraft((current) => ({ ...current, visibility: event.target.value }))} className="w-full rounded-xl border border-brand-secondary/20 bg-white px-3 py-2.5 outline-none focus:border-brand-secondary">
                  {VISIBILITY_OPTIONS.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                </select>
              </label>

              <label className="space-y-1 text-sm">
                <span className="text-brand-secondary/70">Masquage</span>
                <select value={draft.mask_type} disabled={draft.visibility !== 'masked'} onChange={(event) => setDraft((current) => ({ ...current, mask_type: event.target.value }))} className="w-full rounded-xl border border-brand-secondary/20 bg-white px-3 py-2.5 outline-none disabled:cursor-not-allowed disabled:bg-slate-50 focus:border-brand-secondary">
                  {MASK_TYPES.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                </select>
              </label>

              <label className="space-y-1 text-sm">
                <span className="text-brand-secondary/70">Description admin</span>
                <textarea value={draft.description} onChange={(event) => setDraft((current) => ({ ...current, description: event.target.value }))} rows={3} className="w-full rounded-xl border border-brand-secondary/20 bg-white px-3 py-2.5 outline-none focus:border-brand-secondary" placeholder="Pourquoi ce champ est masqué pour ce rôle…" />
              </label>

              <div className="flex items-center justify-between gap-3">
                <button onClick={savePolicy} disabled={saving || !draft.field_key} className="inline-flex items-center gap-2 rounded-xl bg-brand-secondary px-4 py-2.5 text-sm font-medium text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50">
                  <Save size={15} />
                  {selectedCell?.policyId ? 'Mettre à jour' : 'Créer la règle'}
                </button>
                <button onClick={deletePolicy} disabled={saving || !selectedCell?.policyId} className="inline-flex items-center gap-2 rounded-xl border border-brand-danger/20 px-4 py-2.5 text-sm font-medium text-brand-danger transition hover:bg-brand-danger/5 disabled:cursor-not-allowed disabled:opacity-40">
                  <Trash2 size={15} />
                  Supprimer l’override
                </button>
              </div>
            </div>
          </Card>

          <Card>
            <CardHeader
              title="Preview par rôle"
              subtitle="Le rendu ci-dessous est calculé par l’API, pas par un simple masquage visuel front."
              icon={previewResult ? Eye : EyeOff}
            />
            <div className="space-y-4 p-5">
              <div className="flex flex-wrap gap-2">
                {ROLE_ORDER.map((role) => (
                  <button key={role} onClick={() => setPreviewRole(role)} className={cn('rounded-xl px-3 py-2 text-xs font-medium transition-colors', previewRole === role ? 'bg-brand-secondary text-white' : 'border border-brand-secondary/20 bg-white text-brand-secondary/70 hover:border-brand-secondary/40')}>
                    {role}
                  </button>
                ))}
              </div>

              <div className="grid grid-cols-3 gap-2 rounded-2xl bg-brand-light/60 p-3 text-xs text-brand-secondary/80">
                {[
                  ['Self', 'is_self'],
                  ['Manager direct', 'is_manager_of_target'],
                  ['Même département', 'same_department'],
                ].map(([label, key]) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => setPreviewContext((current) => ({ ...current, [key]: !current[key] }))}
                    className={cn('rounded-xl px-3 py-2 transition-colors', previewContext[key] ? 'bg-brand-secondary text-white' : 'bg-white text-brand-secondary/70')}
                  >
                    {label}
                  </button>
                ))}
              </div>

              <div className="rounded-2xl border border-brand-secondary/10 bg-slate-50">
                <div className="border-b border-brand-secondary/10 px-4 py-3 text-xs font-semibold uppercase tracking-[0.18em] text-brand-secondary/50">
                  Payload filtré
                </div>
                <div className="max-h-80 overflow-auto px-4 py-3">
                  <pre className="text-xs leading-6 text-brand-dark">{JSON.stringify(previewResult?.payload || samplePayload, null, 2)}</pre>
                </div>
              </div>

              <div className="rounded-2xl border border-brand-secondary/10 bg-white px-4 py-3">
                <div className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-brand-secondary/50">Visibilité par champ</div>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(previewResult?.field_visibility || {}).map(([field, visibility]) => (
                    <span key={field} className={cn('rounded-full border px-2.5 py-1 text-[11px] font-semibold', VISIBILITY_STYLES[visibility] || VISIBILITY_STYLES.visible)}>
                      {field}: {visibility}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
