import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { CalendarDays, CheckCircle, Circle, FileText, Download, Bot, Shield, TrendingUp, Plane, Activity, Lock } from 'lucide-react';

import { useAuth } from '../../contexts/AuthContext';
import { api } from '../../lib/api';
import { cn } from '../../lib/utils';

export default function CollaborateurDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const handleSuggestionClick = (msg) => {
    navigate('/collaborateur/assistant', { state: { initialMessage: msg } });
  };

  useEffect(() => {
    let mounted = true;
    const loadDashboard = async () => {
      try {
        const data = await api.get('/dashboard/collaborateur-summary');
        if (mounted) setDashboard(data);
      } catch (err) {
        if (mounted) setError(err.message || 'Impossible de charger votre dashboard.');
      } finally {
        if (mounted) setLoading(false);
      }
    };
    loadDashboard();
    return () => {
      mounted = false;
    };
  }, []);

  const firstName = dashboard?.summary?.first_name || user?.name?.split(' ')[0] || 'Alex';
  const today = new Date().toLocaleDateString('fr-FR', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
  });

  const onboarding = dashboard?.onboarding || [];
  const doneSteps = onboarding.filter((step) => step.done).length;
  const onboardingPct = onboarding.length ? Math.round((doneSteps / onboarding.length) * 100) : 0;

  const currentBalance = dashboard?.summary?.leave_current_balance || 0;
  const totalBalance = dashboard?.summary?.leave_total_balance || 30;
  const usedBalance = Math.max(0, totalBalance - currentBalance);
  const recentDocuments = dashboard?.recent_documents || [];

  const complianceLabel = useMemo(() => {
    if (!dashboard) return '—';
    return `${dashboard.summary.compliance_score}%`;
  }, [dashboard]);

  const downloadDocument = async (doc) => {
    try {
      const blob = await api.get(`/documents/${doc.id}/download`, { responseType: 'blob' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = doc.name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message || 'Impossible de télécharger ce document.');
    }
  };

  if (loading) {
    return <div className="animate-pulse rounded-2xl bg-white p-8 text-sm text-brand-secondary">Chargement du dashboard…</div>;
  }

  if (error && !dashboard) {
    return <div className="rounded-2xl bg-white p-8 text-sm text-brand-warning">{error}</div>;
  }

  return (
    <div className="animate-fade-in-up space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between mb-8">
        <div>
          <h1 className="text-[32px] font-bold text-brand-dark">Bonjour {firstName}</h1>
          <p className="mt-1 text-[15px] text-gray-500">Voici un aperçu de votre parcours professionnel aujourd&apos;hui.</p>
          {error ? <p className="mt-2 text-sm text-brand-warning">{error}</p> : null}
        </div>
        <div className="flex items-center gap-3 rounded-2xl bg-white px-4 py-3 shadow-sm border border-gray-50">
          <CalendarDays className="text-gray-400 w-5 h-5" />
          <div>
            <div className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">AUJOURD&apos;HUI</div>
            <div className="text-sm font-medium text-brand-dark">{today}</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Onboarding journey – visible uniquement si un onboarding n'est pas terminé */}
      {onboarding.length > 0 && onboardingPct < 100 && (
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 shadow-sm border border-gray-50 flex flex-col justify-between">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-lg font-bold text-brand-dark">Onboarding Journey</h2>
              <p className="text-sm text-gray-500 mt-1">Vous êtes sur la bonne voie. Les prochaines étapes sont alimentées par votre dossier réel.</p>
            </div>
            <span className="bg-brand-warning text-white text-[10px] font-bold px-3 py-1.5 rounded-full uppercase tracking-wider shadow-sm">
              In Progress
            </span>
          </div>

          <div className="flex flex-col md:flex-row gap-8 items-center mt-2">
            <div className="relative w-36 h-36 flex-shrink-0">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="40" stroke="currentColor" strokeWidth="8" fill="transparent" className="text-gray-100" />
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="transparent"
                  strokeDasharray="251.2"
                  strokeDashoffset={251.2 - (251.2 * onboardingPct) / 100}
                  className="text-brand-secondary transition-all duration-1000 ease-out"
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-bold text-brand-dark">{onboardingPct}%</span>
                <span className="text-[10px] font-semibold uppercase tracking-wider text-gray-400 mt-1">Complete</span>
              </div>
            </div>

            <div className="flex-1 w-full space-y-1">
              {onboarding.slice(0, 3).map((step, idx) => {
                const isLocked = !step.done && idx > 0 && !onboarding[idx - 1]?.done;
                return (
                  <div key={step.label} className="flex items-center justify-between py-3 border-b border-gray-50 last:border-0">
                    <div className="flex items-center gap-3">
                      {step.done ? (
                        <CheckCircle className="w-5 h-5 text-brand-secondary fill-brand-secondary/10" />
                      ) : (
                        <Circle className="w-5 h-5 text-gray-300" />
                      )}
                      <span className={cn('text-[15px]', step.done ? 'text-brand-dark font-medium' : 'text-gray-500')}>
                        {step.label}
                      </span>
                    </div>
                    <span className="text-sm font-medium">
                      {isLocked ? (
                        <Lock className="w-4 h-4 text-gray-300" />
                      ) : step.done ? (
                        <span className="text-gray-400">{step.date_label || 'Validé'}</span>
                      ) : (
                        <Link to="/collaborateur/onboarding" className="text-brand-warning hover:underline">Voir</Link>
                      )}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}



        <div className="lg:col-span-1 lg:row-span-2 bg-[#FDF8F7] rounded-2xl p-6 shadow-sm flex flex-col border border-brand-warning/10">
          <div className="flex items-center gap-3 mb-6">
            <div className="bg-brand-warning text-white p-2.5 rounded-xl shadow-sm shadow-brand-warning/20">
              <Bot className="w-6 h-6" />
            </div>
            <h2 className="text-xl font-bold text-brand-dark">Ask Pulse AI</h2>
          </div>
          <p className="text-[15px] text-gray-600 mb-8 leading-relaxed">
            Obtenez des réponses instantanées sur vos congés, vos documents ou vos démarches RH personnelles.
          </p>
          <div className="space-y-4 mb-8">
            <button 
              onClick={() => handleSuggestionClick("Combien de jours de congés me reste-t-il ?")}
              className="w-full text-left bg-white p-4 rounded-xl text-[14px] text-brand-dark font-medium shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-md transition-shadow hover:text-brand-warning">
              &quot;Combien de jours de congés me reste-t-il ?&quot;
            </button>
            <button 
              onClick={() => handleSuggestionClick("Montre-moi mes derniers documents RH.")}
              className="w-full text-left bg-white p-4 rounded-xl text-[14px] text-brand-dark font-medium shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-md transition-shadow hover:text-brand-warning">
              &quot;Montre-moi mes derniers documents RH.&quot;
            </button>
            <button 
              onClick={() => handleSuggestionClick("Quels sont mes taches à faire ?")}
              className="w-full text-left bg-white p-4 rounded-xl text-[14px] text-brand-dark font-medium shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-md transition-shadow hover:text-brand-warning">
              &quot;Quels sont mes taches à faire ?&quot;
            </button>
          </div>
          <div className="mt-auto">
            <Link to="/collaborateur/assistant" className="flex items-center justify-center w-full bg-brand-warning hover:bg-[#c9412c] text-white text-[15px] font-semibold py-3.5 rounded-xl transition-colors shadow-sm shadow-brand-warning/20">
              Launch Full Chat
            </Link>
          </div>
        </div>

        <div className="lg:col-span-1 bg-white rounded-2xl p-6 shadow-sm border border-gray-50 flex flex-col justify-between">
          <div className="flex justify-between items-start mb-6">
            <div className="p-2.5 bg-[#F3F6F6] text-brand-secondary rounded-xl">
              <Shield className="w-5 h-5" />
            </div>
            <div className="text-[11px] font-bold text-brand-secondary uppercase tracking-wider flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5" />
              {dashboard?.summary?.benefits_status || 'Active'}
            </div>
          </div>
          <div>
            <div className="text-[11px] font-semibold text-gray-400 uppercase tracking-[0.15em] mb-2">Next Benefits Enrollment</div>
            <div className="text-[22px] font-bold text-brand-dark">{dashboard?.summary?.next_benefits_enrollment || '—'}</div>
            {dashboard?.summary?.primary_benefit_label ? (
              <div className="mt-2 text-xs text-brand-secondary/70">{dashboard.summary.primary_benefit_label}</div>
            ) : null}
            <button className="mt-5 w-full py-2.5 border border-gray-200 rounded-xl text-[14px] font-semibold text-gray-600 hover:bg-gray-50 transition-colors">
              View Current Plan
            </button>
          </div>
        </div>

        <div className="lg:col-span-1 bg-white rounded-2xl p-6 shadow-sm border border-gray-50 flex flex-col justify-between">
          <div className="flex justify-between items-start mb-6">
            <div className="p-2.5 bg-rose-50 text-brand-warning rounded-xl">
              <TrendingUp className="w-5 h-5" />
            </div>
            <div className="text-[12px] font-medium text-gray-400">{dashboard?.summary?.performance_target_label || 'Q2 Target'}</div>
          </div>
          <div>
            <div className="text-[11px] font-semibold text-gray-400 uppercase tracking-[0.15em] mb-2">Performance Feedback</div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-[28px] font-bold text-brand-dark">{dashboard?.summary?.performance_score?.toFixed(1) || '—'}</span>
              <span className="text-[15px] font-medium text-gray-400">/ 5.0</span>
            </div>
            {dashboard?.summary?.career_focus_title ? (
              <div className="mt-3 text-xs text-brand-secondary/70">
                Cible carrière: <span className="font-semibold text-brand-dark">{dashboard.summary.career_focus_title}</span>
              </div>
            ) : null}
            <div className="mt-1 text-[11px] text-brand-secondary/55">
              Mobilité: {dashboard?.summary?.mobility_status || 'Aucune demande'}
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 bg-white rounded-2xl p-6 shadow-sm border border-gray-50">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-bold text-brand-dark">Recent Documents</h2>
            <Link to="/collaborateur/documents" className="text-[14px] font-semibold text-gray-500 hover:text-brand-dark transition-colors">See All</Link>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="pb-3 text-[11px] font-semibold text-gray-400 uppercase tracking-wider font-sans">Document Name</th>
                  <th className="pb-3 text-[11px] font-semibold text-gray-400 uppercase tracking-wider font-sans">Date Modified</th>
                  <th className="pb-3 text-[11px] font-semibold text-gray-400 uppercase tracking-wider font-sans">Type</th>
                  <th className="pb-3 text-[11px] font-semibold text-gray-400 uppercase tracking-wider text-right font-sans">Actions</th>
                </tr>
              </thead>
              <tbody>
                {recentDocuments.map((doc) => {
                  const isLegal = /contrat|legal/i.test(doc.type || '');
                  return (
                    <tr key={doc.id} className="border-b border-gray-50 last:border-0 group hover:bg-gray-50/50 transition-colors">
                      <td className="py-4">
                        <div className="flex items-center gap-3">
                          <FileText className={cn('w-5 h-5', isLegal ? 'text-brand-secondary' : 'text-brand-warning')} />
                          <span className="text-[14px] font-medium text-brand-dark">{doc.name}</span>
                        </div>
                      </td>
                      <td className="py-4 text-[14px] text-gray-500">{doc.date}</td>
                      <td className="py-4">
                        <span className={cn('px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider rounded-md', isLegal ? 'bg-brand-secondary/10 text-brand-secondary' : 'bg-brand-warning/10 text-brand-warning')}>
                          {doc.type}
                        </span>
                      </td>
                      <td className="py-4 text-right">
                        <button
                          type="button"
                          onClick={() => downloadDocument(doc)}
                          className="p-2 text-gray-400 hover:text-brand-secondary hover:bg-brand-secondary/10 rounded-xl transition-colors inline-block"
                        >
                          <Download className="w-[18px] h-[18px]" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
                {recentDocuments.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="py-6 text-center text-sm text-brand-secondary/60">Aucun document disponible pour le moment.</td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
            <div className="rounded-xl bg-brand-light/50 p-3 text-brand-secondary">
              <div className="text-[11px] font-semibold uppercase tracking-widest text-brand-secondary/50">Compliance</div>
              <div className="mt-1 text-xl font-bold text-brand-dark">{complianceLabel}</div>
            </div>
            <div className="rounded-xl bg-brand-light/50 p-3 text-brand-secondary">
              <div className="text-[11px] font-semibold uppercase tracking-widest text-brand-secondary/50">Pending Items</div>
              <div className="mt-1 text-xl font-bold text-brand-dark">{dashboard?.summary?.documents_pending || 0}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
