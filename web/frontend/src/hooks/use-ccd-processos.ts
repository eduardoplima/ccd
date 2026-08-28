"use client";

import { keepPreviousData, useQuery } from "@tanstack/react-query";

import {
  getFiltrosCCD,
  listPrescricaoCCD,
  listProcessosCCD,
  type ProcessoCCDFilters,
} from "@/lib/api/ccd";

export function useProcessosCCD(filters: ProcessoCCDFilters) {
  return useQuery({
    queryKey: ["ccd-processos", filters],
    queryFn: () => listProcessosCCD(filters),
    staleTime: 30_000,
    placeholderData: keepPreviousData,
  });
}

export function usePrescricaoCCD(ocultarPermanencia: boolean) {
  return useQuery({
    queryKey: ["ccd-prescricao", ocultarPermanencia],
    queryFn: () => listPrescricaoCCD(ocultarPermanencia),
    staleTime: 60_000,
  });
}

export function useFiltrosCCD() {
  return useQuery({
    queryKey: ["ccd-filtros"],
    queryFn: getFiltrosCCD,
    staleTime: 5 * 60_000,
  });
}
