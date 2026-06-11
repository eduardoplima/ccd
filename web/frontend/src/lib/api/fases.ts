import { apiClient } from "@/lib/api-client";
import {
  debitosFaseResumoSchema,
  enviadosListResponseSchema,
  fasesResumoSchema,
  type DebitosFaseResumo,
  type EnviadosListResponse,
  type FasesResumo,
} from "@/schemas/fases";

export async function getFasesResumo(cpfcnpj: string): Promise<FasesResumo> {
  const { data } = await apiClient.get(`/api/v1/frap/desconto-folha/pessoas/${cpfcnpj}/fases`);
  return fasesResumoSchema.parse(data);
}

export async function getFasesTotais(cpfcnpj: string): Promise<DebitosFaseResumo> {
  const { data } = await apiClient.get(
    `/api/v1/frap/desconto-folha/pessoas/${cpfcnpj}/fases/totais`,
  );
  return debitosFaseResumoSchema.parse(data);
}

export async function getFasesDebitosNotificados(cpfcnpj: string): Promise<DebitosFaseResumo> {
  const { data } = await apiClient.get(
    `/api/v1/frap/desconto-folha/pessoas/${cpfcnpj}/fases/debitos-notificados`,
  );
  return debitosFaseResumoSchema.parse(data);
}

export async function getFasesEnviados(cpfcnpj: string): Promise<EnviadosListResponse> {
  const { data } = await apiClient.get(`/api/v1/frap/desconto-folha/pessoas/${cpfcnpj}/fases/enviados`);
  return enviadosListResponseSchema.parse(data);
}
