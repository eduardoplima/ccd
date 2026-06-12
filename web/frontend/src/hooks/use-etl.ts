"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import {
  abortExtracao,
  deleteExtracao,
  getExtracao,
  listDecisoes,
  listEventos,
  listExtracoes,
  triggerExtraction,
} from "@/lib/etl-api";
import {
  ExtracaoEventoOut,
  ExtracaoListFilters,
  ExtracaoOut,
  ExtractionTriggerRequest,
} from "@/schemas/etl";

export const etlKeys = {
  all: ["etl"] as const,
  extracoes: (args: { page: number; pageSize: number; filters?: ExtracaoListFilters }) =>
    ["etl", "extracoes", args] as const,
  extracao: (id: number) => ["etl", "extracao", id] as const,
  eventos: (id: number) => ["etl", "extracao", id, "eventos"] as const,
  decisoes: (id: number, args: { page: number; pageSize: number }) =>
    ["etl", "extracao", id, "decisoes", args] as const,
};

type ListArgs = {
  page?: number;
  pageSize?: number;
  filters?: ExtracaoListFilters;
};

export function useExtracoes({ page = 1, pageSize = 20, filters }: ListArgs = {}) {
  return useQuery({
    queryKey: etlKeys.extracoes({ page, pageSize, filters }),
    queryFn: () => listExtracoes({ page, pageSize, filters }),
    // Auto-refresh while any row on the page is still active. Stops on its
    // own once everything is done/error — no continuous polling.
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data) return false;
      const hasActive = data.items.some(
        (item) => item.status === "queued" || item.status === "running",
      );
      return hasActive ? 3000 : false;
    },
    refetchIntervalInBackground: false,
  });
}

export function useTriggerExtraction() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: ["etl", "trigger"],
    mutationFn: (body: ExtractionTriggerRequest) => triggerExtraction(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: etlKeys.all });
    },
  });
}

export function useAbortExtracao() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: ["etl", "abort"],
    mutationFn: (id: number) => abortExtracao(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: etlKeys.all });
    },
  });
}

export function useDeleteExtracao() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: ["etl", "delete"],
    mutationFn: (id: number) => deleteExtracao(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: etlKeys.all });
    },
  });
}

/** Polls one ``Extracao`` row every 3s while the run is queued or running.
 * Stops once the row reaches ``done`` or ``error``.
 */
export function useExtracao(id: number | null) {
  return useQuery<ExtracaoOut>({
    queryKey: id !== null ? etlKeys.extracao(id) : ["etl", "extracao", "null"],
    queryFn: () => getExtracao(id as number),
    enabled: id !== null,
    refetchInterval: (query) => {
      const data = query.state.data as ExtracaoOut | undefined;
      if (!data) return 3000;
      return data.status === "queued" || data.status === "running" ? 1500 : false;
    },
    refetchIntervalInBackground: false,
  });
}

/**
 * Live feed of activity events for one extraction. Polls
 * ``GET /etl/extracoes/{id}/eventos?since=<lastSeenTimestamp>`` every 1.5s
 * while the run is queued/running and stops once it lands on done/error
 * (still serves the cached events for replay).
 *
 * Returned ``events`` is the cumulative list, ordered newest-last so the
 * UI can render in chronological order or reverse it for a feed.
 */
export function useExtracaoEventos(id: number | null, status: ExtracaoOut["status"] | undefined) {
  const [events, setEvents] = useState<ExtracaoEventoOut[]>([]);
  const [since, setSince] = useState<string | null>(null);

  // Reset cache when ``id`` changes — opening a different extraction must
  // not show stale events from the previous one.
  useEffect(() => {
    setEvents([]);
    setSince(null);
  }, [id]);

  const isLive = status === "queued" || status === "running";

  const query = useQuery({
    queryKey: id !== null ? [...etlKeys.eventos(id), since] : ["etl", "eventos", "null"],
    queryFn: async () => {
      const page = await listEventos(id as number, { since });
      if (page.items.length > 0) {
        setEvents((prev) => {
          const seen = new Set(prev.map((e) => e.id));
          const fresh = page.items.filter((e) => !seen.has(e.id));
          return prev.concat(fresh);
        });
        setSince(page.items[page.items.length - 1].timestamp);
      }
      return page;
    },
    enabled: id !== null,
    // While running: poll fast. After: do one final fetch and stop.
    refetchInterval: isLive ? 1500 : false,
    refetchIntervalInBackground: false,
  });

  return {
    events,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
  };
}

/** Drill-down: NERDecisões with their obrigações/recomendações. */
export function useDecisoesExtracao(
  id: number | null,
  { page = 1, pageSize = 20 }: { page?: number; pageSize?: number } = {},
) {
  return useQuery({
    queryKey: id !== null ? etlKeys.decisoes(id, { page, pageSize }) : ["etl", "decisoes", "null"],
    queryFn: () => listDecisoes(id as number, { page, pageSize }),
    enabled: id !== null,
  });
}
