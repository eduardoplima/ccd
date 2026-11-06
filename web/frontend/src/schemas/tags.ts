import { z } from "zod";

// Espelha backend/app/ccd/tags/schemas.py (JSON em camelCase).

export const situacaoTagSchema = z.enum(["VIGENTE", "CUMPRIDO", "RESCINDIDO", "PRORROGADO"]);
export type SituacaoTag = z.infer<typeof situacaoTagSchema>;

export const situacaoObrigacaoSchema = z.enum([
  "PENDENTE",
  "CUMPRIDA",
  "DESCUMPRIDA",
  "PRORROGADA",
]);
export type SituacaoObrigacao = z.infer<typeof situacaoObrigacaoSchema>;

export const obrigacaoSchema = z.object({
  id: z.number().int(),
  ordem: z.number().int(),
  clausula: z.string(),
  descricao: z.string(),
  prazoTexto: z.string().nullable().optional(),
  dataLimite: z.string().nullable().optional(),
  situacao: situacaoObrigacaoSchema,
  dataCumprimento: z.string().nullable().optional(),
  eventoComprovacao: z.number().int().nullable().optional(),
  observacoes: z.string().nullable().optional(),
});
export type Obrigacao = z.infer<typeof obrigacaoSchema>;

export const tagListItemSchema = z.object({
  id: z.number().int(),
  idProcesso: z.number().int(),
  processo: z.string(),
  evento: z.number().int(),
  urlEvento: z.string().nullable().optional(),
  numero: z.string(),
  orgao: z.string(),
  responsavel: z.string(),
  prazo: z.string().nullable().optional(),
  situacao: situacaoTagSchema,
  revisado: z.boolean(),
  qtdObrigacoes: z.number().int(),
  proximaDataLimite: z.string().nullable().optional(),
  dataInclusao: z.string().nullable().optional(),
});
export type TagListItem = z.infer<typeof tagListItemSchema>;

export const tagListResponseSchema = z.object({
  items: z.array(tagListItemSchema),
  total: z.number().int(),
});
export type TagListResponse = z.infer<typeof tagListResponseSchema>;

export const tagDetalheSchema = tagListItemSchema.extend({
  idInformacao: z.number().int().nullable().optional(),
  cargoResponsavel: z.string().nullable().optional(),
  cpfResponsavel: z.string().nullable().optional(),
  compromissario: z.string().nullable().optional(),
  dataCelebracao: z.string().nullable().optional(),
  homologacao: z.string().nullable().optional(),
  valorMultaDescumprimento: z.number().nullable().optional(),
  observacoes: z.string().nullable().optional(),
  textoOcr: z.string().nullable().optional(),
  obrigacoes: z.array(obrigacaoSchema),
});
export type TagDetalhe = z.infer<typeof tagDetalheSchema>;

export type ExtrairInput = { processo: string; evento: number };

export type TagPatch = Partial<{
  numero: string;
  orgao: string;
  responsavel: string;
  cargoResponsavel: string | null;
  cpfResponsavel: string | null;
  compromissario: string | null;
  dataCelebracao: string | null;
  prazo: string | null;
  homologacao: string | null;
  valorMultaDescumprimento: number | null;
  situacao: SituacaoTag;
  revisado: boolean;
  observacoes: string | null;
}>;

export type ObrigacaoInput = {
  clausula: string;
  descricao: string;
  prazoTexto: string | null;
  dataLimite: string | null;
  situacao: SituacaoObrigacao;
  dataCumprimento: string | null;
  eventoComprovacao: number | null;
  observacoes: string | null;
};
