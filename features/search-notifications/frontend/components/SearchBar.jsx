// Keyword search box. Owner: search-notifications.
import { useEffect, useState } from "react";

export default function SearchBar({ value = "", onSearch, busy = false }) {
  const [text, setText] = useState(value);
  useEffect(() => setText(value), [value]); // keeps the box in step with the address bar

  return (
    <form
      className="search-form"
      role="search"
      onSubmit={(event) => {
        event.preventDefault();
        onSearch(text.trim());
      }}
    >
      <label className="visually-hidden" htmlFor="search-q">
        Search announcements
      </label>
      <div className="search-input-pill-wrapper">
        <svg className="search-input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input
          id="search-q"
          type="search"
          value={text}
          maxLength={100}
          placeholder="Search announcements..."
          onChange={(e) => setText(e.target.value)}
        />
        <button type="submit" className="search-btn btn btn-primary" disabled={busy}>
          {busy ? "Searching..." : "Search"}
        </button>
      </div>
    </form>
  );
}
