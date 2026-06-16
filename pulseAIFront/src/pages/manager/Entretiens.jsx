import { useEffect, useMemo, useState } from 'react';
import { CalendarCheck, Clock4, Plus, UserPlus } from 'lucide-react';

import PageHeader from '../../components/PageHeader';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import { api } from '../../lib/api';

export default function ManagerEntretiens() {
  const [overview, setOverview] = useState({ items: [], planned_count: 0, pending_count: 0, average_duration_minutes: 45 });
  const [dashboard, setDashboard] = useState(null);
  const [recommendations, setRecommendations] = useState({});
  const [error, setError] = useState('');
  const [form, setForm] = useState({ employee_id: '', scheduled_at: '', title: 'Entretien individuel', location: 'Salle Horizon', notes: '' });
  const [saving, setSaving] = useState(false);
  const [summaryDrafts, setSummaryDrafts] = useState({});

  const load = async () => {
    const [interviews, managerSummary] = await Promise.all([
      api.get('/interviews'),
      api.get('/dashboard/manager-summary'),
    ]);
    setOverview(interviews);
    setDashboard(managerSummary);
    const team = managerSummary?.team || [];
    const entries = await Promise.all(
      team.slice(0, 8).map(async (employee) => {
        const recos = await api.get(`/trainings/recommendations/${employee.id}`).catch(() => []);
        return [employee.id, recos];
      })
    );
    setRecommendations(Object.fromEntries(entries));
  };

  useEffect(() => {
    load().catch((err) => setError(err.message || 'Impossible de charger les entretiens.'));
  }, []);

  const team = dashboard?.team || [];
  const availableEmployees = useMemo(() => team.filter((employee) => !overview.items.some((item) => item.collaborator_id === employee.id)), [team, overview.items]);

  const createInterview = async () => {
    if (!form.employee_id || !form.scheduled_at) return;
    setSaving(true);
    try {
      await api.post('/interviews', form);
      setForm({ employee_id: '', scheduled_at: '', title: 'Entretien individuel', location: 'Salle Horizon', notes: '' });
      await load();
    } catch (err) {
      setError(err.message || 'Impossible de créer l’entretien.');
    } finally {
      setSaving(false);
    }
  };

  const autoScheduleInterview = async () => {
    if (!form.employee_id) {
      setError('Veuillez sélectionner un collaborateur pour l’auto-scheduling.');
      return;
    }
    setSaving(true);
    setError('');
    try {
      await api.post('/manager/interviews/auto-schedule', {
        employee_id: form.employee_id,
        title: form.title || 'Entretien 1:1 Auto',
        interview_type: 'one_on_one',
        duration_minutes: 45
      });
      setForm({ employee_id: '', scheduled_at: '', title: 'Entretien individuel', location: 'Salle Horizon', notes: '' });
      await load();
    } catch (err) {
      setError(err.message || 'Impossible de planifier automatiquement l’entretien.');
    } finally {
      setSaving(false);
    }
  };

  const saveSummary = async (item) => {
    const draft = summaryDrafts[item.id];
    if (!draft?.summary && !draft?.outcome) return;
    setSaving(true);
    try {
      await api.post(`/interviews/${item.id}/summary`, {
        outcome: draft.outcome || null,
        summary: draft.summary || null,
        next_actions: (draft.next_actions || '')
          .split('\n')
          .map((line) => line.trim())
          .filter(Boolean),
      });
      await load();
    } catch (err) {
      setError(err.message || 'Impossible d’enregistrer le compte-rendu.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="animate-fade-in-up space-y-6">
      <PageHeader title="Entretiens" subtitle="Planifiez et suivez les entretiens de votre équipe via le backend." />
      {error ? <div className="rounded-2xl bg-white p-4 text-sm text-brand-warning">{error}</div> : null}

      <Card className="grid gap-4 p-6 sm:grid-cols-3">
        <div className="rounded-3xl border border-brand-secondary/10 bg-brand-light p-5">
          <div className="flex items-center gap-3 text-brand-secondary/80"><UserPlus size={18} /><span>Entretiens planifiés</span></div>
          <p className="mt-3 text-3xl font-semibold text-brand-dark">{overview.planned_count}</p>
        </div>
        <div className="rounded-3xl border border-brand-secondary/10 bg-brand-light p-5">
          <div className="flex items-center gap-3 text-brand-secondary/80"><CalendarCheck size={18} /><span>À planifier</span></div>
          <p className="mt-3 text-3xl font-semibold text-brand-dark">{overview.pending_count}</p>
        </div>
        <div className="rounded-3xl border border-brand-secondary/10 bg-brand-light p-5">
          <div className="flex items-center gap-3 text-brand-secondary/80"><Clock4 size={18} /><span>Temps moyen</span></div>
          <p className="mt-3 text-3xl font-semibold text-brand-dark">{overview.average_duration_minutes} min</p>
        </div>
      </Card>

      <Card className="space-y-4 p-6">
        <div className="flex items-center gap-2">
          <Plus size={16} className="text-brand-secondary" />
          <h2 className="text-lg font-bold text-brand-dark">Créer un entretien</h2>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <select value={form.employee_id} onChange={(event) => setForm((current) => ({ ...current, employee_id: event.target.value }))} className="rounded-2xl border border-brand-secondary/20 px-4 py-3 text-sm bg-white">
            <option value="">Sélectionner un collaborateur</option>
            {availableEmployees.map((employee) => <option key={employee.id} value={employee.id}>{employee.name}</option>)}
          </select>
          <input type="datetime-local" value={form.scheduled_at} onChange={(event) => setForm((current) => ({ ...current, scheduled_at: event.target.value }))} className="rounded-2xl border border-brand-secondary/20 px-4 py-3 text-sm" />
          <input value={form.title} onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))} className="rounded-2xl border border-brand-secondary/20 px-4 py-3 text-sm" placeholder="Titre" />
          <input value={form.location} onChange={(event) => setForm((current) => ({ ...current, location: event.target.value }))} className="rounded-2xl border border-brand-secondary/20 px-4 py-3 text-sm" placeholder="Lieu" />
        </div>
        <textarea value={form.notes} onChange={(event) => setForm((current) => ({ ...current, notes: event.target.value }))} rows={3} className="w-full rounded-2xl border border-brand-secondary/20 px-4 py-3 text-sm" placeholder="Notes de préparation" />
        <div className="flex flex-wrap items-center gap-3">
          <button onClick={createInterview} disabled={saving || !form.scheduled_at} className="rounded-2xl bg-brand-secondary px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60">
            {saving ? 'Création…' : 'Planifier'}
          </button>
          <button onClick={autoScheduleInterview} disabled={saving || !form.employee_id} className="flex items-center gap-2 rounded-2xl bg-brand-primary px-4 py-2.5 text-sm font-semibold text-white hover:bg-brand-primary/90 disabled:opacity-60">
            <CalendarCheck size={16} />
            Auto-Schedule (Trouver un créneau)
          </button>
        </div>
      </Card>

      <Card className="space-y-4 p-6">
        {overview.items.map((item) => (
          (() => {
            const employee = team.find((member) => member.id === item.collaborator_id);
            return (
          <div key={item.id} className="flex flex-col gap-4 rounded-3xl border border-brand-secondary/10 bg-white p-5 shadow-sm sm:flex-row sm:items-center sm:justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 text-xs uppercase tracking-[0.24em] text-brand-secondary/70">{item.collaborator}</div>
              <p className="mt-2 text-lg font-semibold text-brand-dark">{item.date} · {item.time}</p>
              <p className="text-sm text-brand-secondary/80">{item.title} · {item.location || 'À confirmer'} · {item.interview_type || 'one_on_one'}</p>
              {employee ? (
                <div className="mt-2 flex flex-wrap items-center gap-2 text-[11px] text-brand-secondary/70">
                  <span className="rounded-full bg-brand-light px-2.5 py-1">Perf. {typeof employee.performance_score === 'number' ? employee.performance_score.toFixed(1) : '—'}/5</span>
                  {employee.focus_objective_title ? (
                    <span className="rounded-full bg-brand-light px-2.5 py-1">
                      Objectif: {employee.focus_objective_title}
                      {typeof employee.focus_objective_progress_pct === 'number' ? ` · ${employee.focus_objective_progress_pct}%` : ''}
                    </span>
                  ) : null}
                </div>
              ) : null}
              {recommendations[item.collaborator_id]?.[0] ? (
                <p className="mt-2 text-xs text-brand-secondary/70">
                  Suggestion associée: <span className="font-semibold text-brand-dark">{recommendations[item.collaborator_id][0].title}</span>
                </p>
              ) : null}
              {item.summary ? (
                <div className="mt-3 rounded-2xl bg-brand-light/60 p-3 text-xs text-brand-secondary/80">
                  <p className="font-semibold text-brand-dark">Compte-rendu</p>
                  <p className="mt-1">{item.summary}</p>
                  {item.outcome ? <p className="mt-1 text-[11px] uppercase tracking-wide text-brand-secondary/60">Outcome: {item.outcome}</p> : null}
                </div>
              ) : null}
              <div className="mt-3 grid gap-2">
                <input
                  value={summaryDrafts[item.id]?.outcome ?? item.outcome ?? ''}
                  onChange={(event) => setSummaryDrafts((current) => ({ ...current, [item.id]: { ...current[item.id], outcome: event.target.value, summary: current[item.id]?.summary ?? item.summary ?? '', next_actions: current[item.id]?.next_actions ?? (item.next_actions || []).join('\n') } }))}
                  className="rounded-2xl border border-brand-secondary/20 px-3 py-2 text-xs"
                  placeholder="Outcome: aligné, alerte, plan d'action..."
                />
                <textarea
                  rows={3}
                  value={summaryDrafts[item.id]?.summary ?? item.summary ?? ''}
                  onChange={(event) => setSummaryDrafts((current) => ({ ...current, [item.id]: { ...current[item.id], summary: event.target.value, outcome: current[item.id]?.outcome ?? item.outcome ?? '', next_actions: current[item.id]?.next_actions ?? (item.next_actions || []).join('\n') } }))}
                  className="rounded-2xl border border-brand-secondary/20 px-3 py-2 text-xs"
                  placeholder="Résumé de l'entretien"
                />
                <textarea
                  rows={2}
                  value={summaryDrafts[item.id]?.next_actions ?? (item.next_actions || []).join('\n')}
                  onChange={(event) => setSummaryDrafts((current) => ({ ...current, [item.id]: { ...current[item.id], next_actions: event.target.value, outcome: current[item.id]?.outcome ?? item.outcome ?? '', summary: current[item.id]?.summary ?? item.summary ?? '' } }))}
                  className="rounded-2xl border border-brand-secondary/20 px-3 py-2 text-xs"
                  placeholder="Une action par ligne"
                />
              </div>
            </div>
            <div className="flex flex-col items-end gap-3">
              <Badge variant={item.status === 'Planifié' ? 'success' : item.status === 'Complété' ? 'default' : 'warning'}>{item.status}</Badge>
              <button
                onClick={() => saveSummary(item)}
                disabled={saving}
                className="rounded-2xl bg-brand-secondary px-3 py-2 text-xs font-semibold text-white disabled:opacity-60"
              >
                Enregistrer le compte-rendu
              </button>
            </div>
          </div>
            );
          })()
        ))}
      </Card>
    </div>
  );
}
