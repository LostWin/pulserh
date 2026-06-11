// Centralised mock data for the YDAYS HR prototype.
// One roster feeds the manager team view, the RH employee table and all KPIs,
// so figures stay coherent from one screen to the next.

export const engagementTrend = [
  { month: 'Jan', engagement: 74, risque: 18 },
  { month: 'Fév', engagement: 72, risque: 21 },
  { month: 'Mar', engagement: 76, risque: 16 },
  { month: 'Avr', engagement: 71, risque: 24 },
  { month: 'Mai', engagement: 78, risque: 14 },
  { month: 'Juin', engagement: 81, risque: 12 },
];

export const departments = [
  { name: 'Engineering', headcount: 42, engagement: 79, risk: 11 },
  { name: 'Ventes', headcount: 28, engagement: 66, risk: 28 },
  { name: 'Marketing', headcount: 16, engagement: 74, risk: 17 },
  { name: 'Support', headcount: 21, engagement: 70, risk: 23 },
  { name: 'Finance', headcount: 12, engagement: 83, risk: 8 },
  { name: 'RH', headcount: 8, engagement: 86, risk: 5 },
];

export const riskDistribution = [
  { name: 'Engagés', value: 98, level: 'low' },
  { name: 'À surveiller', value: 21, level: 'medium' },
  { name: 'À risque', value: 8, level: 'high' },
];

export const employees = [
  { id: 1, name: 'Camille Laurent', title: 'Lead Developer', department: 'Engineering', engagement: 88, risk: 'low', delta: 3, tenure: '4 ans', lastActive: "Aujourd'hui", signal: 'Forte contribution, mentore 2 juniors' },
  { id: 2, name: 'Yanis Moreau', title: 'Account Executive', department: 'Ventes', engagement: 54, risk: 'high', delta: -12, tenure: '2 ans', lastActive: 'Il y a 3 j', signal: "Baisse d'activité et heures supplémentaires élevées" },
  { id: 3, name: 'Sofia Nguyen', title: 'Brand Manager', department: 'Marketing', engagement: 76, risk: 'low', delta: 1, tenure: '3 ans', lastActive: "Aujourd'hui", signal: 'Stable' },
  { id: 4, name: 'Lucas Bernard', title: 'Support Specialist', department: 'Support', engagement: 61, risk: 'medium', delta: -6, tenure: '1 an', lastActive: 'Hier', signal: 'Volume de tickets en hausse, satisfaction en baisse' },
  { id: 5, name: 'Emma Rossi', title: 'Backend Engineer', department: 'Engineering', engagement: 82, risk: 'low', delta: 4, tenure: '5 ans', lastActive: "Aujourd'hui", signal: 'Très engagée' },
  { id: 6, name: 'Noah Petit', title: 'Sales Representative', department: 'Ventes', engagement: 48, risk: 'high', delta: -15, tenure: '8 mois', lastActive: 'Il y a 5 j', signal: 'Objectifs non atteints, désengagement détecté' },
  { id: 7, name: 'Léa Dubois', title: 'Financial Analyst', department: 'Finance', engagement: 85, risk: 'low', delta: 2, tenure: '6 ans', lastActive: "Aujourd'hui", signal: 'Stable' },
  { id: 8, name: 'Adam Faure', title: 'Support Specialist', department: 'Support', engagement: 58, risk: 'medium', delta: -8, tenure: '2 ans', lastActive: 'Hier', signal: 'Absences répétées ces 30 derniers jours' },
  { id: 9, name: 'Chloé Martin', title: 'Growth Marketer', department: 'Marketing', engagement: 73, risk: 'medium', delta: -4, tenure: '3 ans', lastActive: "Aujourd'hui", signal: 'Engagement en léger recul' },
  { id: 10, name: 'Hugo Lefebvre', title: 'Frontend Engineer', department: 'Engineering', engagement: 79, risk: 'low', delta: 0, tenure: '2 ans', lastActive: "Aujourd'hui", signal: 'Stable' },
  { id: 11, name: 'Inès Garcia', title: 'HR Business Partner', department: 'RH', engagement: 90, risk: 'low', delta: 5, tenure: '4 ans', lastActive: "Aujourd'hui", signal: 'Ambassadrice de la culture' },
  { id: 12, name: 'Théo Roux', title: 'Account Manager', department: 'Ventes', engagement: 64, risk: 'medium', delta: -5, tenure: '1 an', lastActive: 'Il y a 2 j', signal: 'Charge de travail élevée' },
];

/** Personal data for the logged-in collaborator space. */
export const myProfile = {
  engagement: 82,
  engagementDelta: 4,
  trend: [
    { month: 'Jan', score: 75 },
    { month: 'Fév', score: 73 },
    { month: 'Mar', score: 78 },
    { month: 'Avr', score: 77 },
    { month: 'Mai', score: 80 },
    { month: 'Juin', score: 82 },
  ],
  conges: { restants: 18, total: 30 },
  documents: 7,
  prochainEntretien: '24 juin 2026',
  onboarding: [
    { label: 'Compléter le profil', done: true },
    { label: 'Signer le contrat électronique', done: true },
    { label: 'Configurer le poste de travail', done: true },
    { label: 'Formation sécurité & RGPD', done: false },
    { label: 'Rencontrer son buddy', done: false },
  ],
  tasks: [
    { label: 'Valider la note de frais Q2', due: 'Demain', priority: 'high' },
    { label: "Compléter l'auto-évaluation annuelle", due: '18 juin', priority: 'medium' },
    { label: 'Réserver la formation « React avancé »', due: '30 juin', priority: 'low' },
  ],
};

export const assistantSuggestions = [
  'Combien de jours de congés me reste-t-il ?',
  'Comment poser une demande de télétravail ?',
  'Explique-moi les lignes de ma fiche de paie',
  'Quelles formations sont disponibles ce trimestre ?',
];

export const managerAlerts = [
  { level: 'high', text: 'Noah Petit — risque de départ élevé détecté par l’IA', time: 'Il y a 1 j' },
  { level: 'medium', text: '3 entretiens annuels à planifier avant fin juin', time: 'Il y a 2 j' },
  { level: 'low', text: "Rapport d'engagement hebdomadaire disponible", time: 'Il y a 3 j' },
];

export const services = [
  { name: 'API Gateway', status: 'operational', latency: 42, uptime: '99.98%' },
  { name: 'Moteur IA — Prédictions', status: 'operational', latency: 180, uptime: '99.91%' },
  { name: 'Keycloak — Authentification', status: 'operational', latency: 65, uptime: '99.99%' },
  { name: 'Base de données', status: 'degraded', latency: 320, uptime: '99.72%' },
  { name: 'Service Documents', status: 'operational', latency: 88, uptime: '99.95%' },
  { name: "Pipeline d'ingestion", status: 'operational', latency: 110, uptime: '99.88%' },
];

export const trafficData = [
  { time: '08h', req: 320, err: 2 },
  { time: '10h', req: 540, err: 4 },
  { time: '12h', req: 610, err: 3 },
  { time: '14h', req: 720, err: 9 },
  { time: '16h', req: 680, err: 5 },
  { time: '18h', req: 430, err: 2 },
];

export const auditEvents = [
  { user: 'i.garcia@ydays.com', action: 'a exporté la liste des employés', time: 'Il y a 5 min', type: 'export' },
  { user: 'admin@ydays.com', action: 'a modifié un rôle Keycloak', time: 'Il y a 22 min', type: 'security' },
  { user: 'Moteur IA', action: 'a recalculé les scores de risque', time: 'Il y a 1 h', type: 'ai' },
  { user: 'c.laurent@ydays.com', action: 's’est connecté', time: 'Il y a 2 h', type: 'auth' },
  { user: 'Système', action: 'sauvegarde quotidienne effectuée', time: 'Il y a 6 h', type: 'system' },
];

/** Strategic time-series for the Direction space (turnover cost avoided, in k€). */
export const turnoverSaved = [
  { month: 'Jan', economie: 18, depart: 6 },
  { month: 'Fév', economie: 22, depart: 5 },
  { month: 'Mar', economie: 31, depart: 4 },
  { month: 'Avr', economie: 27, depart: 5 },
  { month: 'Mai', economie: 38, depart: 3 },
  { month: 'Juin', economie: 45, depart: 2 },
];
