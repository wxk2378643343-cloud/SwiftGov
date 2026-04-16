const API_BASE = "http://localhost:8001";

export function saveSession(token, user, permissions = []) {
  localStorage.setItem("token", token);
  localStorage.setItem("user", JSON.stringify(user));
  localStorage.setItem("permissions", JSON.stringify(permissions));
}

export function clearSession() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  localStorage.removeItem("permissions");
}

export function getToken() {
  return localStorage.getItem("token");
}

export function getUser() {
  const raw = localStorage.getItem("user");
  return raw ? JSON.parse(raw) : null;
}

export function getPermissions() {
  const raw = localStorage.getItem("permissions");
  return raw ? JSON.parse(raw) : [];
}

export function hasPermission(permission) {
  return getPermissions().includes(permission);
}

export function updateUserSession(user, permissions = null) {
  localStorage.setItem("user", JSON.stringify(user));
  if (permissions) {
    localStorage.setItem("permissions", JSON.stringify(permissions));
  }
}

export async function api(path, options = {}) {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || "请求失败");
  }
  return data;
}
