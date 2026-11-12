// Login page, protected pages and logout. Owner: publisher-auth.
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { getToken } from "@features/publisher-auth/frontend/auth/tokenStorage";
import { mockApi, page, publisherUser, renderApp, signIn } from "@/test/utils";

afterEach(() => vi.unstubAllGlobals());

const dashboardData = { stats: { total: 0, published: 0, drafts: 0, by_category: { Examinations: 0, Events: 0, Clubs: 0, General: 0 } }, items: [] };

describe("Publisher login", () => {
  it("has labelled fields and asks for missing values without calling the server", async () => {
    const api = mockApi();
    renderApp("/publisher/login");
    expect(screen.getByLabelText("Username")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toHaveAttribute("type", "password");
    await userEvent.click(screen.getByRole("button", { name: "Log in" }));
    expect(screen.getByText("Enter your username.")).toBeInTheDocument();
    expect(screen.getByText("Enter your password.")).toBeInTheDocument();
    expect(api.callsTo("POST", "/api/auth/login")).toHaveLength(0);
  });

  it("logs in, keeps the token for this tab and opens the dashboard", async () => {
    const api = mockApi({
      "POST /api/auth/login": { access_token: "abc123", token_type: "bearer", expires_in: 7200, publisher: publisherUser },
      "GET /api/publisher/announcements": dashboardData,
    });
    renderApp("/publisher/login");
    await userEvent.type(screen.getByLabelText("Username"), "editor");
    await userEvent.type(screen.getByLabelText("Password"), "password123");
    await userEvent.click(screen.getByRole("button", { name: "Log in" }));

    expect(await screen.findByRole("heading", { name: "Your announcements" })).toBeInTheDocument();
    expect(getToken()).toBe("abc123");
    expect(api.callsTo("POST", "/api/auth/login")[0].body).toEqual({ username: "editor", password: "password123" });
    expect(api.callsTo("GET", "/api/publisher/announcements")[0].headers.Authorization).toBe("Bearer abc123");
    expect(screen.getByRole("button", { name: "Log out" })).toBeInTheDocument();
  });

  it("shows the server's message when the login fails, and clears the password", async () => {
    mockApi({ "POST /api/auth/login": { status: 401, json: { error: { code: "unauthorized", message: "Invalid username or password.", fields: null } } } });
    renderApp("/publisher/login");
    await userEvent.type(screen.getByLabelText("Username"), "editor");
    await userEvent.type(screen.getByLabelText("Password"), "wrong");
    await userEvent.click(screen.getByRole("button", { name: "Log in" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Invalid username or password.");
    expect(screen.getByLabelText("Password")).toHaveValue("");
    expect(getToken()).toBeNull();
  });
});

describe("Protected pages", () => {
  it.each(["/publisher", "/publisher/announcements/new", "/publisher/announcements/3/edit"])("%s sends logged-out visitors to the login page", async (path) => {
    mockApi();
    renderApp(path);
    expect(await screen.findByRole("heading", { name: "Publisher login" })).toBeInTheDocument();
  });

  it("lets a saved session straight in after checking it with the server", async () => {
    signIn();
    mockApi({ "GET /api/auth/me": publisherUser, "GET /api/publisher/announcements": dashboardData });
    renderApp("/publisher");
    expect(await screen.findByText(/Signed in as editor/)).toBeInTheDocument();
  });

  it("sends the visitor back to login when the session has expired", async () => {
    signIn("old-token");
    mockApi({ "GET /api/auth/me": { status: 401, json: { error: { code: "unauthorized", message: "Your session has ended.", fields: null } } } });
    renderApp("/publisher");
    expect(await screen.findByRole("heading", { name: "Publisher login" })).toBeInTheDocument();
    expect(getToken()).toBeNull();
  });

  it("returns to the page the visitor wanted after logging in", async () => {
    mockApi({
      "POST /api/auth/login": { access_token: "t", token_type: "bearer", expires_in: 1, publisher: publisherUser },
      "GET /api/announcements/4": { id: 4, title: "Existing", description: "d", category: "Clubs", venue: null, event_date: null, event_time: null, registration_link: null, is_published: false, created_at: "2026-10-30T08:00:00Z", updated_at: "2026-10-30T08:00:00Z", published_at: null, attachments: [] },
    });
    renderApp("/publisher/announcements/4/edit");
    await userEvent.type(await screen.findByLabelText("Username"), "editor");
    await userEvent.type(screen.getByLabelText("Password"), "password123");
    await userEvent.click(screen.getByRole("button", { name: "Log in" }));
    expect(await screen.findByRole("heading", { name: "Edit announcement" })).toBeInTheDocument();
  });
});

describe("Logout", () => {
  it("ends the session on the server, forgets the token and returns to the homepage", async () => {
    signIn();
    const api = mockApi({ "GET /api/auth/me": publisherUser, "GET /api/publisher/announcements": dashboardData, "POST /api/auth/logout": { ok: true }, "GET /api/search": page([]) });
    renderApp("/publisher");
    await userEvent.click(await screen.findByRole("button", { name: "Log out" }));
    await waitFor(() => expect(getToken()).toBeNull());
    expect(api.callsTo("POST", "/api/auth/logout")).toHaveLength(1);
    expect(await screen.findByRole("heading", { name: "Campus announcements" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Publisher login" })).toBeInTheDocument();
  });
});
