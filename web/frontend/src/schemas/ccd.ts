import { z } from "zod";

// mirrors backend ProcessoCCDOut
export const processoCCDSchema = z.object({
  processo: z.string(),
  numero_processo: z.string(),
  ano_processo: z.string(),
  marcador: z.string().nullable(),
  data_marcador: z.string().nullable(),
  entrada_ccd: z.string().nullable(),
  dias_ccd: z.number().nullable(),
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

// mirrors backend PrescricaoCCDOut
export const prescricaoCCDSchema = z.object({
  processo: z.string(),
  numero_processo: z.string(),
  ano_processo: z.string(),
  relator: z.string().nullable(),
  assunto: z.string().nullable(),
  responsaveis: z.string().nullable(),
  categoria: z.enum(["prescrito", "risco", "ok", "sem_referencia"]),
  fonte_base: z.string().nullable(),
  data_base: z.string().nullable(),
  data_prescricao: z.string().nullable(),
  dias_decorridos: z.number().nullable(),
  qtd_debitos: z.number(),
  valor_total: z.number(),
});
export type PrescricaoCCD = z.infer<typeof prescricaoCCDSchema>;

// mirrors backend PrescricaoCCDListResponse
export const prescricaoCCDListResponseSchema = z.object({
  items: z.array(prescricaoCCDSchema),
  total: z.number(),
});
export type PrescricaoCCDListResponse = z.infer<typeof prescricaoCCDListResponseSchema>;

// mirrors backend FiltrosCCDResponse
export const filtrosCCDResponseSchema = z.object({
  marcadores: z.array(marcadorOptionSchema),
  sem_marcador: z.number(),
  relatores: z.array(relatorOptionSchema),
});
export type FiltrosCCDResponse = z.infer<typeof filtrosCCDResponseSchema>;
