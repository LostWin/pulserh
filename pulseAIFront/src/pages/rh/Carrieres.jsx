import { useEffect, useMemo, useState } from 'react';
import { BriefcaseBusiness, MoveRight, Search, Sparkles, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';

import { api } from '../../lib/api';
import PageHeader from '../../components/PageHeader';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import Avatar from '../../components/ui/Avatar';
import FieldVisibilityBadge from '../../components/ui/FieldVisibilityBadge';

const READINESS_LABELS = {
  emerging: 'Émergent',
  ready_soon: 'Bientôt prêt',
  ready_now: 'Prêt maintenant',
};

export default function CarrieresRH() {
  const [overview, setOverview] = useState({ items: [], total: 0, active_benefits_count: 0, mobility_open_count: 0, ready_now_count: 0, page: 1, page_size: 20 });
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [department, setDepartment] = useState('all');
  const [readinessLevel, setReadinessLevel] = useState('all');
  const [benefitsStatus, setBenefitsStatus] = useState('all');
  const [mobilityOnly, setMobilityOnly] = useState(false);
  const [page, setPage] = useState(1);
  const [error, setError] = useState('');

  // Debounce search query
  const [filterOptions, setFilterOptions] = useState({
    departments: ['all'],
    readiness_levels: ['all'],
    benefits_statuses: ['all'],
    mobility_statuses: ['all', 'open']
  });

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedQuery(query);
      setPage(1); // Reset page on search
    }, 300);
    return () => clearTimeout(handler);
  }, [query]);

  // Load filter options on mount
  useEffect(() => {
    let mounted = true;
    const loadFilters = async () => {
      try {
        const data = await api.get('/employees/programs/overview/filters');
        if (mounted) {
          setFilterOptions(data);
        }
      } catch (err) {
        console.error('Failed to load filter options', err);
      }
    };
    loadFilters();
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        const params = new URLSearchParams();
        if (debouncedQuery) params.append('q', debouncedQuery);
        if (department !== 'all') params.append('department', department);
        if (readinessLevel !== 'all') params.append('readiness_level', readinessLevel);
        if (benefitsStatus !== 'all') params.append('benefits_status', benefitsStatus);
        if (mobilityOnly) params.append('mobility_status', 'open');
        params.append('page', page);
        params.append('page_size', 20);

        const data = await api.get(`/employees/programs/overview?${params.toString()}`);
        if (mounted) setOverview(data);
      } catch (err) {
        if (mounted) setError(err.message || 'Impossible de charger les parcours carrière.');
      }
    };
    load();
    return () => {
      mounted = false;
    };
  }, [debouncedQuery, department, readinessLevel, benefitsStatus, mobilityOnly, page]);

  const filtered = overview.items || [];
  const totalPages = Math.ceil((overview.total || 0) / 20);

  return (
    <div className="animate-fade-in-up space-y-6">
      <PageHeader
        title="Carrières & Mobilité"
        subtitle={`${overview.total || 0} collaborateurs suivis · parcours, benefits et mobilité interne`}
      />
      {error ? <div className="rounded-xl bg-white p-4 text-sm text-brand-warning">{error}</div> : null}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Card className="p-5">
          <div className="flex items-center gap-3 text-brand-secondary/80"><Sparkles size={18} />Benefits actifs</div>
          <div className="mt-3 text-3xl font-semibold text-brand-dark">{overview.active_benefits_count || 0}</div>
        </Card>
        <Card className="p-5">
          <div className="flex items-center gap-3 text-brand-secondary/80"><MoveRight size={18} />Mobilités ouvertes</div>
          <div className="mt-3 text-3xl font-semibold text-brand-dark">{overview.mobility_open_count || 0}</div>
        </Card>
        <Card className="p-5">
          <div className="flex items-center gap-3 text-brand-secondary/80"><TrendingUp size={18} />Prêts maintenant</div>
          <div className="mt-3 text-3xl font-semibold text-brand-dark">{overview.ready_now_count || 0}</div>
        </Card>
      </div>

      <Card className="flex flex-col gap-4 p-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="relative w-full lg:max-w-xs">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-secondary/70" />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Rechercher un collaborateur, un poste, une cible..."
            className="w-full rounded-xl border border-brand-secondary/20 bg-brand-light py-2 pl-10 pr-3 text-sm text-brand-dark outline-none transition focus:border-brand-secondary focus:bg-white focus:ring-2 focus:ring-brand-secondary/20"
          />
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={department}
            onChange={(event) => { setDepartment(event.target.value); setPage(1); }}
            className="rounded-xl border border-brand-secondary/20 bg-white px-3 py-2 text-sm font-medium text-brand-dark outline-none focus:border-brand-secondary"
          >
            {filterOptions.departments.map((item) => (
              <option key={item} value={item}>{item === 'all' ? 'Tous les départements' : item}</option>
            ))}
          </select>
          <select
            value={readinessLevel}
            onChange={(event) => { setReadinessLevel(event.target.value); setPage(1); }}
            className="rounded-xl border border-brand-secondary/20 bg-white px-3 py-2 text-sm font-medium text-brand-dark outline-none focus:border-brand-secondary"
          >
            {filterOptions.readiness_levels.map((item) => (
              <option key={item} value={item}>{item === 'all' ? 'Tous les niveaux' : READINESS_LABELS[item] || item}</option>
            ))}
          </select>
          <select
            value={benefitsStatus}
            onChange={(event) => { setBenefitsStatus(event.target.value); setPage(1); }}
            className="rounded-xl border border-brand-secondary/20 bg-white px-3 py-2 text-sm font-medium text-brand-dark outline-none focus:border-brand-secondary"
          >
            {filterOptions.benefits_statuses.map((item) => (
              <option key={item} value={item}>{item === 'all' ? 'Tous les benefits' : item}</option>
            ))}
          </select>
          <button
            onClick={() => { setMobilityOnly((current) => !current); setPage(1); }}
            className={`rounded-xl border px-3 py-2 text-sm font-medium transition-colors ${mobilityOnly ? 'border-brand-secondary bg-brand-secondary text-white' : 'border-brand-secondary/20 bg-white text-brand-dark'}`}
          >
            Mobilités ouvertes uniquement
          </button>
        </div>
      </Card>

      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[980px] text-left text-sm">
            <thead>
              <tr className="border-b border-brand-secondary/10 text-xs uppercase tracking-wider text-brand-secondary/70">
                <th className="px-5 py-3 font-medium">Collaborateur</th>
                <th className="px-5 py-3 font-medium">Ancienneté & Manager</th>
                <th className="px-5 py-3 font-medium">Benefits</th>
                <th className="px-5 py-3 font-medium">Cible carrière</th>
                <th className="px-5 py-3 font-medium">Readiness</th>
                <th className="px-5 py-3 font-medium">Mobilité</th>
                <th className="px-5 py-3 font-medium">Évolution & Revue</th>
                <th className="px-5 py-3 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((item) => (
                <tr key={item.employee_id} className="transition-colors hover:bg-brand-light/50">
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-3">
                      <Avatar name={item.employee_name} size="sm" />
                      <div>
                        <div className="font-medium text-brand-dark">{item.employee_name}</div>
                        <div className="text-xs text-brand-secondary/70">{item.job_title || 'Collaborateur'} · {item.department || 'Non assigné'}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-2 font-medium text-brand-dark">
                      {item.tenure_label || '—'}
                      <FieldVisibilityBadge visibility={item._field_visibility?.tenure_label} />
                    </div>
                    <div className="flex items-center gap-2 text-xs text-brand-secondary/70">
                      Mgr: {item.manager_name || '—'}
                      <FieldVisibilityBadge visibility={item._field_visibility?.manager_name} />
                    </div>
                  </td>
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-2 font-medium text-brand-dark">
                      {item.primary_benefit_label || '—'}
                      <FieldVisibilityBadge visibility={item._field_visibility?.primary_benefit_label} />
                    </div>
                    <div className="flex items-center gap-2 text-xs text-brand-secondary/70">
                      {item.benefits_status || '—'}
                      <FieldVisibilityBadge visibility={item._field_visibility?.benefits_status} />
                    </div>
                  </td>
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-2 font-medium text-brand-dark">
                      {item.career_focus_title || '—'}
                      <FieldVisibilityBadge visibility={item._field_visibility?.career_focus_title} />
                    </div>
                  </td>
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-2">
                      <Badge variant={item.readiness_level === 'ready_now' ? 'success' : item.readiness_level === 'ready_soon' ? 'warning' : 'default'}>
                        {READINESS_LABELS[item.readiness_level] || '—'}
                      </Badge>
                      <FieldVisibilityBadge visibility={item._field_visibility?.readiness_level} />
                    </div>
                  </td>
                  <td className="px-5 py-3">
                    {item.mobility_status ? (
                      <>
                        <div className="flex items-center gap-2 font-medium text-brand-dark">
                          {item.mobility_status}
                          <FieldVisibilityBadge visibility={item._field_visibility?.mobility_status} />
                        </div>
                        <div className="flex items-center gap-2 text-xs text-brand-secondary/70">
                          {item.mobility_target || 'Sans cible renseignée'}
                          <FieldVisibilityBadge visibility={item._field_visibility?.mobility_target} />
                        </div>
                      </>
                    ) : (
                      <span className="text-brand-secondary/50">Aucune</span>
                    )}
                  </td>
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-2 font-medium text-brand-dark">
                      {item.promotion_last_title || '—'}
                      <FieldVisibilityBadge visibility={item._field_visibility?.promotion_last_title} />
                    </div>
                    <div className="flex items-center gap-2 text-xs text-brand-secondary/70">
                      Revue: {item.next_career_review_label || 'À planifier'}
                      <FieldVisibilityBadge visibility={item._field_visibility?.next_career_review_label} />
                    </div>
                  </td>
                  <td className="px-5 py-3 text-right">
                    <div className="flex flex-wrap items-center justify-end gap-2 w-max ml-auto">
                      <Link to={`/rh/employes/${item.employee_id}`} className="rounded-lg border border-brand-secondary/20 px-2 py-1 text-xs font-medium text-brand-dark hover:bg-brand-secondary/5 transition">Profil</Link>
                      <Link to={`/rh/employees/${item.employee_id}/carriere`} className="rounded-lg border border-brand-secondary/20 px-2 py-1 text-xs font-medium text-brand-dark hover:bg-brand-secondary/5 transition">Carrière</Link>
                      <button disabled title="Bientôt disponible" className="rounded-lg border border-brand-secondary/20 px-2 py-1 text-xs font-medium text-brand-dark/50 cursor-not-allowed bg-brand-light">Revue</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {!filtered.length ? (
          <div className="py-16 text-center text-sm text-brand-secondary/70">
            Aucun collaborateur ne correspond aux filtres actuels.
          </div>
        ) : null}
        
        {totalPages > 1 && (
          <div className="flex items-center justify-between border-t border-brand-secondary/10 px-5 py-4">
            <div className="text-sm text-brand-secondary/70">
              Page {page} sur {totalPages} (Total: {overview.total})
            </div>
            <div className="flex items-center gap-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage(p => p - 1)}
                className="rounded-xl border border-brand-secondary/20 px-3 py-1.5 text-sm font-medium text-brand-dark disabled:opacity-50"
              >
                Précédent
              </button>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage(p => p + 1)}
                className="rounded-xl border border-brand-secondary/20 px-3 py-1.5 text-sm font-medium text-brand-dark disabled:opacity-50"
              >
                Suivant
              </button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
