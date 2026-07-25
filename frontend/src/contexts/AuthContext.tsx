import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { setOnSessionExpired } from "@/services/apiClient";
import {
  fetchCurrentUser,
  loginUser,
  logoutUser,
  registerUser,
} from "@/services/authService";
import { tokenStorage } from "@/utils/tokenStorage";
import type { LoginPayload, RegisterPayload, User } from "@/types/auth";

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isInitializing: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

/**
 * Provides authentication state (current user + JWT lifecycle) to the
 * whole app. Wrap the router with this once, near the root.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);

  const clearSession = useCallback(() => {
    tokenStorage.clear();
    setUser(null);
  }, []);

  useEffect(() => {
    // If the refresh-token flow ever fails irrecoverably (e.g. refresh
    // token revoked/expired), drop back to a logged-out state everywhere.
    setOnSessionExpired(() => clearSession());
    return () => setOnSessionExpired(null);
  }, [clearSession]);

  useEffect(() => {
    async function restoreSession() {
      const accessToken = tokenStorage.getAccessToken();
      if (!accessToken) {
        setIsInitializing(false);
        return;
      }
      try {
        const currentUser = await fetchCurrentUser();
        setUser(currentUser);
      } catch {
        clearSession();
      } finally {
        setIsInitializing(false);
      }
    }
    restoreSession();
  }, [clearSession]);

  const login = useCallback(async (payload: LoginPayload) => {
    const tokens = await loginUser(payload);
    tokenStorage.setTokens(tokens.access_token, tokens.refresh_token);
    const currentUser = await fetchCurrentUser();
    setUser(currentUser);
  }, []);

  const register = useCallback(async (payload: RegisterPayload) => {
    await registerUser(payload);
    // Registration does not auto-issue tokens — the user logs in next.
  }, []);

  const logout = useCallback(async () => {
    const refreshToken = tokenStorage.getRefreshToken();
    try {
      if (refreshToken) {
        await logoutUser(refreshToken);
      }
    } finally {
      clearSession();
    }
  }, [clearSession]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: user !== null,
      isInitializing,
      login,
      register,
      logout,
    }),
    [user, isInitializing, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider.");
  }
  return context;
}
