// Search box, notification bell and notifications page. Owner: Mridul.
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { getClientId } from "@features/search-notifications/frontend/clientId";
import { announcement, mockApi, page, renderApp } from "@/test/utils";

afterEach(() => vi.unstubAllGlobals());

const note = (id, extra = {}) => ({ id, announcement_id: id + 100, message: `New in Events: Notice ${id}`, created_at: "2026-10-30T08:00:00Z", is_read: false, ...extra });

describe("Search", () => {
  it("sends the typed keyword to the search endpoint", async () => {
    const api = mockApi({ "GET /api/search": page([announcement()]) });
    renderApp("/");
    await screen.findByRole("link", { name: "Mid-sem timetable" });
    await userEvent.type(screen.getByRole("searchbox", { name: "Search announcements" }), "  library ");
    await userEvent.click(screen.getByRole("button", { name: "Search" }));
    await waitFor(() => expect(api.callsTo("GET", "/api/search").at(-1).url).toContain("q=library"));
  });

  it("keeps the keyword and shows it in the result count", async () => {
    mockApi({ "GET /api/search": page([announcement()], { total: 1 }) });
    renderApp("/?q=timetable");
    expect(await screen.findByDisplayValue("timetable")).toBeInTheDocument();
    expect(await screen.findByText(/matching/)).toHaveTextContent("matching “timetable”");
  });
});

describe("Notification bell", () => {
  it("shows the unread count from the server", async () => {
    mockApi({ "GET /api/search": page([]), "GET /api/notifications": { unread: 2, items: [note(1), note(2)] } });
    renderApp("/");
    expect(await screen.findByTestId("bell-count")).toHaveTextContent("2");
    expect(screen.getByRole("button", { name: "Notifications, 2 unread" })).toBeInTheDocument();
  });

  it("hides the badge when everything is read", async () => {
    mockApi({ "GET /api/search": page([]) });
    renderApp("/");
    await screen.findByRole("button", { name: "Notifications, 0 unread" });
    expect(screen.queryByTestId("bell-count")).not.toBeInTheDocument();
  });

  it("sends this browser's id with every notification request", async () => {
    const api = mockApi({ "GET /api/search": page([]) });
    renderApp("/");
    await waitFor(() => expect(api.callsTo("GET", "/api/notifications").length).toBeGreaterThan(0));
    expect(api.callsTo("GET", "/api/notifications")[0].headers["X-Client-Id"]).toBe(getClientId());
    expect(getClientId()).toBe(getClientId());
    expect(getClientId()).toMatch(/^[A-Za-z0-9-]{8,64}$/);
  });

  it("opens the list and shows an empty message", async () => {
    mockApi({ "GET /api/search": page([]) });
    renderApp("/");
    await userEvent.click(screen.getByRole("button", { name: /Notifications/ }));
    expect(screen.getByText(/No notifications yet/)).toBeInTheDocument();
    await userEvent.keyboard("{Escape}");
    expect(screen.queryByText(/No notifications yet/)).not.toBeInTheDocument();
  });

  it("marks a notification read and opens the announcement", async () => {
    const api = mockApi({
      "GET /api/search": page([]),
      "GET /api/notifications": { unread: 1, items: [note(5)] },
      "PATCH /api/notifications/5/read": { ok: true, unread: 0 },
      "GET /api/announcements/105": announcement({ id: 105, title: "Notice 5" }),
    });
    renderApp("/");
    await userEvent.click(await screen.findByRole("button", { name: /Notifications, 1 unread/ }));
    await userEvent.click(screen.getByRole("button", { name: /New in Events: Notice 5/ }));
    expect(await screen.findByRole("heading", { name: "Notice 5" })).toBeInTheDocument();
    expect(api.callsTo("PATCH", "/api/notifications/5/read")).toHaveLength(1);
    expect(api.callsTo("PATCH", "/api/notifications/5/read")[0].headers["X-Client-Id"]).toBe(getClientId());
  });

  it("marks everything as read", async () => {
    let allRead = false; // like the real server, report 0 unread once everything has been marked
    const api = mockApi({
      "GET /api/search": page([]),
      "GET /api/notifications": () => (allRead ? { unread: 0, items: [note(1, { is_read: true }), note(2, { is_read: true })] } : { unread: 2, items: [note(1), note(2)] }),
      "PATCH /api/notifications/read-all": () => {
        allRead = true;
        return { ok: true, unread: 0 };
      },
    });
    renderApp("/");
    await userEvent.click(await screen.findByRole("button", { name: /Notifications, 2 unread/ }));
    await userEvent.click(screen.getByRole("button", { name: "Mark all as read" }));
    expect(api.callsTo("PATCH", "/api/notifications/read-all")).toHaveLength(1);
    await waitFor(() => expect(screen.queryByTestId("bell-count")).not.toBeInTheDocument());
  });

  it("copes with the server being unreachable", async () => {
    mockApi({ "GET /api/search": page([]), "GET /api/notifications": { status: 500, json: { error: { code: "server_error", message: "x", fields: null } } } });
    renderApp("/");
    await userEvent.click(screen.getByRole("button", { name: /Notifications/ }));
    expect(await screen.findByText(/could not be loaded/)).toBeInTheDocument();
  });
});

describe("Notifications page", () => {
  it("lists notifications with read and unread states", async () => {
    mockApi({ "GET /api/notifications": { unread: 1, items: [note(1), note(2, { is_read: true })] } });
    renderApp("/notifications");
    const list = await screen.findByRole("list");
    expect(within(list).getAllByRole("listitem")).toHaveLength(2);
    expect(screen.getByText("1 unread on this browser.")).toBeInTheDocument();
    expect(screen.getByText(/remembered per browser/)).toBeInTheDocument();
  });

  it("explains when there is nothing yet", async () => {
    mockApi();
    renderApp("/notifications");
    expect(await screen.findByText("No notifications yet", { selector: "h2" })).toBeInTheDocument();
  });
});
