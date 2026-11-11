// Publisher dashboard: statistics and the list of own announcements. Owner: core-announcement-engine.
import { useCallback, useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "@features/publisher-auth/frontend/auth/AuthContext";
import StateMessage from "@features/student-dashboard/frontend/components/StateMessage";
import { isAbort } from "@/api/client";
import { usePageTitle } from "@/utils/usePageTitle";
import { deleteAnnouncement, listMine, publishAnnouncement, unpublishAnnouncement } from "../announcementsApi";
import AnnouncementTable from "../components/AnnouncementTable";
import StatsCards from "../components/StatsCards";
import "../publisher.css";

export default function PublisherDashboardPage() {
  usePageTitle("Manage announcements");
  const { publisher } = useAuth();
  const location = useLocation();
  const [state, setState] = useState({ status: "loading", data: null });
  const [busyId, setBusyId] = useState(null);
  const [message, setMessage] = useState(location.state?.notice ? { type: "success", text: location.state.notice } : null);

  const load = useCallback((signal) => {
    return listMine(signal)
      .then((data) => setState({ status: "ready", data }))
      .catch((error) => !isAbort(error) && setState({ status: "error", data: null }));
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    load(controller.signal);
    return () => controller.abort();
  }, [load]);

  async function run(announcement, action, success) {
    setBusyId(announcement.id);
    setMessage(null);
    try {
      await action();
      setMessage({ type: "success", text: success });
      await load();
    } catch (error) {
      setMessage({ type: "error", text: error.message });
    } finally {
      setBusyId(null);
    }
  }

  const togglePublish = (a) =>
    run(a, () => (a.is_published ? unpublishAnnouncement(a.id) : publishAnnouncement(a.id)), a.is_published ? "Announcement unpublished. Students can no longer see it." : "Announcement published.");

  const remove = (a) => {
    if (!window.confirm(`Delete "${a.title}"? This cannot be undone.`)) return;
    run(a, () => deleteAnnouncement(a.id), "Announcement deleted.");
  };

  return (
    <section>
      <div className="page-head admin-head">
        <div>
          <h1>Your announcements</h1>
          <p className="lead">Signed in as {publisher?.username}. Drafts are only visible to you.</p>
        </div>
        <Link className="btn btn-primary" to="/publisher/announcements/new">
          New announcement
        </Link>
      </div>

      {message && (
        <p className={`flash flash-${message.type}`} role={message.type === "error" ? "alert" : "status"}>
          {message.text}
        </p>
      )}

      {state.status === "loading" && <StateMessage kind="loading" title="Loading your announcements" />}
      {state.status === "error" && (
        <StateMessage
          kind="error"
          title="We couldn't load your announcements"
          message="Try again in a moment."
          action={
            <button type="button" className="btn btn-primary" onClick={() => load()}>
              Try again
            </button>
          }
        />
      )}
      {state.status === "ready" && (
        <>
          <StatsCards stats={state.data.stats} />
          {state.data.items.length === 0 ? (
            <StateMessage
              title="You haven't created any announcements"
              message="Create your first announcement. You can save it as a draft or publish it straight away."
              action={
                <Link className="btn btn-primary" to="/publisher/announcements/new">
                  New announcement
                </Link>
              }
            />
          ) : (
            <AnnouncementTable items={state.data.items} busyId={busyId} onTogglePublish={togglePublish} onDelete={remove} />
          )}
        </>
      )}
    </section>
  );
}
