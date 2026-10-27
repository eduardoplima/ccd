import { z } from "zod";

// mirrors backend Urgencia / Fonte
export const urgenciaSchema = z.enum(["alta", "media", "baixa"]);
export type Urgencia = z.infer<typeof urgenciaSchema>;

// mirrors backend MonitoramentoOut
export const monitoramentoSchema = z.object({
  processo: z.string(),
  id_processo: z.number().nullable().optional(),
  tipo: z.string().nullable(),
  relator: z.string().nullable(),
  assunto: z.string().nullable(),
  distribuido_a: z.string().nullable().optional(),
  distribuido_em: z.string().nullable().optional(),
  marcadores: z.array(z.string()),
  dias_ccd: z.number().nullable(),
  ultima_peca_evento: z.number().nullable(),
  ultima_peca_data: z.string().nullable(),
  ultima_peca_resumo: z.string().nullable(),
  jurisdicionado: z.string().nullable(),
  natureza: z.string().nullable(),
  proximo_passo: z.string().nullable(),
  urgencia: urgenciaSchema.nullable(),
  ficha_md: z.string().nullable(),
  fonte: z.enum(["manual", "llm", "pendente"]),
  analisado_em: z.string().nullable(),
  desatualizada: z.boolean(),
});
export type Monitoramento = z.infer<typeof monitoramentoSchema>;

// mirrors backend MonitoramentosResponse
export const monitoramentosResponseSchema = z.object({
  items: z.array(monitoramentoSchema),
  total: z.number(),
  calculado_em: z.string().nullable().optional(),
});
export type MonitoramentosResponse = z.infer<typeof monitoramentosResponseSchema>;
