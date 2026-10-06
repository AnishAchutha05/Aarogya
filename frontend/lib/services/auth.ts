import { apiJson, setTokens, clearTokens, apiFetch, API_URL } from "../api";
import type { TokenResponse, UserResponse } from "@/types";

export const authService = {
  async register(email: string, password: string, name: string): Promise<UserResponse> {
    return apiJson<UserResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, name }),
    });
  },

  async login(email: string, password: string): Promise<UserResponse> {
    const tokens = await apiJson<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    setTokens(tokens.access_token, tokens.refresh_token);
    return apiJson<UserResponse>("/users/me");
  },

  async logout(refreshToken: string): Promise<void> {
    try {
      await apiJson<void>("/auth/logout", {
        method: "POST",
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
    } finally {
      clearTokens();
    }
  },

  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    return apiJson<void>("/auth/change-password", {
      method: "POST",
      body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
    });
  },

  getGoogleLoginUrl(): string {
    return `${API_URL}/auth/google`;
  },

  getYahooLoginUrl(): string {
    return `${API_URL}/auth/yahoo`;
  },
};
