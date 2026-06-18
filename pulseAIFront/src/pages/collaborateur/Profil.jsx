import { useState, useRef, useEffect } from 'react';
import {
  User, Award, Briefcase, TrendingUp, Star,
  ChevronRight, Download, Edit2, Save, X,
  MapPin, Lock, Camera, CheckCircle2, Shield, RefreshCw
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { api } from '../../lib/api';
import FieldVisibilityBadge from '../../components/ui/FieldVisibilityBadge';

// ─── Initial editable profile state ───────────────────────────────────────
const INITIAL_PERSONAL = {
  fullName:  '',
  birthDate: '',
  email:     '',
  address:   '',
  phone:     '',
};

const INITIAL_PROFESSIONAL = {
  employeeId:   '',
  joinDate:     '',
  department:   '',
  contractType: '',
  salary:       '',
  leaveBalance: '',
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
function FieldRow({ label, fieldKey, value, editing, canEdit, onChange, multiline = false, visibility }) {
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
        <FieldVisibilityBadge visibility={visibility} />
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
  const displayName = user?.name || 'Utilisateur';

  // Is the current user RH or admin?
  const isRhOrAdmin = role === 'rh' || role === 'admin';

  // Edit mode
  const [editing,  setEditing]  = useState(false);
  const [saved,    setSaved]    = useState(false);
  const [loading,  setLoading]  = useState(true);
  const [profileSummary, setProfileSummary] = useState({ skills: [], competencies: [], accomplishments: [] });
  const [skillDetails, setSkillDetails] = useState([]);
  const [projectAssignments, setProjectAssignments] = useState([]);
  const [trainingRecommendations, setTrainingRecommendations] = useState([]);
  const [performanceData, setPerformanceData] = useState(null);
  const [engagementData, setEngagementData] = useState(null);
  const [careerOverview, setCareerOverview] = useState({ career_paths: [], mobility_requests: [], promotions: [] });
  const [avatarFile, setAvatarFile] = useState(null);

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
  const [fieldVisibility,   setFieldVisibility]   = useState({});

  const fileRef = useRef(null);

  useEffect(() => {
    async function loadProfile() {
      try {
        const [data, summary, settings] = await Promise.all([
          api.get('/employees/me'),
          api.get('/employees/me/profile-summary'),
          api.get('/users/me/settings'),
        ]);
        if (data) {
          const [skills, projects, recommendations] = await Promise.all([
            api.get(`/employees/${data.id}/skills`).catch(() => []),
            api.get(`/employees/${data.id}/projects`).catch(() => []),
            api.get(`/trainings/recommendations/${data.id}`).catch(() => []),
          ]);
          const [performance, engagement] = await Promise.all([
            api.get(`/employees/${data.id}/performance`).catch(() => null),
            api.get(`/employees/${data.id}/engagement`).catch(() => null),
          ]);
          const career = await api.get(`/employees/${data.id}/career`).catch(() => ({ career_paths: [], mobility_requests: [], promotions: [] }));
          setFieldVisibility(data._field_visibility || {});
          const personalData = {
            fullName: `${data.first_name} ${data.last_name}`,
            birthDate: summary?.birth_date_label || 'Non renseignée',
            email: data.email,
            address: summary?.address_label || 'Adresse non renseignée',
            phone: data.phone || 'Non renseigné',
          };
          
          const profData = {
            employeeId: data.id,
            joinDate: data.hire_date || 'Non renseignée',
            department: data.department || 'Non assigné',
            contractType: data.contract_type || 'CDI',
            salary: data.salary ? `${data.salary.toLocaleString('fr-FR')} € / an` : 'Confidentiel',
            leaveBalance: data.leave_balance || '30 / 30 jours',
            managerName: summary?.manager_name || data.manager_name || 'Aucun manager'
          };
          
          setPersonal(personalData);
          setDraftPersonal(personalData);
          setProfessional(profData);
          setDraftProfessional(profData);
          const resolvedAvatar = settings?.avatar_data_url || summary?.avatar_data_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(personalData.fullName)}&background=1F524B&color=fff&size=80`;
          setAvatarSrc(resolvedAvatar);
          setDraftAvatar(resolvedAvatar);
          setProfileSummary(summary || { skills: [], competencies: [], accomplishments: [] });
          setSkillDetails(skills || []);
          setProjectAssignments(projects || []);
          setTrainingRecommendations(recommendations || []);
          setPerformanceData(performance);
          setEngagementData(engagement);
          setCareerOverview(career || { career_paths: [], mobility_requests: [], promotions: [] });
        }
      } catch (err) {
        console.error("Erreur de chargement du profil", err);
      } finally {
        setLoading(false);
      }
    }
    loadProfile();
  }, [user]);

  // ── Permission helpers ────────────────────────────────────────────────
  const canEditPersonalField = (key) =>
    isRhOrAdmin || COLLAB_EDITABLE_PERSONAL.includes(key);

  const canEditProfessionalField = () => isRhOrAdmin;

  // ── Avatar upload ─────────────────────────────────────────────────────
  const handleAvatarChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const url = URL.createObjectURL(file);
    setAvatarFile(file);
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

  const saveEdit = async () => {
    try {
      let resolvedAvatar = draftAvatar;
      if (avatarFile) {
        const formData = new FormData();
        formData.append('file', avatarFile);
        const avatarResponse = await api.post('/users/me/avatar', formData);
        resolvedAvatar = avatarResponse?.avatar_data_url || draftAvatar;
      }
      if (!isRhOrAdmin && draftPersonal.phone !== personal.phone) {
        await api.post('/employees/me/change-request', {
          field: 'phone',
          new_value: draftPersonal.phone
        });
      }
      setPersonal({ ...draftPersonal });
      setProfessional({ ...draftProfessional });
      setAvatarSrc(resolvedAvatar);
      setDraftAvatar(resolvedAvatar);
      setAvatarFile(null);
      setEditing(false);
      setSaved(true);
      setTimeout(() => setSaved(false), 3500);
    } catch (err) {
      console.error("Erreur de sauvegarde", err);
    }
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
      skillDetails.map((s) => `• ${s.skill_name} (${s.proficiency_level})`).join('\n'),
      '',
      '── Projects ──',
      projectAssignments.map((p) => `• ${p.project_name} — ${p.role_on_project || 'Contributeur'}`).join('\n'),
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

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-brand-secondary/50">
        <RefreshCw className="animate-spin text-brand-secondary mb-4" size={36} />
        <p className="text-sm font-semibold">Chargement du profil...</p>
      </div>
    );
  }

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
              {(profileSummary.profile_title || 'Collaborateur')}&nbsp;·&nbsp;
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
                visibility={fieldVisibility.first_name}
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
                visibility={fieldVisibility.email}
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
                visibility={fieldVisibility.phone}
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
                visibility={fieldVisibility.hire_date}
              />
              <FieldRow
                label="Department"
                fieldKey="department"
                value={PR.department}
                editing={editing}
                canEdit={canEditProfessionalField()}
                onChange={handleProfChange}
                visibility={fieldVisibility.department}
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
                visibility={fieldVisibility.salary}
              />
              <FieldRow
                label="Leave Balance"
                fieldKey="leaveBalance"
                value={PR.leaveBalance}
                editing={editing}
                canEdit={canEditProfessionalField()}
                onChange={handleProfChange}
                visibility={fieldVisibility.leave_balance}
              />
            </div>

            {/* Manager row */}
            <div className="mt-5 pt-4 border-t border-brand-secondary/10">
              <SectionLabel>Manager</SectionLabel>
              <div className="flex items-center gap-2 mt-2">
                <div className="h-8 w-8 rounded-full bg-brand-secondary/20 flex items-center justify-center text-xs font-bold text-brand-secondary shrink-0">
                  {(PR.managerName || 'Sarah Jenkins').split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
                </div>
                <div>
                  <p className="text-sm font-medium text-brand-dark">{PR.managerName || 'Sarah Jenkins'}</p>
                  <p className="text-[10px] text-brand-secondary/50">Manager Direct</p>
                </div>
              </div>
            </div>

            {/* Location */}
            <div className="mt-3 flex items-center gap-1.5">
              <MapPin size={12} className="text-brand-secondary/60" />
              <span className="text-xs text-brand-secondary/70">{profileSummary.work_location_label || 'Remote friendly'}</span>
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
              {profileSummary.skills.map((skill, index) => (
                <span
                  key={`${skill.name}-${index}`}
                  style={{ backgroundColor: '#F3F6F6', color: '#1F524B' }}
                  className="rounded-full px-3 py-1 text-xs font-semibold"
                >
                  {skill.name} {skill.proficiency_level ? `· ${skill.proficiency_level}` : ''} ✦
                </span>
              ))}
            </div>
          </Card>

          <Card>
            <div className="flex items-center gap-2 mb-4">
              <div className="grid h-7 w-7 place-items-center rounded-lg bg-brand-secondary/10">
                <Shield size={14} className="text-brand-secondary" />
              </div>
              <h2 className="text-sm font-bold text-brand-dark">Skill Intelligence</h2>
            </div>
            <div className="space-y-3">
              {skillDetails.map((skill) => (
                <div key={skill.id} className="rounded-2xl border border-brand-secondary/10 bg-brand-light/40 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-brand-dark">{skill.skill_name}</p>
                      <p className="text-xs text-brand-secondary/70">
                        {skill.category || 'Compétence'} · {skill.proficiency_level} · {skill.years_experience ? `${skill.years_experience} ans d’expérience` : 'ancienneté non renseignée'}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-brand-secondary">{skill.confidence_score ? `${skill.confidence_score}%` : '—'}</p>
                      <p className="text-[10px] text-brand-secondary/50">confiance</p>
                    </div>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {skill.is_primary ? <span className="rounded-full bg-brand-secondary/10 px-2 py-1 text-[10px] font-semibold text-brand-secondary">Principale</span> : null}
                    {skill.validated_by ? <span className="rounded-full bg-white px-2 py-1 text-[10px] text-brand-secondary/80">Validée par {skill.validated_by}</span> : null}
                    {skill.source ? <span className="rounded-full bg-white px-2 py-1 text-[10px] text-brand-secondary/80">Source: {skill.source}</span> : null}
                  </div>
                </div>
              ))}
              {!skillDetails.length ? <p className="text-xs text-brand-secondary/60">Aucun détail de compétence disponible.</p> : null}
            </div>
          </Card>

          <Card>
            <div className="flex items-center gap-2 mb-4">
              <div className="grid h-7 w-7 place-items-center rounded-lg bg-brand-secondary/10">
                <CheckCircle2 size={14} className="text-brand-secondary" />
              </div>
              <h2 className="text-sm font-bold text-brand-dark">Benefits & Coverage</h2>
            </div>
            <div className="space-y-3">
              {profileSummary.benefits?.map((benefit) => (
                <div key={`${benefit.plan_name}-${benefit.category}`} className="rounded-2xl border border-brand-secondary/10 bg-brand-light/40 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-brand-dark">{benefit.plan_name}</p>
                      <p className="text-xs text-brand-secondary/70">
                        {benefit.category} {benefit.provider ? `· ${benefit.provider}` : ''} {benefit.tier_label ? `· ${benefit.tier_label}` : ''}
                      </p>
                    </div>
                    <span className="rounded-full bg-white px-2 py-1 text-[10px] font-semibold text-brand-secondary">{benefit.status}</span>
                  </div>
                  <p className="mt-2 text-xs text-brand-secondary/70">{benefit.coverage_summary || 'Couverture disponible via le plan actif.'}</p>
                  {benefit.renewal_date_label ? (
                    <p className="mt-2 text-[11px] text-brand-secondary/55">Renouvellement: {benefit.renewal_date_label}</p>
                  ) : null}
                </div>
              ))}
              {!profileSummary.benefits?.length ? <p className="text-xs text-brand-secondary/60">Aucun benefit actif remonté pour le moment.</p> : null}
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
              <p className="text-sm font-semibold text-brand-dark">
                {careerOverview.career_paths?.[0]?.target_title || performanceData?.objectives?.[0]?.title || 'Prochaine étape de progression'}
              </p>
              {careerOverview.career_paths?.[0]?.next_step ? (
                <p className="mt-1 text-xs text-brand-secondary/65">{careerOverview.career_paths[0].next_step}</p>
              ) : null}
            </div>

            <div className="mb-4">
              <div className="flex items-center justify-between mb-1.5">
                <p className="text-[10px] font-semibold uppercase tracking-widest text-brand-secondary/40">
                  Growth Progress
                </p>
                <span className="text-xs font-bold text-brand-secondary">{performanceData?.objectives?.[0]?.progress_pct ?? 0}%</span>
              </div>
              <div className="h-2 w-full rounded-full bg-brand-light overflow-hidden">
                <div
                  className="h-full rounded-full bg-brand-secondary transition-all duration-700"
                  style={{ width: `${performanceData?.objectives?.[0]?.progress_pct ?? 0}%` }}
                />
              </div>
            </div>

            <div className="mb-4">
              <p className="text-[10px] font-semibold uppercase tracking-widest text-brand-secondary/40 mb-2">
                Required Competencies
              </p>
              <div className="space-y-2">
                {profileSummary.competencies.map((c) => (
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
                {trainingRecommendations[0]
                  ? (
                    <>
                      La formation <strong className="text-brand-secondary">“{trainingRecommendations[0].title}”</strong> est recommandée en priorité, car elle soutient directement votre montée en compétence et les besoins actuels de votre équipe.
                    </>
                  )
                  : (
                    <>
                      Vos recommandations de formation apparaîtront ici dès qu’un besoin ciblé sera détecté à partir de vos compétences et projets.
                    </>
                  )}
              </p>
            </div>

            <div className="mt-4 rounded-xl border border-brand-secondary/10 bg-white p-3">
              <p className="text-[10px] font-bold uppercase tracking-wide text-brand-secondary mb-1.5">
                Engagement Tracking
              </p>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-brand-dark">{engagementData?.current_score ?? '—'}/100</p>
                  <p className="text-[11px] text-brand-secondary/60">Tendance: {engagementData?.trend_label || 'non disponible'}</p>
                </div>
                <span className="rounded-full bg-brand-light px-2.5 py-1 text-[10px] font-semibold text-brand-secondary">{engagementData?.risk_band || 'stable'}</span>
              </div>
            </div>

            <div className="mt-4 rounded-xl border border-brand-secondary/10 bg-white p-3">
              <p className="text-[10px] font-bold uppercase tracking-wide text-brand-secondary mb-2">
                Mobility & Career Moves
              </p>
              {careerOverview.mobility_requests?.[0] ? (
                <div className="mb-3 rounded-xl bg-brand-light/60 p-3">
                  <p className="text-xs font-semibold text-brand-dark">{careerOverview.mobility_requests[0].request_type}</p>
                  <p className="mt-1 text-[11px] text-brand-secondary/70">
                    Statut: {careerOverview.mobility_requests[0].status}
                    {careerOverview.mobility_requests[0].target_department ? ` · ${careerOverview.mobility_requests[0].target_department}` : ''}
                    {careerOverview.mobility_requests[0].target_job_title ? ` · ${careerOverview.mobility_requests[0].target_job_title}` : ''}
                  </p>
                </div>
              ) : null}
              {careerOverview.promotions?.[0] ? (
                <div className="text-xs text-brand-secondary/75">
                  Dernière évolution: <span className="font-semibold text-brand-dark">{careerOverview.promotions[0].new_job_title}</span>
                  <span className="text-brand-secondary/55"> · {careerOverview.promotions[0].effective_date_label}</span>
                </div>
              ) : (
                <div className="text-xs text-brand-secondary/60">Aucun mouvement de mobilité ou d’évolution récent.</div>
              )}
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
              {profileSummary.accomplishments.map((a) => (
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

          <Card>
            <div className="flex items-center gap-2 mb-4">
              <div className="grid h-7 w-7 place-items-center rounded-lg bg-brand-secondary/10">
                <Briefcase size={14} className="text-brand-secondary" />
              </div>
              <h2 className="text-sm font-bold text-brand-dark">Active Projects</h2>
            </div>
            <div className="space-y-3">
              {projectAssignments.map((project) => (
                <div key={project.id} className="rounded-2xl border border-brand-secondary/10 bg-brand-light/40 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-brand-dark">{project.project_name}</p>
                      <p className="text-xs text-brand-secondary/70">
                        {project.business_domain || 'Interne'} · {project.role_on_project || 'Contributeur'} · {project.allocation_pct || 0}% d’allocation
                      </p>
                    </div>
                    <span className="rounded-full bg-white px-2 py-1 text-[10px] font-semibold text-brand-secondary">{project.status}</span>
                  </div>
                  {project.required_skill_names?.length ? (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {project.required_skill_names.map((name) => (
                        <span key={name} className="rounded-full bg-brand-secondary/10 px-2 py-1 text-[10px] font-semibold text-brand-secondary">{name}</span>
                      ))}
                    </div>
                  ) : null}
                </div>
              ))}
              {!projectAssignments.length ? <p className="text-xs text-brand-secondary/60">Aucun projet actif remonté pour le moment.</p> : null}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
