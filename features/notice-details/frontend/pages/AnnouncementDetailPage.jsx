// One announcement in full. Owner: notice-details.
import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { isAbort } from "@/api/client";
import { getAnnouncement } from "@features/core-announcement-engine/frontend/announcementsApi";
import CategoryBadge from "@features/student-dashboard/frontend/components/CategoryBadge";
import StateMessage from "@features/student-dashboard/frontend/components/StateMessage";
import { formatEventDate, formatEventTime, formatTimestampDate } from "@/utils/format";
import { usePageTitle } from "@/utils/usePageTitle";
import AttachmentSection from "../components/AttachmentSection";
import "../notice.css";

export default function AnnouncementDetailPage() {
  const { id } = useParams();
  const [state, setState] = useState({ status: "loading", data: null, error: null });
  const [attempt, setAttempt] = useState(0);
  usePageTitle(state.data?.title || "Announcement");

  useEffect(() => {
    const controller = new AbortController();
    setState({ status: "loading", data: null, error: null });
    getAnnouncement(id, controller.signal)
      .then((data) => setState({ status: "ready", data, error: null }))
      .catch((error) => !isAbort(error) && setState({ status: "error", data: null, error }));
    return () => controller.abort();
  }, [id, attempt]);

  const retry = useCallback(() => setAttempt((n) => n + 1), []);

  if (state.status === "loading") return <StateMessage kind="loading" title="Loading announcement" />;
  if (state.status === "error") {
    const missing = state.error.status === 404;
    return (
      <StateMessage
        kind={missing ? "empty" : "error"}
        title={missing ? "Announcement not found" : "We couldn't load this announcement"}
        message={missing ? "It may have been removed or never published." : state.error.message}
        action={
          missing ? (
            <Link className="btn btn-primary" to="/">
              Back to announcements
            </Link>
          ) : (
            <button type="button" className="btn btn-primary" onClick={retry}>
              Try again
            </button>
          )
        }
      />
    );
  }

  const a = state.data;
  const hasFacts = a.event_date || a.event_time || a.venue;
  return (
    <>
      <p className="back">
        <Link to={`/?category=${encodeURIComponent(a.category)}`}>Back to {a.category}</Link>
      </p>
      <article className="notice">
        <header className="notice-head">
          {!a.is_published && <p className="flash flash-error">This is a draft. Only you can see it.</p>}
          <div className="card-meta">
            <CategoryBadge category={a.category} />
            {a.published_at && <span>Published {formatTimestampDate(a.published_at)}</span>}
          </div>
          <h1>{a.title}</h1>
        </header>

        {hasFacts && (
          <dl className="facts">
            {a.event_date && (
              <div>
                <dt>Date</dt>
                <dd>{formatEventDate(a.event_date)}</dd>
              </div>
            )}
            {a.event_time && (
              <div>
                <dt>Time</dt>
                <dd>{formatEventTime(a.event_time)}</dd>
              </div>
            )}
            {a.venue && (
              <div>
                <dt>Venue</dt>
                <dd>{a.venue}</dd>
              </div>
            )}
          </dl>
        )}

        <div className="notice-body">{a.description}</div>

        {a.registration_link && (
          <p>
            <a className="btn btn-primary" href={a.registration_link} target="_blank" rel="noopener noreferrer">
              Register for this event
            </a>
          </p>
        )}

        <AttachmentSection attachments={a.attachments} title={a.title} />
      </article>
    </>
  );
}
