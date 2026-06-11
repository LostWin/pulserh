import { useState } from 'react';
import { Plus, ChevronRight, CheckCircle, Circle, Clock, User, Users, X } from 'lucide-react';
import { cn } from '../../lib/utils';

const INITIAL_WORKFLOWS = [
  {
    id: 1, name: 'Onboarding — Emma Rossi', type: 'Onboarding', employee: 'Emma Rossi', progress: 80,
    steps: [
      { label: 'Signature contrat', done: true },
      { label: 'Création compte IT', done: true },
      { label: 'Formation RGPD', done: true },
      { label: 'Rencontre buddy', done: false },
      { label: 'Validation période d\'essai', done: false },
    ],
  },
  {
    id: 2, name: 'Offboarding — Noah Petit', type: 'Offboarding', employee: 'Noah Petit', progress: 40,
    steps: [
      { label: 'Entretien de départ', done: true },
      { label: 'Restitution matériel', done: true },
      { label: 'Solde de tout compte', done: false },
      { label: 'Désactivation accès', done: false },
      { label: 'Archivage dossier', done: false },
    ],
  },
  {
    id: 3, name: 'Mutation — Théo Roux', type: 'Mutation', employee: 'Théo Roux', progress: 60,
    steps: [
      { label: 'Accord manager sortant', done: true },
      { label: 'Accord manager entrant', done: true },
      { label: 'Avenant signé', done: true },
      { label: 'Transfert dossier', done: false },
      { label: 'Mise à jour SIRH', done: false },
    ],
  },
];

const TYPE_COLORS = {
  Onboarding: { bg: '#dcfce7', color: '#15803d' },
  Offboarding: { bg: '#fee2e2', color: '#b91c1c' },
  Mutation: { bg: '#dbeafe', color: '#1d4ed8' },
};

export default function Workflows() {
  const [workflows, setWorkflows] = useState(INITIAL_WORKFLOWS);
  const [expanded, setExpanded] = useState(1);
  const [showModal, setShowModal] = useState(false);
  const [newName, setNewName] = useState('');
  const [newType, setNewType] = useState('Onboarding');
  const [newEmployee, setNewEmployee] = useState('');

  const toggleStep = (wfId, stepIdx) => {
    setWorkflows((prev) => prev.map((wf) => {
      if (wf.id !== wfId) return wf;
      const steps = wf.steps.map((s, i) => i === stepIdx ? { ...s, done: !s.done } : s);
      const progress = Math.round((steps.filter((s) => s.done).length / steps.length) * 100);
      return { ...wf, steps, progress };
    }));
  };

  const createWorkflow = () => {
    if (!newName || !newEmployee) return;
    setWorkflows((prev) => [{
      id: Date.now(), name: newName, type: newType, employee: newEmployee, progress: 0,
      steps: [
        { label: 'Étape 1 — À configurer', done: false },
        { label: 'Étape 2 — À configurer', done: false },
        { label: 'Étape 3 — À configurer', done: false },
      ],
    }, ...prev]);
    setShowModal(false); setNewName(''); setNewEmployee('');
  };

  return (
    <div className="animate-fade-in-up space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-brand-dark">Workflows</h1>
          <p className="mt-1 text-sm text-brand-secondary/70">Pilotez les processus d'onboarding, offboarding et mutations.</p>
        </div>
        <button onClick={() => setShowModal(true)}
          className="flex items-center gap-2 rounded-xl bg-brand-secondary px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-brand-dark transition-colors">
          <Plus size={15} />Nouveau workflow
        </button>
      </div>

      <div className="space-y-4">
        {workflows.map((wf) => {
          const tc = TYPE_COLORS[wf.type] || { bg: '#f3f4f6', color: '#374151' };
          const isExpanded = expanded === wf.id;
          return (
            <div key={wf.id} className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm overflow-hidden">
              <button onClick={() => setExpanded(isExpanded ? null : wf.id)}
                className="flex w-full items-center gap-4 px-5 py-4 hover:bg-brand-light/30 transition-colors text-left">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-semibold text-brand-dark">{wf.name}</span>
                    <span className="rounded-full px-2.5 py-0.5 text-xs font-semibold" style={{ backgroundColor: tc.bg, color: tc.color }}>{wf.type}</span>
                  </div>
                  <div className="flex items-center gap-3 mt-2">
                    <div className="flex-1 h-1.5 rounded-full bg-brand-light overflow-hidden max-w-48">
                      <div className="h-full rounded-full bg-brand-secondary transition-all" style={{ width: `${wf.progress}%` }} />
                    </div>
                    <span className="text-xs font-bold text-brand-secondary">{wf.progress}%</span>
                    <span className="text-xs text-brand-secondary/50 flex items-center gap-1"><User size={11} />{wf.employee}</span>
                  </div>
                </div>
                <ChevronRight size={16} className={cn('text-brand-secondary/50 transition-transform shrink-0', isExpanded && 'rotate-90')} />
              </button>

              {isExpanded && (
                <div className="border-t border-brand-secondary/10 px-5 py-4">
                  <div className="space-y-2">
                    {wf.steps.map((step, i) => (
                      <button key={i} onClick={() => toggleStep(wf.id, i)}
                        className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 hover:bg-brand-light/50 transition-colors text-left">
                        {step.done
                          ? <CheckCircle size={17} className="text-brand-secondary shrink-0" />
                          : <Circle size={17} className="text-brand-secondary/30 shrink-0" />}
                        <span className={cn('text-sm', step.done ? 'line-through text-brand-secondary/50' : 'text-brand-dark')}>{step.label}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
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
                <label className="block text-xs font-semibold uppercase tracking-widest text-brand-secondary/50 mb-1.5">Nom du workflow</label>
                <input value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="ex: Onboarding — Prénom Nom"
                  className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm outline-none focus:border-brand-secondary" />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-widest text-brand-secondary/50 mb-1.5">Type</label>
                <select value={newType} onChange={(e) => setNewType(e.target.value)}
                  className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm outline-none focus:border-brand-secondary bg-white">
                  <option>Onboarding</option><option>Offboarding</option><option>Mutation</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-widest text-brand-secondary/50 mb-1.5">Collaborateur</label>
                <input value={newEmployee} onChange={(e) => setNewEmployee(e.target.value)} placeholder="Prénom Nom"
                  className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm outline-none focus:border-brand-secondary" />
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={createWorkflow} className="flex-1 rounded-xl bg-brand-secondary py-2.5 text-sm font-medium text-white hover:bg-brand-dark transition-colors">Créer</button>
              <button onClick={() => setShowModal(false)} className="flex-1 rounded-xl border border-brand-secondary/20 py-2.5 text-sm font-medium text-brand-secondary hover:bg-brand-light transition-colors">Annuler</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
