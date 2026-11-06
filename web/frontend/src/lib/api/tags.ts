import { apiClient } from "@/lib/api-client";
import { jobSchema, type Job } from "@/schemas/job";
import {
  tagDetalheSchema,
  tagListResponseSchema,
  type ExtrairInput,
  type ObrigacaoInput,
  type TagDetalhe,
  type TagListResponse,
  type TagPatch,
} from "@/schemas/tags";

const BASE = "/api/v1/ccd/tags";

export async function listTags(q?: string): Promise<TagListResponse> {
  const { data } = await apiClient.get(BASE, { params: { q: q || undefined } });
  return tagListResponseSchema.parse(data);
}

export async function getTag(id: number): Promise<TagDetalhe> {
  const { data } = await apiClient.get(`${BASE}/${id}`);
  return tagDetalheSchema.parse(data);
}

export async function extrairTag(payload: ExtrairInput): Promise<Job> {
  const { data } = await apiClient.post(`${BASE}/extrair`, payload);
  return jobSchema.parse(data);
}

export async function atualizarTag(id: number, patch: TagPatch): Promise<TagDetalhe> {
  const { data } = await apiClient.patch(`${BASE}/${id}`, patch);
  return tagDetalheSchema.parse(data);
}

export async function salvarObrigacoes(
  id: number,
  obrigacoes: ObrigacaoInput[],
): Promise<TagDetalhe> {
  const { data } = await apiClient.put(`${BASE}/${id}/obrigacoes`, { obrigacoes });
  return tagDetalheSchema.parse(data);
}

export async function removerTag(id: number): Promise<void> {
  await apiClient.delete(`${BASE}/${id}`);
}
