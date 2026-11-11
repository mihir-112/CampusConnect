// Notification state shared by the bell and the notifications page. Owner: Mridul.
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import * as api from "../notificationsApi";

const NotificationsContext = createContext(null);
const REFRESH_MS = 60_000;

export function NotificationsProvider({ children }) {
  const [state, setState] = useState({ status: "loading", items: [], unread: 0 });
  const [version, setVersion] = useState(0); // goes up whenever something changes

  const refresh = useCallback(async () => {
    try {
      const data = await api.listNotifications(10);
      setState({ status: "ready", items: data.items, unread: data.unread });
    } catch {
      setState((previous) => ({ ...previous, status: "error" }));
    }
    setVersion((n) => n + 1);
  }, []);

  useEffect(() => {
    refresh();
    const timer = setInterval(() => document.visibilityState === "visible" && refresh(), REFRESH_MS);
    const onFocus = () => refresh();
    window.addEventListener("focus", onFocus);
    return () => {
      clearInterval(timer);
      window.removeEventListener("focus", onFocus);
    };
  }, [refresh]);

  const markRead = useCallback(
    async (id) => {
      setState((s) => ({ ...s, items: s.items.map((i) => (i.id === id ? { ...i, is_read: true } : i)), unread: Math.max(0, s.unread - (s.items.find((i) => i.id === id && !i.is_read) ? 1 : 0)) }));
      try {
        await api.markNotificationRead(id);
      } finally {
        refresh();
      }
    },
    [refresh],
  );

  const markAllRead = useCallback(async () => {
    setState((s) => ({ ...s, items: s.items.map((i) => ({ ...i, is_read: true })), unread: 0 }));
    try {
      await api.markAllNotificationsRead();
    } finally {
      refresh();
    }
  }, [refresh]);

  const value = useMemo(() => ({ ...state, version, refresh, markRead, markAllRead }), [state, version, refresh, markRead, markAllRead]);
  return <NotificationsContext.Provider value={value}>{children}</NotificationsContext.Provider>;
}

export function useNotifications() {
  const context = useContext(NotificationsContext);
  if (!context) throw new Error("useNotifications must be used inside <NotificationsProvider>");
  return context;
}
