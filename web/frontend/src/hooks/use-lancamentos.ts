"use client";

import { keepPreviousData, useQuery } from "@tanstack/react-query";

import { listLancamentos, type LancamentoFilters } from "@/lib/api/lancamentos";

export function useLancamentos(filters: LancamentoFilters) {
  return useQuery({
    queryKey: ["lancamentos", filters],
    queryFn: () => listLancamentos(filters),
    staleTime: 30_000,
    placeholderData: keepPreviousData,
  });
}
