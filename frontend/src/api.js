// The dashboard does no calculation: it sends requests with the login token and shows the JSON.
const BASE = import.meta.env.VITE_API_BASE || "";
let token = sessionStorage.getItem("token") || "";

export const isLoggedIn = () => !!token;
export const getUsername = () => sessionStorage.getItem("username") || "";
export function logout() { token = ""; sessionStorage.removeItem("token"); sessionStorage.removeItem("username"); }

export class ApiError extends Error {
  constructor(message, status) { super(message); this.status = status; }
}

function messageFor(status, body, isLogin) {
  if (status === 401) return isLogin ? "Wrong username or password." : "Your session expired. Sign in again.";
  if (status === 403) return "Your account is not allowed to do this.";
  if (status === 404) return "That item was not found.";
  if (status === 422) return typeof body?.detail === "string" ? body.detail : "Some of the input was not valid. Check it and try again.";
  if (status === 426) return "This server only accepts HTTPS connections.";
  if (status === 429) return "Too many failed sign-in attempts. Wait 15 minutes and try again.";
  if (status >= 500) return "The server had a problem. Try again. If it continues, check that the API and database are running.";
  return "Something went wrong. Try again.";
}

async function request(path, options = {}, isLogin = false) {
  let res;
  try {
    res = await fetch(BASE + path, {
      ...options,
      headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    });
  } catch {
    throw new ApiError("Cannot reach the server. Check that the API is running.", 0);
  }
  const body = await res.json().catch(() => null);
  if (res.status === 401 && token && !isLogin) { logout(); window.dispatchEvent(new Event("auth-expired")); }
  if (!res.ok) throw new ApiError(messageFor(res.status, body, isLogin), res.status);
  return body;
}

export async function login(username, password) {
  const r = await request("/api/login", { method: "POST", body: JSON.stringify({ username, password }) }, true);
  token = r.token;
  sessionStorage.setItem("token", token);
  sessionStorage.setItem("username", r.username);
  return r;
}
export const getSessions = (offset = 0, limit = 50) => request(`/api/sessions?offset=${offset}&limit=${limit}`);
export const getSession = (id) => request(`/api/sessions/${encodeURIComponent(id)}`);
export const askAssistant = (id, question) =>
  request(`/api/sessions/${encodeURIComponent(id)}/chat`, { method: "POST", body: JSON.stringify({ question }) });
