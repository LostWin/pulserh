import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Briefcase, ArrowLeft, ArrowUpRight, Navigation, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { api } from '../../lib/api';
import PageHeader from '../../components/PageHeader';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import Avatar from '../../components/ui/Avatar';

export default function EmployeeCarriereView() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [data, setData] = useState(null);
  const [employee, setEmployee] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        setLoading(true);
        const [careerData, empData] = await Promise.all([
          api.get(`/employees/${id}/career`),
          api.get(`/employees/${id}`)
        ]);
        if (mounted) {
          setData(careerData);
          setEmployee(empData);
        }
      } catch (err) {
        if (mounted) setError('Impossible de charger les détails de carrière.');
      } finally {
        if (mounted) setLoading(false);
      }
    };
    load();
    return () => { mounted = false; };
  }, [id]);

  if (loading) return <div className="p-8 text-center text-brand-secondary">Chargement...</div>;
  if (error) return <div className="p-8 text-center text-brand-warning">{error}</div>;
  if (!data || !employee) return null;

  return (
    <div className="animate-fade-in-up space-y-6">
      <button 
        onClick={() => navigate('/rh/carrieres')}
        className="flex items-center gap-2 text-sm font-medium text-brand-secondary hover:text-brand-dark transition"
      >
        <ArrowLeft size={16} />
        Retour à l'annuaire carrières
      </button>

      <PageHeader 
        title="Parcours & Carrière" 
        subtitle="Historique des mobilités, promotions et plan de développement"
      />

      <Card className="flex items-center gap-4 p-5">
        <Avatar name={`${employee.first_name} ${employee.last_name}`} size="lg" />
        <div>
          <h2 className="text-xl font-bold text-brand-dark">{employee.first_name} {employee.last_name}</h2>
          <div className="flex items-center gap-2 text-sm text-brand-secondary/70">
            <span>{employee.job_title || 'Collaborateur'}</span>
            <span>•</span>
            <span>{employee.department || 'Non assigné'}</span>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* PROMOTIONS */}
        <Card className="p-5">
          <div className="mb-4 flex items-center gap-2 border-b border-brand-secondary/10 pb-3 font-semibold text-brand-dark">
            <ArrowUpRight size={18} className="text-brand-primary" />
            Historique des Promotions
          </div>
          {data.promotions.length > 0 ? (
            <div className="space-y-4">
              {data.promotions.map((promo) => (
                <div key={promo.id} className="relative pl-6 before:absolute before:left-2 before:top-2 before:h-full before:w-[2px] before:bg-brand-secondary/20 last:before:hidden">
                  <div className="absolute left-[3px] top-[6px] h-3 w-3 rounded-full border-2 border-white bg-brand-primary"></div>
                  <div className="text-sm font-medium text-brand-dark">{promo.new_job_title}</div>
                  {promo.previous_job_title && (
                    <div className="text-xs text-brand-secondary/70">Précédemment : {promo.previous_job_title}</div>
                  )}
                  <div className="mt-1 text-xs font-semibold text-brand-primary/80">{promo.effective_date_label}</div>
                  {promo.notes && <div className="mt-2 text-xs italic text-brand-secondary/60">{promo.notes}</div>}
                </div>
              ))}
            </div>
          ) : (
            <div className="py-8 text-center text-sm text-brand-secondary/60">
              Aucune promotion enregistrée
            </div>
          )}
        </Card>

        {/* MOBILITÉ */}
        <Card className="p-5">
          <div className="mb-4 flex items-center gap-2 border-b border-brand-secondary/10 pb-3 font-semibold text-brand-dark">
            <Navigation size={18} className="text-brand-primary" />
            Demandes de Mobilité
          </div>
          {data.mobility_requests.length > 0 ? (
            <div className="space-y-4">
              {data.mobility_requests.map((mob) => (
                <div key={mob.id} className="rounded-xl border border-brand-secondary/10 bg-brand-light/30 p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="font-medium text-brand-dark">{mob.request_type === 'internal_move' ? 'Mobilité interne' : 'Autre'}</div>
                      <div className="mt-1 text-sm text-brand-secondary">Cible : {mob.target_job_title || mob.target_department || 'Non précisée'}</div>
                    </div>
                    <Badge variant={mob.status === 'approved' ? 'success' : mob.status === 'rejected' ? 'error' : 'warning'}>
                      {mob.status}
                    </Badge>
                  </div>
                  <div className="mt-3 flex items-center gap-4 text-xs text-brand-secondary/70">
                    <span className="flex items-center gap-1"><Clock size={12} /> {mob.requested_at_label}</span>
                    {mob.reviewed_at_label && <span className="flex items-center gap-1"><CheckCircle size={12} /> Traité le {mob.reviewed_at_label}</span>}
                  </div>
                  {mob.rationale && (
                    <div className="mt-3 rounded-lg bg-white p-2 text-xs text-brand-dark/80">
                      "{mob.rationale}"
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="py-8 text-center text-sm text-brand-secondary/60">
              Aucune demande de mobilité
            </div>
          )}
        </Card>

        {/* CIBLES CARRIÈRE */}
        <Card className="p-5 lg:col-span-2">
          <div className="mb-4 flex items-center gap-2 border-b border-brand-secondary/10 pb-3 font-semibold text-brand-dark">
            <Briefcase size={18} className="text-brand-primary" />
            Plans de Carrière / Relève
          </div>
          {data.career_paths.length > 0 ? (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {data.career_paths.map((path) => (
                <div key={path.id} className="rounded-xl border border-brand-secondary/10 p-4">
                  <div className="font-semibold text-brand-dark">{path.target_title}</div>
                  <div className="mt-2 flex items-center gap-2">
                    <Badge variant={path.readiness_level === 'ready_now' ? 'success' : path.readiness_level === 'ready_soon' ? 'warning' : 'default'}>
                      {path.readiness_level === 'ready_now' ? 'Prêt maintenant' : path.readiness_level === 'ready_soon' ? 'Bientôt prêt' : 'Émergent'}
                    </Badge>
                  </div>
                  {path.mentor_name && (
                    <div className="mt-3 text-sm text-brand-secondary">
                      Mentor identifié : <span className="font-medium text-brand-dark">{path.mentor_name}</span>
                    </div>
                  )}
                  {path.next_step && (
                    <div className="mt-3 flex items-start gap-2 rounded-lg bg-brand-light p-3 text-xs text-brand-dark">
                      <AlertCircle size={14} className="mt-0.5 text-brand-primary" />
                      <div>
                        <span className="font-semibold">Prochaine action :</span>
                        <div className="mt-1 text-brand-secondary/80">{path.next_step}</div>
                      </div>
                    </div>
                  )}
                  <div className="mt-3 text-right text-[10px] text-brand-secondary/50 uppercase tracking-widest">
                    Mis à jour : {path.last_reviewed_at_label || '—'}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-8 text-center text-sm text-brand-secondary/60">
              Aucun plan de succession / relève ciblé
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
