export default function CategoryBadge({ category }) {
  return <span className={`chip cat-${String(category).toLowerCase()}`}>{category}</span>;
}
