"use client";

import { useQuery } from "@tanstack/react-query";

import { getCcdJob } from "@/lib/api/ccd-jobs";
import type { JobStatus } from "@/schemas/job";

const FINALIZADOS: ReadonlySet<JobStatus> = new Set(["done", "failed", "cancelled"]);

/**
 * Acompanha um job de geração do CCD. Faz polling a cada 2s enquanto o job
 * estiver pending/running; para quando finaliza. Passe `null` para desativar.
 */
export function useCcdJob(id: number | null) {
  return useQuery({
    queryKey: ["ccd-job", id],
    queryFn: () => getCcdJob(id as number),
    enabled: id != null,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status && FINALIZADOS.has(status) ? false : 2_000;
    },
  });
}
