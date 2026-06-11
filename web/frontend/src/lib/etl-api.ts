import { apiClient } from "@/lib/api-client";
import {
  DecisaoExtraidaListPage,
  decisaoExtraidaListPageSchema,
  ExtracaoEventoListPage,
  extracaoEventoListPageSchema,
  ExtracaoListFilters,
  ExtracaoListPage,
  extracaoListPageSchema,
  ExtracaoOut,
  extracaoOutSchema,
  ExtractionJobAccepted,
  extractionJobAcceptedSchema,
  ExtractionTriggerRequest,
} from "@/schemas/etl";

export async function triggerExtraction(
  body: ExtractionTriggerRequest,
): Promise<ExtractionJobAccepted> {
  const response = await apiClient.post("/api/v1/cgad/etl/run", body);
  return extractionJobAcceptedSchema.parse(response.data);
}

type ListArgs = {
  page?: number;
  pageSize?: number;
  filters?: ExtracaoListFilters;
};

export async function listExtracoes({
  page = 1,
  pageSize = 20,
  filters,
}: ListArgs = {}): Promise<ExtracaoListPage> {
  const response = await apiClient.get("/api/v1/cgad/etl/extracoes", {
    params: {
      page,
      page_size: pageSize,
      status: filters?.status,
      start_date_from: filters?.start_date_from,
      start_date_to: filters?.start_date_to,
    },
  });
  return extracaoListPageSchema.parse(response.data);
}

export async function getExtracao(id: number): Promise<ExtracaoOut> {
  const response = await apiClient.get(`/api/v1/cgad/etl/extracoes/${id}`);
  return extracaoOutSchema.parse(response.data);
}

export async function listEventos(
  id: number,
  { since, limit = 500 }: { since?: string | null; limit?: number } = {},
): Promise<ExtracaoEventoListPage> {
  const response = await apiClient.get(`/api/v1/cgad/etl/extracoes/${id}/eventos`, {
    params: { since: since ?? undefined, limit },
  });
  return extracaoEventoListPageSchema.parse(response.data);
}

export async function listDecisoes(
  id: number,
  { page = 1, pageSize = 20 }: { page?: number; pageSize?: number } = {},
): Promise<DecisaoExtraidaListPage> {
  const response = await apiClient.get(`/api/v1/cgad/etl/extracoes/${id}/decisoes`, {
    params: { page, page_size: pageSize },
  });
  return decisaoExtraidaListPageSchema.parse(response.data);
}

export async function abortExtracao(id: number): Promise<ExtracaoOut> {
  const response = await apiClient.post(`/api/v1/cgad/etl/extracoes/${id}/abort`);
  return extracaoOutSchema.parse(response.data);
}

export async function deleteExtracao(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/cgad/etl/extracoes/${id}`);
}
