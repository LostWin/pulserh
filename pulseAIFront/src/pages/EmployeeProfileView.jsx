import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  User, Briefcase, ChevronLeft, MapPin, CheckCircle2, Shield,
  CalendarDays, FileText, CheckSquare, Layers, Lock
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../lib/api';
import FieldVisibilityBadge from '../components/ui/FieldVisibilityBadge';

function Card({ children, className = '' }) {
  return (
    <div className={`rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-5 ${className}`}>
      {children}
    </div>
  );
}

function SectionLabel({ children }) {
  return (
    <span className="text-[10px] font-bold uppercase tracking-widest text-brand-secondary/40">
      {children}
    </span>
  );
}

function FieldRow({ label, value, visibility }) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-1.5">
        <SectionLabel>{label}</SectionLabel>
        <FieldVisibilityBadge visibility={visibility} />
      </div>
      <div className="w-full rounded-xl border border-transparent bg-transparent text-sm font-medium text-brand-dark p-0">
        {value || 'Non renseigné'}
      </div>
    </div>
  );
}

export default function EmployeeProfileView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { role } = useAuth();
  
  const [employee, setEmployee] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('info'); // info, attendancies, contracts, projects, tasks
  
  // Rôle de la personne qui regarde (hr ou manager)
  const isHr = role === 'rh' || role === 'admin';
  const isManager = role === 'manager';

  useEffect(() => {
    const fetchEmployee = async () => {
      try {
        const data = await api.get(`/employees/${id}`);
        setEmployee(data);
      } catch (err) {
        console.error("Failed to fetch employee", err);
      } finally {
        setLoading(false);
      }
    };
    fetchEmployee();
  }, [id]);

  if (loading) {
    return <div className="py-16 text-center text-sm font-medium text-brand-secondary/80">Chargement de la fiche employé...</div>;
  }
  
  if (!employee) {
    return <div className="py-16 text-center text-sm font-medium text-brand-danger">Employé introuvable ou accès refusé.</div>;
  }

  const fullName = `${employee.first_name} ${employee.last_name}`;
  const fieldVisibility = employee._field_visibility || {};
  const avatarSrc = `https://ui-avatars.com/api/?name=${encodeURIComponent(fullName)}&background=1F524B&color=fff&size=80`;

  return (
    <div className="animate-fade-in-up space-y-5">
      {/* Back button */}
      <button 
        onClick={() => navigate(-1)} 
        className="flex items-center gap-2 text-sm font-medium text-brand-secondary hover:text-brand-dark transition-colors"
      >
        <ChevronLeft size={16} /> Retour à la liste
      </button>

      {/* Permission banner */}
      <div className="flex items-center gap-2 rounded-xl border border-brand-secondary/20 bg-brand-secondary/5 px-4 py-2.5">
        <Shield size={14} className="text-brand-secondary shrink-0" />
        <p className="text-xs font-semibold text-brand-secondary">
          {isHr 
            ? "Mode RH — Vous consultez la fiche complète de ce collaborateur." 
            : "Mode Manager — Vous consultez la fiche de ce membre de votre équipe."}
        </p>
      </div>

      {/* HEADER */}
      <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm overflow-hidden">
        <div className="h-24 bg-gradient-to-r from-brand-secondary/25 via-brand-secondary/10 to-transparent" />
        <div className="flex flex-col gap-4 px-6 pb-6 sm:flex-row sm:items-end -mt-10">
          <div className="relative shrink-0">
            <div className="h-20 w-20 rounded-2xl border-4 border-white shadow-md bg-brand-secondary/20 overflow-hidden">
              <img src={avatarSrc} alt={fullName} className="h-full w-full object-cover" />
            </div>
            <span className="absolute -bottom-1 -right-1 flex h-5 items-center gap-1 rounded-full bg-emerald-500 px-1.5 text-[9px] font-bold text-white uppercase tracking-wide shadow">
              <span className="h-1.5 w-1.5 rounded-full bg-white" />
              {employee.status || 'Actif'}
            </span>
          </div>
          <div className="flex-1 pb-1">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-xl font-bold text-brand-dark">{fullName}</h1>
              <span className="rounded-md bg-brand-secondary/10 px-2 py-0.5 text-[10px] font-semibold text-brand-secondary tracking-wide">
                EMP ID: {employee.id.substring(0, 8)}
              </span>
            </div>
            <p className="mt-0.5 text-sm text-brand-secondary/70">
              {employee.contract_type || 'Collaborateur'}&nbsp;·&nbsp;
              <span className="text-brand-secondary font-semibold">{employee.department || 'Non assigné'}</span>
            </p>
          </div>
        </div>
      </div>

      {/* TAB NAVIGATION */}
      <div className="flex border-b border-brand-secondary/10 overflow-x-auto">
        <button
          onClick={() => setActiveTab('info')}
          className={`flex whitespace-nowrap items-center gap-2 px-5 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'info' ? 'border-brand-secondary text-brand-dark' : 'border-transparent text-brand-secondary/60 hover:text-brand-dark'}`}
        >
          <User size={16} /> Informations
        </button>
        
        {isHr && (
          <>
            <button
              onClick={() => setActiveTab('attendancies')}
              className={`flex whitespace-nowrap items-center gap-2 px-5 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'attendancies' ? 'border-brand-secondary text-brand-dark' : 'border-transparent text-brand-secondary/60 hover:text-brand-dark'}`}
            >
              <CalendarDays size={16} /> Présences & Absences
            </button>
            <button
              onClick={() => setActiveTab('contracts')}
              className={`flex whitespace-nowrap items-center gap-2 px-5 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'contracts' ? 'border-brand-secondary text-brand-dark' : 'border-transparent text-brand-secondary/60 hover:text-brand-dark'}`}
            >
              <FileText size={16} /> Contrats & Avenants
            </button>
          </>
        )}

        {isManager && (
          <>
            <button
              onClick={() => setActiveTab('projects')}
              className={`flex whitespace-nowrap items-center gap-2 px-5 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'projects' ? 'border-brand-secondary text-brand-dark' : 'border-transparent text-brand-secondary/60 hover:text-brand-dark'}`}
            >
              <Layers size={16} /> Projets
            </button>
            <button
              onClick={() => setActiveTab('tasks')}
              className={`flex whitespace-nowrap items-center gap-2 px-5 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'tasks' ? 'border-brand-secondary text-brand-dark' : 'border-transparent text-brand-secondary/60 hover:text-brand-dark'}`}
            >
              <CheckSquare size={16} /> Tâches & Suivi
            </button>
          </>
        )}
      </div>

      {/* TAB CONTENTS */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
        
        {/* COMMON TAB: INFORMATIONS */}
        {activeTab === 'info' && (
          <div className="space-y-5 lg:col-span-3 grid grid-cols-1 lg:grid-cols-2 gap-5">
            <Card>
              <div className="flex items-center gap-2 mb-4">
                <div className="grid h-7 w-7 place-items-center rounded-lg bg-brand-secondary/10">
                  <User size={14} className="text-brand-secondary" />
                </div>
                <h2 className="text-sm font-bold text-brand-dark">Informations Personnelles</h2>
              </div>
              <div className="space-y-4">
                <FieldRow label="Nom Complet" value={fullName} visibility={fieldVisibility.first_name} />
                <FieldRow label="Email Professionnel" value={employee.email} visibility={fieldVisibility.email} />
                <FieldRow label="Date de naissance" value="Non renseignée" />
                <FieldRow label="Téléphone" value={employee.phone || 'Non renseigné'} visibility={fieldVisibility.phone} />
              </div>
            </Card>

            <Card>
              <div className="flex items-center gap-2 mb-4">
                <div className="grid h-7 w-7 place-items-center rounded-lg bg-brand-secondary/10">
                  <Briefcase size={14} className="text-brand-secondary" />
                </div>
                <h2 className="text-sm font-bold text-brand-dark">Informations Professionnelles</h2>
              </div>
              <div className="grid grid-cols-2 gap-x-6 gap-y-4">
                <FieldRow label="Poste" value={employee.contract_type} visibility={fieldVisibility.contract_type} />
                <FieldRow label="Département" value={employee.department} visibility={fieldVisibility.department} />
                <FieldRow label="Date d'embauche" value={employee.hire_date || 'Non renseignée'} visibility={fieldVisibility.hire_date} />
                <FieldRow label="Type de contrat" value={employee.contract_type} />
                <FieldRow label="Salaire Annuel" value={employee.salary ? `${employee.salary} €` : 'Non renseigné'} visibility={fieldVisibility.salary} />
              </div>
              <div className="mt-3 flex items-center gap-1.5">
                <MapPin size={12} className="text-brand-secondary/60" />
                <span className="text-xs text-brand-secondary/70">Bureau localisé</span>
              </div>
            </Card>
          </div>
        )}

        {/* HR TABS */}
        {activeTab === 'attendancies' && (
          <div className="lg:col-span-3">
            <Card>
              <h2 className="text-sm font-bold text-brand-dark mb-4">Historique des présences</h2>
              <div className="flex flex-col items-center justify-center py-10 bg-brand-light/50 rounded-xl border border-dashed border-brand-secondary/30">
                <CalendarDays size={32} className="text-brand-secondary/40 mb-3" />
                <p className="text-sm font-medium text-brand-dark">Aucune donnée de présence récente</p>
                <p className="text-xs text-brand-secondary/70 mt-1">L'historique de pointage et des congés apparaîtra ici.</p>
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'contracts' && (
          <div className="lg:col-span-3">
            <Card>
              <h2 className="text-sm font-bold text-brand-dark mb-4">Contrats et documents légaux</h2>
              <div className="flex flex-col items-center justify-center py-10 bg-brand-light/50 rounded-xl border border-dashed border-brand-secondary/30">
                <FileText size={32} className="text-brand-secondary/40 mb-3" />
                <p className="text-sm font-medium text-brand-dark">Aucun document attaché</p>
                <p className="text-xs text-brand-secondary/70 mt-1">Les avenants et fiches de paie seront listés ici.</p>
              </div>
            </Card>
          </div>
        )}

        {/* MANAGER TABS */}
        {activeTab === 'projects' && (
          <div className="lg:col-span-3">
            <Card>
              <h2 className="text-sm font-bold text-brand-dark mb-4">Projets Actifs</h2>
              <div className="flex flex-col items-center justify-center py-10 bg-brand-light/50 rounded-xl border border-dashed border-brand-secondary/30">
                <Layers size={32} className="text-brand-secondary/40 mb-3" />
                <p className="text-sm font-medium text-brand-dark">Aucun projet assigné</p>
                <p className="text-xs text-brand-secondary/70 mt-1">Les projets sur lesquels {employee.first_name} travaille apparaîtront ici.</p>
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'tasks' && (
          <div className="lg:col-span-3 grid gap-5 lg:grid-cols-2">
            <Card>
              <h2 className="text-sm font-bold text-brand-dark mb-4">Tâches en cours</h2>
              <div className="space-y-3">
                <div className="p-3 border border-brand-secondary/10 rounded-xl bg-brand-light/30">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold text-brand-dark">Migration base de données</span>
                    <span className="text-[10px] bg-brand-warning/10 text-brand-warning px-2 py-0.5 rounded-full font-bold">En cours</span>
                  </div>
                  <div className="w-full bg-brand-secondary/10 rounded-full h-1.5">
                    <div className="bg-brand-warning h-1.5 rounded-full" style={{ width: '60%' }}></div>
                  </div>
                  <p className="text-[10px] text-right text-brand-secondary/60 mt-1">60% complété</p>
                </div>
                <div className="p-3 border border-brand-secondary/10 rounded-xl bg-brand-light/30">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold text-brand-dark">Documentation API</span>
                    <span className="text-[10px] bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full font-bold">Terminé</span>
                  </div>
                  <div className="w-full bg-brand-secondary/10 rounded-full h-1.5">
                    <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: '100%' }}></div>
                  </div>
                  <p className="text-[10px] text-right text-brand-secondary/60 mt-1">100% complété</p>
                </div>
              </div>
            </Card>
            <Card>
              <h2 className="text-sm font-bold text-brand-dark mb-4">Niveau de Complétion Global</h2>
              <div className="flex items-center justify-center py-6">
                <div className="relative h-32 w-32 rounded-full border-8 border-brand-light flex items-center justify-center">
                  <div className="absolute inset-0 rounded-full border-8 border-brand-secondary" style={{ clipPath: 'polygon(0 0, 100% 0, 100% 100%, 0 100%, 0 0)' }}></div>
                  <div className="text-center">
                    <span className="text-3xl font-black text-brand-dark">80<span className="text-lg">%</span></span>
                    <p className="text-[10px] uppercase font-bold text-brand-secondary/50">Ce mois-ci</p>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        )}

      </div>
    </div>
  );
}
