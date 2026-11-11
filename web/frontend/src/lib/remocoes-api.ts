import { apiClient } from "@/lib/api-client";
import {
  ConsultaRemocao,
  RemocaoPayload,
  consultaRemocaoSchema,
  remocaoResultadoSchema,
} from "@/schemas/remocoes";

export async function getRemocoes(processo: string): Promise<ConsultaRemocao> {
  const response = await apiClient.get("/api/v1/cgad/remocoes", { params: { processo } });
  return consultaRemocaoSchema.parse(response.data);
}

export async function postRemocao(payload: RemocaoPayload): Promise<{ removidos: number }> {
  const response = await apiClient.post("/api/v1/cgad/remocoes", payload);
  return remocaoResultadoSchema.parse(response.data);
}
