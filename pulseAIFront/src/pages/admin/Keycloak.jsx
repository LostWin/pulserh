import { useEffect, useMemo, useState } from 'react';
import { Ban, CheckCircle, Key, Search, Shield, Users, Plus, UserPlus } from 'lucide-react';

import { api } from '../../lib/api';
import { cn } from '../../lib/utils';

const ROLES = ['Tous', 'collaborator', 'manager', 'hr', 'director', 'admin'];
const AVAILABLE_ROLES = ['collaborator', 'manager', 'hr', 'director', 'admin'];

const ROLE_COLORS = {
  admin: { bg: '#fee2e2', color: '#b91c1c' },
  hr: { bg: '#dbeafe', color: '#1d4ed8' },
  manager: { bg: '#ede9fe', color: '#7c3aed' },
  director: { bg: '#fef9c3', color: '#854d0e' },
  collaborator: { bg: '#dcfce7', color: '#15803d' },
};

export default function Keycloak() {
  const [activeTab, setActiveTab] = useState('active'); // 'active' | 'pending'
  const [users, setUsers] = useState([]);
  const [employees, setEmployees] = useState([]);
  
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('Tous');
  
  const [loadingId, setLoadingId] = useState(null);
  const [error, setError] = useState('');
  
  const [pendingForms, setPendingForms] = useState({});

  const loadData = async () => {
    try {
      const [usersData, empData] = await Promise.all([
        api.get('/admin/users'),
        api.get('/admin/employees/unlinked')
      ]);
      
      setUsers(usersData.items || []);
      
      const items = empData.items || [];
      // The endpoint already filters for unlinked employees
      const unlinked = items;
      setEmployees(unlinked);
      
      // Initialize pending forms
      const forms = {};
      unlinked.forEach(emp => {
        forms[emp.id] = { role: 'collaborator', password: '' };
      });
      setPendingForms(forms);
      
    } catch (err) {
      setError(err.message || 'Impossible de charger les données.');
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filteredUsers = useMemo(() => users.filter((user) =>
    (roleFilter === 'Tous' || user.role === roleFilter) &&
    (`${user.name} ${user.email} ${user.username}`.toLowerCase().includes(search.toLowerCase()))
  ), [users, roleFilter, search]);
  
  const filteredEmployees = useMemo(() => employees.filter((emp) =>
    (`${emp.first_name} ${emp.last_name} ${emp.email}`.toLowerCase().includes(search.toLowerCase()))
  ), [employees, search]);

  const performAction = async (userId, action) => {
    setLoadingId(`${action}-${userId}`);
    try {
      await api.post(`/admin/users/${userId}/${action}`);
      await loadData();
    } catch (err) {
      setError(err.message || `Impossible d'exécuter ${action}.`);
    } finally {
      setLoadingId(null);
    }
  };

  const handleCreateAccount = async (employeeId) => {
    setLoadingId(`create-${employeeId}`);
    setError('');
    try {
      const form = pendingForms[employeeId] || { role: 'collaborator', password: '' };
      await api.post('/admin/users', { employee_id: employeeId, ...form });
      await loadData();
    } catch (err) {
      setError(err.message || 'Impossible de créer l\'utilisateur.');
    } finally {
      setLoadingId(null);
    }
  };
  
  const updatePendingForm = (employeeId, field, value) => {
    setPendingForms(prev => ({
      ...prev,
      [employeeId]: { ...prev[employeeId], [field]: value }
    }));
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
          { label: 'À synchroniser', val: employees.length, icon: UserPlus },
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
      
      {/* Onglets de navigation */}
      <div className="flex border-b border-brand-secondary/10">
        <button
          onClick={() => setActiveTab('active')}
          className={cn("px-4 py-3 text-sm font-semibold transition-colors border-b-2", activeTab === 'active' ? "border-brand-primary text-brand-primary" : "border-transparent text-brand-secondary/50 hover:text-brand-dark")}
        >
          Comptes Actifs ({users.length})
        </button>
        <button
          onClick={() => setActiveTab('pending')}
          className={cn("px-4 py-3 text-sm font-semibold transition-colors border-b-2 flex items-center gap-2", activeTab === 'pending' ? "border-brand-primary text-brand-primary" : "border-transparent text-brand-secondary/50 hover:text-brand-dark")}
        >
          À synchroniser
          {employees.length > 0 && (
            <span className="rounded-full bg-brand-warning/20 px-2 py-0.5 text-[10px] font-bold text-brand-warning-dark">
              {employees.length}
            </span>
          )}
        </button>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-secondary/50" />
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Rechercher..." className="w-full rounded-xl border border-brand-secondary/20 bg-white pl-9 pr-4 py-2.5 text-sm outline-none focus:border-brand-secondary" />
        </div>
        
        {activeTab === 'active' && (
          <div className="flex gap-1.5 flex-wrap">
            {ROLES.map((role) => (
              <button key={role} onClick={() => setRoleFilter(role)} className={cn('rounded-xl px-3 py-2 text-xs font-medium transition-colors', roleFilter === role ? 'bg-brand-secondary text-white' : 'bg-white border border-brand-secondary/20 text-brand-secondary/70 hover:border-brand-secondary/40')}>
                {role}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="rounded-2xl bg-white border border-brand-secondary/10 shadow-sm overflow-hidden">
        {activeTab === 'active' ? (
          <table className="w-full text-sm">
            <thead className="bg-brand-light/60">
              <tr>{['Utilisateur', 'Email', 'Rôle', 'MFA', 'Dernier accès', 'Statut', 'Actions'].map((header) => (
                <th key={header} className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-widest text-brand-secondary/50">{header}</th>
              ))}</tr>
            </thead>
            <tbody className="divide-y divide-brand-secondary/5">
              {filteredUsers.length === 0 ? (
                <tr><td colSpan="7" className="p-8 text-center text-brand-secondary/50">Aucun compte trouvé.</td></tr>
              ) : (
                filteredUsers.map((user) => {
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
                          <button onClick={() => performAction(user.id, 'reset-password')} disabled={loadingId === `reset-password-${user.id}`} title="Réinitialiser le mot de passe" className={cn('grid h-7 w-7 place-items-center rounded-lg transition-colors', loadingId === `reset-password-${user.id}` ? 'bg-brand-secondary text-white' : 'hover:bg-brand-light text-brand-secondary/50 hover:text-brand-secondary')}>
                            <Key size={13} />
                          </button>
                          <button onClick={() => performAction(user.id, user.active ? 'block' : 'unblock')} disabled={loadingId === `${user.active ? 'block' : 'unblock'}-${user.id}`} title={user.active ? 'Désactiver' : 'Activer'} className={cn('grid h-7 w-7 place-items-center rounded-lg transition-colors', 'hover:bg-brand-light text-brand-secondary/50 hover:text-brand-secondary')}>
                            {user.active ? <Ban size={13} /> : <CheckCircle size={13} />}
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-brand-light/60">
              <tr>{['Employé', 'Email', 'Rôle', 'Mot de passe', 'Actions'].map((header) => (
                <th key={header} className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-widest text-brand-secondary/50">{header}</th>
              ))}</tr>
            </thead>
            <tbody className="divide-y divide-brand-secondary/5">
              {filteredEmployees.length === 0 ? (
                <tr><td colSpan="5" className="p-8 text-center text-brand-secondary/50">Tous les employés ont déjà un compte.</td></tr>
              ) : (
                filteredEmployees.map((emp) => {
                  const form = pendingForms[emp.id] || { role: 'collaborator', password: '' };
                  const isCreating = loadingId === `create-${emp.id}`;
                  
                  return (
                    <tr key={emp.id} className="hover:bg-brand-light/40 transition-colors">
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2.5">
                          <div className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-brand-secondary/10 text-xs font-bold text-brand-secondary">
                            {emp.first_name[0]}{emp.last_name[0]}
                          </div>
                          <div>
                            <span className="font-medium text-brand-dark">{emp.first_name} {emp.last_name}</span>
                            {(emp.job || emp.department) && (
                              <div className="text-[10px] text-brand-secondary/50">
                                {emp.job} {emp.department ? `(${emp.department})` : ''}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-brand-secondary/70">{emp.email}</td>
                      <td className="px-4 py-3 w-40">
                        <select 
                          value={form.role} 
                          onChange={(e) => updatePendingForm(emp.id, 'role', e.target.value)}
                          className="w-full rounded-lg border border-brand-secondary/20 bg-transparent px-2 py-1 text-xs outline-none focus:border-brand-primary"
                        >
                          {AVAILABLE_ROLES.map(role => <option key={role} value={role}>{role}</option>)}
                        </select>
                      </td>
                      <td className="px-4 py-3 w-48">
                        <input 
                          type="password" 
                          value={form.password}
                          onChange={(e) => updatePendingForm(emp.id, 'password', e.target.value)}
                          placeholder="Auto-généré"
                          className="w-full rounded-lg border border-brand-secondary/20 bg-transparent px-2 py-1 text-xs outline-none focus:border-brand-primary"
                        />
                      </td>
                      <td className="px-4 py-3">
                        <button 
                          onClick={() => handleCreateAccount(emp.id)}
                          disabled={isCreating}
                          className={cn(
                            "flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors",
                            isCreating ? "bg-brand-secondary/10 text-brand-secondary" : "bg-brand-primary text-white hover:bg-brand-primary/90"
                          )}
                        >
                          {isCreating ? 'Création...' : (
                            <>
                              <Plus size={12} />
                              Créer
                            </>
                          )}
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
