import { apiClient } from "@/lib/api-client";
import {
  cadastroDetalheSchema,
  cadastroListResponseSchema,
  creditosFrapResponseSchema,
  matchAutomaticoResultadoSchema,
  processoLookupSchema,
  mapaRetencoesSchema,
  retencoesSchema,
  sugestoesSchema,
  type CadastroDetalhe,
  type CadastroInput,
  type CadastroListResponse,
  type CreditosFrapParams,
  type CreditosFrapResponse,
  type ProcessoLookup,
  type MapaRetencoes,
  type Retencoes,
  type Sugestoes,
  type ValorInput,
} from "@/schemas/desconto-folha";
import { jobSchema, type Job } from "@/schemas/job";

const BASE = "/api/v1/ccd/desconto-folha";

export type FiltrosCadastro = {
  q?: string;
  page: number;
  size: number;
  comNotificacao?: boolean;
  comRecebimento?: boolean;
  comResposta?: boolean;
  comValores?: boolean;
  comConciliacao?: boolean;
  cpf?: string;
  orgao?: string;
};

export async function getSugestoes(q: string): Promise<Sugestoes> {
  const { data } = await apiClient.get(`${BASE}/sugestoes`, { params: { q } });
  return sugestoesSchema.parse(data);
}

export async function getMapaRetencoes(cpf: string): Promise<MapaRetencoes> {
  const { data } = await apiClient.get(`${BASE}/retencoes/mapa`, { params: { cpf } });
  return mapaRetencoesSchema.parse(data);
}

export async function getRetencoes(cpf: string): Promise<Retencoes> {
  const { data } = await apiClient.get(`${BASE}/retencoes`, { params: { cpf } });
  return retencoesSchema.parse(data);
}

export async function listCadastros(params: FiltrosCadastro): Promise<CadastroListResponse> {
  const { data } = await apiClient.get(BASE, {
    params: {
      q: params.q || undefined,
      page: params.page,
      size: params.size,
      com_notificacao: params.comNotificacao || undefined,
      com_recebimento: params.comRecebimento || undefined,
      com_resposta: params.comResposta || undefined,
      com_valores: params.comValores || undefined,
      com_conciliacao: params.comConciliacao || undefined,
      cpf: params.cpf || undefined,
      orgao: params.orgao || undefined,
    },
  });
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

export async function localizarNotificacoes(): Promise<Job> {
  const { data } = await apiClient.post(`${BASE}/localizar-notificacoes`);
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

export async function getCreditosFrap(
  id: number,
  params: CreditosFrapParams,
): Promise<CreditosFrapResponse> {
  const { data } = await apiClient.get(`${BASE}/${id}/frap-creditos`, { params });
  return creditosFrapResponseSchema.parse(data);
}

export async function adotarCreditosFrap(
  id: number,
  idsLancamento: number[],
): Promise<CadastroDetalhe> {
  const { data } = await apiClient.post(`${BASE}/${id}/frap-creditos`, { idsLancamento });
  return cadastroDetalheSchema.parse(data);
}
