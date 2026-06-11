const REFRESH_TOKEN_KEY = "frap-controle:refresh-token";

let accessTokenInMemory: string | null = null;

export function setAccessToken(token: string | null): void {
  accessTokenInMemory = token;
}

export function getAccessToken(): string | null {
  return accessTokenInMemory;
}

export function setRefreshToken(token: string | null): void {
  if (typeof window === "undefined") return;
  if (token === null) {
    window.localStorage.removeItem(REFRESH_TOKEN_KEY);
  } else {
    window.localStorage.setItem(REFRESH_TOKEN_KEY, token);
  }
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function clearTokens(): void {
  setAccessToken(null);
  setRefreshToken(null);
}

export function hasSession(): boolean {
  return getAccessToken() !== null || getRefreshToken() !== null;
}
