import { apiClient } from "@/lib/api-client";
import {
  deletarFinalizadosResponseSchema,
  jobListResponseSchema,
  jobSchema,
  uploadExtratoResponseSchema,
  type DeletarFinalizadosResponse,
  type Job,
  type JobListResponse,
  type UploadExtratoResponse,
} from "@/schemas/job";

export async function listJobs(page: number, size: number): Promise<JobListResponse> {
  const { data } = await apiClient.get("/api/v1/frap/jobs", { params: { page, size } });
  return jobListResponseSchema.parse(data);
}

export async function getJob(id: number): Promise<Job> {
  const { data } = await apiClient.get(`/api/v1/frap/jobs/${id}`);
  return jobSchema.parse(data);
}

export async function disparaParseExtratos(): Promise<Job> {
  const { data } = await apiClient.post("/api/v1/frap/jobs/parse-extratos");
  return jobSchema.parse(data);
}

export async function disparaConciliar(ano: number, mes: number): Promise<Job> {
  const { data } = await apiClient.post("/api/v1/frap/jobs/conciliar", { ano, mes });
  return jobSchema.parse(data);
}

export async function disparaConciliarTodos(ano: number): Promise<{ ano: number; jobs: Job[] }> {
  const { data } = await apiClient.post("/api/v1/frap/jobs/conciliar-todos", null, { params: { ano } });
  return { ano: data.ano, jobs: (data.jobs as unknown[]).map((j) => jobSchema.parse(j)) };
}

export async function cancelarJob(id: number): Promise<Job> {
  const { data } = await apiClient.post(`/api/v1/frap/jobs/${id}/cancelar`);
  return jobSchema.parse(data);
}

export async function deletarJob(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/frap/jobs/${id}`);
}

export async function deletarFinalizados(tipo?: string): Promise<DeletarFinalizadosResponse> {
  const { data } = await apiClient.delete("/api/v1/frap/jobs/finalizados", {
    params: tipo ? { tipo } : undefined,
  });
  return deletarFinalizadosResponseSchema.parse(data);
}

export async function uploadExtrato(
  conta: string,
  periodo: string,
  arquivo: File,
): Promise<UploadExtratoResponse> {
  const form = new FormData();
  form.append("arquivo", arquivo);
  const { data } = await apiClient.post("/api/v1/frap/extratos/upload", form, {
    params: { conta, periodo },
    headers: { "Content-Type": "multipart/form-data" },
  });
  return uploadExtratoResponseSchema.parse(data);
}
