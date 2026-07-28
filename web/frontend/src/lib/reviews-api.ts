import { apiClient } from "@/lib/api-client";
import {
  AwaitingDispatchPage,
  awaitingDispatchPageSchema,
  ClaimResponse,
  claimResponseSchema,
  DecisaoDetail,
  decisaoDetailSchema,
  DecisaoListPage,
  decisaoListPageSchema,
  DecisaoReviewPayload,
  DecisaoTexto,
  decisaoTextoSchema,
} from "@/schemas/review";

export async function listDecisoes({
  page = 1,
  pageSize = 20,
  processo,
}: {
  page?: number;
  pageSize?: number;
  processo?: string;
} = {}): Promise<DecisaoListPage> {
  const response = await apiClient.get("/api/v1/cgad/reviews/decisoes", {
    params: { page, page_size: pageSize, processo: processo || undefined },
  });
  return decisaoListPageSchema.parse(response.data);
}

export async function getDecisao(id: number): Promise<DecisaoDetail> {
  const response = await apiClient.get(`/api/v1/cgad/reviews/decisoes/${id}`);
  return decisaoDetailSchema.parse(response.data);
}

export async function getDecisaoTexto(id: number): Promise<DecisaoTexto> {
  const response = await apiClient.get(`/api/v1/cgad/reviews/decisoes/${id}/texto-acordao`);
  return decisaoTextoSchema.parse(response.data);
}

export async function claimDecisao(id: number): Promise<ClaimResponse> {
  const response = await apiClient.post(`/api/v1/cgad/reviews/decisoes/${id}/claim`);
  return claimResponseSchema.parse(response.data);
}

export async function releaseDecisao(id: number): Promise<void> {
  await apiClient.post(`/api/v1/cgad/reviews/decisoes/${id}/release`);
}

export async function approveDecisao(
  id: number,
  payload: DecisaoReviewPayload,
): Promise<DecisaoDetail> {
  const response = await apiClient.post(`/api/v1/cgad/reviews/decisoes/${id}/approve`, payload);
  return decisaoDetailSchema.parse(response.data);
}

export async function listAwaitingDispatch({
  page = 1,
  pageSize = 20,
}: {
  page?: number;
  pageSize?: number;
} = {}): Promise<AwaitingDispatchPage> {
  const response = await apiClient.get("/api/v1/cgad/reviews/awaiting-dispatch", {
    params: { page, page_size: pageSize },
  });
  return awaitingDispatchPageSchema.parse(response.data);
}
