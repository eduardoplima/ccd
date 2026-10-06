import { apiClient } from "@/lib/api-client";
import { jobAgendaSchema, jobEnfileiradoSchema, type JobAgenda } from "@/schemas/admin-jobs";

export async function listarJobs(): Promise<JobAgenda[]> {
  const { data } = await apiClient.get("/api/v1/admin/jobs");
  return jobAgendaSchema.array().parse(data);
}

export async function executarJob(nome: string): Promise<string> {
  const { data } = await apiClient.post(`/api/v1/admin/jobs/${nome}/executar`);
  return jobEnfileiradoSchema.parse(data).job_id;
}
