import { apiClient } from "@/lib/api-client";
import {
  atrasoSistemicoResponseSchema,
  atribuirOrgaoResultadoSchema,
  cadastroManualDetailSchema,
  cadastroManualInputSchema,
  cadastroManualListResponseSchema,
  monitoramentoItemSchema,
  monitoramentoListResponseSchema,
  monitoramentoResumoSchema,
  cpfSemSiaiResponseSchema,
  depositosOrgaoResponseSchema,
  lancamentosDoOrgaoResponseSchema,
  matchManualInputSchema,
  matchManualResultadoSchema,
  orgaoAgregadoListResponseSchema,
  orgaoDisponivelSchema,
  parcelaDuplicadaResponseSchema,
  parcelasPessoaResponseSchema,
  pessoaAgregadaListResponseSchema,
  pessoasDoOrgaoResponseSchema,
  repasseMultiParcelaResponseSchema,
  type AtrasoSistemicoResponse,
  type AtribuirOrgaoResultado,
  type CadastroManualDetail,
  type CadastroManualInput,
  type CadastroManualListResponse,
  type CadastroManualUpdate,
  type GrupoMonitoramento,
  type MonitoramentoItem,
  type MonitoramentoListResponse,
  type MonitoramentoPayload,
  type MonitoramentoResumo,
  type ParcelaManualInput,
  type ParcelaManualUpdate,
  type CpfSemSiaiResponse,
  type DepositosOrgaoResponse,
  type LancamentosDoOrgaoResponse,
  type MatchManualInput,
  type MatchManualResultado,
  type OrgaoAgregadoListResponse,
  type OrgaoDisponivel,
  type ParcelaDuplicadaResponse,
  type ParcelasPessoaResponse,
  type PessoaAgregadaListResponse,
  type PessoasDoOrgaoResponse,
  type RepasseMultiParcelaResponse,
} from "@/schemas/desconto-folha";
import { pessoaSchema, type Pessoa } from "@/schemas/review";

const BASE = "/api/v1/ccd/desconto-folha";

function buildParams(input: Record<string, unknown>): Record<string, unknown> {
  return Object.fromEntries(
    Object.entries(input).filter(([, v]) => v !== undefined && v !== null && v !== ""),
  );
}

export type PessoasSortKey =
  | "nome"
  | "cpf"
  | "orgao"
  | "valor_atualizado"
  | "qtd_notificacoes"
  | "qtd_debitos_notificados"
  | "valor_debitos_notificados"
  | "esperado";

export interface PessoasFilters {
  ano?: number;
  mes?: number;
  status?: string;
  q?: string;
  page: number;
  size: number;
  sortBy?: PessoasSortKey | null;
  sortDir?: "asc" | "desc";
}

export async function listPessoas(f: PessoasFilters): Promise<PessoaAgregadaListResponse> {
  const { data } = await apiClient.get(`${BASE}/pessoas`, { params: buildParams({ ...f }) });
  return pessoaAgregadaListResponseSchema.parse(data);
}

export async function getParcelasPessoa(
  cpfCnpj: string,
  ano?: number,
): Promise<ParcelasPessoaResponse> {
  const { data } = await apiClient.get(`${BASE}/pessoas/${cpfCnpj}/parcelas`, {
    params: buildParams({ ano }),
  });
  return parcelasPessoaResponseSchema.parse(data);
}

export async function atribuirOrgaoPessoa(
  cpfCnpj: string,
  idOrgao: number,
): Promise<AtribuirOrgaoResultado> {
  const { data } = await apiClient.patch(`${BASE}/pessoas/${cpfCnpj}/orgao`, { idOrgao });
  return atribuirOrgaoResultadoSchema.parse(data);
}

export interface OrgaosFilters {
  ano?: number;
  mes?: number;
  q?: string;
  page: number;
  size: number;
}

export async function listOrgaos(f: OrgaosFilters): Promise<OrgaoAgregadoListResponse> {
  const { data } = await apiClient.get(`${BASE}/orgaos`, { params: buildParams({ ...f }) });
  return orgaoAgregadoListResponseSchema.parse(data);
}

export async function getPessoasDoOrgao(
  idOrgao: number,
  ano?: number,
  mes?: number,
): Promise<PessoasDoOrgaoResponse> {
  const { data } = await apiClient.get(`${BASE}/orgaos/${idOrgao}/pessoas`, {
    params: buildParams({ ano, mes }),
  });
  return pessoasDoOrgaoResponseSchema.parse(data);
}

export async function getDepositosOrgao(idOrgao: number): Promise<DepositosOrgaoResponse> {
  const { data } = await apiClient.get(`${BASE}/orgaos/${idOrgao}/depositos`);
  return depositosOrgaoResponseSchema.parse(data);
}

export async function getDepositosOrgaoLancamentos(
  idOrgao: number,
): Promise<LancamentosDoOrgaoResponse> {
  const { data } = await apiClient.get(`${BASE}/orgaos/${idOrgao}/depositos/lancamentos`);
  return lancamentosDoOrgaoResponseSchema.parse(data);
}

export async function listOrgaosDisponiveis(busca?: string): Promise<OrgaoDisponivel[]> {
  const { data } = await apiClient.get(`${BASE}/orgaos-disponiveis`, {
    params: buildParams({ q: busca }),
  });
  return orgaoDisponivelSchema.array().parse(data);
}

export async function listCadastros(
  q?: string,
  page = 1,
  size = 50,
): Promise<CadastroManualListResponse> {
  const { data } = await apiClient.get(`${BASE}/cadastro`, {
    params: buildParams({ q, page, size }),
  });
  return cadastroManualListResponseSchema.parse(data);
}

export async function criarCadastro(
  input: CadastroManualInput,
): Promise<{ idDescontoFolha: number }> {
  const payload = cadastroManualInputSchema.parse(input);
  const { data } = await apiClient.post(`${BASE}/cadastro`, payload);
  return { idDescontoFolha: Number((data as { idDescontoFolha: number }).idDescontoFolha) };
}

export async function deletarCadastro(idDescontoFolha: number): Promise<void> {
  await apiClient.delete(`${BASE}/cadastro/${idDescontoFolha}`);
}

export async function getCadastro(idDescontoFolha: number): Promise<CadastroManualDetail> {
  const { data } = await apiClient.get(`${BASE}/cadastro/${idDescontoFolha}`);
  return cadastroManualDetailSchema.parse(data);
}

export async function atualizarCadastro(
  idDescontoFolha: number,
  input: CadastroManualUpdate,
): Promise<void> {
  await apiClient.patch(`${BASE}/cadastro/${idDescontoFolha}`, input);
}

export async function criarParcela(
  idDescontoFolha: number,
  input: ParcelaManualInput,
): Promise<{ idFrapParcela: number }> {
  const { data } = await apiClient.post(`${BASE}/cadastro/${idDescontoFolha}/parcelas`, input);
  return { idFrapParcela: Number((data as { idFrapParcela: number }).idFrapParcela) };
}

export async function atualizarParcela(
  idDescontoFolha: number,
  idParcela: number,
  input: ParcelaManualUpdate,
): Promise<void> {
  await apiClient.patch(`${BASE}/cadastro/${idDescontoFolha}/parcelas/${idParcela}`, input);
}

export async function deletarParcela(idDescontoFolha: number, idParcela: number): Promise<void> {
  await apiClient.delete(`${BASE}/cadastro/${idDescontoFolha}/parcelas/${idParcela}`);
}

// ---------------------------------------------------------------------------
// Monitoramento
// ---------------------------------------------------------------------------

export type MonitoramentoSortKey =
  | "processo"
  | "nome"
  | "grupo"
  | "dataNotificacao"
  | "valorOriginal";

export interface MonitoramentoFilters {
  q?: string;
  grupo?: GrupoMonitoramento;
  page: number;
  size: number;
  sortBy?: MonitoramentoSortKey | null;
  sortDir?: "asc" | "desc";
}

export async function listMonitoramento(
  f: MonitoramentoFilters,
): Promise<MonitoramentoListResponse> {
  const { data } = await apiClient.get(`${BASE}/monitoramento`, { params: buildParams({ ...f }) });
  return monitoramentoListResponseSchema.parse(data);
}

export async function getMonitoramentoResumo(
  grupo?: GrupoMonitoramento,
): Promise<MonitoramentoResumo> {
  const { data } = await apiClient.get(`${BASE}/monitoramento/resumo`, {
    params: buildParams({ grupo }),
  });
  return monitoramentoResumoSchema.parse(data);
}

export async function criarMonitoramento(
  payload: MonitoramentoPayload,
): Promise<{ idMonitoramento: number }> {
  const { data } = await apiClient.post(`${BASE}/monitoramento`, payload);
  return { idMonitoramento: Number((data as { idMonitoramento: number }).idMonitoramento) };
}

export async function atualizarMonitoramento(
  idMonitoramento: number,
  payload: MonitoramentoPayload,
): Promise<MonitoramentoItem> {
  const { data } = await apiClient.patch(`${BASE}/monitoramento/${idMonitoramento}`, payload);
  return monitoramentoItemSchema.parse(data);
}

export async function deletarMonitoramento(idMonitoramento: number): Promise<void> {
  await apiClient.delete(`${BASE}/monitoramento/${idMonitoramento}`);
}

export async function getPessoasProcesso(processo: string): Promise<Pessoa[]> {
  const { data } = await apiClient.get(`${BASE}/monitoramento/pessoas-processo`, {
    params: { processo },
  });
  return pessoaSchema.array().parse(data);
}

export async function criarMatchManual(input: MatchManualInput): Promise<MatchManualResultado> {
  const payload = matchManualInputSchema.parse(input);
  const { data } = await apiClient.post(`${BASE}/matches/manual`, payload);
  return matchManualResultadoSchema.parse(data);
}

export async function deletarMatchManual(idMatch: number): Promise<void> {
  await apiClient.delete(`${BASE}/matches/manual/${idMatch}`);
}

// ---------------------------------------------------------------------------
// Tipologias
// ---------------------------------------------------------------------------

export interface RepasseMultiFilters {
  ano?: number;
  mes?: number;
  cpfCnpj?: string;
}

export async function getTipologiaRepasseMulti(
  f: RepasseMultiFilters = {},
): Promise<RepasseMultiParcelaResponse> {
  const { data } = await apiClient.get(`${BASE}/tipologias/repasse-multi-parcela`, {
    params: buildParams({ ano: f.ano, mes: f.mes, cpfCnpj: f.cpfCnpj }),
  });
  return repasseMultiParcelaResponseSchema.parse(data);
}

export async function getTipologiaCpfSemSiai(): Promise<CpfSemSiaiResponse> {
  const { data } = await apiClient.get(`${BASE}/tipologias/cpf-sem-siaipessoal`);
  return cpfSemSiaiResponseSchema.parse(data);
}

export async function getTipologiaParcelaDuplicada(
  ano?: number,
  mes?: number,
): Promise<ParcelaDuplicadaResponse> {
  const { data } = await apiClient.get(`${BASE}/tipologias/parcela-duplicada`, {
    params: buildParams({ ano, mes }),
  });
  return parcelaDuplicadaResponseSchema.parse(data);
}

export async function getTipologiaAtrasoSistemico(
  ano?: number,
  mesesConsecutivos = 3,
  pctMinimo = 0.2,
): Promise<AtrasoSistemicoResponse> {
  const { data } = await apiClient.get(`${BASE}/tipologias/atraso-sistemico`, {
    params: buildParams({ ano, mesesConsecutivos, pctMinimo }),
  });
  return atrasoSistemicoResponseSchema.parse(data);
}
