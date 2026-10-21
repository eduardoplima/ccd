"use client";

import { useQuery } from "@tanstack/react-query";

import { listMonitoramentosCCD } from "@/lib/api/ccd-monitoramentos";

export function useMonitoramentosCCD() {
  return useQuery({
    queryKey: ["ccd-monitoramentos"],
    queryFn: listMonitoramentosCCD,
    staleTime: 60_000,
  });
}
