"use client";

import { useQuery } from "@tanstack/react-query";

import { getLancamento } from "@/lib/api/lancamentos";

export function useLancamento(id: number | null) {
  return useQuery({
    queryKey: ["lancamento", id],
    queryFn: () => getLancamento(id!),
    enabled: id !== null,
    staleTime: 60_000,
  });
}
