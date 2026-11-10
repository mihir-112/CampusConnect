// The All / Examinations / Events / Clubs / General tabs. Owner: Moksh.
import { CATEGORIES } from "@/utils/constants";

export default function CategoryNav({ active = "", counts = {}, total = null, onSelect }) {
  const tabs = [{ name: "", label: "All", count: total }, ...CATEGORIES.map((name) => ({ name, label: name, count: counts[name] }))];
  return (
    <nav className="category-nav" aria-label="Categories">
      {tabs.map((tab) => (
        <button key={tab.label} type="button" className={active === tab.name ? "active" : ""} aria-current={active === tab.name ? "page" : undefined} onClick={() => onSelect(tab.name)}>
          {tab.label}
          {typeof tab.count === "number" && <span className="count">{tab.count}</span>}
        </button>
      ))}
    </nav>
  );
}
