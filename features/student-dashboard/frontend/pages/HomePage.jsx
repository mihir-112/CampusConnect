// The student landing page: search, categories, watermark and announcement cards. Owner: student-dashboard.
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useAnnouncementSearch } from "@features/search-notifications/frontend/hooks/useAnnouncementSearch";
import { CATEGORIES } from "@/utils/constants";
import { usePageTitle } from "@/utils/usePageTitle";
import AnnouncementCard from "../components/AnnouncementCard";
import CategoryNav from "../components/CategoryNav";
import Pagination from "../components/Pagination";
import StateMessage from "../components/StateMessage";
import { getDashboard } from "../dashboardApi";
import "../styles/dashboard.css";

export default function HomePage() {
  usePageTitle("Announcements");
  const [params, setParams] = useSearchParams();
  const q = params.get("q") || "";
  const category = CATEGORIES.includes(params.get("category")) ? params.get("category") : "";
  const page = Math.max(parseInt(params.get("page") || "1", 10) || 1, 1);

  const { status, data, retry } = useAnnouncementSearch({ q, category, page });
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    const controller = new AbortController();
    getDashboard(controller.signal)
      .then(setSummary)
      .catch(() => {}); // the counts are a nicety; the page works without them
    return () => controller.abort();
  }, []);

  function update(changes) {
    const next = new URLSearchParams(params);
    for (const [key, value] of Object.entries({ page: "", ...changes })) {
      if (value) next.set(key, value);
      else next.delete(key);
    }
    setParams(next);
  }

  const counts = Object.fromEntries((summary?.categories || []).map((c) => [c.name, c.count]));
  const clear = () => setParams(new URLSearchParams());

  const getQuickCategoryIcon = (catName) => {
    switch (catName) {
      case "Examinations":
      case "Events":
        return (
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
            <line x1="16" y1="2" x2="16" y2="6" />
            <line x1="8" y1="2" x2="8" y2="6" />
            <line x1="3" y1="10" x2="21" y2="10" />
          </svg>
        );
      case "Clubs":
        return (
          <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z" />
          </svg>
        );
      case "General":
      default:
        return (
          <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M3 10v4c0 .55.45 1 1 1h3l4.29 4.29c.63.63 1.71.18 1.71-.71V5.41c0-.89-1.08-1.34-1.71-.71L7 9H4c-.55 0-1 .45-1 1zm13.5 2c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z" />
          </svg>
        );
    }
  };

  return (
    <div className="dashboard-grid-layout">
      {/* Left Navigation Panel */}
      <aside className="dashboard-left-panel">
        <CategoryNav active={category} counts={counts} total={summary?.total ?? null} onSelect={(name) => update({ category: name })} />
      </aside>

      {/* Main Content Area */}
      <section className="dashboard-main-area">
        {/* Large faded NIE logo watermark on the right */}
        <div className="dashboard-watermark" aria-hidden="true">
          <img src="/nie-logo.png" alt="" className="watermark-logo-img" />
        </div>

        <div className="welcome-banner">
          <h1 id="home-title" className="welcome-heading" aria-label="Campus announcements">
            Welcome to CampusConnect
          </h1>
          <p className="welcome-subheading">All your campus announcements, in one place.</p>
        </div>

        {/* Quick Category Filter Pills */}
        <div className="quick-category-pills-row" aria-label="Quick category filters">
          {CATEGORIES.map((catName) => (
            <button
              key={catName}
              type="button"
              className={`quick-cat-pill ${category === catName ? "active" : ""}`}
              onClick={() => update({ category: category === catName ? "" : catName })}
            >
              <span className="pill-icon">{getQuickCategoryIcon(catName)}</span>
              <span className="pill-label">{catName}</span>
            </button>
          ))}
        </div>

        <h2 className="latest-announcements-heading">Latest Announcements</h2>

        {status === "loading" && !data && <StateMessage kind="loading" title="Loading announcements" />}

        {status === "error" && (
          <StateMessage
            kind="error"
            title="We couldn't load announcements"
            message="Something went wrong on our side. Try again in a moment."
            action={
              <button type="button" className="btn btn-primary" onClick={retry}>
                Try again
              </button>
            }
          />
        )}

        {status === "success" && data.items.length === 0 && (q || category) && (
          <StateMessage
            title="No announcements found"
            message={`Nothing matches your search${category ? ` in ${category}` : ""}. Try different words or clear the filters.`}
            action={
              <button type="button" className="btn btn-secondary" onClick={clear}>
                Clear filters
              </button>
            }
          />
        )}

        {status === "success" && data.items.length === 0 && !q && !category && (
          <StateMessage title="No announcements yet" message="Nothing has been published so far. Check back soon." />
        )}

        {data && data.items.length > 0 && status !== "error" && (
          <div aria-busy={status === "loading"}>
            <p className="result-count" role="status">
              {data.total} announcement{data.total === 1 ? "" : "s"}
              {category && ` in ${category}`}
              {q && <> matching &ldquo;{q}&rdquo;</>}
            </p>
            <div className="cards-stacked-list">
              {data.items.map((announcement, index) => (
                <AnnouncementCard key={announcement.id} announcement={announcement} isAlt={index % 2 === 1} />
              ))}
            </div>
            <Pagination page={data.page} pages={data.pages} onChange={(next) => update({ page: next > 1 ? String(next) : "" })} />
          </div>
        )}
      </section>
    </div>
  );
}
