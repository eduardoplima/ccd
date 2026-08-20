"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  FiltroFila,
  getDivergenciaDetail,
  getDivergencias,
  getDocumento,
  getProgresso,
  listDocumentos,
  salvarAnotacao,
} from "@/lib/dataset-api";
import { Span } from "@/schemas/dataset";

export const datasetKeys = {
  all: ["dataset"] as const,
  documentos: (args: Record<string, unknown>) => ["dataset", "documentos", args] as const,
  documento: (id: number) => ["dataset", "documentos", id] as const,
  progresso: () => ["dataset", "progresso"] as const,
  divergencias: () => ["dataset", "divergencias"] as const,
  divergencia: (id: number) => ["dataset", "divergencias", id] as const,
};

export function useDocumentos(
  args: {
    page?: number;
    pageSize?: number;
    status?: string;
    origem?: string;
    ano?: number;
    comEntidades?: boolean;
    semAtosPessoal?: boolean;
  } = {},
) {
  const page = args.page ?? 1;
  const pageSize = args.pageSize ?? 20;
  const params = { page, pageSize, ...args };
  return useQuery({
    queryKey: datasetKeys.documentos(params),
    queryFn: () => listDocumentos(params),
  });
}

export function useDocumento(id: number, filtro: FiltroFila = {}) {
  return useQuery({
    queryKey: [...datasetKeys.documento(id), filtro],
    queryFn: () => getDocumento(id, filtro),
    enabled: Number.isFinite(id),
  });
}

export function useProgresso() {
  return useQuery({
    queryKey: datasetKeys.progresso(),
    queryFn: getProgresso,
    staleTime: 5_000,
  });
}

export function useDivergencias() {
  return useQuery({
    queryKey: datasetKeys.divergencias(),
    queryFn: getDivergencias,
    staleTime: 60_000,
  });
}

export function useDivergenciaDetail(id: number | null) {
  return useQuery({
    queryKey: datasetKeys.divergencia(id ?? -1),
    queryFn: () => getDivergenciaDetail(id!),
    enabled: id != null,
  });
}

export function useSalvarAnotacao(id: number, filtro: FiltroFila = {}) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: { spans: Span[]; status: "pending" | "done" }) =>
      salvarAnotacao(id, body, filtro),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: datasetKeys.documento(id) });
      queryClient.invalidateQueries({ queryKey: ["dataset", "documentos"] });
      queryClient.invalidateQueries({ queryKey: datasetKeys.progresso() });
    },
  });
}
