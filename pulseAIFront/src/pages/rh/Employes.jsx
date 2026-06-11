import { useMemo, useState } from 'react';
import { Search, Download, UserPlus, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { employees } from '../../data/mockData';
import { cn, riskMeta, engagementBar } from '../../lib/utils';
import PageHeader from '../../components/PageHeader';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import Avatar from '../../components/ui/Avatar';
import ProgressBar from '../../components/ui/ProgressBar';

const RISK_FILTERS = [
  { key: 'all', label: 'Tous' },
  { key: 'low', label: 'Engagés' },
  { key: 'medium', label: 'À surveiller' },
  { key: 'high', label: 'À risque' },
];

export default function Employes() {
  const [query, setQuery] = useState('');
  const [dept, setDept] = useState('all');
  const [risk, setRisk] = useState('all');

  const departments = useMemo(
    () => ['all', ...Array.from(new Set(employees.map((e) => e.department)))],
    [],
  );

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return employees.filter((e) => {
      const matchesQuery = !q || e.name.toLowerCase().includes(q) || e.title.toLowerCase().includes(q);
      const matchesDept = dept === 'all' || e.department === dept;
      const matchesRisk = risk === 'all' || e.risk === risk;
      return matchesQuery && matchesDept && matchesRisk;
    });
  }, [query, dept, risk]);

  return (
    <div className="animate-fade-in-up space-y-6">
      <PageHeader title="Employés" subtitle={`${employees.length} collaborateurs · ${filtered.length} affichés`}>
        <button className="inline-flex items-center gap-2 rounded-xl border border-brand-secondary/20 bg-white px-3 py-2 text-sm font-medium text-brand-dark shadow-sm transition-colors hover:bg-brand-light">
          <Download size={16} /> Exporter
        </button>
        <button className="inline-flex items-center gap-2 rounded-xl bg-brand-secondary px-3 py-2 text-sm font-medium text-white shadow-sm transition-colors hover:bg-brand-dark">
          <UserPlus size={16} /> Ajouter
        </button>
      </PageHeader>

      {/* Filters */}
      <Card className="flex flex-col gap-4 p-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="relative w-full lg:max-w-xs">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-secondary/70" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Rechercher un nom, un poste…"
            className="w-full rounded-xl border border-brand-secondary/20 bg-brand-light py-2 pl-10 pr-3 text-sm text-brand-dark outline-none transition focus:border-brand-secondary focus:bg-white focus:ring-2 focus:ring-brand-secondary/20"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <select
            value={dept}
            onChange={(e) => setDept(e.target.value)}
            className="rounded-xl border border-brand-secondary/20 bg-white px-3 py-2 text-sm font-medium text-brand-dark outline-none focus:border-brand-secondary"
          >
            {departments.map((d) => (
              <option key={d} value={d}>{d === 'all' ? 'Tous les départements' : d}</option>
            ))}
          </select>

          <div className="flex rounded-xl border border-brand-secondary/20 bg-brand-light p-0.5">
            {RISK_FILTERS.map((f) => (
              <button
                key={f.key}
                onClick={() => setRisk(f.key)}
                className={cn(
                  'rounded-xl px-3 py-1.5 text-xs font-medium transition-colors',
                  risk === f.key ? 'bg-white text-brand-dark shadow-sm' : 'text-brand-secondary/80 hover:text-brand-dark',
                )}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Table */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead>
              <tr className="border-b border-brand-secondary/10 text-xs uppercase tracking-wider text-brand-secondary/70">
                <th className="px-5 py-3 font-medium">Collaborateur</th>
                <th className="px-5 py-3 font-medium">Département</th>
                <th className="px-5 py-3 font-medium">Engagement</th>
                <th className="px-5 py-3 font-medium">Tendance</th>
                <th className="px-5 py-3 font-medium">Statut</th>
                <th className="px-5 py-3 font-medium">Activité</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((emp) => {
                const meta = riskMeta(emp.risk);
                const up = emp.delta >= 0;
                return (
                  <tr key={emp.id} className="transition-colors hover:bg-brand-light/70">
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-3">
                        <Avatar name={emp.name} size="sm" />
                        <div>
                          <div className="font-medium text-brand-dark">{emp.name}</div>
                          <div className="text-xs text-brand-secondary/70">{emp.title}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-3 text-brand-secondary">{emp.department}</td>
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-2">
                        <ProgressBar value={emp.engagement} barClassName={engagementBar(emp.engagement)} className="w-24" />
                        <span className="w-8 text-xs font-semibold text-brand-secondary">{emp.engagement}</span>
                      </div>
                    </td>
                    <td className="px-5 py-3">
                      <span className={cn('inline-flex items-center gap-0.5 text-xs font-semibold', up ? 'text-brand-secondary' : 'text-brand-danger')}>
                        {up ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                        {up ? '+' : ''}{emp.delta} pts
                      </span>
                    </td>
                    <td className="px-5 py-3"><Badge variant={meta.badge} dot>{meta.label}</Badge></td>
                    <td className="px-5 py-3 text-xs text-brand-secondary/70">{emp.lastActive}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {filtered.length === 0 && (
          <div className="py-16 text-center">
            <p className="text-sm font-medium text-brand-secondary/80">Aucun collaborateur ne correspond à ces critères.</p>
            <button
              onClick={() => { setQuery(''); setDept('all'); setRisk('all'); }}
              className="mt-3 text-sm font-medium text-brand-secondary hover:underline"
            >
              Réinitialiser les filtres
            </button>
          </div>
        )}
      </Card>
    </div>
  );
}
