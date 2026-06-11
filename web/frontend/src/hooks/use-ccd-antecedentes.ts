"use client";

import { useMutation, useQuery } from "@tanstack/react-query";

import {
  gerarAntecedentes,
  listCandidatosAntecedentes,
} from "@/lib/api/ccd-antecedentes";

export function useCandidatosAntecedentes(todos: boolean) {
  return useQuery({
    queryKey: ["ccd-antecedentes-candidatos", todos],
    queryFn: () => listCandidatosAntecedentes(todos),
    staleTime: 30_000,
  });
}

export function useGerarAntecedentes() {
  return useMutation({
    mutationFn: (processos: string[]) => gerarAntecedentes(processos),
  });
}
