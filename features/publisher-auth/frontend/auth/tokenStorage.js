// Where the publisher's token is kept. Owner: publisher-auth.
//
// sessionStorage: the token disappears when the browser tab is closed, and it is never sent to
// any site except through the API client. (An httpOnly cookie would hide it from scripts too, but
// then every write request would also need CSRF protection; see documentation/security.md.)
const KEY = "campusconnect.token";

export function getToken() {
  try {
    return window.sessionStorage.getItem(KEY);
  } catch {
    return null;
  }
}

export function setToken(token) {
  try {
    window.sessionStorage.setItem(KEY, token);
  } catch {
    /* storage blocked: the session simply will not survive a refresh */
  }
}

export function clearToken() {
  try {
    window.sessionStorage.removeItem(KEY);
  } catch {
    /* nothing to clear */
  }
}
