import { z } from "zod";

import { apiClient } from "@/lib/api-client";
import { jobSchema, type Job } from "@/schemas/job";
import {
  beneficioListResponseSchema,
  beneficioResumoSchema,
  dominiosResponseSchema,
  mesSerieSchema,
  type BeneficioListResponse,
  type BeneficioResumo,
  type DominiosResponse,
  type MesSerie,
  type OrigemBeneficio,
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

/** Recorte comum a lista, resumo e export. */
export interface BeneficiosRecorte {
  q?: string;
  origem?: OrigemBeneficio;
  dataDe?: string;
  dataAte?: string;
}

export interface BeneficiosFilters extends BeneficiosRecorte {
  page: number;
  size: number;
  sortBy?: BeneficiosSortKey | null;
  sortDir?: "asc" | "desc";
}

export async function listBeneficios(f: BeneficiosFilters): Promise<BeneficioListResponse> {
  const { data } = await apiClient.get(BASE, { params: buildParams({ ...f }) });
  return beneficioListResponseSchema.parse(data);
}

export async function getBeneficiosResumo(
  recorte: BeneficiosRecorte = {},
): Promise<BeneficioResumo> {
  const { data } = await apiClient.get(`${BASE}/resumo`, { params: buildParams({ ...recorte }) });
  return beneficioResumoSchema.parse(data);
}

export async function getBeneficiosSerie(): Promise<MesSerie[]> {
  const { data } = await apiClient.get(`${BASE}/serie`);
  return z.array(mesSerieSchema).parse(data);
}

export async function getBeneficiosDominios(): Promise<DominiosResponse> {
  const { data } = await apiClient.get(`${BASE}/dominios`);
  return dominiosResponseSchema.parse(data);
}

function nomeArquivoDeContentDisposition(header: string | undefined, fallback: string): string {
  if (!header) return fallback;
  const m = /filename\*?=(?:UTF-8'')?"?([^";]+)"?/i.exec(header);
  return m ? decodeURIComponent(m[1]) : fallback;
}

/** Exporta o recorte atual e dispara o download no browser. */
export async function exportarBeneficios(
  formato: "csv" | "json",
  recorte: BeneficiosRecorte = {},
): Promise<void> {
  const resp = await apiClient.post(
    `${BASE}/export`,
    { formato, ...buildParams({ ...recorte }) },
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
