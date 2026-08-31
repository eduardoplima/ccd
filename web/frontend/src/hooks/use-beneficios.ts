"use client";

import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  atualizarBeneficio,
  criarBeneficio,
  deletarBeneficio,
  dispararDeteccaoBeneficios,
  exportarBeneficios,
  getBeneficiosDominios,
  getBeneficiosResumo,
  listBeneficios,
  transicionarBeneficio,
  type BeneficiosFilters,
} from "@/lib/api/beneficios";
import type { BeneficioPayload, StatusBeneficio } from "@/schemas/beneficios";

const KEY = "ccd-beneficios";

export function useBeneficios(filters: BeneficiosFilters) {
  return useQuery({
    queryKey: [KEY, "lista", filters],
    queryFn: () => listBeneficios(filters),
    staleTime: 30_000,
    placeholderData: keepPreviousData,
  });
}

export function useBeneficiosResumo() {
  return useQuery({
    queryKey: [KEY, "resumo"],
    queryFn: getBeneficiosResumo,
    staleTime: 30_000,
  });
}

export function useBeneficiosDominios() {
  return useQuery({
    queryKey: [KEY, "dominios"],
    queryFn: getBeneficiosDominios,
    staleTime: 30 * 60_000,
  });
}

export function useCriarBeneficio() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: BeneficioPayload) => criarBeneficio(payload),
    onSuccess: () => void qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useAtualizarBeneficio() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: BeneficioPayload }) =>
      atualizarBeneficio(id, payload),
    onSuccess: () => void qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useDeletarBeneficio() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deletarBeneficio(id),
    onSuccess: () => void qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useTransicionarBeneficio() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: StatusBeneficio }) =>
      transicionarBeneficio(id, status),
    onSuccess: () => void qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useExportarBeneficios() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      formato,
      ids,
      marcarEnviado,
    }: {
      formato: "xlsx" | "json";
      ids?: number[];
      marcarEnviado?: boolean;
    }) => exportarBeneficios(formato, ids, marcarEnviado),
    onSuccess: () => void qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useDispararDeteccaoBeneficios() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: dispararDeteccaoBeneficios,
    onSuccess: () => void qc.invalidateQueries({ queryKey: [KEY] }),
  });
}
