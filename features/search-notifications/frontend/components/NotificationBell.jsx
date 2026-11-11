// The bell in the header with its dropdown list. Owner: Mridul.
import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { formatTimestampDate } from "@/utils/format";
import { useNotifications } from "../hooks/NotificationsContext";
import "../notifications.css";

export default function NotificationBell() {
  const { items, unread, status, markRead, markAllRead } = useNotifications();
  const [open, setOpen] = useState(false);
  const wrapper = useRef(null);
  const button = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!open) return undefined;
    const onClick = (event) => wrapper.current && !wrapper.current.contains(event.target) && setOpen(false);
    const onKey = (event) => {
      if (event.key === "Escape") {
        setOpen(false);
        button.current?.focus();
      }
    };
    document.addEventListener("mousedown", onClick);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onClick);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  function openNotification(item) {
    if (!item.is_read) markRead(item.id);
    setOpen(false);
    navigate(`/announcements/${item.announcement_id}`);
  }

  return (
    <div className="bell" ref={wrapper}>
      <button ref={button} type="button" className="bell-button" aria-expanded={open} aria-controls="bell-panel" aria-label={`Notifications, ${unread} unread`} onClick={() => setOpen((v) => !v)}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M6 9a6 6 0 1 1 12 0c0 5 2 6 2 7H4c0-1 2-2 2-7zM10 20a2 2 0 0 0 4 0" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        {unread > 0 && <span className="bell-count" data-testid="bell-count">{unread}</span>}
      </button>

      {open && (
        <div id="bell-panel" className="bell-panel">
          <div className="bell-head">
            <strong>Notifications</strong>
            {unread > 0 && (
              <button type="button" className="link-button" onClick={markAllRead}>
                Mark all as read
              </button>
            )}
          </div>
          {status === "error" && <p className="bell-empty">Notifications could not be loaded right now.</p>}
          {status !== "error" && items.length === 0 && <p className="bell-empty">No notifications yet. New announcements will appear here.</p>}
          {items.length > 0 && (
            <ul className="bell-list">
              {items.map((item) => (
                <li key={item.id} className={item.is_read ? "" : "unread"}>
                  <button type="button" onClick={() => openNotification(item)}>
                    <span className="bell-message">{item.message}</span>
                    <span className="bell-time">{formatTimestampDate(item.created_at)}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
          <div className="bell-foot">
            <Link to="/notifications" onClick={() => setOpen(false)}>
              See all notifications
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
