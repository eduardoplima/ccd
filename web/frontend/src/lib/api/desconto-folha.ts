import { apiClient } from "@/lib/api-client";
import {
  cadastroDetalheSchema,
  cadastroListResponseSchema,
  matchAutomaticoResultadoSchema,
  processoLookupSchema,
  type CadastroDetalhe,
  type CadastroInput,
  type CadastroListResponse,
  type ProcessoLookup,
  type ValorInput,
} from "@/schemas/desconto-folha";
import { jobSchema, type Job } from "@/schemas/job";

const BASE = "/api/v1/ccd/desconto-folha";

export async function listCadastros(params: {
  q?: string;
  page: number;
  size: number;
}): Promise<CadastroListResponse> {
  const { data } = await apiClient.get(BASE, { params: { ...params, q: params.q || undefined } });
  return cadastroListResponseSchema.parse(data);
}

export async function lookupProcesso(processo: string): Promise<ProcessoLookup> {
  const { data } = await apiClient.get(`${BASE}/lookup`, { params: { processo } });
  return processoLookupSchema.parse(data);
}

export async function getCadastro(id: number): Promise<CadastroDetalhe> {
  const { data } = await apiClient.get(`${BASE}/${id}`);
  return cadastroDetalheSchema.parse(data);
}

export async function criarCadastro(payload: CadastroInput): Promise<CadastroDetalhe> {
  const { data } = await apiClient.post(BASE, payload);
  return cadastroDetalheSchema.parse(data);
}

export async function removerCadastro(id: number): Promise<void> {
  await apiClient.delete(`${BASE}/${id}`);
}

export async function atualizarProcesso(id: number): Promise<CadastroDetalhe> {
  const { data } = await apiClient.post(`${BASE}/${id}/atualizar-processo`);
  return cadastroDetalheSchema.parse(data);
}

export async function extrairResposta(id: number): Promise<Job> {
  const { data } = await apiClient.post(`${BASE}/${id}/extrair`);
  return jobSchema.parse(data);
}

export async function criarValor(id: number, payload: ValorInput): Promise<CadastroDetalhe> {
  const { data } = await apiClient.post(`${BASE}/${id}/valores`, payload);
  return cadastroDetalheSchema.parse(data);
}

export async function removerValor(id: number, idValor: number): Promise<CadastroDetalhe> {
  const { data } = await apiClient.delete(`${BASE}/${id}/valores/${idValor}`);
  return cadastroDetalheSchema.parse(data);
}

export async function vincular(
  id: number,
  idValor: number,
  idLancamento: number,
): Promise<CadastroDetalhe> {
  const { data } = await apiClient.post(`${BASE}/${id}/valores/${idValor}/match`, { idLancamento });
  return cadastroDetalheSchema.parse(data);
}

export async function desvincular(id: number, idValor: number): Promise<CadastroDetalhe> {
  const { data } = await apiClient.delete(`${BASE}/${id}/valores/${idValor}/match`);
  return cadastroDetalheSchema.parse(data);
}

export async function matchAutomatico(id: number): Promise<number> {
  const { data } = await apiClient.post(`${BASE}/${id}/match-automatico`);
  return matchAutomaticoResultadoSchema.parse(data).vinculados;
}
