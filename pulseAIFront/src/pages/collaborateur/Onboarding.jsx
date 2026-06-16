import { useEffect, useMemo, useState } from 'react';
import { BookOpen, CheckCircle2, Circle, FileSignature, Monitor, Users } from 'lucide-react';

import { api } from '../../lib/api';

const ICONS = {
  profile: CheckCircle2,
  contract: FileSignature,
  it: Monitor,
  team: Users,
};

export default function Onboarding() {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [recommendations, setRecommendations] = useState([]);

  useEffect(() => {
    let mounted = true;
    api.get('/onboarding/me')
      .then(async (payload) => {
        if (!mounted) return;
        setData(payload);
        try {
          const me = await api.get('/employees/me');
          const recos = await api.get(`/trainings/recommendations/${me.id}`);
          if (mounted) setRecommendations(recos || []);
        } catch {
          if (mounted) setRecommendations([]);
        }
      })
      .catch((err) => {
        if (mounted) setError(err.message || 'Impossible de charger le parcours d’onboarding.');
      });
    return () => {
      mounted = false;
    };
  }, []);

  const path = data?.path || [];
  const tasks = data?.tasks || [];
  const progressPercent = data?.progress_percent || 0;
  const completedText = useMemo(() => `${data?.completed_steps || 0} / ${data?.total_steps || 0} étapes`, [data]);

  return (
    <div className="animate-fade-in-up space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-brand-dark">{data?.title || 'Onboarding'}</h1>
        <p className="mt-1 text-sm text-brand-secondary/70">{data?.subtitle || 'Chargement du parcours...'}</p>
        {error ? <p className="mt-2 text-sm text-brand-warning">{error}</p> : null}
      </div>

      <div className="rounded-2xl border border-brand-secondary/10 bg-white p-5 shadow-sm">
        <div className="mb-5 flex items-center justify-between">
          <p className="text-sm font-bold text-brand-dark">Votre parcours</p>
          <span className="rounded-full bg-brand-secondary/10 px-3 py-1 text-xs font-bold text-brand-secondary">{completedText}</span>
        </div>
        <div className="relative flex items-center justify-between gap-3">
          <div className="absolute left-6 right-6 top-5 h-0.5 bg-brand-secondary/15" />
          <div className="absolute left-6 top-5 h-0.5 bg-brand-secondary transition-all duration-700" style={{ width: `${Math.min(88, progressPercent)}%` }} />
          {path.map((step) => {
            const Icon = ICONS[step.id] || Circle;
            const done = step.status === 'done';
            return (
              <div key={step.id} className="relative z-10 flex w-1/4 flex-col items-center gap-2">
                <div className={`flex h-10 w-10 items-center justify-center rounded-full shadow-sm ${done ? 'bg-brand-secondary text-white' : 'border-2 border-brand-warning bg-brand-warning/10 text-brand-warning'}`}>
                  <Icon size={16} />
                </div>
                <span className={`text-center text-[10px] font-semibold ${done ? 'text-brand-secondary' : 'text-brand-warning'}`}>{step.label}</span>
              </div>
            );
          })}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="space-y-5 lg:col-span-2">
          <div className="rounded-2xl border border-brand-secondary/10 bg-white shadow-sm overflow-hidden">
            <div className="border-b border-brand-secondary/8 px-5 py-4">
              <h2 className="text-sm font-bold text-brand-dark">Checklist réelle</h2>
            </div>
            <ul className="divide-y divide-slate-50">
              {tasks.map((task) => (
                <li key={task.id} className="px-5 py-4">
                  <div className="flex items-start gap-3">
                    {task.status === 'done' ? <CheckCircle2 className="mt-0.5 text-brand-secondary" size={18} /> : <Circle className="mt-0.5 text-brand-warning" size={18} />}
                    <div>
                      <div className="font-medium text-brand-dark">{task.label}</div>
                      <p className="mt-1 text-sm text-brand-secondary/70">{task.detail}</p>
                      {task.due_label ? <p className="mt-1 text-xs text-brand-secondary/50">Échéance: {task.due_label}</p> : null}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="space-y-5">
          <div className="rounded-2xl border border-brand-secondary/10 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <BookOpen size={16} className="text-brand-secondary" />
              <h2 className="text-sm font-bold text-brand-dark">Ressources</h2>
            </div>
            <div className="space-y-3">
              {(data?.resources || []).map((resource) => (
                <div key={resource.label} className="rounded-xl bg-brand-light px-4 py-3 text-sm font-medium text-brand-dark">{resource.label}</div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-brand-secondary/10 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <BookOpen size={16} className="text-brand-secondary" />
              <h2 className="text-sm font-bold text-brand-dark">Formations recommandées</h2>
            </div>
            <div className="space-y-3">
              {recommendations.slice(0, 3).map((item) => (
                <div key={item.training_id} className="rounded-xl border border-brand-secondary/10 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="font-medium text-brand-dark">{item.title}</div>
                      <div className="text-xs text-brand-secondary/70">{item.provider || 'Catalogue interne'} · {item.target_skill_name || 'Montée en compétence'}</div>
                    </div>
                    <span className="rounded-full bg-brand-secondary/10 px-2 py-1 text-[10px] font-bold text-brand-secondary">{item.relevance_score}%</span>
                  </div>
                  <div className="mt-2 text-xs text-brand-secondary/80">
                    {item.reasons[0]}
                  </div>
                </div>
              ))}
              {!recommendations.length ? <div className="rounded-xl bg-brand-light px-4 py-3 text-sm text-brand-secondary/70">Les suggestions de formation apparaîtront ici dès qu’un besoin sera détecté.</div> : null}
            </div>
          </div>

          <div className="rounded-2xl border border-brand-secondary/10 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <Users size={16} className="text-brand-secondary" />
              <h2 className="text-sm font-bold text-brand-dark">Contacts utiles</h2>
            </div>
            <div className="space-y-3">
              {(data?.contacts || []).map((contact) => (
                <div key={contact.name} className="flex items-center gap-3 rounded-xl border border-brand-secondary/10 p-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full text-xs font-bold text-white" style={{ backgroundColor: contact.color }}>{contact.initials}</div>
                  <div>
                    <div className="font-medium text-brand-dark">{contact.name}</div>
                    <div className="text-xs text-brand-secondary/70">{contact.role}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
