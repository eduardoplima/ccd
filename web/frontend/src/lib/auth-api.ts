import { apiClient } from "./api-client";
import { clearTokens, getRefreshToken, setAccessToken, setRefreshToken } from "./auth";
import type { LoginInput, TokenPair, UserOut } from "@/schemas/auth";

export async function login(input: LoginInput): Promise<TokenPair> {
  const { data } = await apiClient.post<TokenPair>("/api/v1/auth/login", input);
  setAccessToken(data.access_token);
  setRefreshToken(data.refresh_token);
  return data;
}

export async function logout(): Promise<void> {
  const refresh = getRefreshToken();
  if (refresh) {
    try {
      await apiClient.post("/api/v1/auth/logout", { refresh_token: refresh });
    } catch {
      // best-effort
    }
  }
  clearTokens();
}

export async function me(): Promise<UserOut> {
  const { data } = await apiClient.get<UserOut>("/api/v1/auth/me");
  return data;
}
