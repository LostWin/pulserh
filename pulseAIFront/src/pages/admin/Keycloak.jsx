import { useEffect, useMemo, useState } from 'react';
import { Ban, CheckCircle, Key, Search, Shield, Users } from 'lucide-react';

import { api } from '../../lib/api';
import { cn } from '../../lib/utils';

const ROLES = ['Tous', 'collaborator', 'manager', 'hr', 'director', 'admin'];

const ROLE_COLORS = {
  admin: { bg: '#fee2e2', color: '#b91c1c' },
  hr: { bg: '#dbeafe', color: '#1d4ed8' },
  manager: { bg: '#ede9fe', color: '#7c3aed' },
  director: { bg: '#fef9c3', color: '#854d0e' },
  collaborator: { bg: '#dcfce7', color: '#15803d' },
};

export default function Keycloak() {
  const [users, setUsers] = useState([]);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('Tous');
  const [loadingId, setLoadingId] = useState(null);
  const [error, setError] = useState('');

  const load = async () => {
    const data = await api.get('/admin/users');
    setUsers(data.items || []);
  };

  useEffect(() => {
    load().catch((err) => setError(err.message || 'Impossible de charger les comptes Keycloak.'));
  }, []);

  const filtered = useMemo(() => users.filter((user) =>
    (roleFilter === 'Tous' || user.role === roleFilter) &&
    (`${user.name} ${user.email} ${user.username}`.toLowerCase().includes(search.toLowerCase()))
  ), [users, roleFilter, search]);

  const perform = async (userId, action) => {
    setLoadingId(`${action}-${userId}`);
    try {
      await api.post(`/admin/users/${userId}/${action}`);
      await load();
    } catch (err) {
      setError(err.message || `Impossible d'exécuter ${action}.`);
    } finally {
      setLoadingId(null);
    }
  };

  return (
    <div className="animate-fade-in-up space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-brand-dark">Gestion Keycloak</h1>
          <p className="mt-1 text-sm text-brand-secondary/70">Les comptes sont automatiquement provisionnés à partir des employés et synchronisés avec les rôles métier.</p>
        </div>
      </div>
      {error ? <div className="rounded-xl bg-white p-4 text-sm text-brand-warning">{error}</div> : null}

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[
          { label: 'Total', val: users.length, icon: Users },
          { label: 'Actifs', val: users.filter((user) => user.active).length, icon: CheckCircle },
          { label: 'MFA activé', val: users.filter((user) => user.mfa).length, icon: Shield },
          { label: 'Inactifs', val: users.filter((user) => !user.active).length, icon: Ban },
        ].map((item) => {
          const Icon = item.icon;
          return (
            <div key={item.label} className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm p-4">
              <div className="mb-1 flex items-center gap-2">
                <Icon size={14} className="text-brand-secondary" />
                <span className="text-xs text-brand-secondary/60 uppercase tracking-wider font-semibold">{item.label}</span>
              </div>
              <div className="text-2xl font-bold text-brand-dark">{item.val}</div>
            </div>
          );
        })}
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-secondary/50" />
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Rechercher un utilisateur…" className="w-full rounded-xl border border-brand-secondary/20 bg-white pl-9 pr-4 py-2.5 text-sm outline-none focus:border-brand-secondary" />
        </div>
        <div className="flex gap-1.5 flex-wrap">
          {ROLES.map((role) => (
            <button key={role} onClick={() => setRoleFilter(role)} className={cn('rounded-xl px-3 py-2 text-xs font-medium transition-colors', roleFilter === role ? 'bg-brand-secondary text-white' : 'bg-white border border-brand-secondary/20 text-brand-secondary/70 hover:border-brand-secondary/40')}>
              {role}
            </button>
          ))}
        </div>
      </div>

      <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-brand-light/60">
            <tr>{['Utilisateur', 'Email', 'Rôle', 'MFA', 'Dernier accès', 'Statut', 'Actions'].map((header) => (
              <th key={header} className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-widest text-brand-secondary/50">{header}</th>
            ))}</tr>
          </thead>
          <tbody className="divide-y divide-brand-secondary/5">
            {filtered.map((user) => {
              const colors = ROLE_COLORS[user.role] || { bg: '#f3f4f6', color: '#374151' };
              return (
                <tr key={user.id} className={cn('hover:bg-brand-light/40 transition-colors', !user.active && 'opacity-60')}>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2.5">
                      <div className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-brand-secondary/10 text-xs font-bold text-brand-secondary">
                        {user.name.split(' ').map((part) => part[0]).join('').slice(0, 2)}
                      </div>
                      <div>
                        <span className="font-medium text-brand-dark">{user.name}</span>
                        <div className="text-xs text-brand-secondary/60">@{user.username}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-brand-secondary/70">{user.email}</td>
                  <td className="px-4 py-3">
                    <span className="rounded-full px-2.5 py-0.5 text-xs font-semibold" style={{ backgroundColor: colors.bg, color: colors.color }}>{user.role}</span>
                  </td>
                  <td className="px-4 py-3">{user.mfa ? <Shield size={14} className="text-brand-secondary" /> : <span className="text-brand-secondary/30 text-xs">—</span>}</td>
                  <td className="px-4 py-3 text-brand-secondary/50 text-xs">{user.lastLogin}</td>
                  <td className="px-4 py-3">
                    <span className={cn('rounded-full px-2.5 py-0.5 text-xs font-medium', user.active ? 'bg-brand-secondary/10 text-brand-secondary' : 'bg-brand-dark/10 text-brand-dark/60')}>
                      {user.active ? 'Actif' : 'Inactif'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <button onClick={() => perform(user.id, 'reset-password')} title="Réinitialiser le mot de passe" className={cn('grid h-7 w-7 place-items-center rounded-lg transition-colors', loadingId === `reset-password-${user.id}` ? 'bg-brand-secondary text-white' : 'hover:bg-brand-light text-brand-secondary/50 hover:text-brand-secondary')}>
                        <Key size={13} />
                      </button>
                      <button onClick={() => perform(user.id, user.active ? 'block' : 'unblock')} title={user.active ? 'Désactiver' : 'Activer'} className={cn('grid h-7 w-7 place-items-center rounded-lg transition-colors', 'hover:bg-brand-light text-brand-secondary/50 hover:text-brand-secondary')}>
                        {user.active ? <Ban size={13} /> : <CheckCircle size={13} />}
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
