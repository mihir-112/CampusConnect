// Announcement detail page, attachments and the file picker. Owner: notice-details.
import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import AttachmentUploader from "@features/notice-details/frontend/components/AttachmentUploader";
import { checkFile } from "@features/notice-details/frontend/fileRules";
import { announcement, mockApi, renderApp } from "@/test/utils";

afterEach(() => vi.unstubAllGlobals());

const poster = { id: 11, kind: "poster", original_filename: "poster.png", mime_type: "image/png", size_bytes: 2048, available: true, url: "/api/attachments/11", download_url: "/api/attachments/11/download" };
const pdf = { id: 12, kind: "pdf", original_filename: "Rules.pdf", mime_type: "application/pdf", size_bytes: 52_224, available: true, url: "/api/attachments/12", download_url: "/api/attachments/12/download" };

describe("Announcement detail page", () => {
  it("shows the event date, time, venue and registration link", async () => {
    mockApi({ "GET /api/announcements/3": announcement({ id: 3, title: "Tech Fest", category: "Events", venue: "Main Hall", event_date: "2026-12-05", event_time: "14:30:00", registration_link: "https://example.com/fest" }) });
    renderApp("/announcements/3");
    expect(await screen.findByRole("heading", { name: "Tech Fest" })).toBeInTheDocument();
    expect(screen.getByText("05 Dec 2026")).toBeInTheDocument();
    expect(screen.getByText("2:30 PM")).toBeInTheDocument();
    expect(screen.getByText("Main Hall")).toBeInTheDocument();
    const register = screen.getByRole("link", { name: "Register for this event" });
    expect(register).toHaveAttribute("href", "https://example.com/fest");
    expect(register).toHaveAttribute("rel", expect.stringContaining("noopener"));
  });

  it("omits the facts box for notices with no event details", async () => {
    mockApi({ "GET /api/announcements/1": announcement() });
    renderApp("/announcements/1");
    await screen.findByRole("heading", { name: "Mid-sem timetable" });
    expect(screen.queryByText("Venue")).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Register for this event" })).not.toBeInTheDocument();
  });

  it("shows the poster and PDF with view, download and preview", async () => {
    mockApi({ "GET /api/announcements/1": announcement({ attachments: [poster, pdf] }) });
    renderApp("/announcements/1");
    const image = await screen.findByAltText("Poster for Mid-sem timetable");
    expect(image).toHaveAttribute("src", "/api/attachments/11");
    expect(screen.getByText("Rules.pdf (51 KB)")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "View PDF" })).toHaveAttribute("href", "/api/attachments/12");
    expect(screen.getByRole("link", { name: "Download PDF" })).toHaveAttribute("href", "/api/attachments/12/download");

    expect(screen.queryByTitle(/PDF preview/)).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Preview PDF" }));
    expect(screen.getByTitle("PDF preview: Mid-sem timetable")).toHaveAttribute("src", "/api/attachments/12");
    await userEvent.click(screen.getByRole("button", { name: "Hide preview" }));
    expect(screen.queryByTitle(/PDF preview/)).not.toBeInTheDocument();
  });

  it("explains gracefully when a file is missing on the server", async () => {
    mockApi({ "GET /api/announcements/1": announcement({ attachments: [{ ...poster, available: false }, { ...pdf, available: false }] }) });
    renderApp("/announcements/1");
    expect(await screen.findByText(/poster is currently unavailable/)).toBeInTheDocument();
    expect(screen.getByText(/PDF is currently unavailable/)).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Download PDF" })).not.toBeInTheDocument();
  });

  it("falls back when the poster image fails to load", async () => {
    mockApi({ "GET /api/announcements/1": announcement({ attachments: [poster] }) });
    renderApp("/announcements/1");
    const image = await screen.findByAltText("Poster for Mid-sem timetable");
    fireEvent.error(image);
    expect(await screen.findByText(/poster is currently unavailable/)).toBeInTheDocument();
  });

  it("shows a not-found message for missing or unpublished announcements", async () => {
    mockApi({ "GET /api/announcements/99": { status: 404, json: { error: { code: "not_found", message: "x", fields: null } } } });
    renderApp("/announcements/99");
    expect(await screen.findByText("Announcement not found")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Back to announcements" })).toBeInTheDocument();
  });

  it("shows an error state with retry when the server fails", async () => {
    let failing = true;
    mockApi({ "GET /api/announcements/1": () => (failing ? { status: 500, json: { error: { code: "server_error", message: "Server trouble.", fields: null } } } : announcement()) });
    renderApp("/announcements/1");
    expect(await screen.findByRole("alert")).toHaveTextContent("We couldn't load this announcement");
    failing = false;
    await userEvent.click(screen.getByRole("button", { name: "Try again" }));
    expect(await screen.findByRole("heading", { name: "Mid-sem timetable" })).toBeInTheDocument();
  });
});

describe("File rules and picker", () => {
  const file = (name, size = 100) => new File([new Uint8Array(size)], name);

  it("accepts good files and rejects wrong types, empty and oversized files", () => {
    expect(checkFile("poster", file("a.PNG"))).toBe("");
    expect(checkFile("pdf", file("a.pdf"))).toBe("");
    expect(checkFile("poster", file("a.pdf"))).toMatch(/must be one of these types/);
    expect(checkFile("pdf", file("noextension"))).toMatch(/must be one of these types/);
    expect(checkFile("pdf", file("a.pdf", 0))).toMatch(/empty/);
    expect(checkFile("poster", file("a.png", 3 * 1024 * 1024 + 1))).toMatch(/3 MB or smaller/);
    expect(checkFile("pdf", file("a.pdf", 5 * 1024 * 1024 + 1))).toMatch(/5 MB or smaller/);
  });

  function Harness({ current }) {
    const [chosen, setChosen] = useState(null);
    const [remove, setRemove] = useState(false);
    return (
      <>
        <AttachmentUploader kind="pdf" current={current} file={chosen} remove={remove} onFile={setChosen} onRemove={setRemove} />
        <output data-testid="chosen">{chosen ? chosen.name : "none"}</output>
        <output data-testid="remove">{String(remove)}</output>
      </>
    );
  }

  it("passes a valid file up and refuses an invalid one with a message", async () => {
    render(<Harness />);
    const input = screen.getByLabelText("PDF");
    await userEvent.upload(input, file("notice.pdf"));
    expect(screen.getByTestId("chosen")).toHaveTextContent("notice.pdf");
    await userEvent.upload(input, file("virus.exe"), { applyAccept: false });
    expect(await screen.findByRole("alert")).toHaveTextContent("must be one of these types");
    expect(screen.getByTestId("chosen")).toHaveTextContent("none");
  });

  it("offers to remove the current file", async () => {
    render(<Harness current={pdf} />);
    expect(screen.getByText("Current pdf: Rules.pdf")).toBeInTheDocument();
    await userEvent.click(screen.getByLabelText("Remove current pdf"));
    expect(screen.getByTestId("remove")).toHaveTextContent("true");
  });
});
