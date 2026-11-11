"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { getRemocoes, postRemocao } from "@/lib/remocoes-api";
import { RemocaoPayload } from "@/schemas/remocoes";

export const remocoesKeys = {
  processo: (processo: string) => ["cgad-remocoes", processo] as const,
};

export function useRemocoes(processo: string | null) {
  return useQuery({
    queryKey: remocoesKeys.processo(processo ?? ""),
    queryFn: () => getRemocoes(processo as string),
    enabled: !!processo,
    retry: false,
  });
}

export function useRemover(processo: string | null) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: RemocaoPayload) => postRemocao(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: remocoesKeys.processo(processo ?? "") });
      // painéis e listas do CGAD deixam de contar o item
      qc.invalidateQueries({ queryKey: ["dashboards"] });
      qc.invalidateQueries({ queryKey: ["multas-nao-cominadas"] });
    },
  });
}
