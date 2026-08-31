import { apiClient } from "@/lib/api-client";
import { jobSchema, type Job } from "@/schemas/job";
import {
  beneficioItemSchema,
  beneficioListResponseSchema,
  beneficioResumoSchema,
  dominiosResponseSchema,
  type BeneficioItem,
  type BeneficioListResponse,
  type BeneficioPayload,
  type BeneficioResumo,
  type DominiosResponse,
  type OrigemBeneficio,
  type StatusBeneficio,
} from "@/schemas/beneficios";

const BASE = "/api/v1/ccd/beneficios";

function buildParams(input: Record<string, unknown>): Record<string, unknown> {
  return Object.fromEntries(
    Object.entries(input).filter(([, v]) => v !== undefined && v !== null && v !== ""),
  );
}

export type BeneficiosSortKey =
  | "processo"
  | "nome"
  | "valor"
  | "dataOcorrencia"
  | "origem"
  | "dataInclusao";

export interface BeneficiosFilters {
  q?: string;
  status?: StatusBeneficio;
  situacaoEfetivacao?: number;
  idTipo?: number;
  origem?: OrigemBeneficio;
  fonte?: "propostas" | "carteira";
  page: number;
  size: number;
  sortBy?: BeneficiosSortKey | null;
  sortDir?: "asc" | "desc";
}

export async function listBeneficios(f: BeneficiosFilters): Promise<BeneficioListResponse> {
  const { data } = await apiClient.get(BASE, { params: buildParams({ ...f }) });
  return beneficioListResponseSchema.parse(data);
}

export async function getBeneficiosResumo(): Promise<BeneficioResumo> {
  const { data } = await apiClient.get(`${BASE}/resumo`);
  return beneficioResumoSchema.parse(data);
}

export async function getBeneficiosDominios(): Promise<DominiosResponse> {
  const { data } = await apiClient.get(`${BASE}/dominios`);
  return dominiosResponseSchema.parse(data);
}

export async function criarBeneficio(payload: BeneficioPayload): Promise<{ idBeneficio: number }> {
  const { data } = await apiClient.post(BASE, payload);
  return { idBeneficio: Number((data as { idBeneficio: number }).idBeneficio) };
}

export async function atualizarBeneficio(
  idBeneficio: number,
  payload: BeneficioPayload,
): Promise<BeneficioItem> {
  const { data } = await apiClient.patch(`${BASE}/${idBeneficio}`, payload);
  return beneficioItemSchema.parse(data);
}

export async function deletarBeneficio(idBeneficio: number): Promise<void> {
  await apiClient.delete(`${BASE}/${idBeneficio}`);
}

export async function transicionarBeneficio(
  idBeneficio: number,
  status: StatusBeneficio,
): Promise<BeneficioItem> {
  const { data } = await apiClient.post(`${BASE}/${idBeneficio}/status`, { status });
  return beneficioItemSchema.parse(data);
}

function nomeArquivoDeContentDisposition(header: string | undefined, fallback: string): string {
  if (!header) return fallback;
  const m = /filename\*?=(?:UTF-8'')?"?([^";]+)"?/i.exec(header);
  return m ? decodeURIComponent(m[1]) : fallback;
}

/** Exporta os VALIDADO (todos ou a seleção) e dispara o download no browser. */
export async function exportarBeneficios(
  formato: "xlsx" | "json",
  ids?: number[],
  marcarEnviado = true,
): Promise<void> {
  const resp = await apiClient.post(
    `${BASE}/export`,
    { ids: ids && ids.length > 0 ? ids : null, formato, marcarEnviado },
    { responseType: "blob" },
  );
  const blob = resp.data as Blob;
  const filename = nomeArquivoDeContentDisposition(
    resp.headers["content-disposition"],
    `beneficios-ccd.${formato}`,
  );
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export async function dispararDeteccaoBeneficios(): Promise<Job> {
  const { data } = await apiClient.post(`${BASE}/deteccao`);
  return jobSchema.parse(data);
}
