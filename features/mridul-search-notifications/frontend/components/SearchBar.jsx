// Keyword search box. Owner: Mridul.
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
      <input id="search-q" type="search" value={text} maxLength={100} placeholder="Search by title, details or venue" onChange={(e) => setText(e.target.value)} />
      <button type="submit" className="btn btn-primary" disabled={busy}>
        {busy ? "Searching..." : "Search"}
      </button>
    </form>
  );
}
