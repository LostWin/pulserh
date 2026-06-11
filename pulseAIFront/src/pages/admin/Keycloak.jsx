import { useState } from 'react';
import { Users, Search, Plus, Shield, Key, Ban, CheckCircle, X } from 'lucide-react';
import { cn } from '../../lib/utils';

const ROLES = ['Tous', 'Collaborateur', 'Manager', 'RH', 'Direction', 'Admin'];

const INITIAL_USERS = [
  { id: 1, name: 'Inès Garcia', email: 'i.garcia@pulse-rh.ai', role: 'RH', active: true, lastLogin: 'Il y a 5 min', mfa: true },
  { id: 2, name: 'Camille Laurent', email: 'c.laurent@pulse-rh.ai', role: 'Manager', active: true, lastLogin: 'Il y a 2 h', mfa: true },
  { id: 3, name: 'Admin Système', email: 'admin@pulse-rh.ai', role: 'Admin', active: true, lastLogin: 'Il y a 22 min', mfa: true },
  { id: 4, name: 'Alex Dupont', email: 'a.dupont@pulse-rh.ai', role: 'Collaborateur', active: true, lastLogin: 'Hier', mfa: false },
  { id: 5, name: 'Noah Petit', email: 'n.petit@pulse-rh.ai', role: 'Collaborateur', active: false, lastLogin: 'Il y a 5 j', mfa: false },
  { id: 6, name: 'Sophie Martin', email: 's.martin@pulse-rh.ai', role: 'Direction', active: true, lastLogin: 'Il y a 1 j', mfa: true },
];

const ROLE_COLORS = {
  Admin: { bg: '#fee2e2', color: '#b91c1c' },
  RH: { bg: '#dbeafe', color: '#1d4ed8' },
  Manager: { bg: '#ede9fe', color: '#7c3aed' },
  Direction: { bg: '#fef9c3', color: '#854d0e' },
  Collaborateur: { bg: '#dcfce7', color: '#15803d' },
};

export default function Keycloak() {
  const [users, setUsers] = useState(INITIAL_USERS);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('Tous');
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', role: 'Collaborateur' });
  const [resetId, setResetId] = useState(null);

  const filtered = users.filter((u) =>
    (roleFilter === 'Tous' || u.role === roleFilter) &&
    (u.name.toLowerCase().includes(search.toLowerCase()) || u.email.toLowerCase().includes(search.toLowerCase()))
  );

  const toggleActive = (id) => setUsers((p) => p.map((u) => u.id === id ? { ...u, active: !u.active } : u));

  const addUser = () => {
    if (!form.name || !form.email) return;
    setUsers((p) => [...p, { id: Date.now(), ...form, active: true, lastLogin: '—', mfa: false }]);
    setShowModal(false); setForm({ name: '', email: '', role: 'Collaborateur' });
  };

  const resetPassword = (id) => {
    setResetId(id);
    setTimeout(() => setResetId(null), 2000);
  };

  return (
    <div className="animate-fade-in-up space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-brand-dark">Gestion Keycloak</h1>
          <p className="mt-1 text-sm text-brand-secondary/70">Gérez les utilisateurs, rôles et accès de la plateforme.</p>
        </div>
        <button onClick={() => setShowModal(true)}
          className="flex items-center gap-2 rounded-xl bg-brand-secondary px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-brand-dark transition-colors">
          <Plus size={15} />Créer un utilisateur
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[
          { label: 'Total', val: users.length, icon: Users },
          { label: 'Actifs', val: users.filter((u) => u.active).length, icon: CheckCircle },
          { label: 'MFA activé', val: users.filter((u) => u.mfa).length, icon: Shield },
          { label: 'Inactifs', val: users.filter((u) => !u.active).length, icon: Ban },
        ].map((s) => {
          const Icon = s.icon;
          return (
            <div key={s.label} className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-4">
              <div className="flex items-center gap-2 mb-1">
                <Icon size={14} className="text-brand-secondary" />
                <span className="text-xs text-brand-secondary/60 uppercase tracking-wider font-semibold">{s.label}</span>
              </div>
              <div className="text-2xl font-bold text-brand-dark">{s.val}</div>
            </div>
          );
        })}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-secondary/50" />
          <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Rechercher un utilisateur…"
            className="w-full rounded-xl border border-brand-secondary/20 bg-white pl-9 pr-4 py-2.5 text-sm outline-none focus:border-brand-secondary" />
        </div>
        <div className="flex gap-1.5 flex-wrap">
          {ROLES.map((r) => (
            <button key={r} onClick={() => setRoleFilter(r)}
              className={cn('rounded-xl px-3 py-2 text-xs font-medium transition-colors',
                roleFilter === r ? 'bg-brand-secondary text-white' : 'bg-white border border-brand-secondary/20 text-brand-secondary/70 hover:border-brand-secondary/40')}>
              {r}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-brand-light/60">
            <tr>{['Utilisateur', 'Email', 'Rôle', 'MFA', 'Dernier accès', 'Statut', 'Actions'].map((h) => (
              <th key={h} className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-widest text-brand-secondary/50">{h}</th>
            ))}</tr>
          </thead>
          <tbody className="divide-y divide-brand-secondary/5">
            {filtered.map((u) => {
              const rc = ROLE_COLORS[u.role] || { bg: '#f3f4f6', color: '#374151' };
              return (
                <tr key={u.id} className={cn('hover:bg-brand-light/40 transition-colors', !u.active && 'opacity-60')}>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2.5">
                      <div className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-brand-secondary/10 text-xs font-bold text-brand-secondary">
                        {u.name.split(' ').map((n) => n[0]).join('').slice(0, 2)}
                      </div>
                      <span className="font-medium text-brand-dark">{u.name}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-brand-secondary/70">{u.email}</td>
                  <td className="px-4 py-3">
                    <span className="rounded-full px-2.5 py-0.5 text-xs font-semibold" style={{ backgroundColor: rc.bg, color: rc.color }}>{u.role}</span>
                  </td>
                  <td className="px-4 py-3">
                    {u.mfa ? <Shield size={14} className="text-brand-secondary" /> : <span className="text-brand-secondary/30 text-xs">—</span>}
                  </td>
                  <td className="px-4 py-3 text-brand-secondary/50 text-xs">{u.lastLogin}</td>
                  <td className="px-4 py-3">
                    <span className={cn('rounded-full px-2.5 py-0.5 text-xs font-medium',
                      u.active ? 'bg-brand-secondary/10 text-brand-secondary' : 'bg-brand-dark/10 text-brand-dark/60')}>
                      {u.active ? 'Actif' : 'Inactif'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <button onClick={() => resetPassword(u.id)} title="Réinitialiser le mot de passe"
                        className={cn('grid h-7 w-7 place-items-center rounded-lg transition-colors',
                          resetId === u.id ? 'bg-brand-secondary text-white' : 'hover:bg-brand-light text-brand-secondary/50 hover:text-brand-secondary')}>
                        {resetId === u.id ? <CheckCircle size={13} /> : <Key size={13} />}
                      </button>
                      <button onClick={() => toggleActive(u.id)} title={u.active ? 'Désactiver' : 'Activer'}
                        className={cn('grid h-7 w-7 place-items-center rounded-lg transition-colors',
                          u.active ? 'hover:bg-brand-warning/10 text-brand-secondary/50 hover:text-brand-warning' : 'hover:bg-brand-secondary/10 text-brand-secondary/50 hover:text-brand-secondary')}>
                        {u.active ? <Ban size={13} /> : <CheckCircle size={13} />}
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-bold text-brand-dark">Créer un utilisateur</h2>
              <button onClick={() => setShowModal(false)} className="grid h-8 w-8 place-items-center rounded-lg hover:bg-brand-light text-brand-secondary/60"><X size={16} /></button>
            </div>
            <div className="space-y-4">
              {[{ label: 'Nom complet', key: 'name', placeholder: 'Prénom Nom' }, { label: 'Email', key: 'email', placeholder: 'prenom.nom@pulse-rh.ai' }].map((f) => (
                <div key={f.key}>
                  <label className="block text-xs font-semibold uppercase tracking-widest text-brand-secondary/50 mb-1.5">{f.label}</label>
                  <input value={form[f.key]} onChange={(e) => setForm((p) => ({ ...p, [f.key]: e.target.value }))} placeholder={f.placeholder}
                    className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm outline-none focus:border-brand-secondary" />
                </div>
              ))}
              <div>
                <label className="block text-xs font-semibold uppercase tracking-widest text-brand-secondary/50 mb-1.5">Rôle</label>
                <select value={form.role} onChange={(e) => setForm((p) => ({ ...p, role: e.target.value }))}
                  className="w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm outline-none bg-white">
                  {ROLES.filter((r) => r !== 'Tous').map((r) => <option key={r}>{r}</option>)}
                </select>
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={addUser} className="flex-1 rounded-xl bg-brand-secondary py-2.5 text-sm font-medium text-white hover:bg-brand-dark transition-colors">Créer</button>
              <button onClick={() => setShowModal(false)} className="flex-1 rounded-xl border border-brand-secondary/20 py-2.5 text-sm font-medium text-brand-secondary hover:bg-brand-light transition-colors">Annuler</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
