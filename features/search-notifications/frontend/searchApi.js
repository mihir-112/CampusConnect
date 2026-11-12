import { api } from "@/api/client";

export function searchAnnouncements({ q = "", category = "", page = 1, perPage = 9, signal } = {}) {
  const params = new URLSearchParams({ page: String(page), per_page: String(perPage) });
  if (q.trim()) params.set("q", q.trim());
  if (category) params.set("category", category);
  return api(`/api/search?${params}`, { signal });
}
