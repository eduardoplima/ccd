import { apiClient } from "@/lib/api-client";
import {
  lancamentoDetailSchema,
  lancamentoListResponseSchema,
  type LancamentoDetail,
  type LancamentoListResponse,
} from "@/schemas/lancamento";

export interface LancamentoFilters {
  conta?: string;
  periodo?: string;
  categoria?: string;
  valorDc?: "C" | "D";
  dtInicio?: string;
  dtFim?: string;
  valorMin?: string;
  valorMax?: string;
  cpfCnpj?: string;
  q?: string;
  page: number;
  size: number;
}

export async function listLancamentos(filters: LancamentoFilters): Promise<LancamentoListResponse> {
  const params: Record<string, string | number> = { page: filters.page, size: filters.size };
  if (filters.conta) params.conta = filters.conta;
  if (filters.periodo) params.periodo = filters.periodo;
  if (filters.categoria) params.categoria = filters.categoria;
  if (filters.valorDc) params.valor_dc = filters.valorDc;
  if (filters.dtInicio) params.dt_inicio = filters.dtInicio;
  if (filters.dtFim) params.dt_fim = filters.dtFim;
  if (filters.valorMin) params.valor_min = filters.valorMin;
  if (filters.valorMax) params.valor_max = filters.valorMax;
  if (filters.cpfCnpj) params.cpfCnpj = filters.cpfCnpj;
  if (filters.q) params.q = filters.q;

  const { data } = await apiClient.get("/api/v1/frap/lancamentos", { params });
  return lancamentoListResponseSchema.parse(data);
}

export async function getLancamento(id: number): Promise<LancamentoDetail> {
  const { data } = await apiClient.get(`/api/v1/frap/lancamentos/${id}`);
  return lancamentoDetailSchema.parse(data);
}
