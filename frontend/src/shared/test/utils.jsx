// Helpers shared by every member's frontend tests. Owner: Moksh.
import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { vi } from "vitest";
import App from "@/App";

export function announcement(overrides = {}) {
  return {
    id: 1,
    title: "Mid-sem timetable",
    description: "Full details about the mid-sem timetable.",
    category: "Examinations",
    venue: null,
    event_date: null,
    event_time: null,
    registration_link: null,
    is_published: true,
    created_at: "2026-10-30T08:00:00Z",
    updated_at: "2026-10-30T08:00:00Z",
    published_at: "2026-10-30T08:00:00Z",
    attachments: [],
    ...overrides,
  };
}

export const page = (items, extra = {}) => ({ items, page: 1, per_page: 9, pages: 1, total: items.length, q: "", category: null, ...extra });

const DEFAULTS = {
  "GET /api/notifications": { unread: 0, items: [] },
  "GET /api/dashboard": {
    total: 0,
    categories: ["Examinations", "Events", "Clubs", "General"].map((name) => ({ name, count: 0 })),
  },
};

const errorBody = (code, message, fields = null) => ({ status: code === "not_found" ? 404 : 400, json: { error: { code, message, fields } } });
export { errorBody };

/**
 * Replaces fetch with a fake server. Keys look like "GET /api/search"; a handler is a value
 * or a function ({ url, method, body }) returning the JSON (or { status, json }).
 */
export function mockApi(handlers = {}) {
  const table = { ...DEFAULTS, ...handlers };
  const calls = [];
  const fake = vi.fn(async (url, init = {}) => {
    const method = (init.method || "GET").toUpperCase();
    const path = String(url);
    const body = typeof init.body === "string" ? JSON.parse(init.body) : init.body;
    calls.push({ method, url: path, body, headers: init.headers || {} });
    for (const [key, handler] of Object.entries(table)) {
      const [m, p] = key.split(" ");
      if (m === method && (path === p || path.startsWith(p + "?"))) {
        const result = typeof handler === "function" ? handler({ url: path, method, body }) : handler;
        const status = result?.status ?? 200;
        if (status === 204) return new Response(null, { status });
        return new Response(JSON.stringify(result?.json ?? result), { status, headers: { "Content-Type": "application/json" } });
      }
    }
    return new Response(JSON.stringify({ error: { code: "not_found", message: "Not found", fields: null } }), { status: 404 });
  });
  vi.stubGlobal("fetch", fake);
  return { fetch: fake, calls, callsTo: (method, prefix) => calls.filter((c) => c.method === method && c.url.startsWith(prefix)) };
}

export function renderApp(route = "/") {
  return render(
    <MemoryRouter initialEntries={[route]} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <App />
    </MemoryRouter>,
  );
}

export function signIn(token = "test-token") {
  window.sessionStorage.setItem("campusconnect.token", token);
}

export const publisherUser = { id: 1, username: "editor", email: "editor@example.com" };
