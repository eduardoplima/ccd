import { apiClient } from "@/lib/api-client";
import {
  filtrosCCDResponseSchema,
  prescricaoCCDListResponseSchema,
  processoCCDListResponseSchema,
  type FiltrosCCDResponse,
  type PrescricaoCCDListResponse,
  type ProcessoCCDListResponse,
} from "@/schemas/ccd";

export interface ProcessoCCDFilters {
  marcador?: string;
  semMarcador?: boolean;
  relator?: string;
  assunto?: string;
  sort?: string;
  order?: "asc" | "desc";
  ocultarPermanencia?: boolean;
  page: number;
  size: number;
}

export async function listProcessosCCD(
  filters: ProcessoCCDFilters,
): Promise<ProcessoCCDListResponse> {
  const params: Record<string, string | number> = {
    page: filters.page,
    size: filters.size,
  };
  if (filters.semMarcador) params.sem_marcador = "true";
  else if (filters.marcador) params.marcador = filters.marcador;
  if (filters.relator) params.relator = filters.relator;
  if (filters.assunto) params.assunto = filters.assunto;
  if (filters.sort) {
    params.sort = filters.sort;
    params.order = filters.order ?? "asc";
  }
  if (filters.ocultarPermanencia) params.ocultar_permanencia = "true";

  const { data } = await apiClient.get("/api/v1/ccd/processos", { params });
  return processoCCDListResponseSchema.parse(data);
}

export async function listPrescricaoCCD(
  ocultarPermanencia: boolean,
): Promise<PrescricaoCCDListResponse> {
  const { data } = await apiClient.get("/api/v1/ccd/prescricao", {
    params: { ocultar_permanencia: ocultarPermanencia ? "true" : "false" },
  });
  return prescricaoCCDListResponseSchema.parse(data);
}

export async function getFiltrosCCD(): Promise<FiltrosCCDResponse> {
  const { data } = await apiClient.get("/api/v1/ccd/processos/filtros");
  return filtrosCCDResponseSchema.parse(data);
}
