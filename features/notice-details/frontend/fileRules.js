// Upload rules, mirrored from backend/core/constants.py for quick feedback. Owner: notice-details.
// The server checks the real file contents again, so these are a convenience, not the protection.
export const FILE_RULES = {
  poster: { label: "Poster", extensions: ["png", "jpg", "jpeg", "webp"], maxBytes: 3 * 1024 * 1024, accept: ".png,.jpg,.jpeg,.webp" },
  pdf: { label: "PDF", extensions: ["pdf"], maxBytes: 5 * 1024 * 1024, accept: ".pdf" },
};

/** Returns an error message, or "" when the file looks fine. */
export function checkFile(kind, file) {
  const rules = FILE_RULES[kind];
  const extension = (file.name.split(".").pop() || "").toLowerCase();
  if (!file.name.includes(".") || !rules.extensions.includes(extension)) return `${rules.label} must be one of these types: ${rules.extensions.join(", ")}.`;
  if (file.size === 0) return `The ${rules.label.toLowerCase()} file is empty.`;
  if (file.size > rules.maxBytes) return `${rules.label} must be ${rules.maxBytes / (1024 * 1024)} MB or smaller.`;
  return "";
}
