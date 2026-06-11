import { z } from "zod";

// mirrors backend CandidatoOut
export const candidatoSchema = z.object({
  processo: z.string(),
  assunto: z.string().nullable(),
});
export type Candidato = z.infer<typeof candidatoSchema>;

// mirrors backend CandidatosResponse
export const candidatosResponseSchema = z.object({
  items: z.array(candidatoSchema),
  total: z.number(),
});
export type CandidatosResponse = z.infer<typeof candidatosResponseSchema>;

// mirrors backend GerarRequest
export const gerarRequestSchema = z.object({
  processos: z.array(z.string()),
});
export type GerarRequest = z.infer<typeof gerarRequestSchema>;
