import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, GitMerge } from 'lucide-react';
import { api } from '../../lib/api';
import { engagementBar, engagementText } from '../../lib/utils';
import PageHeader from '../../components/PageHeader';
import Card from '../../components/ui/Card';
import StatCard from '../../components/ui/StatCard';
import Badge from '../../components/ui/Badge';
import Avatar from '../../components/ui/Avatar';
import ProgressBar from '../../components/ui/ProgressBar';



function riskVariant(risk) {
  if (risk > 20) return 'danger';
  if (risk > 12) return 'warning';
  return 'success';
}

export default function Departements() {
  const navigate = useNavigate();
  const [dbDepartments, setDbDepartments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDepartments = async () => {
      try {
        const data = await api.get('/departments/');
        const mapped = data.map(d => {
          return {
            id: d.id,
            name: d.name,
            headcount: d.employee_count || 0,
            risk: d.risk_score || 0,
            engagement: d.engagement_score || 0,
            leadName: d.manager,
            leadTitle: d.manager_title || 'Manager',
          };
        });
        setDbDepartments(mapped);
      } catch (err) {
        console.error("Failed to fetch departments", err);
      } finally {
        setLoading(false);
      }
    };
    fetchDepartments();
  }, []);

  const headcount = dbDepartments.reduce((s, d) => s + d.headcount, 0);
  const avg = headcount > 0 ? Math.round(dbDepartments.reduce((s, d) => s + d.engagement * d.headcount, 0) / headcount) : 0;

  return (
    <div className="animate-fade-in-up space-y-6">
      <PageHeader title="Départements" subtitle={`${dbDepartments.length} entités · ${headcount} collaborateurs`} />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard icon={GitMerge} label="Départements" value={dbDepartments.length} accent="blue" />
        <StatCard icon={Users} label="Effectif total" value={headcount} accent="purple" />
        <StatCard icon={Users} label="Engagement moyen" value={avg} suffix="/100" delta={4} accent="emerald" />
      </div>

      {loading ? (
        <div className="py-16 text-center">
          <p className="text-sm font-medium text-brand-secondary/80">Chargement des départements...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {dbDepartments.map((d) => {
          return (
            <Card
              key={d.id || d.name}
              className="cursor-pointer p-5 transition-colors hover:bg-brand-light/40"
              onClick={() => navigate(`/rh/employes?department=${encodeURIComponent(d.name)}`)}
            >
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

              {d.leadName && (
                <div className="mt-4 flex items-center gap-3 border-t border-brand-secondary/10 pt-4">
                  <Avatar name={d.leadName} size="sm" />
                  <div className="min-w-0">
                    <div className="truncate text-sm font-medium text-brand-dark capitalize">{d.leadName}</div>
                    <div className="text-xs text-brand-secondary/70">Référent · {d.leadTitle}</div>
                  </div>
                </div>
              )}
            </Card>
          );
        })}
      </div>
      )}
    </div>
  );
}
