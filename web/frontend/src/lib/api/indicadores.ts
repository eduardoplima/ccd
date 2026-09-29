import { apiClient } from "@/lib/api-client";
import { painelSchema, type Painel } from "@/schemas/indicadores";

export async function getPainelIndicadores(): Promise<Painel> {
  const { data } = await apiClient.get("/api/v1/ccd/indicadores");
  return painelSchema.parse(data);
}
