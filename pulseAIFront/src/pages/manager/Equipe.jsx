import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, Heart, AlertTriangle, ArrowUpRight, ArrowDownRight, CalendarClock } from 'lucide-react';
import { employees } from '../../data/mockData';
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
  const [filter, setFilter] = useState('all');
  const team = employees;
  const avg = Math.round(team.reduce((s, e) => s + e.engagement, 0) / team.length);
  const atRisk = team.filter((e) => e.risk !== 'low').length;

  const visible = useMemo(
    () => (filter === 'all' ? team : team.filter((e) => e.risk === filter)),
    [filter, team],
  );

  return (
    <div className="animate-fade-in-up space-y-6">
      <PageHeader title="Mon équipe" subtitle={`${team.length} collaborateurs sous votre responsabilité`} />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard icon={Users} label="Effectif" value={team.length} accent="purple" />
        <StatCard icon={Heart} label="Engagement moyen" value={avg} suffix="/100" delta={3} accent="emerald" />
        <StatCard icon={AlertTriangle} label="À risque" value={atRisk} delta={2} invertDelta accent="rose" />
      </div>

      <div className="flex rounded-xl border border-brand-secondary/20 bg-brand-light p-0.5 w-fit">
        {FILTERS.map((f) => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            className={cn(
              'rounded-xl px-3 py-1.5 text-sm font-medium transition-colors',
              filter === f.key ? 'bg-white text-brand-dark shadow-sm' : 'text-brand-secondary/80 hover:text-brand-dark',
            )}
          >
            {f.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {visible.map((emp) => {
          const meta = riskMeta(emp.risk);
          const up = emp.delta >= 0;
          return (
            <Card key={emp.id} className="p-5">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <Avatar name={emp.name} size="lg" />
                  <div>
                    <div className="font-semibold text-brand-dark">{emp.name}</div>
                    <div className="text-xs text-brand-secondary/70">{emp.title}</div>
                  </div>
                </div>
                <Badge variant={meta.badge} dot>{meta.label}</Badge>
              </div>

              <div className="mt-4">
                <div className="mb-1 flex items-center justify-between text-xs">
                  <span className="text-brand-secondary/80">Engagement</span>
                  <span className="flex items-center gap-2 font-semibold text-brand-dark">
                    {emp.engagement}/100
                    <span className={cn('inline-flex items-center', up ? 'text-brand-secondary' : 'text-brand-danger')}>
                      {up ? <ArrowUpRight size={13} /> : <ArrowDownRight size={13} />}{Math.abs(emp.delta)}
                    </span>
                  </span>
                </div>
                <ProgressBar value={emp.engagement} barClassName={engagementBar(emp.engagement)} />
              </div>

              <p className="mt-3 line-clamp-2 text-xs text-brand-secondary/80">{emp.signal}</p>

              <div className="mt-4 flex gap-2 border-t border-brand-secondary/10 pt-4">
                <button className="flex flex-1 items-center justify-center gap-1.5 rounded-xl bg-brand-dark py-2 text-xs font-medium text-white transition-colors hover:bg-brand-dark">
                  <CalendarClock size={14} /> Entretien
                </button>
                <button 
                  onClick={() => navigate(`/manager/equipe/${emp.id}`)}
                  className="flex-1 rounded-xl border border-brand-secondary/20 py-2 text-xs font-medium text-brand-secondary transition-colors hover:bg-brand-light"
                >
                  Profil
                </button>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
