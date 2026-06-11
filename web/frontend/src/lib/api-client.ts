import axios, { AxiosError, type AxiosRequestConfig, type InternalAxiosRequestConfig } from "axios";

import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  setAccessToken,
  setRefreshToken,
} from "./auth";

const baseURL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const apiClient = axios.create({ baseURL, withCredentials: false });

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refresh = getRefreshToken();
  if (!refresh) return null;
  try {
    const response = await axios.post(
      `${baseURL}/api/v1/auth/refresh`,
      { refresh_token: refresh },
      { headers: { "Content-Type": "application/json" } },
    );
    const { access_token, refresh_token } = response.data as {
      access_token: string;
      refresh_token: string;
    };
    setAccessToken(access_token);
    setRefreshToken(refresh_token);
    return access_token;
  } catch {
    clearTokens();
    if (typeof window !== "undefined") {
      window.location.assign("/login");
    }
    return null;
  }
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as
      | (InternalAxiosRequestConfig & { _retry?: boolean })
      | undefined;
    if (!original || error.response?.status !== 401) {
      return Promise.reject(error);
    }
    const url = original.url ?? "";
    if (url.includes("/auth/login") || url.includes("/auth/refresh")) {
      return Promise.reject(error);
    }
    if (original._retry) {
      return Promise.reject(error);
    }
    original._retry = true;
    if (!refreshPromise) {
      refreshPromise = refreshAccessToken().finally(() => {
        refreshPromise = null;
      });
    }
    const newToken = await refreshPromise;
    if (!newToken) {
      return Promise.reject(error);
    }
    if (original.headers) {
      original.headers.Authorization = `Bearer ${newToken}`;
    }
    return apiClient.request(original as AxiosRequestConfig);
  },
);
