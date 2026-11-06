// Date and time formatting shared by every page. Owner: Moksh.
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

/** "2026-12-05" (an event date, no timezone) -> "05 Dec 2026". */
export function formatEventDate(value) {
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(value || "");
  if (!match) return "";
  return `${match[3]} ${MONTHS[Number(match[2]) - 1]} ${match[1]}`;
}

/** "14:30:00" -> "2:30 PM". */
export function formatEventTime(value) {
  const match = /^(\d{1,2}):(\d{2})/.exec(value || "");
  if (!match) return "";
  const hours = Number(match[1]);
  return `${hours % 12 || 12}:${match[2]} ${hours >= 12 ? "PM" : "AM"}`;
}

/** A UTC timestamp from the API -> "31 Oct 2026" in the reader's own timezone. */
export function formatTimestampDate(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return `${String(date.getDate()).padStart(2, "0")} ${MONTHS[date.getMonth()]} ${date.getFullYear()}`;
}

export function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function truncate(text, length = 150) {
  if (!text || text.length <= length) return text || "";
  return text.slice(0, length).trimEnd() + "\u2026";
}
