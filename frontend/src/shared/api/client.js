// The one place that talks to FastAPI. Owner: core-announcement-engine (shared API conventions).
//
// - Adds the publisher's token when there is one.
// - Turns every error response ({"error": {code, message, fields}}) into an ApiError.
// - Tells the app when a token stops working, so it can send the publisher back to login.
import { clearToken, getToken } from "@features/publisher-auth/frontend/auth/tokenStorage";

export const UNAUTHORIZED_EVENT = "campusconnect:unauthorized";
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export class ApiError extends Error {
  constructor({ status, code, message, fields }) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.fields = fields || null;
  }
}

export async function api(path, { method = "GET", json, form, headers = {}, signal, auth = true } = {}) {
  const requestHeaders = { Accept: "application/json", ...headers };
  const token = auth ? getToken() : null;
  if (token) requestHeaders.Authorization = `Bearer ${token}`;

  let body;
  if (json !== undefined) {
    requestHeaders["Content-Type"] = "application/json";
    body = JSON.stringify(json);
  } else if (form) {
    body = form; // the browser sets the multipart boundary itself
  }

  let response;
  try {
    response = await fetch(BASE_URL + path, { method, headers: requestHeaders, body, signal });
  } catch (error) {
    if (error?.name === "AbortError") throw error;
    throw new ApiError({
      status: 0,
      code: "network_error",
      message: "We couldn't reach the server. Check your connection and try again.",
    });
  }

  if (response.status === 204) return null;

  let data = null;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const problem = data?.error || {};
    if (response.status === 401 && token) {
      clearToken();
      window.dispatchEvent(new Event(UNAUTHORIZED_EVENT));
    }
    throw new ApiError({
      status: response.status,
      code: problem.code || "error",
      message: problem.message || "Something went wrong. Please try again.",
      fields: problem.fields,
    });
  }
  return data;
}

export function isAbort(error) {
  return error?.name === "AbortError";
}
