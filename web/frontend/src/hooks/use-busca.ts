"use client";

import { keepPreviousData, useQuery } from "@tanstack/react-query";

import { buscarDebitosPessoa, buscarPessoas, buscarProcesso } from "@/lib/api/busca";

export function useBuscarPessoas(q: string, page: number, size: number, enabled: boolean) {
  return useQuery({
    queryKey: ["busca", "pessoas", q, page, size],
    queryFn: () => buscarPessoas(q, page, size),
    enabled,
    staleTime: 30_000,
    placeholderData: keepPreviousData,
  });
}

export function useBuscarProcesso(
  numero: string,
  ano: string,
  tipo: "origem" | "execucao",
  enabled: boolean,
) {
  return useQuery({
    queryKey: ["busca", "processo", numero, ano, tipo],
    queryFn: () => buscarProcesso(numero, ano, tipo),
    enabled,
    staleTime: 30_000,
  });
}

export function useBuscarDebitosPessoa(
  cpfcnpj: string | null,
  idProcesso: number | undefined,
  enabled: boolean,
) {
  return useQuery({
    queryKey: ["busca", "debitos-pessoa", cpfcnpj, idProcesso],
    queryFn: () => buscarDebitosPessoa(cpfcnpj!, idProcesso),
    enabled: enabled && cpfcnpj !== null,
    staleTime: 30_000,
  });
}
