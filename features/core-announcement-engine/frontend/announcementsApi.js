// Announcement calls. Owner: core-announcement-engine.
import { api } from "@/api/client";

export const getAnnouncement = (id, signal) => api(`/api/announcements/${id}`, { signal });
export const listMine = (signal) => api("/api/publisher/announcements", { signal });
export const createAnnouncement = (body) => api("/api/announcements", { method: "POST", json: body });
export const updateAnnouncement = (id, body) => api(`/api/announcements/${id}`, { method: "PUT", json: body });
export const publishAnnouncement = (id) => api(`/api/announcements/${id}/publish`, { method: "PATCH" });
export const unpublishAnnouncement = (id) => api(`/api/announcements/${id}/unpublish`, { method: "PATCH" });
export const deleteAnnouncement = (id) => api(`/api/announcements/${id}`, { method: "DELETE" });
