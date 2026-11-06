// The publisher's list with Edit / Publish / Delete actions. Owner: Mihir.
import { Link } from "react-router-dom";
import CategoryBadge from "@features/student-dashboard/frontend/components/CategoryBadge";
import { formatTimestampDate } from "@/utils/format";

export default function AnnouncementTable({ items, busyId, onTogglePublish, onDelete }) {
  return (
    <div className="table-wrap">
      <table className="admin-table">
        <thead>
          <tr>
            <th>Title</th>
            <th>Category</th>
            <th>Status</th>
            <th>Last updated</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map((a) => (
            <tr key={a.id}>
              <td data-label="Title">
                <Link to={`/announcements/${a.id}`}>{a.title}</Link>
              </td>
              <td data-label="Category">
                <CategoryBadge category={a.category} />
              </td>
              <td data-label="Status">
                <span className={`status ${a.is_published ? "live" : "draft"}`}>{a.is_published ? "Published" : "Draft"}</span>
              </td>
              <td data-label="Last updated">{formatTimestampDate(a.updated_at)}</td>
              <td data-label="Actions" className="actions">
                <Link className="btn btn-small btn-secondary" to={`/publisher/announcements/${a.id}/edit`} aria-label={`Edit ${a.title}`}>
                  Edit
                </Link>
                <button type="button" className="btn btn-small btn-secondary" disabled={busyId === a.id} onClick={() => onTogglePublish(a)} aria-label={`${a.is_published ? "Unpublish" : "Publish"} ${a.title}`}>
                  {a.is_published ? "Unpublish" : "Publish"}
                </button>
                <button type="button" className="btn btn-small btn-danger" disabled={busyId === a.id} onClick={() => onDelete(a)} aria-label={`Delete ${a.title}`}>
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
