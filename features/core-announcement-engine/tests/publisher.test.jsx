// Publisher dashboard and the announcement form. Owner: core-announcement-engine.
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { validate } from "@features/core-announcement-engine/frontend/pages/AnnouncementFormPage";
import { announcement, mockApi, publisherUser, renderApp, signIn } from "@/test/utils";

afterEach(() => vi.unstubAllGlobals());

const stats = (extra = {}) => ({ total: 2, published: 1, drafts: 1, by_category: { Examinations: 1, Events: 1, Clubs: 0, General: 0 }, ...extra });
const listing = (items) => ({ stats: stats(), items });
const draft = announcement({ id: 2, title: "Club draft", category: "Clubs", is_published: false, published_at: null });
const live = announcement({ id: 1, title: "Mid-sem timetable" });

function loggedIn(handlers) {
  signIn();
  return mockApi({ "GET /api/auth/me": publisherUser, ...handlers });
}

describe("Publisher dashboard", () => {
  it("shows real statistics and every announcement with its status", async () => {
    loggedIn({ "GET /api/publisher/announcements": listing([live, draft]) });
    renderApp("/publisher");
    const statsBox = await screen.findByRole("region", { name: "Announcement statistics" });
    expect(within(statsBox).getByText("Published").nextSibling).toHaveTextContent("1");
    expect(within(statsBox).getByText("Drafts").nextSibling).toHaveTextContent("1");
    const rows = screen.getAllByRole("row").slice(1);
    expect(rows).toHaveLength(2);
    expect(within(rows[0]).getByText("Published")).toBeInTheDocument();
    expect(within(rows[1]).getByText("Draft")).toBeInTheDocument();
  });

  it("shows an empty state for a new publisher", async () => {
    loggedIn({ "GET /api/publisher/announcements": { stats: stats({ total: 0, published: 0, drafts: 0 }), items: [] } });
    renderApp("/publisher");
    expect(await screen.findByText("You haven't created any announcements")).toBeInTheDocument();
  });

  it("shows an error state when loading fails", async () => {
    loggedIn({ "GET /api/publisher/announcements": { status: 500, json: { error: { code: "server_error", message: "x", fields: null } } } });
    renderApp("/publisher");
    expect(await screen.findByRole("alert")).toHaveTextContent("We couldn't load your announcements");
  });

  it("publishes a draft and refreshes the list", async () => {
    let published = false;
    const api = loggedIn({
      "GET /api/publisher/announcements": () => listing([live, published ? { ...draft, is_published: true } : draft]),
      "PATCH /api/announcements/2/publish": () => {
        published = true;
        return { ...draft, is_published: true };
      },
    });
    renderApp("/publisher");
    await userEvent.click(await screen.findByRole("button", { name: "Publish Club draft" }));
    expect(await screen.findByText("Announcement published.")).toBeInTheDocument();
    expect(api.callsTo("PATCH", "/api/announcements/2/publish")).toHaveLength(1);
    expect(await screen.findByRole("button", { name: "Unpublish Club draft" })).toBeInTheDocument();
  });

  it("unpublishes a live announcement", async () => {
    const api = loggedIn({ "GET /api/publisher/announcements": listing([live]), "PATCH /api/announcements/1/unpublish": { ...live, is_published: false } });
    renderApp("/publisher");
    await userEvent.click(await screen.findByRole("button", { name: "Unpublish Mid-sem timetable" }));
    expect(await screen.findByText(/Students can no longer see it/)).toBeInTheDocument();
    expect(api.callsTo("PATCH", "/api/announcements/1/unpublish")).toHaveLength(1);
  });

  it("asks before deleting and deletes only when confirmed", async () => {
    const api = loggedIn({ "GET /api/publisher/announcements": listing([live]), "DELETE /api/announcements/1": { status: 204 } });
    const confirm = vi.spyOn(window, "confirm").mockReturnValueOnce(false).mockReturnValueOnce(true);
    renderApp("/publisher");
    const button = await screen.findByRole("button", { name: "Delete Mid-sem timetable" });
    await userEvent.click(button);
    expect(api.callsTo("DELETE", "/api/announcements")).toHaveLength(0);
    await userEvent.click(button);
    expect(await screen.findByText("Announcement deleted.")).toBeInTheDocument();
    expect(confirm).toHaveBeenCalledTimes(2);
    expect(api.callsTo("DELETE", "/api/announcements/1")).toHaveLength(1);
  });

  it("shows the server's message when an action fails", async () => {
    loggedIn({ "GET /api/publisher/announcements": listing([live]), "PATCH /api/announcements/1/unpublish": { status: 403, json: { error: { code: "forbidden", message: "You can only change announcements that you created.", fields: null } } } });
    renderApp("/publisher");
    await userEvent.click(await screen.findByRole("button", { name: "Unpublish Mid-sem timetable" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("You can only change announcements that you created.");
  });
});

describe("validate()", () => {
  const good = { title: "T", category: "Events", description: "D", event_date: "", event_time: "", venue: "", registration_link: "", is_published: false };
  it("accepts a valid form", () => expect(validate(good)).toEqual({}));
  it("flags each problem", () => {
    expect(Object.keys(validate({ ...good, title: " ", category: "", description: "" }))).toEqual(["title", "category", "description"]);
    expect(validate({ ...good, title: "x".repeat(151) }).title).toMatch(/150/);
    expect(validate({ ...good, registration_link: "ftp://x" }).registration_link).toMatch(/http/);
    expect(validate({ ...good, registration_link: "https://ok.example" })).toEqual({});
  });
});

describe("Announcement form", () => {
  async function fill(user) {
    await user.type(await screen.findByLabelText("Title"), "Hackathon");
    await user.selectOptions(screen.getByLabelText("Category"), "Events");
    await user.type(screen.getByLabelText("Description"), "Build something in 24 hours.");
  }

  it("shows validation messages and does not call the server", async () => {
    const api = loggedIn({});
    renderApp("/publisher/announcements/new");
    await userEvent.click(await screen.findByRole("button", { name: "Save announcement" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Title is required.");
    expect(screen.getByLabelText("Title")).toHaveAttribute("aria-invalid", "true");
    expect(api.callsTo("POST", "/api/announcements")).toHaveLength(0);
  });

  it("saves a draft by default", async () => {
    const api = loggedIn({ "POST /api/announcements": { ...announcement({ id: 8, title: "Hackathon", category: "Events", is_published: false }) }, "GET /api/publisher/announcements": listing([]) });
    renderApp("/publisher/announcements/new");
    const user = userEvent.setup();
    await fill(user);
    await user.click(screen.getByRole("button", { name: "Save announcement" }));
    expect(await screen.findByText("Announcement saved. It is saved as a draft.")).toBeInTheDocument();
    expect(api.callsTo("POST", "/api/announcements")[0].body).toMatchObject({ title: "Hackathon", category: "Events", is_published: false, venue: null, event_date: null });
  });

  it("publishes immediately and sends event details", async () => {
    const api = loggedIn({ "POST /api/announcements": announcement({ id: 8, is_published: true }), "GET /api/publisher/announcements": listing([]) });
    renderApp("/publisher/announcements/new");
    const user = userEvent.setup();
    await fill(user);
    await user.type(screen.getByLabelText("Venue (optional)"), "Seminar Hall");
    await user.type(screen.getByLabelText("Event date (optional)"), "2026-12-05");
    await user.type(screen.getByLabelText("Registration link (optional)"), "https://example.com/join");
    await user.click(screen.getByLabelText(/Publish now/));
    await user.click(screen.getByRole("button", { name: "Save announcement" }));
    expect(await screen.findByText(/It is now live/)).toBeInTheDocument();
    expect(api.callsTo("POST", "/api/announcements")[0].body).toMatchObject({ is_published: true, venue: "Seminar Hall", event_date: "2026-12-05", registration_link: "https://example.com/join" });
  });

  it("uploads the chosen poster after saving", async () => {
    const api = loggedIn({
      "POST /api/announcements": announcement({ id: 8 }),
      "POST /api/announcements/8/attachments": announcement({ id: 8 }),
      "GET /api/publisher/announcements": listing([]),
    });
    renderApp("/publisher/announcements/new");
    const user = userEvent.setup();
    await fill(user);
    await user.upload(screen.getByLabelText("Poster"), new File([new Uint8Array(10)], "poster.png", { type: "image/png" }));
    await user.click(screen.getByRole("button", { name: "Save announcement" }));
    await screen.findByRole("heading", { name: "Your announcements" });
    const [upload] = api.callsTo("POST", "/api/announcements/8/attachments");
    expect(upload.body.get("kind")).toBe("poster");
    expect(upload.body.get("file").name).toBe("poster.png");
  });

  it("shows server-side field errors next to the fields", async () => {
    loggedIn({ "POST /api/announcements": { status: 422, json: { error: { code: "validation_error", message: "Please correct the highlighted fields.", fields: { event_date: "Event date must look like 2026-12-31." } } } } });
    renderApp("/publisher/announcements/new");
    const user = userEvent.setup();
    await fill(user);
    await user.click(screen.getByRole("button", { name: "Save announcement" }));
    expect((await screen.findAllByText("Event date must look like 2026-12-31.")).length).toBeGreaterThan(0);
    expect(screen.getByLabelText("Event date (optional)")).toHaveAttribute("aria-invalid", "true");
  });

  it("loads an existing announcement for editing and saves with PUT", async () => {
    const api = loggedIn({
      "GET /api/announcements/2": { ...draft, event_time: "14:30:00", venue: "Lab 3" },
      "PUT /api/announcements/2": draft,
      "GET /api/publisher/announcements": listing([draft]),
    });
    renderApp("/publisher/announcements/2/edit");
    expect(await screen.findByDisplayValue("Club draft")).toBeInTheDocument();
    expect(screen.getByLabelText("Category")).toHaveValue("Clubs");
    expect(screen.getByLabelText("Event time (optional)")).toHaveValue("14:30");
    expect(screen.getByLabelText("Venue (optional)")).toHaveValue("Lab 3");
    await userEvent.clear(screen.getByLabelText("Title"));
    await userEvent.type(screen.getByLabelText("Title"), "Renamed");
    await userEvent.click(screen.getByRole("button", { name: "Save changes" }));
    await waitFor(() => expect(api.callsTo("PUT", "/api/announcements/2")).toHaveLength(1));
    expect(api.callsTo("PUT", "/api/announcements/2")[0].body.title).toBe("Renamed");
    expect(await screen.findByText("Changes saved.")).toBeInTheDocument();
  });

  it("removes a current attachment when asked", async () => {
    const pdf = { id: 12, kind: "pdf", original_filename: "Rules.pdf", mime_type: "application/pdf", size_bytes: 10, available: true, url: "/a", download_url: "/b" };
    const api = loggedIn({
      "GET /api/announcements/2": { ...draft, attachments: [pdf] },
      "PUT /api/announcements/2": draft,
      "DELETE /api/attachments/12": { status: 204 },
      "GET /api/publisher/announcements": listing([draft]),
    });
    renderApp("/publisher/announcements/2/edit");
    await userEvent.click(await screen.findByLabelText("Remove current pdf"));
    await userEvent.click(screen.getByRole("button", { name: "Save changes" }));
    await screen.findByText("Changes saved.");
    expect(api.callsTo("DELETE", "/api/attachments/12")).toHaveLength(1);
  });

  it("keeps the announcement and reports a failed upload", async () => {
    loggedIn({
      "POST /api/announcements": announcement({ id: 8 }),
      "POST /api/announcements/8/attachments": { status: 413, json: { error: { code: "file_too_large", message: "Poster must be 3 MB or smaller.", fields: { file: "Poster is too large." } } } },
      "GET /api/announcements/8": announcement({ id: 8 }),
    });
    renderApp("/publisher/announcements/new");
    const user = userEvent.setup();
    await fill(user);
    await user.upload(screen.getByLabelText("Poster"), new File([new Uint8Array(10)], "poster.png"));
    await user.click(screen.getByRole("button", { name: "Save announcement" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(/Announcement saved, but the poster could not be saved/);
    expect(screen.getByRole("heading", { name: "Edit announcement" })).toBeInTheDocument();
  });

  it("shows not found for an announcement that is not yours", async () => {
    loggedIn({ "GET /api/announcements/77": { status: 404, json: { error: { code: "not_found", message: "We couldn't find that.", fields: null } } } });
    renderApp("/publisher/announcements/77/edit");
    expect(await screen.findByText("Announcement not found")).toBeInTheDocument();
  });
});
