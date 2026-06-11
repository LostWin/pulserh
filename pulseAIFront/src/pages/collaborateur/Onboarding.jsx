import { useState } from 'react';
import {
  CheckCircle2, Circle, Clock, Monitor, Users, BookOpen,
  FileSignature, Download, Send, BotMessageSquare, MapPin,
  ChevronRight, PartyPopper, AlertCircle,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

// ─── Steps on the progress path ──────────────────────────────────────────────
const PATH_STEPS = [
  { id: 'profile',   label: 'Profile Setup',      icon: CheckCircle2 },
  { id: 'contract',  label: 'Contract Signing',    icon: FileSignature },
  { id: 'it',        label: 'IT Setup',            icon: Monitor },
  { id: 'team',      label: 'Team Intro',          icon: Users },
];

// ─── Checklist tasks ─────────────────────────────────────────────────────────
const INITIAL_TASKS = [
  { id: 1,  label: 'Upload ID and Passport copy',          status: 'done',      detail: 'Documents verified by HR.' },
  { id: 2,  label: 'Sign Employment Contract',             status: 'pending',   detail: 'Legal documents ready for your e-signature.' },
  { id: 3,  label: 'Configure Workstation (MacBook Pro)',  status: 'next',      detail: 'IT team will assist you on Day 1.' },
  { id: 4,  label: 'Meet your Manager (Sarah Chen)',       status: 'scheduled', detail: 'Intro call scheduled for tomorrow 10:00 AM.' },
  { id: 5,  label: 'Complete GDPR / Security Training',    status: 'todo',      detail: 'E-learning module — approx. 45 min.' },
  { id: 6,  label: 'Set up your development environment',  status: 'todo',      detail: 'Follow the Dev Setup Guide in Resources.' },
  { id: 7,  label: 'Join #general and #engineering Slack', status: 'todo',      detail: 'Invite sent to your professional email.' },
  { id: 8,  label: 'Attend company all-hands',             status: 'todo',      detail: 'Next all-hands: Monday 9:00 AM.' },
];

const STATUS_META = {
  done:      { label: 'Done',      color: 'text-emerald-600 bg-emerald-50 border-emerald-200' },
  pending:   { label: 'Pending',   color: 'text-brand-warning bg-brand-warning/8 border-brand-warning/30' },
  next:      { label: 'Next',      color: 'text-blue-600 bg-blue-50 border-blue-200' },
  scheduled: { label: 'Scheduled', color: 'text-purple-600 bg-purple-50 border-purple-200' },
  todo:      { label: 'To do',     color: 'text-brand-secondary/60 bg-brand-light border-brand-secondary/15' },
};

// ─── Team members ─────────────────────────────────────────────────────────────
const TEAM = [
  { name: 'Sarah Chen',   role: 'Engineering Manager', initials: 'SC', color: '#1F524B', main: true  },
  { name: 'Jordan Dale',  role: 'Senior Developer',    initials: 'JD', color: '#DF4931', main: false },
  { name: 'Mia Wong',     role: 'Product Designer',    initials: 'MW', color: '#7c3aed', main: false },
];

// ─── AI suggestions ───────────────────────────────────────────────────────────
const AI_RESOURCES = [
  { icon: BookOpen, label: 'Employee Handbook 2024' },
  { icon: MapPin,   label: 'Office Map & Hubs'      },
  { icon: Users,    label: 'Company Directory'      },
];

// ─── Helper: Avatar ───────────────────────────────────────────────────────────
function Avatar({ name, initials, color, size = 'md' }) {
  const sz = size === 'lg' ? 'h-12 w-12 text-sm' : 'h-9 w-9 text-xs';
  return (
    <div
      className={`${sz} shrink-0 rounded-full flex items-center justify-center font-bold text-white shadow-sm`}
      style={{ backgroundColor: color }}
    >
      {initials}
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────
export default function Onboarding() {
  const { user } = useAuth();
  const firstName = (user?.name || 'Alex').split(' ')[0];

  const [tasks, setTasks]         = useState(INITIAL_TASKS);
  const [signed,  setSigned]      = useState(false);
  const [msgSent, setMsgSent]     = useState(false);
  const [expanded, setExpanded]   = useState(null);

  const doneCount  = tasks.filter((t) => t.status === 'done').length;
  const totalCount = tasks.length;
  const pct        = Math.round((doneCount / totalCount) * 100);
  const complete   = doneCount === totalCount;

  // Which path step is currently active
  const activeStep = signed ? 2 : 1; // after signing → IT Setup

  const toggleDone = (id) => {
    setTasks((prev) =>
      prev.map((t) =>
        t.id === id
          ? { ...t, status: t.status === 'done' ? 'pending' : 'done' }
          : t,
      ),
    );
  };

  const handleSign = () => {
    setSigned(true);
    setTasks((prev) =>
      prev.map((t) => (t.id === 2 ? { ...t, status: 'done' } : t)),
    );
  };

  const handleDownloadDraft = () => {
    const blob = new Blob(
      ['EMPLOYMENT CONTRACT DRAFT\n\nThis is a placeholder for your employment contract draft.\nPlease review all clauses carefully before signing.'],
      { type: 'text/plain;charset=utf-8' },
    );
    const url = URL.createObjectURL(blob);
    const a = Object.assign(document.createElement('a'), {
      href: url,
      download: 'Employment_Contract_Draft.txt',
    });
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleSendMessage = () => {
    setMsgSent(true);
    setTimeout(() => setMsgSent(false), 3000);
  };

  return (
    <div className="animate-fade-in-up space-y-6">

      {/* ── Page header ─────────────────────────────────────────── */}
      <div>
        <h1 className="text-2xl font-bold text-brand-dark">
          {complete ? '🎉 Onboarding Complete!' : `Welcome to the Team, ${firstName}!`}
        </h1>
        <p className="mt-0.5 text-sm text-brand-secondary/70">
          {complete
            ? 'You have successfully completed all onboarding steps.'
            : "We're thrilled to have you on board. Your journey at Pulse RH starts here — let's get you set up for success."}
        </p>
      </div>

      {/* ── Onboarding path ─────────────────────────────────────── */}
      <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-5">
        <div className="flex items-center justify-between mb-5">
          <p className="text-sm font-bold text-brand-dark">Your Onboarding Path</p>
          <span className="rounded-full bg-brand-secondary/10 px-3 py-1 text-xs font-bold text-brand-secondary">
            {pct}% Completed
          </span>
        </div>

        {/* Step rail */}
        <div className="relative flex items-center justify-between">
          {/* Connector line */}
          <div className="absolute left-6 right-6 top-5 h-0.5 bg-brand-secondary/15" />
          <div
            className="absolute left-6 top-5 h-0.5 bg-brand-secondary transition-all duration-700"
            style={{ width: `${(activeStep / (PATH_STEPS.length - 1)) * 88}%` }}
          />

          {PATH_STEPS.map((step, i) => {
            const done_ = i < activeStep;
            const active_ = i === activeStep;
            const Icon = step.icon;
            return (
              <div key={step.id} className="relative z-10 flex flex-col items-center gap-2 w-1/4">
                <div
                  className={`h-10 w-10 rounded-full flex items-center justify-center shadow-sm transition-colors
                    ${done_   ? 'bg-brand-secondary text-white'
                    : active_ ? 'bg-brand-warning/15 border-2 border-brand-warning text-brand-warning'
                              : 'bg-white border-2 border-brand-secondary/15 text-brand-secondary/30'}`}
                >
                  <Icon size={17} />
                </div>
                <span
                  className={`text-[10px] font-semibold text-center leading-tight
                    ${done_   ? 'text-brand-secondary'
                    : active_ ? 'text-brand-warning'
                              : 'text-brand-secondary/40'}`}
                >
                  {step.label}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Body grid ─────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">

        {/* Left col (2/3) */}
        <div className="lg:col-span-2 space-y-5">

          {/* Priority action */}
          {!signed && (
            <div className="rounded-2xl bg-gradient-to-r from-brand-danger/8 via-brand-warning/5 to-transparent border border-brand-danger/20 shadow-sm p-5">
              <div className="flex items-start gap-4">
                <div className="grid h-12 w-12 shrink-0 place-items-center rounded-xl bg-brand-danger/10">
                  <AlertCircle size={22} className="text-brand-danger" />
                </div>
                <div className="flex-1">
                  <p className="text-[10px] font-bold uppercase tracking-widest text-brand-danger mb-1">
                    Priority Action
                  </p>
                  <h2 className="text-lg font-bold text-brand-dark mb-1">
                    Sign your Employment Contract
                  </h2>
                  <p className="text-sm text-brand-secondary/70 mb-4">
                    The legal documents are ready for your electronic signature. This is the final step to finalize your administrative onboarding.
                  </p>
                  <div className="flex items-center gap-3 flex-wrap">
                    <button
                      onClick={handleSign}
                      className="flex items-center gap-2 rounded-xl bg-brand-danger px-5 py-2.5 text-sm font-bold text-white hover:opacity-90 transition-opacity shadow-sm"
                    >
                      <FileSignature size={15} />
                      Sign Now
                    </button>
                    <button
                      onClick={handleDownloadDraft}
                      className="flex items-center gap-2 rounded-xl border border-brand-secondary/20 px-4 py-2.5 text-sm font-medium text-brand-secondary hover:bg-brand-light transition-colors"
                    >
                      <Download size={14} />
                      Download Draft
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Contract signed banner */}
          {signed && (
            <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4 flex items-center gap-3">
              <CheckCircle2 size={22} className="text-emerald-600 shrink-0" />
              <div>
                <p className="text-sm font-bold text-emerald-800">Contract signed successfully!</p>
                <p className="text-xs text-emerald-600/80">HR has been notified. Your digital copy will appear in Documents.</p>
              </div>
            </div>
          )}

          {/* Checklist */}
          <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm overflow-hidden">
            <div className="flex items-center justify-between px-5 py-4 border-b border-brand-secondary/8">
              <h2 className="text-sm font-bold text-brand-dark">Your Checklist</h2>
              <span className="text-xs font-semibold text-brand-secondary/60">
                {doneCount} of {totalCount} tasks completed
              </span>
            </div>

            {/* Progress mini bar */}
            <div className="h-1 bg-brand-light">
              <div
                className="h-full bg-brand-secondary transition-all duration-700 rounded-r-full"
                style={{ width: `${pct}%` }}
              />
            </div>

            <ul className="divide-y divide-slate-50">
              {tasks.map((task) => {
                const meta = STATUS_META[task.status];
                const isExp = expanded === task.id;
                return (
                  <li key={task.id}>
                    <div
                      className={`flex items-center gap-4 px-5 py-3.5 hover:bg-brand-light/40 transition-colors cursor-pointer
                        ${task.status === 'pending' ? 'bg-brand-warning/5' : ''}`}
                      onClick={() => setExpanded(isExp ? null : task.id)}
                    >
                      {/* Checkbox */}
                      <button
                        onClick={(e) => { e.stopPropagation(); toggleDone(task.id); }}
                        className="shrink-0 text-brand-secondary/40 hover:text-brand-secondary transition-colors"
                      >
                        {task.status === 'done'
                          ? <CheckCircle2 size={20} className="text-brand-secondary" />
                          : <Circle size={20} />}
                      </button>

                      {/* Label */}
                      <span
                        className={`flex-1 text-sm font-medium transition-colors
                          ${task.status === 'done' ? 'line-through text-brand-secondary/40' : 'text-brand-dark'}`}
                      >
                        {task.label}
                      </span>

                      {/* Status badge */}
                      <span className={`shrink-0 rounded-full border px-2.5 py-0.5 text-[11px] font-semibold hidden sm:block ${meta.color}`}>
                        {meta.label}
                      </span>

                      <ChevronRight
                        size={14}
                        className={`shrink-0 text-brand-secondary/30 transition-transform ${isExp ? 'rotate-90' : ''}`}
                      />
                    </div>

                    {/* Expanded detail */}
                    {isExp && (
                      <div className="px-14 pb-3.5 pt-0">
                        <p className="text-xs text-brand-secondary/70 leading-relaxed bg-brand-light rounded-xl px-3 py-2">
                          {task.detail}
                        </p>
                      </div>
                    )}
                  </li>
                );
              })}
            </ul>
          </div>
        </div>

        {/* Right col (1/3) */}
        <div className="space-y-5">

          {/* Your Team */}
          <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-5">
            <div className="flex items-center gap-2 mb-4">
              <div className="grid h-7 w-7 place-items-center rounded-lg bg-brand-secondary/10">
                <Users size={14} className="text-brand-secondary" />
              </div>
              <h3 className="text-sm font-bold text-brand-dark">Your Team</h3>
            </div>

            {/* Manager */}
            {TEAM.filter((t) => t.main).map((m) => (
              <div key={m.name} className="flex items-center gap-3 mb-4 p-3 rounded-xl bg-brand-secondary/5 border border-brand-secondary/10">
                <Avatar name={m.name} initials={m.initials} color={m.color} size="lg" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-bold text-brand-dark truncate">{m.name}</p>
                  <p className="text-xs text-brand-secondary/60">{m.role}</p>
                </div>
                <button className="grid h-8 w-8 place-items-center rounded-lg border border-brand-secondary/15 text-brand-secondary hover:bg-brand-secondary hover:text-white transition-colors">
                  <Send size={13} />
                </button>
              </div>
            ))}

            {/* Close colleagues */}
            <p className="text-[10px] font-bold uppercase tracking-widest text-brand-secondary/40 mb-3">
              Close Colleagues
            </p>
            <div className="space-y-3">
              {TEAM.filter((t) => !t.main).map((m) => (
                <div key={m.name} className="flex items-center gap-3">
                  <Avatar name={m.name} initials={m.initials} color={m.color} />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-semibold text-brand-dark truncate">{m.name}</p>
                    <p className="text-[10px] text-brand-secondary/55">{m.role}</p>
                  </div>
                </div>
              ))}
            </div>

            <button
              onClick={handleSendMessage}
              className={`mt-4 w-full rounded-xl py-2.5 text-sm font-bold transition-colors shadow-sm
                ${msgSent
                  ? 'bg-emerald-100 text-emerald-700'
                  : 'bg-brand-secondary text-white hover:bg-brand-dark'}`}
            >
              {msgSent ? '✓ Message Sent!' : 'Send Welcome Message'}
            </button>
          </div>

          {/* Pulse AI Assistant */}
          <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-5">
            <div className="flex items-center gap-2 mb-3">
              <div className="grid h-7 w-7 place-items-center rounded-lg bg-brand-secondary/10">
                <BotMessageSquare size={14} className="text-brand-secondary" />
              </div>
              <h3 className="text-sm font-bold text-brand-dark">Pulse Assistant</h3>
            </div>

            <p className="text-xs text-brand-secondary/70 leading-relaxed mb-4">
              I've analyzed your role. Here are some resources you might find useful today:
            </p>

            <div className="space-y-2">
              {AI_RESOURCES.map(({ icon: Icon, label }) => (
                <button
                  key={label}
                  className="flex items-center gap-3 w-full rounded-xl border border-brand-secondary/15 px-3 py-2.5 text-left hover:bg-brand-light hover:border-brand-secondary/30 transition-colors"
                >
                  <div className="grid h-7 w-7 place-items-center rounded-lg bg-brand-secondary/8 shrink-0">
                    <Icon size={13} className="text-brand-secondary" />
                  </div>
                  <span className="text-xs font-medium text-brand-dark">{label}</span>
                  <ChevronRight size={12} className="ml-auto text-brand-secondary/30" />
                </button>
              ))}
            </div>

            {complete && (
              <div className="mt-4 rounded-xl bg-brand-secondary/8 p-3 flex items-center gap-2">
                <PartyPopper size={16} className="text-brand-secondary shrink-0" />
                <p className="text-xs font-semibold text-brand-secondary">
                  All steps done — welcome aboard! 🎉
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
