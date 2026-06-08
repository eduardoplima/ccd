"use client";

import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  cancelarJob,
  deletarFinalizados,
  deletarJob,
  disparaConciliar,
  disparaConciliarTodos,
  disparaParseExtratos,
  listJobs,
  uploadExtrato,
} from "@/lib/api/jobs";

export function useJobs(page: number, size: number) {
  return useQuery({
    queryKey: ["jobs", page, size],
    queryFn: () => listJobs(page, size),
    staleTime: 5_000,
    refetchInterval: 5_000,
    placeholderData: keepPreviousData,
  });
}

export function useDispararParse() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: disparaParseExtratos,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["jobs"] }),
  });
}

export function useDispararConciliar() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ ano, mes }: { ano: number; mes: number }) => disparaConciliar(ano, mes),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["jobs"] }),
  });
}

export function useDispararConciliarTodos() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (ano: number) => disparaConciliarTodos(ano),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["jobs"] }),
  });
}

export function useUploadExtrato() {
  return useMutation({
    mutationFn: ({ conta, periodo, arquivo }: { conta: string; periodo: string; arquivo: File }) =>
      uploadExtrato(conta, periodo, arquivo),
  });
}

export function useCancelarJob() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => cancelarJob(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["jobs"] }),
  });
}

export function useDeletarJob() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deletarJob(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["jobs"] }),
  });
}

export function useDeletarFinalizados() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (tipo?: string) => deletarFinalizados(tipo),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["jobs"] }),
  });
}
