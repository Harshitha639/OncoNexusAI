import { apiClient } from "@/services/apiClient";
import type { ApiResponse } from "@/types/api";
import type { LoginPayload, RegisterPayload, TokenPair, User } from "@/types/auth";

export async function registerUser(payload: RegisterPayload): Promise<User> {
  const { data } = await apiClient.post<ApiResponse<User>>("/auth/register", payload);
  if (!data.data) {
    throw new Error("Registration response did not include a user.");
  }
  return data.data;
}

export async function loginUser(payload: LoginPayload): Promise<TokenPair> {
  const { data } = await apiClient.post<ApiResponse<TokenPair>>("/auth/login", payload);
  if (!data.data) {
    throw new Error("Login response did not include tokens.");
  }
  return data.data;
}

export async function refreshTokens(refreshToken: string): Promise<TokenPair> {
  const { data } = await apiClient.post<ApiResponse<TokenPair>>("/auth/refresh", {
    refresh_token: refreshToken,
  });
  if (!data.data) {
    throw new Error("Refresh response did not include tokens.");
  }
  return data.data;
}

export async function logoutUser(refreshToken: string): Promise<void> {
  await apiClient.post("/auth/logout", { refresh_token: refreshToken });
}

export async function fetchCurrentUser(): Promise<User> {
  const { data } = await apiClient.get<ApiResponse<User>>("/users/me");
  if (!data.data) {
    throw new Error("Response did not include a user profile.");
  }
  return data.data;
}
