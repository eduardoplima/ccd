"use client";

import { useQuery } from "@tanstack/react-query";

import { listAlertasCCD } from "@/lib/api/ccd-alertas";
import type { TipoAlerta } from "@/schemas/ccd-alertas";

export function useAlertasCCD(tipo?: TipoAlerta) {
  return useQuery({
    queryKey: ["ccd-alertas", tipo ?? null],
    queryFn: () => listAlertasCCD(tipo),
    staleTime: 60_000,
  });
}
