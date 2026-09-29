"use client";

import { useQuery } from "@tanstack/react-query";

import { getPainelIndicadores } from "@/lib/api/indicadores";

export function usePainelIndicadores() {
  return useQuery({
    queryKey: ["ccd-indicadores"],
    queryFn: getPainelIndicadores,
    staleTime: 10 * 60_000,
  });
}
