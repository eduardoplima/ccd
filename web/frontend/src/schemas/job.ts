import { z } from "zod";

export const jobStatusSchema = z.enum(["pending", "running", "done", "failed", "cancelled"]);
export type JobStatus = z.infer<typeof jobStatusSchema>;

export const jobSchema = z.object({
  idJob: z.number(),
  arqJobId: z.string(),
  tipo: z.string(),
  argumentos: z.string().nullable().optional(),
  status: jobStatusSchema,
  idUsuario: z.number(),
  dataCriacao: z.string(),
  dataInicio: z.string().nullable().optional(),
  dataFim: z.string().nullable().optional(),
  erroMensagem: z.string().nullable().optional(),
  resultado: z.string().nullable().optional(),
});
export type Job = z.infer<typeof jobSchema>;

export const jobListResponseSchema = z.object({
  items: z.array(jobSchema),
  total: z.number(),
  page: z.number(),
  size: z.number(),
});
export type JobListResponse = z.infer<typeof jobListResponseSchema>;

export const uploadExtratoResponseSchema = z.object({
  conta: z.string(),
  periodo: z.string(),
  bytes: z.number(),
  caminho: z.string(),
});
export type UploadExtratoResponse = z.infer<typeof uploadExtratoResponseSchema>;

export const deletarFinalizadosResponseSchema = z.object({
  deletados: z.number(),
});
export type DeletarFinalizadosResponse = z.infer<typeof deletarFinalizadosResponseSchema>;
