import { apiClient } from "@/lib/api-client";
import { jobSchema, type Job } from "@/schemas/job";
import {
  candidatosAntecedentesResponseSchema,
  type CandidatosAntecedentesResponse,
} from "@/schemas/ccd-antecedentes";

export async function listCandidatosAntecedentes(
  todos: boolean,
): Promise<CandidatosAntecedentesResponse> {
  const { data } = await apiClient.get("/api/v1/ccd/antecedentes/candidatos", {
    params: { todos: todos ? "true" : "false" },
  });
  return candidatosAntecedentesResponseSchema.parse(data);
}

export async function gerarAntecedentes(processos: string[]): Promise<Job> {
  const { data } = await apiClient.post("/api/v1/ccd/antecedentes/gerar", { processos });
  return jobSchema.parse(data);
}
