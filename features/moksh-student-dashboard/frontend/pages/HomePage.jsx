// The student landing page: search, categories and announcement cards. Owner: Moksh.
import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useAnnouncementSearch } from "@features/search-notifications/frontend/hooks/useAnnouncementSearch";
import SearchBar from "@features/search-notifications/frontend/components/SearchBar";
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

  return (
    <>
      <section className="hero" aria-labelledby="home-title">
        <h1 id="home-title">Campus announcements</h1>
        <p className="lead">Exams, events, clubs and general notices, all in one place. No login needed.</p>
        <SearchBar value={q} busy={status === "loading" && Boolean(q)} onSearch={(text) => update({ q: text })} />
      </section>

      <CategoryNav active={category} counts={counts} total={summary?.total ?? null} onSelect={(name) => update({ category: name })} />

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
          <div className="card-grid">
            {data.items.map((announcement) => (
              <AnnouncementCard key={announcement.id} announcement={announcement} />
            ))}
          </div>
          <Pagination page={data.page} pages={data.pages} onChange={(next) => update({ page: next > 1 ? String(next) : "" })} />
        </div>
      )}
    </>
  );
}
