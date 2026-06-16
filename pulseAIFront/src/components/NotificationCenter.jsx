import { useEffect, useRef, useState } from 'react';
import { Bell, CheckCheck, Info, ShieldAlert, TriangleAlert, X } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useNotifications } from '../hooks/useNotifications';
import { cn } from '../lib/utils';

const LEVEL_STYLES = {
  critical: { icon: ShieldAlert, panel: 'border-red-200/80 bg-red-50/80', title: 'text-red-800' },
  warning: { icon: TriangleAlert, panel: 'border-yellow-200/80 bg-yellow-50/80', title: 'text-yellow-800' },
  info: { icon: Info, panel: 'border-brand-secondary/10 bg-white', title: 'text-brand-dark' },
};

function NotificationToast({ notification, onClose, onRead }) {
  const style = LEVEL_STYLES[notification.level] || LEVEL_STYLES.info;
  const Icon = style.icon;

  return (
    <div className={cn('w-full rounded-2xl border p-4 shadow-lg backdrop-blur animate-fade-in-up', style.panel)}>
      <div className="flex items-start gap-3">
        <div className="mt-0.5 rounded-xl bg-white/80 p-2">
          <Icon size={16} className="text-brand-dark" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-3">
            <Link
              to={notification.link}
              onClick={() => onRead(notification.id)}
              className={cn('min-w-0 text-sm font-semibold transition hover:underline', style.title)}
            >
              {notification.title}
            </Link>
            <button
              onClick={() => onClose(notification.id)}
              className="grid h-7 w-7 shrink-0 place-items-center rounded-lg text-brand-secondary/50 transition hover:bg-white hover:text-brand-secondary"
              aria-label="Fermer la notification"
            >
              <X size={14} />
            </button>
          </div>
          <div className="mt-2 text-[11px] font-medium text-brand-secondary/70">
            {notification.department} · {notification.time}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function NotificationCenter() {
  const {
    notifications,
    unreadCount,
    toastNotifications,
    markAsRead,
    markAllAsRead,
    removeToast,
  } = useNotifications();
  const [open, setOpen] = useState(false);
  const containerRef = useRef(null);
  const timeoutIdsRef = useRef(new Map());

  useEffect(() => {
    function handleOutsideClick(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setOpen(false);
      }
    }

    document.addEventListener('mousedown', handleOutsideClick);
    return () => document.removeEventListener('mousedown', handleOutsideClick);
  }, []);

  useEffect(() => {
    const timeoutIds = timeoutIdsRef.current;

    toastNotifications.forEach((notification) => {
      if (timeoutIds.has(notification.id)) return;

      const timeoutId = window.setTimeout(() => {
        removeToast(notification.id);
        timeoutIds.delete(notification.id);
      }, 5000);

      timeoutIds.set(notification.id, timeoutId);
    });

    return () => {
      timeoutIds.forEach((timeoutId, notificationId) => {
        if (!toastNotifications.find((notification) => notification.id === notificationId)) {
          window.clearTimeout(timeoutId);
          timeoutIds.delete(notificationId);
        }
      });
    };
  }, [toastNotifications, removeToast]);

  const latestNotifications = notifications.slice(0, 6);

  return (
    <>
      <div className="relative" ref={containerRef}>
        <button
          onClick={() => setOpen((current) => !current)}
          className="relative grid h-11 w-11 place-items-center rounded-2xl border border-brand-secondary/10 bg-white text-brand-secondary transition hover:border-brand-secondary/30 hover:bg-brand-light"
          aria-label="Ouvrir le centre de notifications"
        >
          <Bell size={18} />
          {unreadCount > 0 && (
            <span className="absolute -right-1 -top-1 min-w-5 rounded-full bg-brand-warning px-1.5 py-0.5 text-[10px] font-bold text-white">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </button>

        {open && (
          <div className="absolute right-0 top-14 z-40 w-[360px] rounded-3xl border border-brand-secondary/10 bg-white p-4 shadow-2xl">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-brand-dark">Notifications internes</p>
                <p className="text-xs text-brand-secondary/60">{unreadCount} non lue{unreadCount > 1 ? 's' : ''}</p>
              </div>
              <button
                onClick={() => markAllAsRead()}
                className="inline-flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-xs font-semibold text-brand-secondary transition hover:bg-brand-light"
              >
                <CheckCheck size={14} />
                Tout lire
              </button>
            </div>

            <div className="mt-4 space-y-3">
              {latestNotifications.length === 0 && (
                <div className="rounded-2xl border border-dashed border-brand-secondary/15 bg-brand-light/40 px-4 py-8 text-center text-sm text-brand-secondary/60">
                  Aucune notification pour le moment.
                </div>
              )}

              {latestNotifications.map((notification) => {
                const style = LEVEL_STYLES[notification.level] || LEVEL_STYLES.info;
                const Icon = style.icon;

                return (
                  <div
                    key={notification.id}
                    className={cn(
                      'rounded-2xl border px-4 py-3 transition',
                      style.panel,
                      !notification.read && 'ring-1 ring-brand-secondary/10',
                    )}
                  >
                    <div className="flex items-start gap-3">
                      <div className="mt-0.5 rounded-xl bg-white/90 p-2">
                        <Icon size={15} className="text-brand-dark" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-start justify-between gap-3">
                          <Link
                            to={notification.link}
                            onClick={() => {
                              markAsRead(notification.id);
                              setOpen(false);
                            }}
                            className={cn('min-w-0 text-sm font-semibold transition hover:underline', style.title)}
                          >
                            {notification.title}
                          </Link>
                          {!notification.read && <span className="mt-1 h-2.5 w-2.5 shrink-0 rounded-full bg-brand-warning" />}
                        </div>
                        <div className="mt-2 text-[11px] text-brand-secondary/55">
                          {notification.department} · {notification.time}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      <div className="pointer-events-none fixed right-4 top-20 z-50 flex w-full max-w-sm flex-col gap-3">
        {toastNotifications.map((notification) => (
          <div key={notification.id} className="pointer-events-auto">
            <NotificationToast
              notification={notification}
              onClose={removeToast}
              onRead={markAsRead}
            />
          </div>
        ))}
      </div>
    </>
  );
}
