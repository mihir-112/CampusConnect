export default function Pagination({ page, pages, onChange }) {
  if (pages <= 1) return null;
  return (
    <nav className="pager" aria-label="Pages">
      {page > 1 && (
        <button type="button" className="btn btn-secondary" onClick={() => onChange(page - 1)}>
          Newer
        </button>
      )}
      <span>
        Page {page} of {pages}
      </span>
      {page < pages && (
        <button type="button" className="btn btn-secondary" onClick={() => onChange(page + 1)}>
          Older
        </button>
      )}
    </nav>
  );
}
