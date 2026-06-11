import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { myProfile } from '../../data/mockData';
import { cn } from '../../lib/utils';
import { CalendarDays, CheckCircle, Circle, FileText, Download, Bot, Shield, TrendingUp, Plane, Activity, Lock } from 'lucide-react';

export default function CollaborateurDashboard() {
  const { user } = useAuth();
  const firstName = user?.name?.split(' ')[0] || 'Alex';
  const today = new Date().toLocaleDateString('fr-FR', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
  });
  const doneSteps = myProfile.onboarding.filter((s) => s.done).length;
  const onboardingPct = Math.round((doneSteps / myProfile.onboarding.length) * 100);

  const currentBalance = myProfile.conges.restants;
  const totalBalance = myProfile.conges.total;
  const usedBalance = totalBalance - currentBalance;

  const recentDocuments = [
    { name: 'Employment_Contract_V2.pdf', date: '20 mai 2024', type: 'Contrat' },
    { name: 'Security_Policy_Handshake.pdf', date: '18 mai 2024', type: 'Politique' },
  ];

  function downloadDocument(doc) {
    const blob = new Blob([
      `Document : ${doc.name}\nType : ${doc.type}\nDate : ${doc.date}`,
    ], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${doc.name.replace(/[^a-z0-9]+/gi, '_')}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  return (
    <div className="animate-fade-in-up space-y-6">
      {/* Header Section */}
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between mb-8">
        <div>
          <h1 className="text-[32px] font-bold text-brand-dark">Bonjour {firstName}</h1>
          <p className="mt-1 text-[15px] text-gray-500">Voici un aperçu de votre parcours professionnel aujourd'hui.</p>
        </div>
        <div className="flex items-center gap-3 rounded-2xl bg-white px-4 py-3 shadow-sm border border-gray-50">
          <CalendarDays className="text-gray-400 w-5 h-5" />
          <div>
            <div className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">AUJOURD'HUI</div>
            <div className="text-sm font-medium text-brand-dark">{today}</div>
          </div>
        </div>
      </div>

      {/* Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Onboarding Journey */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 shadow-sm border border-gray-50 flex flex-col justify-between">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-lg font-bold text-brand-dark">Onboarding Journey</h2>
              <p className="text-sm text-gray-500 mt-1">Vous êtes sur la bonne voie ! Terminez ces tâches pour débloquer votre premier badge.</p>
            </div>
            <span className="bg-brand-warning text-white text-[10px] font-bold px-3 py-1.5 rounded-full uppercase tracking-wider shadow-sm">
              In Progress
            </span>
          </div>

          <div className="flex flex-col md:flex-row gap-8 items-center mt-2">
            {/* Left: Progress Circle */}
            <div className="relative w-36 h-36 flex-shrink-0">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="40" stroke="currentColor" strokeWidth="8" fill="transparent" className="text-gray-100" />
                <circle cx="50" cy="50" r="40" stroke="currentColor" strokeWidth="8" fill="transparent"
                  strokeDasharray="251.2" strokeDashoffset={251.2 - (251.2 * onboardingPct) / 100}
                  className="text-brand-secondary transition-all duration-1000 ease-out" strokeLinecap="round" />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-bold text-brand-dark">{onboardingPct}%</span>
                <span className="text-[10px] font-semibold uppercase tracking-wider text-gray-400 mt-1">Complete</span>
              </div>
            </div>

            {/* Right: Checklist */}
            <div className="flex-1 w-full space-y-1">
              {myProfile.onboarding.slice(0, 3).map((step, idx) => {
                const isLocked = !step.done && idx > 0 && !myProfile.onboarding[idx - 1].done;
                return (
                  <div key={step.label} className="flex items-center justify-between py-3 border-b border-gray-50 last:border-0">
                    <div className="flex items-center gap-3">
                      {step.done ? (
                        <CheckCircle className="w-5 h-5 text-brand-secondary fill-brand-secondary/10" />
                      ) : (
                        <Circle className="w-5 h-5 text-gray-300" />
                      )}
                      <span className={cn("text-[15px]", step.done ? "text-brand-dark font-medium" : "text-gray-500")}>
                        {step.label}
                      </span>
                    </div>
                    <span className="text-sm font-medium">
                      {isLocked ? (
                         <Lock className="w-4 h-4 text-gray-300" />
                      ) : step.done ? (
                        <span className="text-gray-400">May 12</span>
                      ) : (
                        <button className="text-brand-warning hover:underline">Start Now</button>
                      )}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* ACTIVE BALANCE */}
        <div className="lg:col-span-1 bg-brand-secondary rounded-2xl p-6 shadow-sm text-white flex flex-col justify-between">
          <div className="flex justify-between items-start mb-4">
            <div className="p-2.5 bg-white/10 rounded-xl backdrop-blur-sm">
              <Plane className="w-5 h-5 text-white/90" />
            </div>
            <span className="text-[11px] font-semibold tracking-[0.2em] text-white/70 uppercase">Active Balance</span>
          </div>
          <div className="mt-8 mb-4">
            <div className="text-[48px] font-bold leading-none tracking-tight">{currentBalance} days</div>
            <div className="text-[15px] text-white/80 mt-2">Paid Time Off available</div>
          </div>
          <div className="mt-auto pt-8">
            <div className="flex justify-between text-[13px] text-white/90 mb-2.5 font-medium">
              <span>Used: {usedBalance} days</span>
              <span>Total: {totalBalance} days</span>
            </div>
            <div className="h-1.5 w-full bg-black/20 rounded-full overflow-hidden">
              <div className="h-full bg-white rounded-full transition-all duration-1000 ease-out" style={{ width: `${(usedBalance/totalBalance)*100}%` }}></div>
            </div>
          </div>
        </div>

        {/* Ask Pulse AI */}
        <div className="lg:col-span-1 lg:row-span-2 bg-[#FDF8F7] rounded-2xl p-6 shadow-sm flex flex-col border border-brand-warning/10">
          <div className="flex items-center gap-3 mb-6">
            <div className="bg-brand-warning text-white p-2.5 rounded-xl shadow-sm shadow-brand-warning/20">
              <Bot className="w-6 h-6" />
            </div>
            <h2 className="text-xl font-bold text-brand-dark">Ask Pulse AI</h2>
          </div>
          <p className="text-[15px] text-gray-600 mb-8 leading-relaxed">
            Obtenez des réponses instantanées sur les politiques, les avantages ou votre dossier RH personnel.
          </p>

          <div className="space-y-4 mb-8">
            <button className="w-full text-left bg-white p-4 rounded-xl text-[14px] text-brand-dark font-medium shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-md transition-shadow hover:text-brand-warning">
              "Quelle est notre politique de télétravail ?"
            </button>
            <button className="w-full text-left bg-white p-4 rounded-xl text-[14px] text-brand-dark font-medium shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-md transition-shadow hover:text-brand-warning">
              "Comment demander une amélioration de bureau ?"
            </button>
          </div>

          <div className="mt-auto">
            <Link to="/collaborateur/assistant" className="flex items-center justify-center w-full bg-brand-warning hover:bg-[#c9412c] text-white text-[15px] font-semibold py-3.5 rounded-xl transition-colors shadow-sm shadow-brand-warning/20">
              Launch Full Chat
            </Link>
          </div>
        </div>

        {/* Benefits */}
        <div className="lg:col-span-1 bg-white rounded-2xl p-6 shadow-sm border border-gray-50 flex flex-col justify-between">
          <div className="flex justify-between items-start mb-6">
            <div className="p-2.5 bg-[#F3F6F6] text-brand-secondary rounded-xl">
              <Shield className="w-5 h-5" />
            </div>
            <div className="text-[11px] font-bold text-brand-secondary uppercase tracking-wider flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5" />
              Active
            </div>
          </div>
          <div>
            <div className="text-[11px] font-semibold text-gray-400 uppercase tracking-[0.15em] mb-2">Next Benefits Enrollment</div>
            <div className="text-[22px] font-bold text-brand-dark">Oct 12, 2024</div>
            <button className="mt-5 w-full py-2.5 border border-gray-200 rounded-xl text-[14px] font-semibold text-gray-600 hover:bg-gray-50 transition-colors">
              View Current Plan
            </button>
          </div>
        </div>

        {/* Performance */}
        <div className="lg:col-span-1 bg-white rounded-2xl p-6 shadow-sm border border-gray-50 flex flex-col justify-between">
          <div className="flex justify-between items-start mb-6">
            <div className="p-2.5 bg-rose-50 text-brand-warning rounded-xl">
              <TrendingUp className="w-5 h-5" />
            </div>
            <div className="text-[12px] font-medium text-gray-400">Q2 Target</div>
          </div>
          <div>
            <div className="text-[11px] font-semibold text-gray-400 uppercase tracking-[0.15em] mb-2">Performance Feedback</div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-[28px] font-bold text-brand-dark">4.8</span>
              <span className="text-[15px] font-medium text-gray-400">/ 5.0</span>
            </div>
            <div className="mt-5 flex -space-x-2.5 relative">
              <img src="https://i.pravatar.cc/100?img=11" alt="team" className="w-8 h-8 rounded-full border-2 border-white relative z-30" />
              <img src="https://i.pravatar.cc/100?img=12" alt="team" className="w-8 h-8 rounded-full border-2 border-white relative z-20" />
              <img src="https://i.pravatar.cc/100?img=13" alt="team" className="w-8 h-8 rounded-full border-2 border-white relative z-10" />
              <div className="w-8 h-8 rounded-full border-2 border-white bg-gray-100 flex items-center justify-center text-[10px] font-bold text-gray-600 relative z-0">
                +3
              </div>
            </div>
          </div>
        </div>

        {/* Recent Documents */}
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
                {recentDocuments.map((doc, idx) => {
                  const isLegal = doc.type === 'Contrat' || doc.type === 'LEGAL';
                  return (
                    <tr key={idx} className="border-b border-gray-50 last:border-0 group hover:bg-gray-50/50 transition-colors">
                      <td className="py-4">
                        <div className="flex items-center gap-3">
                          <FileText className={cn("w-5 h-5", isLegal ? "text-brand-secondary" : "text-brand-warning")} />
                          <span className="text-[14px] font-medium text-brand-dark">{doc.name}</span>
                        </div>
                      </td>
                      <td className="py-4 text-[14px] text-gray-500">{doc.date}</td>
                      <td className="py-4">
                        <span className={cn(
                          "px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider rounded-md",
                          isLegal ? "bg-brand-secondary/10 text-brand-secondary" : "bg-brand-warning/10 text-brand-warning"
                        )}>
                          {isLegal ? 'LEGAL' : 'POLICY'}
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
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
}
