"use client";

import { useMutation, useQuery } from "@tanstack/react-query";

import { gerarDescontoFolha, listCandidatosDescontoFolha } from "@/lib/api/ccd-desconto-folha";

export function useCandidatosDescontoFolha(todos: boolean) {
  return useQuery({
    queryKey: ["ccd-desconto-folha-candidatos", todos],
    queryFn: () => listCandidatosDescontoFolha(todos),
    staleTime: 30_000,
  });
}

export function useGerarDescontoFolha() {
  return useMutation({
    mutationFn: (processos: string[]) => gerarDescontoFolha(processos),
  });
}
