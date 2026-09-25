import { apiClient } from "@/lib/api-client";
import { MultasNaoCominadas, multasNaoCominadasSchema } from "@/schemas/multas-nao-cominadas";

export async function getMultasNaoCominadas(): Promise<MultasNaoCominadas> {
  const response = await apiClient.get("/api/v1/cgad/multas-nao-cominadas");
  return multasNaoCominadasSchema.parse(response.data);
}
