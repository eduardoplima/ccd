import { apiClient } from "@/lib/api-client";
import {
  matchDescontoFolhaListResponseSchema,
  matchGuiaListResponseSchema,
  matchOBListResponseSchema,
  matchPessoaListResponseSchema,
  type MatchDescontoFolhaListResponse,
  type MatchGuiaListResponse,
  type MatchOBListResponse,
  type MatchPessoaListResponse,
} from "@/schemas/match";

export interface MatchesFilters {
  ano?: number;
  mes?: number;
  conta?: string;
  q?: string;
  page: number;
  size: number;
}

function buildParams(f: MatchesFilters): Record<string, string | number> {
  const out: Record<string, string | number> = { page: f.page, size: f.size };
  if (f.ano) out.ano = f.ano;
  if (f.mes) out.mes = f.mes;
  if (f.conta) out.conta = f.conta;
  if (f.q) out.q = f.q;
  return out;
}

export async function listMatchesOB(f: MatchesFilters): Promise<MatchOBListResponse> {
  const { data } = await apiClient.get("/api/v1/frap/matches/ob", { params: buildParams(f) });
  return matchOBListResponseSchema.parse(data);
}

export async function listMatchesPessoa(f: MatchesFilters): Promise<MatchPessoaListResponse> {
  const { data } = await apiClient.get("/api/v1/frap/matches/pessoa", { params: buildParams(f) });
  return matchPessoaListResponseSchema.parse(data);
}

export async function listMatchesGuia(f: MatchesFilters): Promise<MatchGuiaListResponse> {
  const { data } = await apiClient.get("/api/v1/frap/matches/guia", { params: buildParams(f) });
  return matchGuiaListResponseSchema.parse(data);
}

export async function listMatchesDescontoFolha(
  f: MatchesFilters,
): Promise<MatchDescontoFolhaListResponse> {
  const params = buildParams(f);
  delete params.conta;
  const { data } = await apiClient.get("/api/v1/frap/matches/desconto-folha", { params });
  return matchDescontoFolhaListResponseSchema.parse(data);
}
