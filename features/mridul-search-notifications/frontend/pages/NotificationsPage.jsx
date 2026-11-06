// Full notification list. Owner: Mridul.
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import StateMessage from "@features/student-dashboard/frontend/components/StateMessage";
import { formatTimestampDate } from "@/utils/format";
import { usePageTitle } from "@/utils/usePageTitle";
import { useNotifications } from "../hooks/NotificationsContext";
import { listNotifications } from "../notificationsApi";
import "../notifications.css";

export default function NotificationsPage() {
  usePageTitle("Notifications");
  const { version, markRead, markAllRead } = useNotifications();
  const [state, setState] = useState({ status: "loading", data: null });

  useEffect(() => {
    let cancelled = false;
    listNotifications(50)
      .then((data) => !cancelled && setState({ status: "ready", data }))
      .catch(() => !cancelled && setState({ status: "error", data: null }));
    return () => {
      cancelled = true;
    };
  }, [version]);

  if (state.status === "loading") return <StateMessage kind="loading" title="Loading notifications" />;
  if (state.status === "error") return <StateMessage kind="error" title="We couldn't load notifications" message="Refresh the page in a moment." />;

  const { items, unread } = state.data;
  return (
    <section>
      <div className="page-head notif-head">
        <div>
          <h1>Notifications</h1>
          <p className="lead">{unread ? `${unread} unread on this browser.` : "You are all caught up."}</p>
        </div>
        {unread > 0 && (
          <button type="button" className="btn btn-secondary" onClick={markAllRead}>
            Mark all as read
          </button>
        )}
      </div>
      {items.length === 0 ? (
        <StateMessage kind="empty" title="No notifications yet" message="When an announcement is published, it will show up here." />
      ) : (
        <ul className="notif-list">
          {items.map((item) => (
            <li key={item.id} className={item.is_read ? "" : "unread"}>
              <Link to={`/announcements/${item.announcement_id}`} onClick={() => !item.is_read && markRead(item.id)}>
                <span className="bell-message">{item.message}</span>
                <span className="bell-time">{formatTimestampDate(item.created_at)}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
      <p className="hint">Read and unread is remembered per browser, because students do not have accounts.</p>
    </section>
  );
}
