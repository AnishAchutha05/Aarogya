const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Token management using memory + localStorage
let accessToken: string | null = null;

export function setTokens(access: string, refresh: string) {
  accessToken = access;
  localStorage.setItem("aarogya_refresh", refresh);
}

export function setAccessToken(access: string) {
  accessToken = access;
}

export function getAccessToken(): string | null {
  return accessToken;
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("aarogya_refresh");
}

export function clearTokens() {
  accessToken = null;
  if (typeof window !== "undefined") {
    localStorage.removeItem("aarogya_refresh");
  }
}

export async function apiFetch(
  endpoint: string,
  options: RequestInit = {},
  isRetry = false
): Promise<Response> {
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> || {}),
  };

  // Don't set Content-Type for FormData
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  if (accessToken) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    credentials: "include",
    headers,
  });

  // Try to refresh token on 401
  if (response.status === 401 && !isRetry) {
    const refreshToken = getRefreshToken();
    if (refreshToken) {
      try {
        const refreshResponse = await fetch(`${API_URL}/auth/refresh`, {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          ...(refreshToken ? { body: JSON.stringify({ refresh_token: refreshToken }) } : {}),
        });
        if (refreshResponse.ok) {
          const data = await refreshResponse.json();
          setTokens(data.access_token, data.refresh_token);
          return apiFetch(endpoint, options, true);
        }
      } catch {
        // Refresh failed, clear tokens
      }
      clearTokens();
      throw new ApiError(401, "Session expired");
    }
  }

  return response;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

export async function apiJson<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await apiFetch(endpoint, options);
  if (!response.ok) {
    let message = `Request failed: ${response.status}`;
    try {
      const err = await response.json();
      message = err.detail || message;
    } catch {}
    throw new ApiError(response.status, message);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

export { API_URL };
