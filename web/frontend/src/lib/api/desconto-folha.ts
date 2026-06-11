import { apiClient } from "@/lib/api-client";
import {
  atrasoSistemicoResponseSchema,
  atribuirOrgaoResultadoSchema,
  cadastroManualInputSchema,
  cadastroManualListResponseSchema,
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
  type CadastroManualInput,
  type CadastroManualListResponse,
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

const BASE = "/api/v1/frap/desconto-folha";

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
