import { z } from "zod";

// mirrors backend app.cgad.dataset.schemas

export const LABELS = ["MULTA", "OBRIGACAO", "RECOMENDACAO", "RESSARCIMENTO"] as const;

export const spanSchema = z.object({
  start: z.number().int(),
  end: z.number().int(),
  label: z.enum(LABELS),
});

export const documentoListItemSchema = z.object({
  id: z.number().int(),
  processo: z.string().nullable(),
  codigo_tipo_processo: z.string().nullable(),
  data_sessao: z.string().nullable(),
  origem: z.enum(["decicontas", "ampliacao"]),
  trecho: z.string(),
  status: z.enum(["pending", "done"]),
  total_spans: z.number().int(),
});

export const documentoListPageSchema = z.object({
  items: z.array(documentoListItemSchema),
  page: z.number().int(),
  page_size: z.number().int(),
  total: z.number().int(),
  pendentes: z.number().int(),
  concluidos: z.number().int(),
  com_entidades: z.number().int(),
});

export const documentoDetailSchema = z.object({
  id: z.number().int(),
  processo: z.string().nullable(),
  codigo_tipo_processo: z.string().nullable(),
  data_sessao: z.string().nullable(),
  origem: z.enum(["decicontas", "ampliacao"]),
  texto: z.string(),
  spans: z.array(spanSchema),
  status: z.enum(["pending", "done"]),
  data_conclusao: z.string().nullable(),
  proximo_pendente: z.number().int().nullable(),
});

export const progressoSchema = z.object({
  documentos: z.number().int(),
  anotadores: z.array(
    z.object({
      anotador: z.string(),
      total: z.number().int(),
      concluidos: z.number().int(),
      spans: z.number().int(),
    }),
  ),
  concordancia: z.array(
    z.object({
      a: z.string(),
      b: z.string(),
      documentos_comuns: z.number().int(),
      f1: z.number().nullable(),
    }),
  ),
});

export type Label = (typeof LABELS)[number];
export type Span = z.infer<typeof spanSchema>;
export type DocumentoListItem = z.infer<typeof documentoListItemSchema>;
export type DocumentoListPage = z.infer<typeof documentoListPageSchema>;
export type DocumentoDetail = z.infer<typeof documentoDetailSchema>;
export type Progresso = z.infer<typeof progressoSchema>;
