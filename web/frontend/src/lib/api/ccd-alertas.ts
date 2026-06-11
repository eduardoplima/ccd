import { apiClient } from "@/lib/api-client";
import {
  alertasResponseSchema,
  type AlertasResponse,
  type TipoAlerta,
} from "@/schemas/ccd-alertas";

export async function listAlertasCCD(tipo?: TipoAlerta): Promise<AlertasResponse> {
  const params: Record<string, string> = {};
  if (tipo) params.tipo = tipo;
  const { data } = await apiClient.get("/api/v1/ccd/alertas", { params });
  return alertasResponseSchema.parse(data);
}
