import { apiClient } from "@/lib/api-client";
import {
  contrachequeMesSchema,
  type ContrachequeMes,
  type ContrachequeParams,
} from "@/schemas/siai-pessoal";

const BASE = "/api/v1/ccd/siai-pessoal";

export async function getContracheque(params: ContrachequeParams): Promise<ContrachequeMes> {
  const { data } = await apiClient.get(`${BASE}/contracheque`, {
    params: { ...params, processo: params.processo || undefined },
  });
  return contrachequeMesSchema.parse(data);
}
