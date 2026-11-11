// One announcement in the grid / stacked list. Owner: student-dashboard.
import { Link } from "react-router-dom";
import { formatEventDate, formatTimestampDate, truncate } from "@/utils/format";
import CategoryBadge from "./CategoryBadge";

export default function AnnouncementCard({ announcement: a, isAlt = false }) {
  const poster = a.attachments.some((x) => x.kind === "poster");
  const pdf = a.attachments.some((x) => x.kind === "pdf");
  const href = `/announcements/${a.id}`;

  return (
    <article className={`card announcement-card ${isAlt ? "card-alt" : ""}`}>
      <div className="card-top-row">
        <CategoryBadge category={a.category} />
      </div>

      <h2 className="card-title">
        <Link to={href}>{a.title}</Link>
      </h2>

      <p className="card-summary">{truncate(a.description, 160)}</p>

      <div className="card-foot">
        <div className="card-foot-left">
          <span className="card-date-badge">
            <svg className="card-cal-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
              <line x1="16" y1="2" x2="16" y2="6" />
              <line x1="8" y1="2" x2="8" y2="6" />
              <line x1="3" y1="10" x2="21" y2="10" />
            </svg>
            <time dateTime={a.published_at || undefined}>{formatTimestampDate(a.published_at)}</time>
          </span>

          <span className="card-tags">
            {a.event_date && <span>Event: {formatEventDate(a.event_date)}</span>}
            {poster && <span>Poster</span>}
            {pdf && <span>PDF</span>}
          </span>
        </div>

        <Link className="card-link" to={href}>
          View Details &rarr;
        </Link>
      </div>
    </article>
  );
}
