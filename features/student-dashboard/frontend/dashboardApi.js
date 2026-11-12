import { api } from "@/api/client";

/** Total published announcements and the count in each category. */
export const getDashboard = (signal) => api("/api/dashboard", { signal });
