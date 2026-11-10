// Student dashboard: cards, category tabs, search integration, loading / empty / error states. Owner: Moksh.
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { announcement, mockApi, page, renderApp } from "@/test/utils";

afterEach(() => vi.unstubAllGlobals());

describe("Student dashboard", () => {
  it("shows a loading state and then the announcement cards", async () => {
    mockApi({
      "GET /api/search": page([
        announcement({ id: 1, title: "Mid-sem timetable" }),
        announcement({ id: 2, title: "Tech Fest", category: "Events", event_date: "2026-12-05", attachments: [{ id: 9, kind: "poster", available: true }, { id: 10, kind: "pdf", available: true }] }),
      ]),
    });
    renderApp("/");
    expect(screen.getByText("Loading announcements")).toBeInTheDocument();

    const link = await screen.findByRole("link", { name: "Tech Fest" });
    expect(link).toHaveAttribute("href", "/announcements/2");
    expect(screen.getByRole("link", { name: "Mid-sem timetable" })).toBeInTheDocument();
    expect(screen.getByText("Event: 05 Dec 2026")).toBeInTheDocument();
    expect(screen.getByText("Poster")).toBeInTheDocument();
    expect(screen.getByText("PDF")).toBeInTheDocument();
    expect(screen.getByRole("status", { name: "" })).toHaveTextContent("2 announcements");
  });

  it("needs no login to read announcements", async () => {
    const api = mockApi({ "GET /api/search": page([announcement()]) });
    renderApp("/");
    await screen.findByRole("link", { name: "Mid-sem timetable" });
    expect(api.callsTo("GET", "/api/search")[0].headers.Authorization).toBeUndefined();
    expect(screen.getByRole("link", { name: "Publisher login" })).toBeInTheDocument();
  });

  it("filters by category and updates the request", async () => {
    const api = mockApi({
      "GET /api/search": ({ url }) => (url.includes("category=Clubs") ? page([announcement({ id: 3, title: "Robotics meet", category: "Clubs" })]) : page([announcement()])),
    });
    renderApp("/");
    await screen.findByRole("link", { name: "Mid-sem timetable" });

    const nav = screen.getByRole("navigation", { name: "Categories" });
    expect(within(nav).getAllByRole("button").map((b) => b.textContent.replace(/\d+$/, ""))).toEqual(["All", "Examinations", "Events", "Clubs", "General"]);
    await userEvent.click(within(nav).getByRole("button", { name: /Clubs/ }));

    await screen.findByRole("link", { name: "Robotics meet" });
    expect(within(nav).getByRole("button", { name: /Clubs/ })).toHaveAttribute("aria-current", "page");
    expect(api.callsTo("GET", "/api/search").at(-1).url).toContain("category=Clubs");
  });

  it("shows counts from the dashboard endpoint", async () => {
    mockApi({
      "GET /api/search": page([announcement()]),
      "GET /api/dashboard": { total: 7, categories: [{ name: "Examinations", count: 3 }, { name: "Events", count: 2 }, { name: "Clubs", count: 1 }, { name: "General", count: 1 }] },
    });
    renderApp("/");
    const nav = screen.getByRole("navigation", { name: "Categories" });
    expect(await within(nav).findByRole("button", { name: /^All\s*7$/ })).toBeInTheDocument();
    expect(within(nav).getByRole("button", { name: /Examinations\s*3/ })).toBeInTheDocument();
  });

  it("shows an empty state with a way to clear filters", async () => {
    mockApi({ "GET /api/search": page([]) });
    renderApp("/?q=zzz&category=Events");
    expect(await screen.findByText("No announcements found")).toBeInTheDocument();
    expect(screen.getByText(/Nothing matches your search in Events/)).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Clear filters" }));
    await waitFor(() => expect(screen.queryByText("No announcements found")).not.toBeInTheDocument());
  });

  it("explains when nothing has been published yet", async () => {
    mockApi({ "GET /api/search": page([]) });
    renderApp("/");
    expect(await screen.findByText("No announcements yet")).toBeInTheDocument();
  });

  it("shows an error state and lets the visitor retry", async () => {
    let failing = true;
    mockApi({ "GET /api/search": () => (failing ? { status: 500, json: { error: { code: "server_error", message: "x", fields: null } } } : page([announcement()])) });
    renderApp("/");
    expect(await screen.findByRole("alert")).toHaveTextContent("We couldn't load announcements");
    failing = false;
    await userEvent.click(screen.getByRole("button", { name: "Try again" }));
    expect(await screen.findByRole("link", { name: "Mid-sem timetable" })).toBeInTheDocument();
  });

  it("pages through results", async () => {
    const api = mockApi({
      "GET /api/search": ({ url }) => (url.includes("page=2") ? page([announcement({ id: 20, title: "Older notice" })], { page: 2, pages: 2, total: 10 }) : page([announcement()], { pages: 2, total: 10 })),
    });
    renderApp("/");
    await screen.findByText("Page 1 of 2");
    await userEvent.click(screen.getByRole("button", { name: "Older" }));
    await screen.findByRole("link", { name: "Older notice" });
    expect(api.callsTo("GET", "/api/search").at(-1).url).toContain("page=2");
  });

  it("shows a friendly page for unknown addresses", async () => {
    mockApi();
    renderApp("/no/such/page");
    expect(await screen.findByText("Page not found")).toBeInTheDocument();
  });
});
