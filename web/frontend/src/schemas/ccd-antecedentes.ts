import { z } from "zod";

// mirrors backend CandidatoAntecedentes
export const candidatoAntecedentesSchema = z.object({
  processo: z.string(),
  assunto: z.string().nullable(),
  interessado: z.string().nullable(),
});
export type CandidatoAntecedentes = z.infer<typeof candidatoAntecedentesSchema>;

// mirrors backend CandidatosAntecedentesResponse
export const candidatosAntecedentesResponseSchema = z.object({
  items: z.array(candidatoAntecedentesSchema),
  total: z.number(),
});
export type CandidatosAntecedentesResponse = z.infer<typeof candidatosAntecedentesResponseSchema>;

// mirrors backend GerarAntecedentesRequest
export const gerarAntecedentesRequestSchema = z.object({
  processos: z.array(z.string()),
});
export type GerarAntecedentesRequest = z.infer<typeof gerarAntecedentesRequestSchema>;
