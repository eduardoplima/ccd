"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { getDocumento, getProgresso, listDocumentos, salvarAnotacao } from "@/lib/dataset-api";
import { Span } from "@/schemas/dataset";

export const datasetKeys = {
  all: ["dataset"] as const,
  documentos: (args: Record<string, unknown>) => ["dataset", "documentos", args] as const,
  documento: (id: number) => ["dataset", "documentos", id] as const,
  progresso: () => ["dataset", "progresso"] as const,
};

export function useDocumentos(
  args: {
    page?: number;
    pageSize?: number;
    status?: string;
    ano?: number;
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

export function useDocumento(id: number) {
  return useQuery({
    queryKey: datasetKeys.documento(id),
    queryFn: () => getDocumento(id),
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

export function useSalvarAnotacao(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: { spans: Span[]; status: "pending" | "done" }) => salvarAnotacao(id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: datasetKeys.documento(id) });
      queryClient.invalidateQueries({ queryKey: ["dataset", "documentos"] });
      queryClient.invalidateQueries({ queryKey: datasetKeys.progresso() });
    },
  });
}
