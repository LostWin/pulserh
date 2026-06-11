import { Users, GitMerge } from 'lucide-react';
import { departments, employees } from '../../data/mockData';
import { engagementBar, engagementText } from '../../lib/utils';
import PageHeader from '../../components/PageHeader';
import Card from '../../components/ui/Card';
import StatCard from '../../components/ui/StatCard';
import Badge from '../../components/ui/Badge';
import Avatar from '../../components/ui/Avatar';
import ProgressBar from '../../components/ui/ProgressBar';

/** Most engaged person in a department acts as its lead (for display). */
function leadOf(deptName) {
  const members = employees.filter((e) => e.department === deptName);
  if (!members.length) return null;
  return members.reduce((best, e) => (e.engagement > best.engagement ? e : best));
}

function riskVariant(risk) {
  if (risk > 20) return 'danger';
  if (risk > 12) return 'warning';
  return 'success';
}

export default function Departements() {
  const headcount = departments.reduce((s, d) => s + d.headcount, 0);
  const avg = Math.round(departments.reduce((s, d) => s + d.engagement * d.headcount, 0) / headcount);

  return (
    <div className="animate-fade-in-up space-y-6">
      <PageHeader title="Départements" subtitle={`${departments.length} entités · ${headcount} collaborateurs`} />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard icon={GitMerge} label="Départements" value={departments.length} accent="blue" />
        <StatCard icon={Users} label="Effectif total" value={headcount} accent="purple" />
        <StatCard icon={Users} label="Engagement moyen" value={avg} suffix="/100" delta={4} accent="emerald" />
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {departments.map((d) => {
          const lead = leadOf(d.name);
          return (
            <Card key={d.name} className="p-5">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-bold text-brand-dark">{d.name}</h3>
                  <p className="text-xs text-brand-secondary/70">{d.headcount} collaborateurs</p>
                </div>
                <Badge variant={riskVariant(d.risk)} dot>{d.risk}% risque</Badge>
              </div>

              <div className="mt-4">
                <div className="mb-1 flex items-center justify-between text-xs">
                  <span className="text-brand-secondary/80">Engagement moyen</span>
                  <span className={`font-semibold ${engagementText(d.engagement)}`}>{d.engagement}/100</span>
                </div>
                <ProgressBar value={d.engagement} barClassName={engagementBar(d.engagement)} />
              </div>

              {lead && (
                <div className="mt-4 flex items-center gap-3 border-t border-brand-secondary/10 pt-4">
                  <Avatar name={lead.name} size="sm" />
                  <div className="min-w-0">
                    <div className="truncate text-sm font-medium text-brand-dark">{lead.name}</div>
                    <div className="text-xs text-brand-secondary/70">Référent · {lead.title}</div>
                  </div>
                </div>
              )}
            </Card>
          );
        })}
      </div>
    </div>
  );
}
