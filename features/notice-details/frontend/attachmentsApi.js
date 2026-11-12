import { api } from "@/api/client";

export function uploadAttachment(announcementId, kind, file) {
  const form = new FormData();
  form.append("kind", kind);
  form.append("file", file);
  return api(`/api/announcements/${announcementId}/attachments`, { method: "POST", form });
}

export const deleteAttachment = (attachmentId) => api(`/api/attachments/${attachmentId}`, { method: "DELETE" });
