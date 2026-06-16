import { useEffect, useMemo, useState } from 'react';
import { Brain, Lightbulb, ChevronRight } from 'lucide-react';

import { api } from '../../lib/api';
import { cn, riskMeta } from '../../lib/utils';
import PageHeader from '../../components/PageHeader';
import Card, { CardHeader } from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import Avatar from '../../components/ui/Avatar';
import FieldVisibilityBadge from '../../components/ui/FieldVisibilityBadge';

function factorColor(value) {
  if (value >= 60) return 'bg-brand-danger';
  if (value >= 35) return 'bg-brand-danger/10';
  return 'bg-brand-secondary';
}

export default function Predictions() {
  const [dashboard, setDashboard] = useState(null);
  const [detail, setDetail] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        const data = await api.get('/dashboard/manager-summary');
        if (mounted) setDashboard(data);
      } catch (err) {
        if (mounted) setError(err.message || 'Impossible de charger les prédictions.');
      }
    };
    load();
    return () => {
      mounted = false;
    };
  }, []);

  const ranked = useMemo(() => [...(dashboard?.team || [])].sort((left, right) => right.risk_score - left.risk_score), [dashboard]);
  const [selectedId, setSelectedId] = useState(null);

  useEffect(() => {
    if (!selectedId && ranked[0]?.id) {
      setSelectedId(ranked[0].id);
    }
  }, [ranked, selectedId]);

  const selected = ranked.find((employee) => employee.id === selectedId) || ranked[0];
  const enrichedSelected = detail && selected && detail.employee_id === selected.id
    ? {
      ...selected,
      risk_score: detail._field_visibility?.score === 'hidden' ? null : (typeof detail.score === 'number' ? detail.score : selected.risk_score),
      recommendation: detail._field_visibility?.recommendation === 'hidden' ? 'Contenu masqué par la politique DAC.' : (detail.recommendation ?? selected.recommendation),
      factors: detail._field_visibility?.factors === 'hidden' ? [] : (detail.factors ?? selected.factors),
      _field_visibility: detail._field_visibility || {},
    }
    : selected;
  const factors = enrichedSelected?.factors || [];
  const meta = enrichedSelected ? riskMeta(enrichedSelected.risk) : riskMeta('low');

  useEffect(() => {
    let mounted = true;
    const loadDetail = async () => {
      if (!selected?.id) return;
      try {
        const data = await api.get(`/predict/risk/${selected.id}`);
        if (mounted) setDetail(data);
      } catch (err) {
        if (mounted) setDetail(null);
      }
    };
    loadDetail();
    return () => {
      mounted = false;
    };
  }, [selected?.id]);

  return (
    <div className="animate-fade-in-up space-y-6">
      <PageHeader title="Prédictions IA" subtitle="Risque de départ estimé et facteurs explicatifs par collaborateur" />
      {error ? <div className="rounded-xl bg-white p-4 text-sm text-brand-warning">{error}</div> : null}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardHeader title="Classement par risque" subtitle="Détecté par le moteur backend" icon={Brain} />
          <ul className="max-h-[28rem] divide-y divide-slate-100 overflow-y-auto">
            {ranked.map((employee) => {
              const active = employee.id === selectedId;
              return (
                <li key={employee.id}>
                  <button onClick={() => setSelectedId(employee.id)} className={cn('flex w-full items-center gap-3 px-4 py-3 text-left transition-colors', active ? 'bg-brand-light' : 'hover:bg-brand-light')}>
                    <Avatar name={employee.name} size="sm" />
                    <div className="min-w-0 flex-1">
                      <div className="truncate text-sm font-medium text-brand-dark">{employee.name}</div>
                      <div className="truncate text-xs text-brand-secondary/70">{employee.department}</div>
                    </div>
                    <span className={cn('text-sm font-bold', employee.risk_score >= 60 ? 'text-brand-danger' : employee.risk_score >= 35 ? 'text-brand-danger/10' : 'text-brand-secondary')}>{employee.risk_score}%</span>
                    <ChevronRight size={16} className={cn('shrink-0', active ? 'text-brand-secondary' : 'text-brand-secondary/40')} />
                  </button>
                </li>
              );
            })}
          </ul>
        </Card>

        {enrichedSelected ? (
          <Card className="lg:col-span-2">
            <div className="flex flex-col gap-4 border-b border-brand-secondary/10 p-5 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-3">
                <Avatar name={enrichedSelected.name} size="lg" />
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-brand-dark">{enrichedSelected.name}</h3>
                    <Badge variant={meta.badge} dot>{meta.label}</Badge>
                  </div>
                  <p className="text-sm text-brand-secondary/80">{enrichedSelected.title} · {enrichedSelected.department} · {enrichedSelected.tenure}</p>
                  {enrichedSelected.focus_objective_title ? (
                    <p className="mt-1 text-xs text-brand-secondary/65">
                      Objectif prioritaire: <span className="font-medium text-brand-dark">{enrichedSelected.focus_objective_title}</span>
                      {typeof enrichedSelected.focus_objective_progress_pct === 'number' ? ` · ${enrichedSelected.focus_objective_progress_pct}%` : ''}
                    </p>
                  ) : null}
                </div>
              </div>
              <div className="text-center">
                <div className={cn('text-4xl font-black tracking-tight', enrichedSelected.risk_score >= 60 ? 'text-brand-danger' : enrichedSelected.risk_score >= 35 ? 'text-brand-danger/10' : 'text-brand-secondary')}>
                  {typeof enrichedSelected.risk_score === 'number' ? `${enrichedSelected.risk_score}%` : '—'}
                </div>
                <div className="text-xs text-brand-secondary/70">risque de départ (12 mois)</div>
                <div className="mt-2 flex justify-center">
                  <FieldVisibilityBadge visibility={enrichedSelected?._field_visibility?.score} />
                </div>
                <div className="mt-2 text-xs text-brand-secondary/70">
                  Perf. {typeof enrichedSelected.performance_score === 'number' ? `${enrichedSelected.performance_score.toFixed(1)}/5` : '—'}
                </div>
              </div>
            </div>

            <div className="p-5">
              <div className="mb-4 flex items-center gap-2">
                <h4 className="text-sm font-semibold text-brand-dark">Facteurs contributifs</h4>
                <FieldVisibilityBadge visibility={enrichedSelected?._field_visibility?.factors} />
              </div>
              <div className="space-y-3">
                {factors.map((factor) => (
                  <div key={factor.label}>
                    <div className="mb-1 flex items-center justify-between text-sm">
                      <span className="text-brand-secondary">{factor.label}</span>
                      <span className="font-semibold text-brand-dark">{factor.value}%</span>
                    </div>
                    <div className="h-2 w-full overflow-hidden rounded-full bg-brand-light">
                      <div className={cn('h-full rounded-full transition-all duration-500', factorColor(factor.value))} style={{ width: `${factor.value}%` }} />
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-5 flex gap-3 rounded-xl border border-brand-secondary/20 bg-brand-light/60 p-4">
                <Lightbulb size={20} className="shrink-0 text-brand-secondary" />
                  <div>
                    <div className="text-sm font-semibold text-brand-dark">Recommandation du backend</div>
                  <div className="mt-1 flex items-center gap-2">
                    <FieldVisibilityBadge visibility={enrichedSelected?._field_visibility?.recommendation} />
                    <p className="text-sm text-brand-secondary/80">{enrichedSelected.recommendation}</p>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        ) : (
          <Card className="lg:col-span-2 p-6 text-sm text-brand-secondary/70">Aucune donnée disponible pour le moment.</Card>
        )}
      </div>
    </div>
  );
}
