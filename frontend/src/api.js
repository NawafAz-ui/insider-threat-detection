// The dashboard does no calculation: it sends HTTPS requests with the login token and shows the JSON.
const BASE = import.meta.env.VITE_API_BASE || "";
let token = sessionStorage.getItem("token") || "";

export const isLoggedIn = () => !!token;
export const getUsername = () => sessionStorage.getItem("username") || "";
export function logout() { token = ""; sessionStorage.removeItem("token"); sessionStorage.removeItem("username"); }

async function request(path, options = {}) {
  const res = await fetch(BASE + path, {
    ...options,
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
  });
  if (res.status === 401 && token) { logout(); window.location.reload(); }
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(typeof body.detail === "string" ? body.detail : "Request failed");
  return body;
}

export async function login(username, password) {
  const r = await request("/api/login", { method: "POST", body: JSON.stringify({ username, password }) });
  token = r.token;
  sessionStorage.setItem("token", token);
  sessionStorage.setItem("username", r.username);
  return r;
}
export const getSessions = (offset = 0, limit = 50) => request(`/api/sessions?offset=${offset}&limit=${limit}`);
export const getSession = (id) => request(`/api/sessions/${encodeURIComponent(id)}`);
export const askAssistant = (id, question) =>
  request(`/api/sessions/${encodeURIComponent(id)}/chat`, { method: "POST", body: JSON.stringify({ question }) });
