import { z } from "zod";

// mirrors backend ProcessoCCDOut
export const processoCCDSchema = z.object({
  processo: z.string(),
  numero_processo: z.string(),
  ano_processo: z.string(),
  marcador: z.string().nullable(),
  data_marcador: z.string().nullable(),
  origem: z.string().nullable(),
  relator: z.string().nullable(),
  tipo: z.string().nullable(),
  assunto: z.string().nullable(),
});
export type ProcessoCCD = z.infer<typeof processoCCDSchema>;

// mirrors backend ProcessoCCDListResponse
export const processoCCDListResponseSchema = z.object({
  items: z.array(processoCCDSchema),
  total: z.number(),
  page: z.number(),
  size: z.number(),
});
export type ProcessoCCDListResponse = z.infer<typeof processoCCDListResponseSchema>;

// mirrors backend RelatorOption
export const relatorOptionSchema = z.object({
  codigo: z.string(),
  nome: z.string(),
});
export type RelatorOption = z.infer<typeof relatorOptionSchema>;

// mirrors backend MarcadorOption
export const marcadorOptionSchema = z.object({
  descricao: z.string(),
  quantidade: z.number(),
});
export type MarcadorOption = z.infer<typeof marcadorOptionSchema>;

// mirrors backend FiltrosCCDResponse
export const filtrosCCDResponseSchema = z.object({
  marcadores: z.array(marcadorOptionSchema),
  sem_marcador: z.number(),
  relatores: z.array(relatorOptionSchema),
});
export type FiltrosCCDResponse = z.infer<typeof filtrosCCDResponseSchema>;
