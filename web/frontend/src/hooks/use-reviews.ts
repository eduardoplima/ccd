"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  approveDecisao,
  claimDecisao,
  claimLoteDecisoes,
  getDecisao,
  getDecisaoTexto,
  listAwaitingDispatch,
  listDecisoes,
  listOrgaos,
  releaseDecisao,
} from "@/lib/reviews-api";
import { useCurrentUser } from "@/hooks/use-current-user";
import { ClaimResponse, DecisaoDetail, DecisaoReviewPayload } from "@/schemas/review";

export const reviewKeys = {
  all: ["reviews"] as const,
  list: (args: {
    page: number;
    pageSize: number;
    processo?: string;
    listaCompleta?: boolean;
    reserva?: "pendentes" | "minhas";
  }) => ["reviews", "decisoes", args] as const,
  detail: (id: number) => ["reviews", "decisao", id] as const,
  texto: (id: number) => ["reviews", "decisao-texto", id] as const,
  awaitingDispatch: (args: { page: number; pageSize: number }) =>
    ["reviews", "awaiting-dispatch", args] as const,
  orgaos: ["reviews", "orgaos"] as const,
};

export function useOrgaos() {
  return useQuery({
    queryKey: reviewKeys.orgaos,
    queryFn: listOrgaos,
    staleTime: Infinity,
    gcTime: 60 * 60_000,
  });
}

export function useDecisoes({
  page = 1,
  pageSize = 20,
  processo,
  listaCompleta,
  reserva,
  enabled = true,
}: {
  page?: number;
  pageSize?: number;
  processo?: string;
  listaCompleta?: boolean;
  reserva?: "pendentes" | "minhas";
  enabled?: boolean;
} = {}) {
  return useQuery({
    queryKey: reviewKeys.list({ page, pageSize, processo, listaCompleta, reserva }),
    queryFn: () => listDecisoes({ page, pageSize, processo, listaCompleta, reserva }),
    enabled,
  });
}

export function useAwaitingDispatch({
  page = 1,
  pageSize = 20,
  enabled = true,
}: {
  page?: number;
  pageSize?: number;
  enabled?: boolean;
} = {}) {
  return useQuery({
    queryKey: reviewKeys.awaitingDispatch({ page, pageSize }),
    queryFn: () => listAwaitingDispatch({ page, pageSize }),
    enabled,
  });
}

export function useDecisao(id: number) {
  return useQuery({
    queryKey: reviewKeys.detail(id),
    queryFn: () => getDecisao(id),
  });
}

export function useDecisaoTexto(id: number) {
  return useQuery({
    queryKey: reviewKeys.texto(id),
    queryFn: () => getDecisaoTexto(id),
    // Texto can be slow (MSSQL); don't refetch automatically.
    staleTime: 5 * 60_000,
    gcTime: 10 * 60_000,
    retry: 1,
  });
}

export function useClaim(id: number) {
  const queryClient = useQueryClient();
  const { data: me } = useCurrentUser();

  return useMutation({
    mutationFn: () => claimDecisao(id),
    onMutate: async () => {
      // Optimistic: paint ourselves as the claimant immediately so the
      // banner doesn't flash.
      const prev = queryClient.getQueryData<DecisaoDetail>(reviewKeys.detail(id));
      // No cached detail yet means the initial load is still in flight (the
      // page fires claim() on mount). Cancelling it here would strand the
      // detail query in a cancelled-pending state with no data — leaving the
      // page on "Carregando decisão..." forever in production builds (dev only
      // survives because StrictMode's double-mount refetches). Skip the
      // optimistic step entirely; the claim's onSuccess fills claimed_by.
      if (!prev || !me) return { prev };
      await queryClient.cancelQueries({
        queryKey: reviewKeys.detail(id),
      });
      const now = new Date().toISOString();
      queryClient.setQueryData<DecisaoDetail>(reviewKeys.detail(id), {
        ...prev,
        claimed_by: me.login,
        claimed_at: now,
      });
      return { prev };
    },
    onError: (_err, _vars, context) => {
      if (context?.prev) {
        queryClient.setQueryData(reviewKeys.detail(id), context.prev);
      }
    },
    onSuccess: (claim: ClaimResponse) => {
      const prev = queryClient.getQueryData<DecisaoDetail>(reviewKeys.detail(id));
      if (prev) {
        queryClient.setQueryData<DecisaoDetail>(reviewKeys.detail(id), {
          ...prev,
          claimed_by: claim.claimed_by,
          claimed_at: claim.claimed_at,
        });
      }
    },
  });
}

export function useClaimLote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (quantidade: number) => claimLoteDecisoes(quantidade),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: reviewKeys.all });
    },
  });
}

export function useReleaseFromList() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => releaseDecisao(id),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: reviewKeys.all });
    },
  });
}

export function useRelease(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => releaseDecisao(id),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: reviewKeys.all });
    },
  });
}

export function useApproveDecisao(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: DecisaoReviewPayload) => approveDecisao(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: reviewKeys.all });
    },
  });
}
