import { z } from "zod";

// mirrors backend JobAgendaOut
export const jobAgendaSchema = z.object({
  nome: z.string(),
  descricao: z.string(),
  cron: z.string().nullable(),
  horario_brasilia: z.string().nullable(),
});
export type JobAgenda = z.infer<typeof jobAgendaSchema>;

// mirrors backend JobEnfileiradoOut
export const jobEnfileiradoSchema = z.object({ job_id: z.string() });
