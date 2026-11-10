// One announcement in the grid. Owner: Moksh.
import { Link } from "react-router-dom";
import { formatEventDate, formatTimestampDate, truncate } from "@/utils/format";
import CategoryBadge from "./CategoryBadge";

export default function AnnouncementCard({ announcement: a }) {
  const poster = a.attachments.some((x) => x.kind === "poster");
  const pdf = a.attachments.some((x) => x.kind === "pdf");
  const href = `/announcements/${a.id}`;
  return (
    <article className="card">
      <div className="card-meta">
        <CategoryBadge category={a.category} />
        <time dateTime={a.published_at || undefined}>{formatTimestampDate(a.published_at)}</time>
      </div>
      <h2 className="card-title">
        <Link to={href}>{a.title}</Link>
      </h2>
      <p className="card-summary">{truncate(a.description, 150)}</p>
      <div className="card-foot">
        <span className="card-tags">
          {a.event_date && <span>Event: {formatEventDate(a.event_date)}</span>}
          {poster && <span>Poster</span>}
          {pdf && <span>PDF</span>}
        </span>
        <Link className="card-link" to={href}>
          Read notice
        </Link>
      </div>
    </article>
  );
}
