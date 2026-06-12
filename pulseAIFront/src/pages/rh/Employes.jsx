import { useMemo, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Download, UserPlus, ArrowUpRight, ArrowDownRight, ChevronLeft, ChevronRight } from 'lucide-react';
import { api } from '../../lib/api';
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
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [dept, setDept] = useState('all');
  const [risk, setRisk] = useState('all');
  const [dbEmployees, setDbEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 15;

  useEffect(() => {
    const fetchEmployees = async () => {
      try {
        const response = await api.get('/employees/?page_size=500'); // Added trailing slash
        // Mapping DB format to the UI format
        const mapped = response.items.map(emp => {
          // Mock data for missing metrics
          const hash = emp.id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
          const engagement = 50 + (hash % 50);
          const risks = ['low', 'medium', 'high'];
          const riskLevel = risks[hash % 3];
          const delta = (hash % 20) - 10;
          
          return {
            id: emp.id,
            name: `${emp.first_name} ${emp.last_name}`,
            title: emp.contract_type || 'Collaborateur', // Temporarily mapped to contract_type
            department: emp.department || 'Non assigné',
            risk: riskLevel,
            engagement: engagement,
            delta: delta,
            lastActive: 'Il y a ' + ((hash % 5) + 1) + 'h'
          };
        });
        setDbEmployees(mapped);
      } catch (err) {
        console.error("Failed to fetch employees", err);
      } finally {
        setLoading(false);
      }
    };
    fetchEmployees();
  }, []);

  const departments = useMemo(
    () => ['all', ...Array.from(new Set(dbEmployees.map((e) => e.department)))],
    [dbEmployees],
  );

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const result = dbEmployees.filter((e) => {
      const matchesQuery = !q || e.name.toLowerCase().includes(q) || e.title.toLowerCase().includes(q);
      const matchesDept = dept === 'all' || e.department === dept;
      const matchesRisk = risk === 'all' || e.risk === risk;
      return matchesQuery && matchesDept && matchesRisk;
    });
    // Reset to page 1 when filters change
    setCurrentPage(1);
    return result;
  }, [query, dept, risk, dbEmployees]);

  const totalPages = Math.ceil(filtered.length / pageSize);
  const paginated = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filtered.slice(start, start + pageSize);
  }, [filtered, currentPage, pageSize]);

  return (
    <div className="animate-fade-in-up space-y-6">
      <PageHeader title="Employés" subtitle={`${dbEmployees.length} collaborateurs · ${filtered.length} affichés`}>
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
              {paginated.map((emp) => {
                const meta = riskMeta(emp.risk);
                const up = emp.delta >= 0;
                return (
                  <tr 
                    key={emp.id} 
                    onClick={() => navigate(`/rh/employes/${emp.id}`)}
                    className="transition-colors hover:bg-brand-light/70 cursor-pointer"
                  >
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

        {/* Pagination controls */}
        {!loading && filtered.length > 0 && (
          <div className="flex items-center justify-between border-t border-brand-secondary/10 bg-brand-light/30 px-5 py-3">
            <p className="text-xs font-medium text-brand-secondary/70">
              Affichage de {(currentPage - 1) * pageSize + 1} à {Math.min(currentPage * pageSize, filtered.length)} sur {filtered.length} collaborateurs
            </p>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="rounded-lg border border-brand-secondary/20 bg-white p-1.5 text-brand-secondary/70 shadow-sm transition-colors hover:bg-brand-light disabled:opacity-50"
              >
                <ChevronLeft size={16} />
              </button>
              <span className="text-xs font-medium text-brand-dark">
                Page {currentPage} / {totalPages || 1}
              </span>
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages || totalPages === 0}
                className="rounded-lg border border-brand-secondary/20 bg-white p-1.5 text-brand-secondary/70 shadow-sm transition-colors hover:bg-brand-light disabled:opacity-50"
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>
        )}

        {loading ? (
          <div className="py-16 text-center">
            <p className="text-sm font-medium text-brand-secondary/80">Chargement des données en cours...</p>
          </div>
        ) : filtered.length === 0 && (
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
