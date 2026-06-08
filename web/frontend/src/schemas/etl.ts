import { z } from "zod";

// Mirrors DTOs in backend/app/etl/schemas.py.

const isoDateSchema = z
  .string()
  .regex(/^\d{4}-\d{2}-\d{2}$/, { message: "Use o formato AAAA-MM-DD." });

// Mirrors ExtractionFiltersBody.
export const extractionFiltersSchema = z.object({
  start_date: isoDateSchema,
  end_date: isoDateSchema,
  process_numbers: z.array(z.string()).nullable().optional(),
  overwrite: z.boolean().optional().default(false),
});
export type ExtractionFilters = z.infer<typeof extractionFiltersSchema>;

// Mirrors ExtractionTriggerRequest. Single-shot orchestration — no kind.
export const extractionTriggerRequestSchema = z.object({
  filters: extractionFiltersSchema,
});
export type ExtractionTriggerRequest = z.infer<
  typeof extractionTriggerRequestSchema
>;

// Mirrors ExtractionJobAccepted.
export const extractionJobAcceptedSchema = z.object({
  extracao_id: z.number().int(),
  job_id: z.string(),
  status_url: z.string(),
  enqueued_at: z.string(),
});
export type ExtractionJobAccepted = z.infer<typeof extractionJobAcceptedSchema>;

export const runStatusSchema = z.enum(["queued", "running", "done", "error"]);
export type RunStatus = z.infer<typeof runStatusSchema>;

export const etapaSchema = z.enum([
  "queued",
  "decisoes",
  "obrigacoes",
  "recomendacoes",
  "done",
]);
export type Etapa = z.infer<typeof etapaSchema>;

// Mirrors ExtracaoOut.
export const extracaoOutSchema = z.object({
  id: z.number().int(),
  data_inicio: isoDateSchema,
  data_fim: isoDateSchema,
  data_execucao: z.string(),
  status: runStatusSchema,
  etapa_atual: etapaSchema,
  decisoes_processadas: z.number().int(),
  obrigacoes_geradas: z.number().int(),
  recomendacoes_geradas: z.number().int(),
  erros: z.number().int(),
  mensagem_erro: z.string().nullable().optional(),
  job_id: z.string().nullable().optional(),
});
export type ExtracaoOut = z.infer<typeof extracaoOutSchema>;

// Mirrors ExtracaoListPage.
export const extracaoListPageSchema = z.object({
  items: z.array(extracaoOutSchema),
  page: z.number().int(),
  page_size: z.number().int(),
  total: z.number().int(),
});
export type ExtracaoListPage = z.infer<typeof extracaoListPageSchema>;

// Form: dates only, end >= start.
export const triggerFormSchema = z
  .object({
    start_date: isoDateSchema,
    end_date: isoDateSchema,
  })
  .refine((v) => v.end_date >= v.start_date, {
    message: "A data final deve ser igual ou posterior à inicial.",
    path: ["end_date"],
  });
export type TriggerForm = z.infer<typeof triggerFormSchema>;

// Mirrors ExtracaoEventoOut. ``payload`` is intentionally loose — each ``tipo``
// has its own keys (id_processo, processed/total, message, ...) and the UI
// renders them opaquely.
export const extracaoEventoOutSchema = z.object({
  id: z.number().int(),
  extracao_id: z.number().int(),
  timestamp: z.string(),
  tipo: z.string(),
  payload: z.record(z.string(), z.unknown()).nullable().optional(),
});
export type ExtracaoEventoOut = z.infer<typeof extracaoEventoOutSchema>;

export const extracaoEventoListPageSchema = z.object({
  items: z.array(extracaoEventoOutSchema),
  has_more: z.boolean(),
});
export type ExtracaoEventoListPage = z.infer<
  typeof extracaoEventoListPageSchema
>;

// Mirrors DecisaoItemRow.
export const decisaoItemRowSchema = z.object({
  id: z.number().int(),
  descricao: z.string(),
  status: z.enum(["pending", "approved", "rejected"]),
});
export type DecisaoItemRow = z.infer<typeof decisaoItemRowSchema>;

// Mirrors DecisaoExtraidaItem.
export const decisaoExtraidaItemSchema = z.object({
  id_ner_decisao: z.number().int(),
  id_processo: z.number().int(),
  id_composicao_pauta: z.number().int(),
  id_voto_pauta: z.number().int(),
  data_extracao: z.string().nullable().optional(),
  obrigacoes: z.array(decisaoItemRowSchema),
  recomendacoes: z.array(decisaoItemRowSchema),
});
export type DecisaoExtraidaItem = z.infer<typeof decisaoExtraidaItemSchema>;

export const decisaoExtraidaListPageSchema = z.object({
  items: z.array(decisaoExtraidaItemSchema),
  page: z.number().int(),
  page_size: z.number().int(),
  total: z.number().int(),
});
export type DecisaoExtraidaListPage = z.infer<
  typeof decisaoExtraidaListPageSchema
>;

export const extracaoListFiltersSchema = z.object({
  status: runStatusSchema.optional(),
  start_date_from: isoDateSchema.optional(),
  start_date_to: isoDateSchema.optional(),
});
export type ExtracaoListFilters = z.infer<typeof extracaoListFiltersSchema>;
