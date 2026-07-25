import axios, {
  type AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from "axios";

import { tokenStorage } from "@/utils/tokenStorage";
import type { ApiResponse } from "@/types/api";
import type { TokenPair } from "@/types/auth";

/**
 * Centralized Axios instance for all backend API calls.
 *
 * Every request/response interceptor (auth headers, error normalization,
 * refresh-token handling, etc.) is attached here — feature-level services
 * should never construct their own axios instance.
 */
const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30_000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Separate, un-intercepted instance used only for the refresh call itself,
// so a failed refresh never recursively triggers the response interceptor.
const refreshClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30_000,
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokenStorage.getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/** Notified when the session can no longer be refreshed (logout everywhere). */
let onSessionExpired: (() => void) | null = null;
export function setOnSessionExpired(callback: (() => void) | null): void {
  onSessionExpired = callback;
}

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

let isRefreshing = false;
let pendingRequests: Array<(token: string | null) => void> = [];

function resolvePendingRequests(token: string | null): void {
  pendingRequests.forEach((callback) => callback(token));
  pendingRequests = [];
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetryableRequestConfig | undefined;
    const status = error.response?.status;

    const isAuthEndpoint = originalRequest?.url?.includes("/auth/login") ||
      originalRequest?.url?.includes("/auth/register") ||
      originalRequest?.url?.includes("/auth/refresh");

    if (status !== 401 || !originalRequest || originalRequest._retry || isAuthEndpoint) {
      return Promise.reject(error);
    }

    const refreshToken = tokenStorage.getRefreshToken();
    if (!refreshToken) {
      tokenStorage.clear();
      onSessionExpired?.();
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    if (isRefreshing) {
      // Queue this request until the in-flight refresh resolves.
      return new Promise((resolve, reject) => {
        pendingRequests.push((newToken) => {
          if (!newToken) {
            reject(error);
            return;
          }
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          resolve(apiClient(originalRequest));
        });
      });
    }

    isRefreshing = true;
    try {
      const { data } = await refreshClient.post<ApiResponse<TokenPair>>("/auth/refresh", {
        refresh_token: refreshToken,
      });
      const tokens = data.data;
      if (!tokens) {
        throw new Error("Refresh response did not include tokens.");
      }
      tokenStorage.setTokens(tokens.access_token, tokens.refresh_token);
      resolvePendingRequests(tokens.access_token);
      originalRequest.headers.Authorization = `Bearer ${tokens.access_token}`;
      return apiClient(originalRequest);
    } catch (refreshError) {
      resolvePendingRequests(null);
      tokenStorage.clear();
      onSessionExpired?.();
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  },
);
