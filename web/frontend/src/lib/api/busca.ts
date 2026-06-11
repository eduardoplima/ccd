import { apiClient } from "@/lib/api-client";
import {
  debitoPessoaListResponseSchema,
  pessoaListResponseSchema,
  processoResultadoSchema,
  type DebitoPessoaListResponse,
  type PessoaListResponse,
  type ProcessoResultado,
} from "@/schemas/busca";

export async function buscarPessoas(
  q: string,
  page: number,
  size: number,
): Promise<PessoaListResponse> {
  const { data } = await apiClient.get("/api/v1/frap/busca/pessoas", {
    params: { q, page, size },
  });
  return pessoaListResponseSchema.parse(data);
}

export async function buscarProcesso(
  numero: string,
  ano: string,
  tipo: "origem" | "execucao",
): Promise<ProcessoResultado> {
  const { data } = await apiClient.get("/api/v1/frap/busca/processo", {
    params: { numero, ano, tipo },
  });
  return processoResultadoSchema.parse(data);
}

export async function buscarDebitosPessoa(
  cpfcnpj: string,
  idProcesso?: number,
): Promise<DebitoPessoaListResponse> {
  const params: Record<string, string | number> = { cpfcnpj };
  if (idProcesso != null) params.id_processo = idProcesso;
  const { data } = await apiClient.get("/api/v1/frap/busca/debitos-pessoa", { params });
  return debitoPessoaListResponseSchema.parse(data);
}
