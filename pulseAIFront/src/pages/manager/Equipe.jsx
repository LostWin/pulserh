import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, Heart, AlertTriangle, ArrowUpRight, ArrowDownRight, CalendarClock } from 'lucide-react';

import { api } from '../../lib/api';
import { cn, riskMeta, engagementBar } from '../../lib/utils';
import PageHeader from '../../components/PageHeader';
import Card from '../../components/ui/Card';
import StatCard from '../../components/ui/StatCard';
import Badge from '../../components/ui/Badge';
import Avatar from '../../components/ui/Avatar';
import ProgressBar from '../../components/ui/ProgressBar';

const FILTERS = [
  { key: 'all', label: 'Tous' },
  { key: 'low', label: 'Engagés' },
  { key: 'medium', label: 'À surveiller' },
  { key: 'high', label: 'À risque' },
];

export default function Equipe() {
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState(null);
  const [teamProjects, setTeamProjects] = useState([]);
  const [filter, setFilter] = useState('all');
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        const data = await api.get('/dashboard/manager-summary');
        if (mounted) {
          setDashboard(data);
          if (data?.manager_id) {
            const projects = await api.get(`/teams/${data.manager_id}/projects`).catch(() => []);
            if (mounted) setTeamProjects(projects || []);
          }
        }
      } catch (err) {
        if (mounted) setError(err.message || 'Impossible de charger l’équipe.');
      }
    };
    load();
    return () => {
      mounted = false;
    };
  }, []);

  const team = dashboard?.team || [];
  const avg = dashboard?.summary?.avg_engagement || 0;
  const atRisk = dashboard?.summary?.at_risk_count || 0;
  const visible = useMemo(() => (filter === 'all' ? team : team.filter((employee) => employee.risk === filter)), [filter, team]);

  return (
    <div className="animate-fade-in-up space-y-6">
      <PageHeader title="Mon équipe" subtitle={`${team.length} collaborateurs sous votre responsabilité`} />
      {error ? <div className="rounded-xl bg-white p-4 text-sm text-brand-warning">{error}</div> : null}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard icon={Users} label="Effectif" value={team.length} accent="purple" />
        <StatCard icon={Heart} label="Engagement moyen" value={avg} suffix="/100" delta={3} accent="emerald" />
        <StatCard icon={AlertTriangle} label="À risque" value={atRisk} delta={2} invertDelta accent="rose" />
      </div>

      <div className="flex rounded-xl border border-brand-secondary/20 bg-brand-light p-0.5 w-fit">
        {FILTERS.map((item) => (
          <button
            key={item.key}
            onClick={() => setFilter(item.key)}
            className={cn('rounded-xl px-3 py-1.5 text-sm font-medium transition-colors', filter === item.key ? 'bg-white text-brand-dark shadow-sm' : 'text-brand-secondary/80 hover:text-brand-dark')}
          >
            {item.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {visible.map((employee) => {
          const meta = riskMeta(employee.risk);
          const up = employee.delta >= 0;
          return (
            <Card key={employee.id} className="p-5">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <Avatar name={employee.name} size="lg" />
                  <div>
                    <div className="font-semibold text-brand-dark">{employee.name}</div>
                    <div className="text-xs text-brand-secondary/70">{employee.title}</div>
                  </div>
                </div>
                <Badge variant={meta.badge} dot>{meta.label}</Badge>
              </div>

              <div className="mt-4">
                <div className="mb-1 flex items-center justify-between text-xs">
                  <span className="text-brand-secondary/80">Engagement</span>
                  <span className="flex items-center gap-2 font-semibold text-brand-dark">
                    {employee.engagement}/100
                    <span className={cn('inline-flex items-center', up ? 'text-brand-secondary' : 'text-brand-danger')}>
                      {up ? <ArrowUpRight size={13} /> : <ArrowDownRight size={13} />}{Math.abs(employee.delta)}
                    </span>
                  </span>
                </div>
                <ProgressBar value={employee.engagement} barClassName={engagementBar(employee.engagement)} />
              </div>

              <p className="mt-3 line-clamp-2 text-xs text-brand-secondary/80">{employee.signal}</p>

              <div className="mt-4 flex gap-2 border-t border-brand-secondary/10 pt-4">
                <button className="flex flex-1 items-center justify-center gap-1.5 rounded-xl bg-brand-dark py-2 text-xs font-medium text-white transition-colors hover:bg-brand-dark">
                  <CalendarClock size={14} /> Entretien
                </button>
                <button onClick={() => navigate(`/manager/equipe/${employee.id}`)} className="flex-1 rounded-xl border border-brand-secondary/20 py-2 text-xs font-medium text-brand-secondary transition-colors hover:bg-brand-light">
                  Profil
                </button>
              </div>
            </Card>
          );
        })}
      </div>

      <Card className="p-5">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-brand-dark">Projets d’équipe</h2>
            <p className="mt-1 text-xs text-brand-secondary/70">Contexte opérationnel remonté par le backend</p>
          </div>
          <Badge variant="default">{teamProjects.length} projet(s)</Badge>
        </div>
        <div className="grid gap-3 md:grid-cols-2">
          {teamProjects.slice(0, 6).map((project) => (
            <div key={project.id} className="rounded-2xl border border-brand-secondary/10 bg-brand-light/40 p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="font-semibold text-brand-dark">{project.name}</div>
                  <div className="text-xs text-brand-secondary/70">{project.business_domain || 'Interne'} · {project.priority || 'Priorité non définie'}</div>
                </div>
                <span className="rounded-full bg-white px-2 py-1 text-[10px] font-semibold text-brand-secondary">{project.status}</span>
              </div>
              {project.required_skill_names?.length ? (
                <div className="mt-3 flex flex-wrap gap-2">
                  {project.required_skill_names.map((name) => (
                    <span key={name} className="rounded-full bg-brand-secondary/10 px-2 py-1 text-[10px] font-semibold text-brand-secondary">{name}</span>
                  ))}
                </div>
              ) : null}
            </div>
          ))}
          {!teamProjects.length ? <div className="text-sm text-brand-secondary/70">Aucun projet d’équipe remonté pour le moment.</div> : null}
        </div>
      </Card>
    </div>
  );
}
