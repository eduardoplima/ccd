import { apiClient } from "@/lib/api-client";
import {
  monitoramentosResponseSchema,
  type MonitoramentosResponse,
} from "@/schemas/ccd-monitoramentos";

export async function listMonitoramentosCCD(): Promise<MonitoramentosResponse> {
  const { data } = await apiClient.get("/api/v1/ccd/monitoramentos");
  return monitoramentosResponseSchema.parse(data);
}
