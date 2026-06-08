"use client";

import { keepPreviousData, useQuery } from "@tanstack/react-query";

import {
  listMatchesDescontoFolha,
  listMatchesGuia,
  listMatchesOB,
  listMatchesPessoa,
  type MatchesFilters,
} from "@/lib/api/matches";

export function useMatchesOB(filters: MatchesFilters, enabled = true) {
  return useQuery({
    queryKey: ["matches", "ob", filters],
    queryFn: () => listMatchesOB(filters),
    enabled,
    staleTime: 30_000,
    placeholderData: keepPreviousData,
  });
}

export function useMatchesPessoa(filters: MatchesFilters, enabled = true) {
  return useQuery({
    queryKey: ["matches", "pessoa", filters],
    queryFn: () => listMatchesPessoa(filters),
    enabled,
    staleTime: 30_000,
    placeholderData: keepPreviousData,
  });
}

export function useMatchesGuia(filters: MatchesFilters, enabled = true) {
  return useQuery({
    queryKey: ["matches", "guia", filters],
    queryFn: () => listMatchesGuia(filters),
    enabled,
    staleTime: 30_000,
    placeholderData: keepPreviousData,
  });
}

export function useMatchesDescontoFolha(filters: MatchesFilters, enabled = true) {
  return useQuery({
    queryKey: ["matches", "desconto-folha", filters],
    queryFn: () => listMatchesDescontoFolha(filters),
    enabled,
    staleTime: 30_000,
    placeholderData: keepPreviousData,
  });
}
