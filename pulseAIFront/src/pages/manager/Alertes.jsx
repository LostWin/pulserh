import { Bell, ShieldAlert, Clock4 } from 'lucide-react';
import PageHeader from '../../components/PageHeader';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import { useNotifications } from '../../hooks/useNotifications';

const ALERT_STYLES = {
  critical: 'border-l-brand-danger bg-brand-danger/10',
  warning: 'border-l-brand-secondary bg-brand-light/80',
  info: 'border-l-brand-secondary/10 bg-brand-light',
};

const ALERT_BADGE = {
  critical: 'danger',
  warning: 'warning',
  info: 'neutral',
};

export default function ManagerAlertes() {
  const { notifications, markAsRead } = useNotifications();
  const managerAlerts = notifications;

  return (
    <div className="animate-fade-in-up space-y-6">
      <PageHeader title="Alertes" subtitle="Suivi opérationnel des alertes réelles remontées par PulseAI" />

      <Card className="rounded-4xl p-8 text-center">
        <div className="mx-auto grid h-16 w-16 place-items-center rounded-2xl bg-brand-secondary text-white shadow-sm">
          <Bell size={28} />
        </div>
        <Badge variant="neutral" className="mt-5 bg-brand-secondary text-white ring-brand-secondary/20">
          Temps réel
        </Badge>
        <h2 className="mt-4 text-2xl font-bold text-brand-dark">Alertes manager</h2>
        <p className="mx-auto mt-3 max-w-xl text-sm leading-relaxed text-brand-secondary/80">
          Ce tableau de bord centralise les alertes pertinentes pour votre équipe à partir des données réelles PulseAI.
        </p>
      </Card>

      <Card className="space-y-4 p-6">
        {managerAlerts.map((alert) => (
          <div key={alert.id} className={"rounded-3xl border p-4 shadow-sm " + ALERT_STYLES[alert.level]}>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <div className="flex items-center gap-2 text-sm text-brand-secondary/70">
                  <ShieldAlert size={16} />
                  Niveau {alert.level}
                </div>
                <p className="mt-2 text-base font-semibold text-brand-dark">{alert.title}</p>
                <p className="mt-1 text-sm text-brand-secondary/70">{alert.message}</p>
              </div>
              <div className="flex items-center gap-3">
                <Badge variant={ALERT_BADGE[alert.level]}>{alert.level === 'critical' ? 'Critique' : alert.level === 'warning' ? 'Important' : 'Info'}</Badge>
                <div className="text-xs text-brand-secondary/80">{alert.time}</div>
              </div>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              <button className="rounded-2xl bg-brand-dark px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-secondary">
                Voir le détail
              </button>
              <button onClick={() => markAsRead(alert.id)} className="rounded-2xl border border-brand-secondary/20 px-4 py-2 text-sm font-semibold text-brand-secondary transition hover:bg-brand-light">
                Marquer comme lu
              </button>
            </div>
          </div>
        ))}
      </Card>

      <Card className="grid gap-4 p-6 sm:grid-cols-2">
        <div className="rounded-3xl border border-brand-secondary/10 bg-brand-light p-5">
          <div className="flex items-center gap-3 text-brand-secondary/80">
            <Clock4 size={18} />
            <span>Dernière synchronisation</span>
          </div>
          <p className="mt-3 text-lg font-semibold text-brand-dark">À l’instant</p>
        </div>
        <div className="rounded-3xl border border-brand-secondary/10 bg-brand-light p-5">
          <div className="flex items-center gap-3 text-brand-secondary/80">
            <Bell size={18} />
            <span>Alertes actives</span>
          </div>
          <p className="mt-3 text-lg font-semibold text-brand-dark">{managerAlerts.length}</p>
        </div>
      </Card>
    </div>
  );
}
