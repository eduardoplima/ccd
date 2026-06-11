import { apiClient } from "@/lib/api-client";
import { jobSchema, type Job } from "@/schemas/job";

// Acompanhamento e download dos jobs de geração de documentos do módulo CCD.
// As páginas (Desconto em Folha, Antecedentes) enfileiram pelos seus próprios
// endpoints e depois usam isto para o polling + download do PDF/ZIP final.

export async function getCcdJob(id: number): Promise<Job> {
  const { data } = await apiClient.get(`/api/v1/ccd/jobs/${id}`);
  return jobSchema.parse(data);
}

function nomeArquivoDeContentDisposition(header: string | undefined, fallback: string): string {
  if (!header) return fallback;
  const m = /filename\*?=(?:UTF-8'')?"?([^";]+)"?/i.exec(header);
  return m ? decodeURIComponent(m[1]) : fallback;
}

/** Baixa o artefato final do job e dispara o download no browser. */
export async function downloadCcdArtefato(id: number): Promise<void> {
  const resp = await apiClient.get(`/api/v1/ccd/jobs/${id}/download`, {
    responseType: "blob",
  });
  const blob = resp.data as Blob;
  const fallbackExt = blob.type === "application/zip" ? "zip" : "pdf";
  const filename = nomeArquivoDeContentDisposition(
    resp.headers["content-disposition"],
    `ccd_${id}.${fallbackExt}`,
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
