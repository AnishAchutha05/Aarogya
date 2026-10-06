"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { setTokens, setAccessToken, clearTokens, getRefreshToken, getAccessToken } from "@/lib/api";
import { authService } from "@/lib/services/auth";
import { usersService } from "@/lib/services/users";
import type { UserResponse } from "@/types";

interface AuthState {
  user: UserResponse | null;
  loading: boolean;
  error: string | null;
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

let isRefreshing = false;
let refreshPromise: Promise<any> | null = null;

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    loading: true,
    error: null,
  });

  const loadUser = useCallback(async () => {
    const token = getAccessToken();
    if (!token) {
      setState({ user: null, loading: false, error: null });
      return;
    }
    try {
      const user = await usersService.getMe();
      setState({ user, loading: false, error: null });
    } catch {
      setState({ user: null, loading: false, error: null });
    }
  }, []);

  // On mount, try to refresh if we have a refresh token
  useEffect(() => {
    const callbackParams = new URLSearchParams(window.location.hash.slice(1));
    const callbackAccessToken = callbackParams.get("access_token");
    if (callbackAccessToken && callbackParams.get("token_type") === "bearer") {
      setAccessToken(callbackAccessToken);
      window.history.replaceState(
        window.history.state,
        "",
        `${window.location.pathname}${window.location.search}`
      );
      void loadUser();
      return;
    }

    const refreshToken = getRefreshToken();
    if (!refreshPromise) {
      refreshPromise = fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/auth/refresh`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        ...(refreshToken ? { body: JSON.stringify({ refresh_token: refreshToken }) } : {}),
      }).then(async (res) => {
        if (res.ok) {
          const data = await res.json();
          setTokens(data.access_token, data.refresh_token);
          return loadUser();
        } else {
          clearTokens();
          setState({ user: null, loading: false, error: null });
        }
      }).catch(() => {
        clearTokens();
        setState({ user: null, loading: false, error: null });
      }).finally(() => {
        refreshPromise = null;
      });
    }
  }, [loadUser]);

  const login = async (email: string, password: string) => {
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      const user = await authService.login(email, password);
      setState({ user, loading: false, error: null });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Login failed";
      setState((s) => ({ ...s, loading: false, error: message }));
      throw err;
    }
  };

  const register = async (email: string, password: string, name: string) => {
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      await authService.register(email, password, name);
      // Auto-login after register
      await login(email, password);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Registration failed";
      setState((s) => ({ ...s, loading: false, error: message }));
      throw err;
    }
  };

  const logout = async () => {
    const refreshToken = getRefreshToken();
    try {
      if (refreshToken) {
        await authService.logout(refreshToken);
      }
    } finally {
      clearTokens();
      setState({ user: null, loading: false, error: null });
    }
  };

  const refreshUser = async () => {
    try {
      const user = await usersService.getMe();
      setState((s) => ({ ...s, user }));
    } catch {}
  };

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
