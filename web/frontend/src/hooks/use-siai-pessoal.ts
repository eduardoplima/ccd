import { useQuery } from "@tanstack/react-query";

import { getContracheque } from "@/lib/api/siai-pessoal";
import type { ContrachequeParams } from "@/schemas/siai-pessoal";

export function useContracheque(params: ContrachequeParams | null) {
  return useQuery({
    queryKey: ["ccd-siai-pessoal", "contracheque", params],
    queryFn: () => getContracheque(params as ContrachequeParams),
    enabled: params != null,
  });
}
