"use client";

import { useQuery } from "@tanstack/react-query";

import { me } from "@/lib/auth-api";

export function useCurrentUser() {
  return useQuery({
    queryKey: ["auth", "me"],
    queryFn: me,
    retry: 0,
    staleTime: 60_000,
  });
}
