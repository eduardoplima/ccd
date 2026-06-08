"use client";

import { useQuery } from "@tanstack/react-query";

import {
  getFasesDebitosNotificados,
  getFasesEnviados,
  getFasesResumo,
  getFasesTotais,
} from "@/lib/api/fases";

export function useFasesResumo(cpfcnpj: string | null) {
  return useQuery({
    queryKey: ["fases", "resumo", cpfcnpj],
    queryFn: () => getFasesResumo(cpfcnpj!),
    enabled: cpfcnpj !== null,
    staleTime: 30_000,
  });
}

export function useFasesTotais(cpfcnpj: string | null, enabled: boolean) {
  return useQuery({
    queryKey: ["fases", "totais", cpfcnpj],
    queryFn: () => getFasesTotais(cpfcnpj!),
    enabled: enabled && cpfcnpj !== null,
    // valor atualizado vem de UDF lenta — vale cachear mais
    staleTime: 5 * 60_000,
  });
}

export function useFasesDebitosNotificados(cpfcnpj: string | null, enabled: boolean) {
  return useQuery({
    queryKey: ["fases", "debitos-notificados", cpfcnpj],
    queryFn: () => getFasesDebitosNotificados(cpfcnpj!),
    enabled: enabled && cpfcnpj !== null,
    staleTime: 5 * 60_000,
  });
}

export function useFasesEnviados(cpfcnpj: string | null, enabled: boolean) {
  return useQuery({
    queryKey: ["fases", "enviados", cpfcnpj],
    queryFn: () => getFasesEnviados(cpfcnpj!),
    enabled: enabled && cpfcnpj !== null,
    staleTime: 60_000,
  });
}
