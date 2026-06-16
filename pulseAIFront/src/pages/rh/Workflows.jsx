import { useState, useMemo, useEffect, useRef } from 'react';
import { Plus, ChevronRight, CheckCircle, Circle, X, Briefcase, Calendar, RefreshCw, Search } from 'lucide-react';
import { cn } from '../../lib/utils';
import { api } from '../../lib/api';
import { useNotifications } from '../../hooks/useNotifications';

const TYPE_COLORS = {
  Onboarding: { bg: '#dcfce7', color: '#15803d' },
  Offboarding: { bg: '#fee2e2', color: '#b91c1c' },
  Mutation: { bg: '#dbeafe', color: '#1d4ed8' },
};

const STATUS_LABELS = {
  generating: 'En génération',
  draft: 'Brouillon',
  running: 'En cours',
  completed: 'Terminé',
  failed: 'Échoué'
};

export default function Workflows() {
  const { pushNotification } = useNotifications();
  const [workflows, setWorkflows] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [expanded, setExpanded] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [activeTab, setActiveTab] = useState('Tous');
  const [loading, setLoading] = useState(true);
  
  const [newType, setNewType] = useState('Onboarding');
  const [newEmployee, setNewEmployee] = useState('');
  const [offboardingDate, setOffboardingDate] = useState(new Date().toISOString().slice(0, 10));
  const [offboardingReason, setOffboardingReason] = useState('Départ planifié');
  const [employeeSearch, setEmployeeSearch] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);

  const tabs = ['Tous', 'Onboarding', 'Offboarding', 'Mutation'];

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      const data = await api.get('/workflows/');
      
      const formattedData = data.map(wf => ({
        id: wf.id,
        type: wf.type === 'onboarding' ? 'Onboarding' : wf.type === 'offboarding' ? 'Offboarding' : 'Mutation',
        employee: wf.employee_name || `Employé ${wf.employee_id.substring(0, 8)}`,
        role: wf.job_title || 'N/A',
        department: wf.department || 'N/A',
        status: wf.status,
        progress: wf.progress_percent || 0,
        startDate: wf.created_at ? new Date(wf.created_at).toLocaleDateString('fr-FR') : 'N/A',
        steps: wf.steps.map(step => ({
          id: step.id,
          label: step.name,
          done: step.status === 'done',
          assignee: step.assigned_to || 'N/A',
          rationale: step.rationale || '',
          description: step.description || '',
          sequence: step.sequence || 1,
          urgency: step.urgency || 'medium',
          step_type: step.step_type || 'manual'
        }))
      }));
      setWorkflows(formattedData);
    } catch (error) {
      console.error("Erreur lors de la récupération des workflows:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchEmployees = async () => {
    try {
      const data = await api.get('/employees/');
      setEmployees(data.items || []);
    } catch (error) {
      console.error("Erreur lors de la récupération des employés:", error);
    }
  };

  useEffect(() => {
    fetchWorkflows();
    fetchEmployees();
  }, []);

  // Close dropdown if clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const filteredWorkflows = useMemo(() => {
    if (activeTab === 'Tous') return workflows;
    return workflows.filter(wf => wf.type === activeTab);
  }, [workflows, activeTab]);

  const filteredEmployees = useMemo(() => {
    return employees.filter(emp => 
      `${emp.first_name} ${emp.last_name} ${emp.email}`.toLowerCase().includes(employeeSearch.toLowerCase())
    );
  }, [employees, employeeSearch]);

  const toggleStepLocal = (wfId, stepIdx) => {
    setWorkflows((prev) => prev.map((wf) => {
      if (wf.id !== wfId) return wf;
      const steps = wf.steps.map((s, i) => i === stepIdx ? { ...s, done: !s.done } : s);
      return { ...wf, steps };
    }));
  };

  const approveWorkflow = async (wf) => {
    try {
      const payload = {
        steps: wf.steps.map(s => ({
          id: s.id,
          name: s.label,
          description: s.description,
          step_type: s.step_type,
          assigned_to: s.assignee,
          urgency: s.urgency,
          sequence: s.sequence
        }))
      };
      await api.post(`/workflows/${wf.id}/approve`, payload);
      await fetchWorkflows();
      pushNotification({
        targetRole: 'RH',
        level: 'warning',
        title: `Workflow ${wf.type} approuvé`,
        message: `Le workflow pour ${wf.employee} a été validé et transmis au centre de notifications interne.`,
        department: wf.department || 'RH',
        link: '/rh/alertes',
      });
    } catch (error) {
      console.error("Erreur lors de l'approbation :", error);
      pushNotification({
        targetRole: 'RH',
        level: 'critical',
        title: "Échec d'approbation du workflow",
        message: error.message || "Le workflow n'a pas pu être approuvé.",
        department: 'RH',
        link: '/rh/alertes',
      });
    }
  };

  const createWorkflow = async () => {
    if (!newEmployee) return;
    try {
      if (newType === 'Onboarding') {
        await api.post('/workflows/onboarding', { employee_id: newEmployee, start_date: new Date().toISOString() });
      } else {
        await api.post('/workflows/offboarding', {
          employee_id: newEmployee,
          departure_date: offboardingDate,
          reason: offboardingReason,
        });
      }
      setShowModal(false); 
      setNewEmployee('');
      setEmployeeSearch('');
      setOffboardingDate(new Date().toISOString().slice(0, 10));
      setOffboardingReason('Départ planifié');
      await fetchWorkflows();
      pushNotification({
        targetRole: 'RH',
        level: 'info',
        title: `Nouveau workflow ${newType.toLowerCase()} généré`,
        message: 'Une notification interne a été créée pour suivre la progression du parcours.',
        department: 'RH',
        link: '/rh/alertes',
      });
    } catch (error) {
      console.error("Erreur création workflow :", error);
      pushNotification({
        targetRole: 'RH',
        level: 'critical',
        title: 'Échec de création du workflow',
        message: "La génération du workflow a échoué. Vérifiez l'employé sélectionné et réessayez.",
        department: 'RH',
        link: '/rh/alertes',
      });
    }
  };

  return (
    <div className="animate-fade-in-up space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-brand-dark">Gestion des Workflows</h1>
          <p className="mt-1 text-sm text-brand-secondary/70">Pilotez les parcours employés générés par l'IA ou manuels.</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={fetchWorkflows} className="p-2.5 rounded-xl border border-brand-secondary/20 text-brand-secondary hover:bg-brand-light transition-colors">
            <RefreshCw size={18} className={loading ? "animate-spin" : ""} />
          </button>
          <button onClick={() => setShowModal(true)}
            className="flex items-center gap-2 rounded-xl bg-brand-secondary px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-brand-dark transition-colors">
            <Plus size={15} />Nouveau workflow
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-brand-secondary/10 pb-2">
        {tabs.map(tab => (
          <button key={tab} onClick={() => setActiveTab(tab)}
            className={cn("px-4 py-2 text-sm font-medium rounded-t-lg transition-colors border-b-2", 
              activeTab === tab ? "text-brand-dark border-brand-secondary bg-brand-light/20" : "text-brand-secondary/60 border-transparent hover:text-brand-dark hover:bg-brand-light/10")}>
            {tab}
          </button>
        ))}
      </div>

      <div className="space-y-4">
        {loading && workflows.length === 0 ? (
          <div className="text-center py-10 text-brand-secondary/50 text-sm">Chargement des workflows...</div>
        ) : (
          filteredWorkflows.map((wf) => {
            const tc = TYPE_COLORS[wf.type] || { bg: '#f3f4f6', color: '#374151' };
            const isExpanded = expanded === wf.id;
            return (
              <div key={wf.id} className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm overflow-hidden transition-all">
                <button onClick={() => setExpanded(isExpanded ? null : wf.id)}
                  className="flex w-full items-center gap-4 px-5 py-4 hover:bg-brand-light/30 transition-colors text-left">
                  
                  {/* Employee Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 flex-wrap">
                      <span className="font-semibold text-brand-dark text-lg">{wf.employee}</span>
                      <span className="rounded-full px-2.5 py-0.5 text-xs font-semibold" style={{ backgroundColor: tc.bg, color: tc.color }}>{wf.type}</span>
                      <span className={cn("rounded-full px-2.5 py-0.5 text-xs font-medium border", 
                        wf.status === 'running' ? "border-blue-200 bg-blue-50 text-blue-700" :
                        wf.status === 'completed' ? "border-green-200 bg-green-50 text-green-700" :
                        wf.status === 'draft' ? "border-orange-200 bg-orange-50 text-orange-700" :
                        wf.status === 'generating' ? "border-purple-200 bg-purple-50 text-purple-700" :
                        "border-gray-200 bg-gray-50 text-gray-700"
                      )}>
                        {STATUS_LABELS[wf.status] || wf.status}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-4 mt-2 text-xs text-brand-secondary/70">
                      <span className="flex items-center gap-1.5"><Briefcase size={12}/> {wf.role} ({wf.department})</span>
                      <span className="flex items-center gap-1.5"><Calendar size={12}/> Début: {wf.startDate}</span>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="hidden sm:flex flex-col items-end gap-1 w-32 shrink-0">
                    <span className="text-xs font-bold text-brand-secondary text-right w-full">{wf.progress}% achevé</span>
                    <div className="w-full h-2 rounded-full bg-brand-light overflow-hidden">
                      <div className="h-full rounded-full bg-brand-secondary transition-all" style={{ width: `${wf.progress}%` }} />
                    </div>
                  </div>

                  <ChevronRight size={20} className={cn('text-brand-secondary/50 transition-transform shrink-0 ml-4', isExpanded && 'rotate-90')} />
                </button>

                {/* Detailed View */}
                {isExpanded && (
                  <div className="border-t border-brand-secondary/10 bg-gray-50/50 px-5 py-5">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-sm font-bold text-brand-dark">Détail des étapes</h3>
                      {wf.status === 'draft' && (
                        <button onClick={() => approveWorkflow(wf)} className="text-xs font-medium bg-brand-secondary text-white px-4 py-2 rounded-lg shadow-sm hover:bg-brand-dark transition-colors">
                          Approuver et Lancer
                        </button>
                      )}
                    </div>
                    
                    {wf.status === 'generating' ? (
                      <div className="text-sm text-brand-secondary/60 py-4 flex items-center gap-2">
                        <RefreshCw size={14} className="animate-spin" /> L'IA génère actuellement le parcours d'intégration personnalisé...
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {wf.steps.map((step, i) => (
                          <div key={i} className="flex items-start gap-3 rounded-xl bg-white p-3 border border-brand-secondary/5 shadow-sm">
                            <button onClick={() => toggleStepLocal(wf.id, i)} className="mt-0.5 cursor-default">
                              {step.done
                                ? <CheckCircle size={18} className="text-green-600 shrink-0" />
                                : <Circle size={18} className="text-brand-secondary/30 shrink-0 hover:text-brand-secondary transition-colors" />}
                            </button>
                            <div className="flex-1">
                              <div className="flex items-center justify-between">
                                <span className={cn('text-sm font-semibold', step.done ? 'line-through text-brand-secondary/50' : 'text-brand-dark')}>{step.label}</span>
                                <span className="text-xs font-medium text-brand-secondary/60 bg-brand-light/40 px-2 py-0.5 rounded-md">Assigné: {step.assignee}</span>
                              </div>
                              {step.rationale && (
                                <p className={cn("text-xs mt-1.5", step.done ? "text-gray-400" : "text-gray-600")}>
                                  <span className="font-medium text-brand-secondary/60">Raison IA :</span> {step.rationale}
                                </p>
                              )}
                            </div>
                          </div>
                        ))}
                        {wf.steps.length === 0 && <p className="text-xs text-brand-secondary/50">Aucune étape trouvée.</p>}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
        {!loading && filteredWorkflows.length === 0 && (
          <div className="text-center py-10 text-brand-secondary/50 text-sm">
            Aucun workflow trouvé dans cette catégorie.
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-bold text-brand-dark">Nouveau workflow</h2>
              <button onClick={() => setShowModal(false)} className="grid h-8 w-8 place-items-center rounded-lg hover:bg-brand-light text-brand-secondary/60"><X size={16} /></button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-widest text-brand-secondary/50 mb-1.5">Type</label>
                <select value={newType} onChange={(e) => setNewType(e.target.value)}
                  className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm outline-none focus:border-brand-secondary bg-white">
                  <option value="Onboarding">Onboarding</option>
                  <option value="Offboarding">Offboarding</option>
                </select>
              </div>
              <div className="relative" ref={dropdownRef}>
                <label className="block text-xs font-semibold uppercase tracking-widest text-brand-secondary/50 mb-1.5">Collaborateur</label>
                <div className="relative">
                  <input 
                    value={employeeSearch} 
                    onChange={(e) => {
                      setEmployeeSearch(e.target.value);
                      setNewEmployee(''); // Reset id if user types
                      setShowDropdown(true);
                    }} 
                    onFocus={() => setShowDropdown(true)}
                    placeholder="Rechercher un employé..."
                    className="w-full rounded-xl border border-brand-secondary/20 pl-9 pr-3 py-2.5 text-sm outline-none focus:border-brand-secondary" 
                  />
                  <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-secondary/40" />
                </div>
                
                {showDropdown && (
                  <div className="absolute z-10 w-full mt-1 bg-white border border-brand-secondary/10 rounded-xl shadow-xl max-h-56 overflow-y-auto">
                    {filteredEmployees.length > 0 ? (
                      filteredEmployees.map(emp => (
                        <button 
                          key={emp.id} 
                          onClick={() => {
                            setNewEmployee(emp.id);
                            setEmployeeSearch(`${emp.first_name} ${emp.last_name}`);
                            setShowDropdown(false);
                          }}
                          className={cn("w-full text-left px-4 py-2.5 text-sm transition-colors border-b border-brand-secondary/5 last:border-0",
                            newEmployee === emp.id ? "bg-brand-light/50" : "hover:bg-brand-light/30")}
                        >
                          <div className="font-semibold text-brand-dark">{emp.first_name} {emp.last_name}</div>
                          <div className="text-xs text-brand-secondary/60 mt-0.5">{emp.email} • {emp.department || 'Sans dépt.'}</div>
                        </button>
                      ))
                    ) : (
                      <div className="px-4 py-3 text-sm text-brand-secondary/60 text-center">Aucun employé trouvé.</div>
                    )}
                  </div>
                )}
              </div>

              {newType === 'Offboarding' && (
                <>
                  <div>
                    <label className="block text-xs font-semibold uppercase tracking-widest text-brand-secondary/50 mb-1.5">Date de départ</label>
                    <input
                      type="date"
                      value={offboardingDate}
                      onChange={(e) => setOffboardingDate(e.target.value)}
                      className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm outline-none focus:border-brand-secondary"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold uppercase tracking-widest text-brand-secondary/50 mb-1.5">Motif</label>
                    <input
                      value={offboardingReason}
                      onChange={(e) => setOffboardingReason(e.target.value)}
                      placeholder="Ex: départ volontaire, fin de mission..."
                      className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm outline-none focus:border-brand-secondary"
                    />
                  </div>
                </>
              )}
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={createWorkflow} disabled={!newEmployee} className="flex-1 rounded-xl bg-brand-secondary py-2.5 text-sm font-medium text-white hover:bg-brand-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                Déclencher la génération IA
              </button>
              <button onClick={() => setShowModal(false)} className="flex-1 rounded-xl border border-brand-secondary/20 py-2.5 text-sm font-medium text-brand-secondary hover:bg-brand-light transition-colors">
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
