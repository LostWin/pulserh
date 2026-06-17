import {
  LayoutDashboard, MessageSquare, FileText, User, Calendar, CheckSquare,
  Users, TrendingUp, Bell, Users2, Upload, GitMerge, ShieldAlert,
  BarChart4, FileSpreadsheet, Shield, Cpu, Activity, Settings, Briefcase, Database
} from 'lucide-react';

/** Single source of truth for the five access profiles of the platform. */
export const ROLES = ['Collaborateur', 'Manager', 'RH', 'Direction', 'Admin'];

export const ROLE_META = {
  Collaborateur: {
    icon: User, color: 'bg-brand-secondary', accent: 'blue', section: 'collaborateur',
    desc: 'Accès espace personnel', home: '/collaborateur/dashboard',
  },
  Manager: {
    icon: Users, color: 'bg-brand-secondary', accent: 'purple', section: 'manager',
    desc: "Gestion d'équipe", home: '/manager/dashboard',
  },
  RH: {
    icon: Briefcase, color: 'bg-brand-secondary', accent: 'emerald', section: 'rh',
    desc: 'Pilotage ressources humaines', home: '/rh/dashboard',
  },
  Direction: {
    icon: Shield, color: 'bg-brand-secondary', accent: 'amber', section: 'direction',
    desc: 'Vue stratégique', home: '/direction/dashboard',
  },
  Admin: {
    icon: Settings, color: 'bg-brand-secondary', accent: 'slate', section: 'admin',
    desc: 'Administration plateforme', home: '/admin/monitoring',
  },
};

/** Navigation entries per role — consumed by the sidebar. */
export const SIDEBAR_LINKS = {
  Collaborateur: [
    { name: 'Dashboard', path: '/collaborateur/dashboard', icon: LayoutDashboard },
    { name: 'Assistant IA', path: '/collaborateur/assistant', icon: MessageSquare },
    { name: 'Documents', path: '/collaborateur/documents', icon: FileText },
    { name: 'Profil', path: '/collaborateur/profil', icon: User },
    { name: 'Congés', path: '/collaborateur/conges', icon: Calendar },
    { name: 'Onboarding', path: '/collaborateur/onboarding', icon: CheckSquare },
  ],
  Manager: [
    { name: 'Dashboard', path: '/manager/dashboard', icon: LayoutDashboard },
    { name: 'Mon Équipe', path: '/manager/equipe', icon: Users },
    { name: 'Prédictions', path: '/manager/predictions', icon: TrendingUp },
    { name: 'Alertes', path: '/manager/alertes', icon: Bell },
    { name: 'Entretiens', path: '/manager/entretiens', icon: Users2 },
  ],
  RH: [
    { name: 'Dashboard', path: '/rh/dashboard', icon: LayoutDashboard },
    { name: 'Import Données', path: '/rh/import', icon: Upload },
    { name: 'Départements', path: '/rh/departements', icon: GitMerge },
    { name: 'Employés', path: '/rh/employes', icon: Users },
    { name: 'Carrières', path: '/rh/carrieres', icon: TrendingUp },
    { name: 'Documents', path: '/rh/documents', icon: FileText },
    { name: 'Workflows', path: '/rh/workflows', icon: CheckSquare },
    { name: 'Alertes', path: '/rh/alertes', icon: ShieldAlert },
    { name: 'Supervision IA', path: '/rh/supervision-ia', icon: Cpu },
  ],
  Direction: [
    { name: 'Dashboard', path: '/direction/dashboard', icon: LayoutDashboard },
    { name: 'Simulations', path: '/direction/simulations', icon: BarChart4 },
    { name: 'Rapports', path: '/direction/rapports', icon: FileSpreadsheet },
    { name: 'Alertes Critiques', path: '/direction/alertes', icon: ShieldAlert },
  ],
  Admin: [
    { name: 'Monitoring', path: '/admin/monitoring', icon: Activity },
    { name: 'Keycloak', path: '/admin/keycloak', icon: Users },
    { name: 'Base de données', path: '/admin/database', icon: Database },
    { name: 'Sécurité', path: '/admin/securite', icon: Shield },
    { name: 'Config IA', path: '/admin/config-ia', icon: Cpu },
    { name: 'Data Access', path: '/admin/data-access', icon: ShieldAlert },
    { name: 'Moteur Doc.', path: '/admin/documents', icon: FileText },
    { name: 'Audit', path: '/admin/audit', icon: FileText },
  ],
};
