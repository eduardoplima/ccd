import { apiClient } from "@/lib/api-client";
import { jobSchema, type Job } from "@/schemas/job";
import { candidatosResponseSchema, type CandidatosResponse } from "@/schemas/ccd-desconto-folha";

// API da página "Desconto em Folha" do CCD. O acompanhamento e o download do
// job ficam em `@/lib/api/ccd-jobs` (compartilhados entre as páginas do CCD).

export async function listCandidatosDescontoFolha(todos: boolean): Promise<CandidatosResponse> {
  const { data } = await apiClient.get("/api/v1/ccd/desconto-folha/candidatos", {
    params: { todos: todos ? "true" : "false" },
  });
  return candidatosResponseSchema.parse(data);
}

export async function gerarDescontoFolha(processos: string[]): Promise<Job> {
  const { data } = await apiClient.post("/api/v1/ccd/desconto-folha/gerar", { processos });
  return jobSchema.parse(data);
}
