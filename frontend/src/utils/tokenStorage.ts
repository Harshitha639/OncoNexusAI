/**
 * Centralized JWT persistence (localStorage).
 *
 * Kept as the single module that touches `localStorage` for tokens so
 * the storage mechanism can be swapped later (e.g. httpOnly cookies)
 * without touching call sites.
 */

const ACCESS_TOKEN_KEY = "onconexus.access_token";
const REFRESH_TOKEN_KEY = "onconexus.refresh_token";

export const tokenStorage = {
  getAccessToken(): string | null {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  },
  getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  },
  setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  },
  clear(): void {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  },
};
