import { api } from "@/api/client";
import { getClientId } from "./clientId";

const headers = () => ({ "X-Client-Id": getClientId() });

export const listNotifications = (limit = 10, signal) => api(`/api/notifications?limit=${limit}`, { headers: headers(), signal });
export const markNotificationRead = (id) => api(`/api/notifications/${id}/read`, { method: "PATCH", headers: headers() });
export const markAllNotificationsRead = () => api("/api/notifications/read-all", { method: "PATCH", headers: headers() });
