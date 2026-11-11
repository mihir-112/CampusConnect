// A random id for this browser. Owner: search-notifications.
// There are no student accounts, so this is how the server remembers which notifications
// *this browser* has read. Clearing browser data creates a new id (everything shows as unread).
const KEY = "campusconnect.clientId";
let fallback = null;

function makeId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) return crypto.randomUUID();
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    return (c === "x" ? r : (r & 3) | 8).toString(16);
  });
}

export function getClientId() {
  try {
    let id = window.localStorage.getItem(KEY);
    if (!id) {
      id = makeId();
      window.localStorage.setItem(KEY, id);
    }
    return id;
  } catch {
    fallback = fallback || makeId(); // storage blocked: lasts until the page is closed
    return fallback;
  }
}
