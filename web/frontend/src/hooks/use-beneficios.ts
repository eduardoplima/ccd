"use client";

import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  dispararDeteccaoBeneficios,
  exportarBeneficios,
  getBeneficiosDominios,
  getBeneficiosResumo,
  getBeneficiosSerie,
  listBeneficios,
  type BeneficiosFilters,
  type BeneficiosRecorte,
} from "@/lib/api/beneficios";

const KEY = "ccd-beneficios";

export function useBeneficios(filters: BeneficiosFilters) {
  return useQuery({
    queryKey: [KEY, "lista", filters],
    queryFn: () => listBeneficios(filters),
    staleTime: 30_000,
    placeholderData: keepPreviousData,
  });
}

export function useBeneficiosResumo(recorte: BeneficiosRecorte = {}) {
  return useQuery({
    queryKey: [KEY, "resumo", recorte],
    queryFn: () => getBeneficiosResumo(recorte),
    staleTime: 30_000,
  });
}

export function useBeneficiosSerie() {
  return useQuery({
    queryKey: [KEY, "serie"],
    queryFn: getBeneficiosSerie,
    staleTime: 5 * 60_000,
  });
}

export function useBeneficiosDominios() {
  return useQuery({
    queryKey: [KEY, "dominios"],
    queryFn: getBeneficiosDominios,
    staleTime: 30 * 60_000,
  });
}

export function useExportarBeneficios() {
  return useMutation({
    mutationFn: ({ formato, recorte }: { formato: "csv" | "json"; recorte?: BeneficiosRecorte }) =>
      exportarBeneficios(formato, recorte),
  });
}

export function useDispararDeteccaoBeneficios() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: dispararDeteccaoBeneficios,
    onSuccess: () => void qc.invalidateQueries({ queryKey: [KEY] }),
  });
}
