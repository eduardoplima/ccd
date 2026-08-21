"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  deleteWikiOverride,
  getWikiPage,
  listWikiPages,
  saveWikiPage,
  searchWiki,
} from "@/lib/api/wiki";

export function useWikiPages() {
  return useQuery({
    queryKey: ["wiki", "pages"],
    queryFn: listWikiPages,
    staleTime: 60_000,
  });
}

export function useWikiPage(slug: string) {
  return useQuery({
    queryKey: ["wiki", "page", slug],
    queryFn: () => getWikiPage(slug),
    staleTime: 60_000,
    retry: false,
  });
}

export function useWikiSearch(q: string) {
  return useQuery({
    queryKey: ["wiki", "search", q],
    queryFn: () => searchWiki(q),
    enabled: q.trim().length >= 2,
    staleTime: 30_000,
  });
}

export function useSaveWikiPage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ slug, content }: { slug: string; content: string }) =>
      saveWikiPage(slug, content),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["wiki"] }),
  });
}

export function useDeleteWikiOverride() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (slug: string) => deleteWikiOverride(slug),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["wiki"] }),
  });
}
