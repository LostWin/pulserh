import { useEffect, useMemo, useRef, useState } from 'react';
import {
  Bell, Camera, CheckCircle2, ChevronRight, Globe, KeyRound, LayoutGrid,
  Mail, MessageSquareMore, MoonStar, Palette, Save, ShieldCheck, UserCircle2,
} from 'lucide-react';
import { useKeycloak } from '@react-keycloak/web';

import PageHeader from '../components/PageHeader';
import Card, { CardHeader } from '../components/ui/Card';
import Avatar from '../components/ui/Avatar';
import Badge from '../components/ui/Badge';
import { api } from '../lib/api';
import { cn } from '../lib/utils';

const SECTIONS = [
  { id: 'profile', label: 'Profil', icon: UserCircle2 },
  { id: 'security', label: 'Sécurité', icon: ShieldCheck },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'appearance', label: 'Préférences', icon: Palette },
];

const DIGEST_OPTIONS = {
  never: { label: 'Jamais', hint: 'Aucun résumé automatique' },
  daily: { label: 'Quotidien', hint: 'Un point chaque matin' },
  weekly: { label: 'Hebdomadaire', hint: 'Un résumé chaque semaine' },
};

const THEME_OPTIONS = [
  { value: 'dark', label: 'Sombre', icon: MoonStar, description: 'Sidebar sombre, contraste fort' },
  { value: 'light', label: 'Clair', icon: LayoutGrid, description: 'Ambiance lumineuse et épurée' },
];

const LOCALE_OPTIONS = [
  { value: 'fr', label: 'Français' },
  { value: 'en', label: 'English' },
];

function SectionNav({ current, onChange }) {
  return (
    <Card className="sticky top-4 overflow-hidden">
      <div className="border-b border-brand-secondary/10 px-5 py-4">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-secondary/50">Navigation</p>
        <h2 className="mt-1 text-sm font-semibold text-brand-dark">Paramètres du compte</h2>
      </div>
      <div className="space-y-1 p-3">
        {SECTIONS.map((section) => {
          const Icon = section.icon;
          const active = current === section.id;
          return (
            <button
              key={section.id}
              type="button"
              onClick={() => onChange(section.id)}
              className={cn(
                'flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-left transition-colors',
                active ? 'bg-brand-secondary text-white shadow-sm' : 'text-brand-secondary/75 hover:bg-brand-light hover:text-brand-dark',
              )}
            >
              <span className="flex items-center gap-2">
                <Icon size={16} />
                <span className="text-sm font-medium">{section.label}</span>
              </span>
              <ChevronRight size={14} className={active ? 'opacity-100' : 'opacity-50'} />
            </button>
          );
        })}
      </div>
    </Card>
  );
}

function ChannelToggle({ icon: Icon, title, subtitle, checked, onChange }) {
  return (
    <label className="flex items-center justify-between gap-4 rounded-2xl border border-brand-secondary/10 bg-white px-4 py-4">
      <div className="flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-2xl bg-brand-light text-brand-secondary">
          <Icon size={18} />
        </div>
        <div>
          <div className="text-sm font-semibold text-brand-dark">{title}</div>
          <div className="text-xs text-brand-secondary/65">{subtitle}</div>
        </div>
      </div>
      <button
        type="button"
        onClick={onChange}
        className={cn(
          'relative h-7 w-12 rounded-full transition-colors',
          checked ? 'bg-brand-secondary' : 'bg-brand-secondary/20',
        )}
      >
        <span
          className={cn(
            'absolute top-0.5 h-6 w-6 rounded-full bg-white shadow transition-transform',
            checked ? 'left-5.5' : 'left-0.5',
          )}
        />
      </button>
    </label>
  );
}

export default function SettingsPage() {
  const { keycloak } = useKeycloak();
  const fileInputRef = useRef(null);
  const [activeSection, setActiveSection] = useState('profile');
  const [settings, setSettings] = useState({
    theme: 'dark',
    locale: 'fr',
    timezone: 'Africa/Lome',
    digest_frequency: 'daily',
    avatar_data_url: null,
    profile_title: '',
    email_enabled: true,
    in_app_enabled: true,
    slack_enabled: false,
  });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('info');

  const displayName = useMemo(
    () => [keycloak.tokenParsed?.given_name, keycloak.tokenParsed?.family_name].filter(Boolean).join(' ')
      || keycloak.tokenParsed?.name
      || keycloak.tokenParsed?.preferred_username
      || 'Utilisateur Pulse AI',
    [keycloak.tokenParsed],
  );
  const email = keycloak.tokenParsed?.email || 'Email indisponible';
  const roleLabel = useMemo(() => {
    const roles = keycloak.realmAccess?.roles || [];
    if (roles.includes('admin')) return 'Administrateur';
    if (roles.includes('director')) return 'Direction';
    if (roles.includes('hr')) return 'Ressources Humaine';
    if (roles.includes('manager')) return 'Manager';
    return 'Collaborateur';
  }, [keycloak.realmAccess?.roles]);

  useEffect(() => {
    let mounted = true;
    api.get('/users/me/settings')
      .then((data) => {
        if (!mounted) return;
        setSettings(data);
      })
      .catch((error) => {
        if (!mounted) return;
        setMessage(error.message || 'Impossible de charger vos paramètres.');
        setMessageType('error');
      });
    return () => {
      mounted = false;
    };
  }, []);

  const update = (patch) => setSettings((current) => ({ ...current, ...patch }));

  const save = async () => {
    setSaving(true);
    setMessage('');
    try {
      const data = await api.put('/users/me/settings', settings);
      setSettings(data);
      localStorage.setItem('pulse-theme', data.theme);
      setMessage('Paramètres enregistrés avec succès.');
      setMessageType('success');
    } catch (error) {
      setMessage(error.message || 'Impossible d’enregistrer vos paramètres.');
      setMessageType('error');
    } finally {
      setSaving(false);
    }
  };

  const uploadAvatar = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
      const data = await api.post('/users/me/avatar', formData);
      update({ avatar_data_url: data.avatar_data_url });
      setMessage('Photo de profil mise à jour.');
      setMessageType('success');
    } catch (error) {
      setMessage(error.message || 'Impossible de mettre à jour la photo.');
      setMessageType('error');
    }
  };

  const triggerPasswordChange = () => {
    keycloak.login({ action: 'UPDATE_PASSWORD' });
  };

  const digestMeta = DIGEST_OPTIONS[settings.digest_frequency] || DIGEST_OPTIONS.daily;

  return (
    <div className="animate-fade-in-up space-y-6">
      <PageHeader title="Settings" subtitle="Pilotez votre profil, votre sécurité et vos préférences personnelles depuis un seul espace.">
        <Badge variant="success" dot>
          Compte synchronisé Keycloak
        </Badge>
      </PageHeader>

      {message ? (
        <div className={cn(
          'rounded-2xl border px-4 py-3 text-sm',
          messageType === 'success' ? 'border-emerald-200 bg-emerald-50 text-emerald-700' : 'border-brand-danger/20 bg-brand-danger/5 text-brand-danger',
        )}>
          {message}
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-[280px_1fr]">
        <div className="space-y-6">
          <Card className="overflow-hidden">
            <div className="h-24 bg-gradient-to-r from-brand-secondary/20 via-brand-secondary/10 to-transparent" />
            <div className="-mt-10 px-5 pb-5">
              <Avatar name={displayName} src={settings.avatar_data_url} size="lg" className="h-20 w-20 rounded-2xl ring-4 ring-white" />
              <div className="mt-4">
                <h2 className="text-xl font-bold text-brand-dark">{displayName}</h2>
                <p className="mt-1 text-sm text-brand-secondary/70">{email}</p>
                <div className="mt-3 flex flex-wrap items-center gap-2">
                  <Badge variant="info">{roleLabel}</Badge>
                  <Badge variant="neutral">{digestMeta.label}</Badge>
                </div>
              </div>
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="mt-4 inline-flex items-center gap-2 rounded-xl border border-brand-secondary/15 bg-white px-4 py-2 text-sm font-medium text-brand-secondary transition-colors hover:bg-brand-light"
              >
                <Camera size={14} />
                Changer l’avatar
              </button>
              <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={uploadAvatar} />
            </div>
          </Card>

          <SectionNav current={activeSection} onChange={setActiveSection} />
        </div>

        <div className="space-y-6">
          {activeSection === 'profile' ? (
            <Card>
              <CardHeader title="Profil public" subtitle="Ce que voient les autres dans l’application." icon={UserCircle2} />
              <div className="grid grid-cols-1 gap-6 p-5 lg:grid-cols-[1.1fr_0.9fr]">
                <div className="space-y-4">
                  <label className="block text-sm font-medium text-brand-dark">
                    Titre affiché
                    <input
                      value={settings.profile_title || ''}
                      onChange={(event) => update({ profile_title: event.target.value })}
                      className="mt-2 w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm outline-none focus:border-brand-secondary"
                      placeholder="Ex: HR Business Partner"
                    />
                  </label>
                  <div className="rounded-2xl border border-brand-secondary/10 bg-brand-light/50 p-4">
                    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-secondary/50">Identité synchronisée</p>
                    <div className="mt-3 space-y-2 text-sm text-brand-dark">
                      <p><span className="font-semibold">Nom:</span> {displayName}</p>
                      <p><span className="font-semibold">Email:</span> {email}</p>
                      <p><span className="font-semibold">Rôle:</span> {roleLabel}</p>
                    </div>
                  </div>
                </div>
                <div className="rounded-3xl border border-brand-secondary/10 bg-white p-5 shadow-sm">
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-secondary/50">Preview carte profil</p>
                  <div className="mt-4 rounded-2xl border border-brand-secondary/10 bg-brand-light/40 p-4">
                    <div className="flex items-center gap-3">
                      <Avatar name={displayName} src={settings.avatar_data_url} />
                      <div>
                        <div className="font-semibold text-brand-dark">{displayName}</div>
                        <div className="text-sm text-brand-secondary/75">{settings.profile_title || roleLabel}</div>
                      </div>
                    </div>
                    <div className="mt-4 text-xs text-brand-secondary/65">
                      Ce titre est utilisé dans le header, les vues collaboratives et certains écrans métier.
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          ) : null}

          {activeSection === 'security' ? (
            <Card>
              <CardHeader title="Sécurité du compte" subtitle="L’authentification et le mot de passe sont gérés par Keycloak." icon={ShieldCheck} />
              <div className="grid grid-cols-1 gap-6 p-5 lg:grid-cols-[1fr_320px]">
                <div className="space-y-4">
                  <div className="rounded-2xl border border-brand-secondary/10 bg-brand-light/40 p-4">
                    <div className="flex items-start gap-3">
                      <div className="grid h-10 w-10 place-items-center rounded-2xl bg-white text-brand-secondary shadow-sm">
                        <KeyRound size={18} />
                      </div>
                      <div>
                        <h3 className="text-sm font-semibold text-brand-dark">Modifier le mot de passe</h3>
                        <p className="mt-1 text-sm text-brand-secondary/70">
                          Vous serez redirigé vers le parcours sécurisé Keycloak avec l’action `UPDATE_PASSWORD`.
                        </p>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={triggerPasswordChange}
                    className="inline-flex items-center gap-2 rounded-xl bg-brand-dark px-4 py-2.5 text-sm font-medium text-white transition hover:opacity-95"
                  >
                    <ShieldCheck size={15} />
                    Ouvrir la page de changement
                  </button>
                </div>
                <div className="rounded-3xl border border-brand-secondary/10 bg-white p-5 shadow-sm">
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-secondary/50">Bonnes pratiques</p>
                  <ul className="mt-4 space-y-3 text-sm text-brand-secondary/80">
                    <li className="flex items-start gap-2"><CheckCircle2 size={15} className="mt-0.5 text-brand-secondary" /> Utilisez un mot de passe unique pour Pulse AI.</li>
                    <li className="flex items-start gap-2"><CheckCircle2 size={15} className="mt-0.5 text-brand-secondary" /> Changez-le immédiatement si un poste partagé a été utilisé.</li>
                    <li className="flex items-start gap-2"><CheckCircle2 size={15} className="mt-0.5 text-brand-secondary" /> Vérifiez vos notifications de sécurité dans votre messagerie.</li>
                  </ul>
                </div>
              </div>
            </Card>
          ) : null}

          {activeSection === 'notifications' ? (
            <Card>
              <CardHeader title="Notifications" subtitle="Choisissez comment Pulse AI vous informe des événements RH et système." icon={Bell} />
              <div className="space-y-4 p-5">
                <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
                  <ChannelToggle
                    icon={Mail}
                    title="Email"
                    subtitle="Résumé, rappels et événements importants"
                    checked={Boolean(settings.email_enabled)}
                    onChange={() => update({ email_enabled: !settings.email_enabled })}
                  />
                  <ChannelToggle
                    icon={Bell}
                    title="Notifications internes"
                    subtitle="Cloche, toasts et centre de notifications"
                    checked={Boolean(settings.in_app_enabled)}
                    onChange={() => update({ in_app_enabled: !settings.in_app_enabled })}
                  />
                  <ChannelToggle
                    icon={MessageSquareMore}
                    title="Slack"
                    subtitle="Canal complémentaire si votre équipe l’utilise"
                    checked={Boolean(settings.slack_enabled)}
                    onChange={() => update({ slack_enabled: !settings.slack_enabled })}
                  />
                </div>

                <div className="grid grid-cols-1 gap-4 lg:grid-cols-[1fr_320px]">
                  <label className="block text-sm font-medium text-brand-dark">
                    Résumé automatique
                    <select
                      value={settings.digest_frequency}
                      onChange={(event) => update({ digest_frequency: event.target.value })}
                      className="mt-2 w-full rounded-xl border border-brand-secondary/20 bg-white px-3 py-2.5 text-sm outline-none focus:border-brand-secondary"
                    >
                      <option value="never">Jamais</option>
                      <option value="daily">Quotidien</option>
                      <option value="weekly">Hebdomadaire</option>
                    </select>
                  </label>

                  <div className="rounded-2xl border border-brand-secondary/10 bg-brand-light/50 p-4">
                    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-secondary/50">Résumé actuel</p>
                    <div className="mt-3 text-sm text-brand-dark">{digestMeta.label}</div>
                    <p className="mt-1 text-xs text-brand-secondary/70">{digestMeta.hint}</p>
                  </div>
                </div>
              </div>
            </Card>
          ) : null}

          {activeSection === 'appearance' ? (
            <Card>
              <CardHeader title="Préférences d’interface" subtitle="Thème, langue et fuseau horaire de référence pour vos écrans." icon={Palette} />
              <div className="grid grid-cols-1 gap-6 p-5 lg:grid-cols-[1fr_1fr]">
                <div className="space-y-4">
                  <div>
                    <div className="mb-3 text-sm font-medium text-brand-dark">Thème</div>
                    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                      {THEME_OPTIONS.map((option) => {
                        const Icon = option.icon;
                        const active = settings.theme === option.value;
                        return (
                          <button
                            key={option.value}
                            type="button"
                            onClick={() => update({ theme: option.value })}
                            className={cn(
                              'rounded-2xl border p-4 text-left transition-all',
                              active ? 'border-brand-secondary bg-brand-secondary/5 ring-2 ring-brand-secondary/10' : 'border-brand-secondary/10 bg-white hover:border-brand-secondary/30',
                            )}
                          >
                            <div className="flex items-center gap-3">
                              <div className={cn('grid h-10 w-10 place-items-center rounded-2xl', active ? 'bg-brand-secondary text-white' : 'bg-brand-light text-brand-secondary')}>
                                <Icon size={18} />
                              </div>
                              <div>
                                <div className="font-semibold text-brand-dark">{option.label}</div>
                                <div className="text-xs text-brand-secondary/65">{option.description}</div>
                              </div>
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  <label className="block text-sm font-medium text-brand-dark">
                    Langue
                    <select
                      value={settings.locale}
                      onChange={(event) => update({ locale: event.target.value })}
                      className="mt-2 w-full rounded-xl border border-brand-secondary/20 bg-white px-3 py-2.5 text-sm outline-none focus:border-brand-secondary"
                    >
                      {LOCALE_OPTIONS.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                    </select>
                  </label>

                  <label className="block text-sm font-medium text-brand-dark">
                    Fuseau horaire
                    <input
                      value={settings.timezone}
                      onChange={(event) => update({ timezone: event.target.value })}
                      className="mt-2 w-full rounded-xl border border-brand-secondary/20 px-3 py-2.5 text-sm outline-none focus:border-brand-secondary"
                    />
                  </label>
                </div>

                <div className="rounded-3xl border border-brand-secondary/10 bg-white p-5 shadow-sm">
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-secondary/50">Résumé interface</p>
                  <div className="mt-4 space-y-4">
                    <div className="rounded-2xl border border-brand-secondary/10 bg-brand-light/40 p-4">
                      <div className="flex items-center gap-2 text-sm font-semibold text-brand-dark">
                        <Globe size={16} className="text-brand-secondary" />
                        Langue active
                      </div>
                      <p className="mt-1 text-sm text-brand-secondary/75">
                        {LOCALE_OPTIONS.find((option) => option.value === settings.locale)?.label || settings.locale}
                      </p>
                    </div>
                    <div className="rounded-2xl border border-brand-secondary/10 bg-brand-light/40 p-4">
                      <div className="flex items-center gap-2 text-sm font-semibold text-brand-dark">
                        <Palette size={16} className="text-brand-secondary" />
                        Thème actif
                      </div>
                      <p className="mt-1 text-sm text-brand-secondary/75">
                        {THEME_OPTIONS.find((option) => option.value === settings.theme)?.label || settings.theme}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          ) : null}

          <div className="sticky bottom-4 z-20">
            <div className="flex items-center justify-between gap-4 rounded-2xl border border-brand-secondary/15 bg-white/95 px-5 py-4 shadow-lg backdrop-blur">
              <div>
                <div className="text-sm font-semibold text-brand-dark">Sauvegarder les préférences</div>
                <div className="text-xs text-brand-secondary/70">Le thème, les notifications et le profil seront persistés côté backend.</div>
              </div>
              <button
                onClick={save}
                disabled={saving}
                className="inline-flex items-center gap-2 rounded-xl bg-brand-secondary px-5 py-3 text-sm font-medium text-white transition hover:opacity-95 disabled:opacity-60"
              >
                <Save size={15} />
                {saving ? 'Enregistrement…' : 'Enregistrer'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
