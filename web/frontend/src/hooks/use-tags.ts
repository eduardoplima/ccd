"use client";

import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  atualizarTag,
  extrairTag,
  getTag,
  listTags,
  removerTag,
  salvarObrigacoes,
} from "@/lib/api/tags";
import type { ExtrairInput, ObrigacaoInput, TagPatch } from "@/schemas/tags";

const KEY = ["ccd-tags"] as const;

export function useTags(q: string) {
  return useQuery({
    queryKey: [...KEY, "lista", q],
    queryFn: () => listTags(q),
    placeholderData: keepPreviousData,
  });
}

export function useTag(id: number | null) {
  return useQuery({
    queryKey: [...KEY, "detalhe", id],
    queryFn: () => getTag(id as number),
    enabled: id != null,
  });
}

function useInvalidar() {
  const qc = useQueryClient();
  return () => qc.invalidateQueries({ queryKey: KEY });
}

export function useExtrairTag() {
  return useMutation({ mutationFn: (payload: ExtrairInput) => extrairTag(payload) });
}

export function useAtualizarTag(id: number) {
  const invalidar = useInvalidar();
  return useMutation({
    mutationFn: (patch: TagPatch) => atualizarTag(id, patch),
    onSuccess: invalidar,
  });
}

export function useSalvarObrigacoes(id: number) {
  const invalidar = useInvalidar();
  return useMutation({
    mutationFn: (obrigacoes: ObrigacaoInput[]) => salvarObrigacoes(id, obrigacoes),
    onSuccess: invalidar,
  });
}

export function useRemoverTag() {
  const invalidar = useInvalidar();
  return useMutation({ mutationFn: (id: number) => removerTag(id), onSuccess: invalidar });
}
