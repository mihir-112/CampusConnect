// The category navigation panel on the left sidebar. Owner: student-dashboard.
import { CATEGORIES } from "@/utils/constants";

export default function CategoryNav({ active = "", counts = {}, total = null, onSelect }) {
  const tabs = [
    { name: "", label: "All", count: total, icon: "home", isAll: true },
    ...CATEGORIES.map((name) => ({
      name,
      label: name,
      count: counts[name],
      icon: name === "Examinations" || name === "Events" ? "calendar" : name === "Clubs" ? "users" : "megaphone",
    })),
  ];

  const renderIcon = (type) => {
    switch (type) {
      case "home":
        return (
          <svg className="tab-icon" width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" />
          </svg>
        );
      case "calendar":
        return (
          <svg className="tab-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
            <line x1="16" y1="2" x2="16" y2="6" />
            <line x1="8" y1="2" x2="8" y2="6" />
            <line x1="3" y1="10" x2="21" y2="10" />
          </svg>
        );
      case "users":
        return (
          <svg className="tab-icon" width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z" />
          </svg>
        );
      case "megaphone":
      default:
        return (
          <svg className="tab-icon" width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M3 10v4c0 .55.45 1 1 1h3l4.29 4.29c.63.63 1.71.18 1.71-.71V5.41c0-.89-1.08-1.34-1.71-.71L7 9H4c-.55 0-1 .45-1 1zm13.5 2c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z" />
          </svg>
        );
    }
  };

  return (
    <nav className="category-nav" aria-label="Categories">
      {tabs.map((tab) => (
        <button
          key={tab.label}
          type="button"
          className={`sidebar-tab-btn ${active === tab.name ? "active" : ""} ${tab.isAll ? "tab-all" : ""}`}
          aria-current={active === tab.name ? "page" : undefined}
          onClick={() => onSelect(tab.name)}
        >
          <span className="tab-icon-wrap">{renderIcon(tab.icon)}</span>
          <span className="tab-title">{tab.label}</span>
          {typeof tab.count === "number" && <span className="count">{tab.count}</span>}
        </button>
      ))}
    </nav>
  );
}
