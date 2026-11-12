import { api } from "@/api/client";

export const login = (username, password) => api("/api/auth/login", { method: "POST", json: { username, password }, auth: false });
export const logout = () => api("/api/auth/logout", { method: "POST" });
export const fetchCurrentPublisher = () => api("/api/auth/me");
