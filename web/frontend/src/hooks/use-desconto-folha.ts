"use client";

import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  atualizarProcesso,
  criarCadastro,
  criarValor,
  desvincular,
  extrairResposta,
  getCadastro,
  listCadastros,
  lookupProcesso,
  matchAutomatico,
  removerCadastro,
  removerValor,
  vincular,
} from "@/lib/api/desconto-folha";
import type { CadastroInput, ValorInput } from "@/schemas/desconto-folha";

const KEY = ["ccd-desconto-folha"] as const;

export function useCadastros(params: { q?: string; page: number; size: number }) {
  return useQuery({
    queryKey: [...KEY, "lista", params],
    queryFn: () => listCadastros(params),
    placeholderData: keepPreviousData,
  });
}

export function useCadastro(id: number | null) {
  return useQuery({
    queryKey: [...KEY, "detalhe", id],
    queryFn: () => getCadastro(id as number),
    enabled: id != null,
  });
}

export function useLookupProcesso(processo: string) {
  return useQuery({
    queryKey: [...KEY, "lookup", processo],
    queryFn: () => lookupProcesso(processo),
    enabled: /^\d{1,6}\/\d{4}$/.test(processo),
    retry: false,
  });
}

function useInvalidar() {
  const qc = useQueryClient();
  return () => qc.invalidateQueries({ queryKey: KEY });
}

export function useCriarCadastro() {
  const invalidar = useInvalidar();
  return useMutation({
    mutationFn: (payload: CadastroInput) => criarCadastro(payload),
    onSuccess: invalidar,
  });
}

export function useRemoverCadastro() {
  const invalidar = useInvalidar();
  return useMutation({ mutationFn: (id: number) => removerCadastro(id), onSuccess: invalidar });
}

export function useAtualizarProcesso() {
  const invalidar = useInvalidar();
  return useMutation({ mutationFn: (id: number) => atualizarProcesso(id), onSuccess: invalidar });
}

export function useExtrairResposta() {
  return useMutation({ mutationFn: (id: number) => extrairResposta(id) });
}

export function useCriarValor(id: number) {
  const invalidar = useInvalidar();
  return useMutation({
    mutationFn: (payload: ValorInput) => criarValor(id, payload),
    onSuccess: invalidar,
  });
}

export function useRemoverValor(id: number) {
  const invalidar = useInvalidar();
  return useMutation({
    mutationFn: (idValor: number) => removerValor(id, idValor),
    onSuccess: invalidar,
  });
}

export function useVincular(id: number) {
  const invalidar = useInvalidar();
  return useMutation({
    mutationFn: (args: { idValor: number; idLancamento: number }) =>
      vincular(id, args.idValor, args.idLancamento),
    onSuccess: invalidar,
  });
}

export function useDesvincular(id: number) {
  const invalidar = useInvalidar();
  return useMutation({
    mutationFn: (idValor: number) => desvincular(id, idValor),
    onSuccess: invalidar,
  });
}

export function useMatchAutomatico(id: number) {
  const invalidar = useInvalidar();
  return useMutation({ mutationFn: () => matchAutomatico(id), onSuccess: invalidar });
}
