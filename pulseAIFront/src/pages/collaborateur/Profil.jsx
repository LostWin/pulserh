import { useState, useRef } from 'react';
import {
  User, Award, Briefcase, TrendingUp, Star,
  ChevronRight, Download, Edit2, Save, X,
  MapPin, Lock, Camera, CheckCircle2, Shield,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

// ─── Static mock data (from mockData context) ─────────────────────────────
const SKILLS = [
  { name: 'React.js',     bg: '#dbeafe', color: '#1d4ed8' },
  { name: 'TypeScript',   bg: '#ede9fe', color: '#7c3aed' },
  { name: 'Tailwind CSS', bg: '#ccfbf1', color: '#0f766e' },
  { name: 'Docker',       bg: '#e0f2fe', color: '#0369a1' },
  { name: 'Kubernetes',   bg: '#ffedd5', color: '#c2410c' },
  { name: 'PostgreSQL',   bg: '#e0e7ff', color: '#4338ca' },
  { name: 'CI/CD',        bg: '#dcfce7', color: '#15803d' },
  { name: 'GraphQL',      bg: '#fce7f3', color: '#be185d' },
];

const REQUIRED_COMPETENCIES = [
  { name: 'System Architecture', status: 'done' },
  { name: 'Advanced Node.js',    status: 'done' },
  { name: 'Team Leadership',     status: 'in_progress' },
  { name: 'Product Strategy',    status: 'pending' },
];

const ACCOMPLISHMENTS = [
  { title: 'Led "Modern Auth" migration',  desc: 'Completed 2 weeks ahead of schedule.', icon: '🏆' },
  { title: 'Certified Cloud Practitioner', desc: 'AWS Certification obtained in April 2025.', icon: '☁️' },
];

// ─── Initial editable profile state ───────────────────────────────────────
const INITIAL_PERSONAL = {
  fullName:  'Alexandre Dupont',
  birthDate: 'March 14, 1996',
  email:     'alex.dupont@pulse-rh.ai',
  address:   '12 bis Rue de l\'Innovation,\n75008 Paris, France',
  phone:     '+33 6 12 34 56 78',
};

const INITIAL_PROFESSIONAL = {
  employeeId:   '#88429',
  joinDate:     'Jan 12, 2023',
  department:   'Cloud Architecture & R&D',
  contractType: 'Permanent (CDI)',
  salary:       '52 000 € / year',
  leaveBalance: '18 / 30 days',
};

// ─── Permission rules ──────────────────────────────────────────────────────
// Fields the collaborateur can edit (personal only)
const COLLAB_EDITABLE_PERSONAL = ['address', 'phone'];
// RH / admin can edit everything

// ─── Small reusable components ────────────────────────────────────────────
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

/** A field row: shows input when editing & permitted, read-only otherwise */
function FieldRow({ label, fieldKey, value, editing, canEdit, onChange, multiline = false }) {
  const locked = editing && !canEdit;
  const active = editing && canEdit;

  const inputClass = `
    w-full rounded-xl border px-3 py-2 text-sm font-medium outline-none transition
    ${locked
      ? 'border-transparent bg-brand-light/50 text-brand-secondary/40 cursor-not-allowed opacity-60'
      : active
        ? 'border-brand-secondary/40 bg-white text-brand-dark focus:border-brand-secondary focus:ring-2 focus:ring-brand-secondary/20'
        : 'border-transparent bg-transparent text-brand-dark p-0'}
  `;

  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-1.5">
        <SectionLabel>{label}</SectionLabel>
        {locked && <Lock size={9} className="text-brand-secondary/30" />}
      </div>

      {multiline ? (
        <textarea
          rows={2}
          disabled={!active}
          value={value}
          onChange={(e) => onChange(fieldKey, e.target.value)}
          className={`${inputClass} resize-none`}
        />
      ) : (
        <input
          type="text"
          disabled={!active}
          value={value}
          onChange={(e) => onChange(fieldKey, e.target.value)}
          className={inputClass}
        />
      )}
    </div>
  );
}

// ─── Main component ────────────────────────────────────────────────────────
export default function Profil() {
  const { user, role } = useAuth();
  const displayName = user?.name || 'Alex Dupont';

  // Is the current user RH or admin?
  const isRhOrAdmin = role === 'rh' || role === 'admin';

  // Edit mode
  const [editing,  setEditing]  = useState(false);
  const [saved,    setSaved]    = useState(false);

  // Editable states
  const [personal,     setPersonal]     = useState(INITIAL_PERSONAL);
  const [professional, setProfessional] = useState(INITIAL_PROFESSIONAL);
  const [avatarSrc,    setAvatarSrc]    = useState(
    user?.avatar ||
    `https://ui-avatars.com/api/?name=${encodeURIComponent(displayName)}&background=1F524B&color=fff&size=80`,
  );

  // Draft copies (used while editing, committed on Save)
  const [draftPersonal,     setDraftPersonal]     = useState(INITIAL_PERSONAL);
  const [draftProfessional, setDraftProfessional] = useState(INITIAL_PROFESSIONAL);
  const [draftAvatar,       setDraftAvatar]       = useState(avatarSrc);

  const fileRef = useRef(null);

  // ── Permission helpers ────────────────────────────────────────────────
  const canEditPersonalField = (key) =>
    isRhOrAdmin || COLLAB_EDITABLE_PERSONAL.includes(key);

  const canEditProfessionalField = () => isRhOrAdmin;

  // ── Avatar upload ─────────────────────────────────────────────────────
  const handleAvatarChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const url = URL.createObjectURL(file);
    setDraftAvatar(url);
  };

  // ── Edit / Save / Cancel ──────────────────────────────────────────────
  const startEdit = () => {
    setDraftPersonal({ ...personal });
    setDraftProfessional({ ...professional });
    setDraftAvatar(avatarSrc);
    setEditing(true);
    setSaved(false);
  };

  const saveEdit = () => {
    setPersonal({ ...draftPersonal });
    setProfessional({ ...draftProfessional });
    setAvatarSrc(draftAvatar);
    setEditing(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 3500);
  };

  const cancelEdit = () => {
    setEditing(false);
  };

  const handlePersonalChange = (key, val) => {
    setDraftPersonal((p) => ({ ...p, [key]: val }));
  };

  const handleProfChange = (key, val) => {
    setDraftProfessional((p) => ({ ...p, [key]: val }));
  };

  // ── Download CV ───────────────────────────────────────────────────────
  const downloadCV = () => {
    const lines = [
      '==========================================',
      `  CURRICULUM VITAE — ${personal.fullName}`,
      '==========================================',
      '',
      `Email    : ${personal.email}`,
      `Phone    : ${personal.phone}`,
      `Address  : ${personal.address}`,
      '',
      '── Professional ──',
      `Employee ID   : ${professional.employeeId}`,
      `Join Date     : ${professional.joinDate}`,
      `Department    : ${professional.department}`,
      `Contract      : ${professional.contractType}`,
      '',
      '── Skills ──',
      SKILLS.map((s) => `• ${s.name}`).join('\n'),
    ].join('\n');

    const blob = new Blob([lines], { type: 'text/plain;charset=utf-8' });
    const url  = URL.createObjectURL(blob);
    const a    = Object.assign(document.createElement('a'), {
      href: url,
      download: `CV_${personal.fullName.replace(/\s+/g, '_')}.txt`,
    });
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // ── Current values (draft when editing, saved otherwise) ─────────────
  const P  = editing ? draftPersonal     : personal;
  const PR = editing ? draftProfessional : professional;
  const AV = editing ? draftAvatar       : avatarSrc;

  return (
    <div className="animate-fade-in-up space-y-5">

      {/* ── Permission banner ──────────────────────────────────────── */}
      {isRhOrAdmin ? (
        <div className="flex items-center gap-2 rounded-xl border border-brand-secondary/20 bg-brand-secondary/5 px-4 py-2.5">
          <Shield size={14} className="text-brand-secondary shrink-0" />
          <p className="text-xs font-semibold text-brand-secondary">
            Mode RH/Admin — Tous les champs sont modifiables.
          </p>
        </div>
      ) : (
        <div className="flex items-center gap-2 rounded-xl border border-brand-secondary/15 bg-brand-light px-4 py-2.5">
          <Lock size={14} className="text-brand-secondary/50 shrink-0" />
          <p className="text-xs text-brand-secondary/60">
            Vous pouvez modifier votre <strong className="text-brand-secondary">adresse</strong> et votre <strong className="text-brand-secondary">téléphone</strong>. Les informations professionnelles sont en lecture seule.
          </p>
        </div>
      )}

      {/* ── Save toast ─────────────────────────────────────────────── */}
      {saved && (
        <div className="flex items-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-2.5">
          <CheckCircle2 size={15} className="text-emerald-600 shrink-0" />
          <p className="text-sm font-semibold text-emerald-700">Profil mis à jour avec succès !</p>
        </div>
      )}

      {/* ── PROFILE HEADER ─────────────────────────────────────────── */}
      <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm overflow-hidden">
        <div className="h-24 bg-gradient-to-r from-brand-secondary/25 via-brand-secondary/10 to-transparent" />

        <div className="flex flex-col gap-4 px-6 pb-6 sm:flex-row sm:items-end -mt-10">
          {/* Avatar */}
          <div className="relative shrink-0">
            <div className="h-20 w-20 rounded-2xl border-4 border-white shadow-md bg-brand-secondary/20 overflow-hidden">
              <img
                src={AV}
                alt={displayName}
                className="h-full w-full object-cover"
                onError={(e) => {
                  e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(displayName)}&background=1F524B&color=fff&size=80`;
                }}
              />
            </div>
            {/* Camera overlay — only when editing (collab can always change avatar) */}
            {editing && (
              <>
                <button
                  onClick={() => fileRef.current?.click()}
                  className="absolute inset-0 flex items-center justify-center rounded-2xl bg-brand-dark/50 text-white opacity-0 hover:opacity-100 transition-opacity"
                >
                  <Camera size={18} />
                </button>
                <input
                  ref={fileRef}
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleAvatarChange}
                />
              </>
            )}
            <span className="absolute -bottom-1 -right-1 flex h-5 items-center gap-1 rounded-full bg-emerald-500 px-1.5 text-[9px] font-bold text-white uppercase tracking-wide shadow">
              <span className="h-1.5 w-1.5 rounded-full bg-white" />
              Active
            </span>
          </div>

          {/* Name & role */}
          <div className="flex-1 pb-1">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-xl font-bold text-brand-dark">{P.fullName}</h1>
              <span className="rounded-md bg-brand-secondary/10 px-2 py-0.5 text-[10px] font-semibold text-brand-secondary tracking-wide">
                EMP ID: {PR.employeeId}
              </span>
            </div>
            <p className="mt-0.5 text-sm text-brand-secondary/70">
              Junior Developer&nbsp;·&nbsp;
              <span className="text-brand-secondary font-semibold">{PR.department}</span>
            </p>
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-2 pb-1">
            {editing ? (
              <>
                <button
                  onClick={cancelEdit}
                  className="flex items-center gap-1.5 rounded-xl border border-brand-secondary/20 px-3 py-2 text-xs font-medium text-brand-secondary hover:bg-brand-light transition-colors"
                >
                  <X size={13} />
                  Annuler
                </button>
                <button
                  onClick={saveEdit}
                  className="flex items-center gap-1.5 rounded-xl bg-brand-secondary px-4 py-2 text-xs font-bold text-white hover:bg-brand-dark transition-colors shadow-sm"
                >
                  <Save size={13} />
                  Enregistrer
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={startEdit}
                  className="flex items-center gap-1.5 rounded-xl border border-brand-secondary/20 px-3 py-2 text-xs font-medium text-brand-secondary hover:bg-brand-light transition-colors"
                >
                  <Edit2 size={13} />
                  Modifier le profil
                </button>
                <button
                  onClick={downloadCV}
                  className="flex items-center gap-1.5 rounded-xl bg-brand-danger px-4 py-2 text-xs font-bold text-white hover:opacity-90 transition-opacity shadow-sm"
                >
                  <Download size={13} />
                  Download CV
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* ── MAIN GRID ──────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">

        {/* LEFT COL (span 2) */}
        <div className="space-y-5 lg:col-span-2">

          {/* Personal Information */}
          <Card>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="grid h-7 w-7 place-items-center rounded-lg bg-brand-secondary/10">
                  <User size={14} className="text-brand-secondary" />
                </div>
                <h2 className="text-sm font-bold text-brand-dark">Personal Information</h2>
              </div>
              {!editing && (
                <span className="text-[10px] text-brand-secondary/40 italic">
                  {isRhOrAdmin ? 'Tous les champs modifiables' : 'Adresse & téléphone modifiables'}
                </span>
              )}
            </div>

            <div className="space-y-4">
              {/* Full Legal Name */}
              <FieldRow
                label="Full Legal Name"
                fieldKey="fullName"
                value={P.fullName}
                editing={editing}
                canEdit={isRhOrAdmin}
                onChange={handlePersonalChange}
              />
              {/* Date of Birth */}
              <FieldRow
                label="Date of Birth"
                fieldKey="birthDate"
                value={P.birthDate}
                editing={editing}
                canEdit={isRhOrAdmin}
                onChange={handlePersonalChange}
              />
              {/* Email Address */}
              <FieldRow
                label="Email Address"
                fieldKey="email"
                value={P.email}
                editing={editing}
                canEdit={isRhOrAdmin}
                onChange={handlePersonalChange}
              />
              {/* Residential Address */}
              <FieldRow
                label="Residential Address"
                fieldKey="address"
                value={P.address}
                editing={editing}
                canEdit={canEditPersonalField('address')}
                onChange={handlePersonalChange}
                multiline
              />
              {/* Phone Number */}
              <FieldRow
                label="Phone Number"
                fieldKey="phone"
                value={P.phone}
                editing={editing}
                canEdit={canEditPersonalField('phone')}
                onChange={handlePersonalChange}
              />
            </div>
          </Card>

          {/* Professional Information */}
          <Card>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="grid h-7 w-7 place-items-center rounded-lg bg-brand-secondary/10">
                  <Briefcase size={14} className="text-brand-secondary" />
                </div>
                <h2 className="text-sm font-bold text-brand-dark">Professional Information</h2>
              </div>
              {!isRhOrAdmin && (
                <span className="flex items-center gap-1 rounded-full bg-brand-light border border-brand-secondary/10 px-2.5 py-0.5 text-[10px] font-semibold text-brand-secondary/50">
                  <Lock size={9} />
                  Read-only
                </span>
              )}
            </div>

            <div className="grid grid-cols-2 gap-x-6 gap-y-4">
              <FieldRow
                label="Employee ID"
                fieldKey="employeeId"
                value={PR.employeeId}
                editing={editing}
                canEdit={canEditProfessionalField()}
                onChange={handleProfChange}
              />
              <FieldRow
                label="Join Date"
                fieldKey="joinDate"
                value={PR.joinDate}
                editing={editing}
                canEdit={canEditProfessionalField()}
                onChange={handleProfChange}
              />
              <FieldRow
                label="Department"
                fieldKey="department"
                value={PR.department}
                editing={editing}
                canEdit={canEditProfessionalField()}
                onChange={handleProfChange}
              />
              <FieldRow
                label="Contract Type"
                fieldKey="contractType"
                value={PR.contractType}
                editing={editing}
                canEdit={canEditProfessionalField()}
                onChange={handleProfChange}
              />
              <FieldRow
                label="Salary"
                fieldKey="salary"
                value={PR.salary}
                editing={editing}
                canEdit={canEditProfessionalField()}
                onChange={handleProfChange}
              />
              <FieldRow
                label="Leave Balance"
                fieldKey="leaveBalance"
                value={PR.leaveBalance}
                editing={editing}
                canEdit={canEditProfessionalField()}
                onChange={handleProfChange}
              />
            </div>

            {/* Manager row */}
            <div className="mt-5 pt-4 border-t border-brand-secondary/10">
              <SectionLabel>Manager</SectionLabel>
              <div className="flex items-center gap-2 mt-2">
                <div className="h-8 w-8 rounded-full bg-brand-secondary/20 flex items-center justify-center text-xs font-bold text-brand-secondary shrink-0">
                  SJ
                </div>
                <div>
                  <p className="text-sm font-medium text-brand-dark">Sarah Jenkins</p>
                  <p className="text-[10px] text-brand-secondary/50">Engineering Lead</p>
                </div>
              </div>
            </div>

            {/* Location */}
            <div className="mt-3 flex items-center gap-1.5">
              <MapPin size={12} className="text-brand-secondary/60" />
              <span className="text-xs text-brand-secondary/70">Paris Hub · Remote Friendly</span>
            </div>
          </Card>

          {/* Validated Skills */}
          <Card>
            <div className="flex items-center gap-2 mb-4">
              <div className="grid h-7 w-7 place-items-center rounded-lg bg-brand-secondary/10">
                <Award size={14} className="text-brand-secondary" />
              </div>
              <h2 className="text-sm font-bold text-brand-dark">Validated Skills</h2>
            </div>
            <div className="flex flex-wrap gap-2">
              {SKILLS.map((skill) => (
                <span
                  key={skill.name}
                  style={{ backgroundColor: skill.bg, color: skill.color }}
                  className="rounded-full px-3 py-1 text-xs font-semibold"
                >
                  {skill.name} ✦
                </span>
              ))}
            </div>
          </Card>

          {/* Save bar (sticky, visible only in edit mode) */}
          {editing && (
            <div className="sticky bottom-4 z-20 flex items-center justify-between gap-4 rounded-2xl border border-brand-secondary/20 bg-white px-5 py-3.5 shadow-lg">
              <p className="text-sm font-medium text-brand-secondary/70">
                {isRhOrAdmin
                  ? '✏️ Mode RH — tous les champs sont modifiables.'
                  : '✏️ Vous modifiez votre adresse et téléphone.'}
              </p>
              <div className="flex items-center gap-2">
                <button
                  onClick={cancelEdit}
                  className="rounded-xl border border-brand-secondary/20 px-4 py-2 text-sm font-medium text-brand-secondary hover:bg-brand-light transition-colors"
                >
                  Annuler
                </button>
                <button
                  onClick={saveEdit}
                  className="flex items-center gap-2 rounded-xl bg-brand-secondary px-4 py-2 text-sm font-bold text-white hover:bg-brand-dark transition-colors"
                >
                  <Save size={14} />
                  Enregistrer les modifications
                </button>
              </div>
            </div>
          )}
        </div>

        {/* RIGHT COL */}
        <div className="space-y-5">

          {/* Career Insight */}
          <Card>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="grid h-7 w-7 place-items-center rounded-lg bg-brand-secondary/10">
                  <TrendingUp size={14} className="text-brand-secondary" />
                </div>
                <h2 className="text-sm font-bold text-brand-dark">Career Insight</h2>
              </div>
              <span className="rounded-full bg-brand-warning/10 px-2.5 py-0.5 text-[10px] font-bold text-brand-warning uppercase tracking-wide border border-brand-warning/20">
                AI Predictive
              </span>
            </div>

            <div className="mb-4">
              <p className="text-[10px] font-semibold uppercase tracking-widest text-brand-secondary/40 mb-1">
                Next Milestone
              </p>
              <p className="text-sm font-semibold text-brand-dark">Senior Developer</p>
            </div>

            <div className="mb-4">
              <div className="flex items-center justify-between mb-1.5">
                <p className="text-[10px] font-semibold uppercase tracking-widest text-brand-secondary/40">
                  Growth Progress
                </p>
                <span className="text-xs font-bold text-brand-secondary">68%</span>
              </div>
              <div className="h-2 w-full rounded-full bg-brand-light overflow-hidden">
                <div
                  className="h-full rounded-full bg-brand-secondary transition-all duration-700"
                  style={{ width: '68%' }}
                />
              </div>
            </div>

            <div className="mb-4">
              <p className="text-[10px] font-semibold uppercase tracking-widest text-brand-secondary/40 mb-2">
                Required Competencies
              </p>
              <div className="space-y-2">
                {REQUIRED_COMPETENCIES.map((c) => (
                  <div key={c.name} className="flex items-center justify-between gap-2">
                    <span className="text-xs text-brand-dark">{c.name}</span>
                    {c.status === 'done' ? (
                      <span className="grid h-5 w-5 place-items-center rounded-full bg-brand-secondary text-white text-[10px] font-bold shrink-0">
                        ✓
                      </span>
                    ) : c.status === 'in_progress' ? (
                      <span className="rounded-full bg-brand-warning/10 border border-brand-warning/30 px-2 py-0.5 text-[9px] font-bold text-brand-warning uppercase tracking-wide shrink-0">
                        In Progress
                      </span>
                    ) : (
                      <span className="text-[10px] text-brand-secondary/40 shrink-0">–</span>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-xl bg-brand-light p-3">
              <p className="text-[10px] font-bold uppercase tracking-wide text-brand-secondary mb-1.5">
                🤖 AI Suggestion
              </p>
              <p className="text-xs text-brand-secondary/80 leading-relaxed">
                Based on your recent commits and peer reviews, focusing on{' '}
                <strong className="text-brand-secondary">"System Architecture"</strong> workshops next
                quarter could accelerate your promotion by{' '}
                <strong className="text-brand-secondary">4 months</strong>.
              </p>
            </div>
          </Card>

          {/* Recent Accomplishments */}
          <Card>
            <div className="flex items-center gap-2 mb-4">
              <div className="grid h-7 w-7 place-items-center rounded-lg bg-brand-secondary/10">
                <Star size={14} className="text-brand-secondary" />
              </div>
              <h2 className="text-sm font-bold text-brand-dark">Recent Accomplishments</h2>
            </div>
            <div className="space-y-3">
              {ACCOMPLISHMENTS.map((a) => (
                <div key={a.title} className="flex items-start gap-3">
                  <div className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-brand-light text-base">
                    {a.icon}
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-brand-dark leading-snug">{a.title}</p>
                    <p className="text-[11px] text-brand-secondary/60 mt-0.5">{a.desc}</p>
                  </div>
                </div>
              ))}
            </div>
            <button className="mt-4 flex w-full items-center justify-center gap-1 rounded-xl border border-brand-secondary/15 py-2 text-xs font-medium text-brand-secondary hover:bg-brand-light transition-colors">
              View all
              <ChevronRight size={12} />
            </button>
          </Card>
        </div>
      </div>
    </div>
  );
}
