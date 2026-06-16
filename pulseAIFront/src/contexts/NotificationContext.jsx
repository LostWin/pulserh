import { createContext, useEffect, useMemo, useRef, useState } from 'react';
import keycloak from '../config/keycloak';
import { api, WS_BASE_URL } from '../lib/api';

const NotificationContext = createContext(null);

function toLevel(severity) {
  if (severity === 'critical') return 'critical';
  if (severity === 'medium') return 'warning';
  return 'info';
}

function formatRelativeTime(createdAt) {
  if (!createdAt) return "À l'instant";

  const date = new Date(createdAt);
  const diffMs = Date.now() - date.getTime();
  const diffMinutes = Math.max(1, Math.round(diffMs / 60000));

  if (diffMinutes < 60) return `Il y a ${diffMinutes} min`;
  const diffHours = Math.round(diffMinutes / 60);
  if (diffHours < 24) return `Il y a ${diffHours} h`;
  const diffDays = Math.round(diffHours / 24);
  return `Il y a ${diffDays} j`;
}

function normalizeNotification(alert) {
  const priority = alert.payload?.priority || (alert.severity === 'critical' ? 'P1' : alert.severity === 'medium' ? 'P2' : 'P3');
  const impact = alert.payload?.impact || alert.employee_name || alert.department || 'Signal interne';
  return {
    id: alert.id,
    type: alert.type,
    severity: alert.severity,
    level: toLevel(alert.severity),
    title: alert.title,
    message: alert.message,
    employeeId: alert.employee_id,
    employeeName: alert.employee_name,
    workflowId: alert.workflow_id,
    department: alert.department || 'PulseAI',
    link: alert.link || '/',
    source: alert.source || 'pulse_ai',
    status: alert.status,
    priority,
    impact,
    read: Boolean(alert.is_read),
    archived: Boolean(alert.is_archived),
    createdAt: alert.created_at,
    time: formatRelativeTime(alert.created_at),
    actionPlan: alert.action_plan,
    payload: alert.payload || {},
  };
}

export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([]);
  const [toastNotifications, setToastNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadedOnce, setLoadedOnce] = useState(false);
  const previousUnreadIdsRef = useRef(new Set());
  const websocketRef = useRef(null);

  const unreadCount = useMemo(
    () => notifications.filter((notification) => !notification.read && !notification.archived).length,
    [notifications],
  );

  const loadNotifications = async ({ silent = false } = {}) => {
    if (!silent) {
      setLoading(true);
    }

    try {
      const data = await api.get('/alerts');
      const nextNotifications = data.map(normalizeNotification);
      const nextUnreadIds = new Set(
        nextNotifications
          .filter((notification) => !notification.read && !notification.archived)
          .map((notification) => notification.id),
      );

      if (loadedOnce) {
        const newToastItems = nextNotifications.filter(
          (notification) =>
            nextUnreadIds.has(notification.id) &&
            !previousUnreadIdsRef.current.has(notification.id),
        );

        if (newToastItems.length > 0) {
          setToastNotifications((current) => {
            const merged = [...newToastItems, ...current];
            const seen = new Set();
            return merged.filter((notification) => {
              if (seen.has(notification.id)) return false;
              seen.add(notification.id);
              return true;
            }).slice(0, 4);
          });
        }
      }

      previousUnreadIdsRef.current = nextUnreadIds;
      setNotifications(nextNotifications);
      setLoadedOnce(true);
    } catch (error) {
      console.error('Erreur lors du chargement des notifications :', error);
    } finally {
      if (!silent) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    loadNotifications();
    const intervalId = window.setInterval(() => {
      loadNotifications({ silent: true });
    }, 30000);

    return () => window.clearInterval(intervalId);
  }, []);

  useEffect(() => {
    if (!keycloak.token) return undefined;

    const websocket = new WebSocket(`${WS_BASE_URL}/alerts/ws?token=${encodeURIComponent(keycloak.token)}`);
    websocketRef.current = websocket;

    websocket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === 'alert.upsert' && payload.alert) {
          const nextNotification = normalizeNotification(payload.alert);

          setNotifications((current) => {
            const existingIndex = current.findIndex((notification) => notification.id === nextNotification.id);
            if (existingIndex === -1) {
              return [nextNotification, ...current];
            }

            const updated = [...current];
            updated[existingIndex] = {
              ...updated[existingIndex],
              ...nextNotification,
            };
            return updated;
          });

          if (!nextNotification.read && !previousUnreadIdsRef.current.has(nextNotification.id)) {
            previousUnreadIdsRef.current.add(nextNotification.id);
            setToastNotifications((current) => [nextNotification, ...current].slice(0, 4));
          }
        }

        if (payload.type === 'alert.state') {
          setNotifications((current) => current.map((notification) => (
            notification.id === payload.alertId
              ? { ...notification, read: Boolean(payload.read), archived: Boolean(payload.archived) }
              : notification
          )));
        }
      } catch (error) {
        console.error('Erreur websocket notifications :', error);
      }
    };

    websocket.onclose = () => {
      websocketRef.current = null;
    };

    return () => {
      if (websocket.readyState === WebSocket.OPEN || websocket.readyState === WebSocket.CONNECTING) {
        websocket.close();
      }
      websocketRef.current = null;
    };
  }, [loadedOnce]);

  const markAsRead = async (notificationId) => {
    setNotifications((current) => current.map((notification) => (
      notification.id === notificationId
        ? { ...notification, read: true }
        : notification
    )));

    try {
      await api.post(`/alerts/${notificationId}/read`);
    } catch (error) {
      console.error('Erreur lors du marquage lu :', error);
      loadNotifications({ silent: true });
    }
  };

  const markAllAsRead = async () => {
    const unreadIds = notifications.filter((notification) => !notification.read).map((notification) => notification.id);
    setNotifications((current) => current.map((notification) => ({ ...notification, read: true })));

    try {
      await Promise.all(unreadIds.map((id) => api.post(`/alerts/${id}/read`)));
    } catch (error) {
      console.error('Erreur lors du marquage global :', error);
      loadNotifications({ silent: true });
    }
  };

  const archiveNotification = async (notificationId) => {
    setNotifications((current) => current.map((notification) => (
      notification.id === notificationId
        ? { ...notification, archived: true, read: true }
        : notification
    )));

    try {
      await api.post(`/alerts/${notificationId}/archive`);
    } catch (error) {
      console.error("Erreur lors de l'archivage :", error);
      loadNotifications({ silent: true });
    }
  };

  const updateNotification = async (notificationId, patch) => {
    setNotifications((current) => current.map((notification) => (
      notification.id === notificationId
        ? { ...notification, ...patch }
        : notification
    )));
  };

  const pushNotification = async () => {
    await loadNotifications({ silent: true });
  };

  const removeToast = (notificationId) => {
    setToastNotifications((current) => current.filter((notification) => notification.id !== notificationId));
  };

  const value = {
    notifications: notifications.filter((notification) => !notification.archived),
    unreadCount,
    toastNotifications,
    loading,
    markAsRead,
    markAllAsRead,
    archiveNotification,
    updateNotification,
    pushNotification,
    removeToast,
    refreshNotifications: loadNotifications,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
}

export { NotificationContext };
