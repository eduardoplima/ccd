import { z } from "zod";

// All schemas in this file mirror DTOs in backend/app/cgad/review/schemas.py.
// Field names and types must stay one-to-one with the Pydantic source —
// mismatches cause silent data loss on approve.

export const tipoEntidadeSchema = z.enum(["multa", "obrigacao", "recomendacao", "ressarcimento"]);
export type TipoEntidade = z.infer<typeof tipoEntidadeSchema>;

export const reviewStatusSchema = z.enum(["pending", "approved", "rejected"]);
export type ReviewStatus = z.infer<typeof reviewStatusSchema>;

export const spanMatchStatusSchema = z.enum(["exact", "fuzzy", "not_found"]);
export type SpanMatchStatus = z.infer<typeof spanMatchStatusSchema>;

// Pydantic `date` — ISO yyyy-mm-dd on the wire.
const isoDateSchema = z.string().regex(/^\d{4}-\d{2}-\d{2}$/, { message: "Data inválida." });

// Mirrors SolidarioMulta in backend schemas.
export const solidarioMultaSchema = z.object({
  nome: z.string().trim().min(1, { message: "Informe o nome do solidário." }),
  documento: z.string().nullable().optional(),
});
export type SolidarioMulta = z.infer<typeof solidarioMultaSchema>;

// Mirrors PessoaCargo in backend schemas.
export const pessoaCargoSchema = z.object({
  fonte: z.enum(["anexo42", "siai_pessoal"]),
  cargo: z.string(),
  orgao: z.string().nullable().optional(),
  inicio: z.string().nullable().optional(), // date ISO
  fim: z.string().nullable().optional(),
});
export type PessoaCargo = z.infer<typeof pessoaCargoSchema>;

// Mirrors Pessoa in backend schemas.
export const pessoaSchema = z.object({
  nome: z.string(),
  documento: z.string().nullable().optional(),
  cargos: z.array(pessoaCargoSchema).default([]),
});
export type Pessoa = z.infer<typeof pessoaSchema>;

// mirrors backend OrgaoOut
export const orgaoSchema = z.object({
  id: z.number().int(),
  nome: z.string(),
});
export type Orgao = z.infer<typeof orgaoSchema>;

// ----- Per-type editable fields (mirror *Fields in backend schemas) ---------
// `tipo` is injected when the payload is built; the form schemas below omit it.

export const multaFieldsSchema = z.object({
  descricao_multa: z.string().trim().min(1, { message: "Descreva a multa." }),
  valor_fixo: z.number().nullable().optional(),
  percentual: z.number().nullable().optional(),
  base_calculo: z.number().nullable().optional(),
  nome_responsavel: z.string().nullable().optional(),
  documento_responsavel: z.string().nullable().optional(),
  e_multa_solidaria: z.boolean().nullable().optional(),
  solidarios: z.array(solidarioMultaSchema).nullable().optional(),
});
export type MultaFields = z.infer<typeof multaFieldsSchema>;

export const obrigacaoFieldsSchema = z.object({
  descricao_obrigacao: z.string().trim().min(1, { message: "Descreva a obrigação." }),
  de_fazer: z.boolean().nullable().optional(),
  prazo: z.string().nullable().optional(),
  data_cumprimento: isoDateSchema.nullable().optional(),
  orgao_responsavel: z.string().nullable().optional(),
  id_orgao_responsavel: z.number().int().nullable().optional(),
  tem_multa_cominatoria: z.boolean().nullable().optional(),
  nome_responsavel_multa_cominatoria: z.string().nullable().optional(),
  documento_responsavel_multa_cominatoria: z.string().nullable().optional(),
  id_pessoa_multa_cominatoria: z.number().int().nullable().optional(),
  valor_multa_cominatoria: z.number().nullable().optional(),
  periodo_multa_cominatoria: z.string().nullable().optional(),
  e_multa_cominatoria_solidaria: z.boolean().nullable().optional(),
  solidarios_multa_cominatoria: z.array(solidarioMultaSchema).nullable().optional(),
});
export type ObrigacaoFields = z.infer<typeof obrigacaoFieldsSchema>;

export const recomendacaoFieldsSchema = z.object({
  descricao_recomendacao: z.string().trim().min(1, { message: "Descreva a recomendação." }),
  prazo_cumprimento_recomendacao: z.string().nullable().optional(),
  data_cumprimento_recomendacao: isoDateSchema.nullable().optional(),
  nome_responsavel: z.string().nullable().optional(),
  id_pessoa_responsavel: z.number().int().nullable().optional(),
  orgao_responsavel: z.string().nullable().optional(),
  id_orgao_responsavel: z.number().int().nullable().optional(),
  cancelado: z.boolean().nullable().optional(),
});
export type RecomendacaoFields = z.infer<typeof recomendacaoFieldsSchema>;

export const ressarcimentoFieldsSchema = z.object({
  descricao_ressarcimento: z.string().trim().min(1, { message: "Descreva o ressarcimento." }),
  valor_dano: z.number().nullable().optional(),
  percentual_imputado: z.number().nullable().optional(),
  valor_imputado: z.number().nullable().optional(),
  nome_responsavel: z.string().nullable().optional(),
  documento_responsavel: z.string().nullable().optional(),
});
export type RessarcimentoFields = z.infer<typeof ressarcimentoFieldsSchema>;

export const fieldsSchemaByTipo = {
  multa: multaFieldsSchema,
  obrigacao: obrigacaoFieldsSchema,
  recomendacao: recomendacaoFieldsSchema,
  ressarcimento: ressarcimentoFieldsSchema,
} as const;

export type EntidadeFields =
  | MultaFields
  | ObrigacaoFields
  | RecomendacaoFields
  | RessarcimentoFields;

// ----- Approve payload (mirrors EntidadeReview / DecisaoReviewPayload) ------

export type EntidadeReview = {
  tipo: TipoEntidade;
  id_ner: number | null;
  resultado: "approved" | "rejected";
  observacoes?: string | null;
  // Backend discriminated union requires `tipo` inside campos too.
  campos?: (EntidadeFields & { tipo: TipoEntidade }) | null;
};

export type DecisaoReviewPayload = {
  entidades: EntidadeReview[];
};

// ----- List / detail responses ----------------------------------------------

// Mirrors DecisaoListItem in backend schemas.
export const decisaoListItemSchema = z.object({
  id: z.number().int(),
  id_processo: z.number().int(),
  id_composicao_pauta: z.number().int(),
  id_voto_pauta: z.number().int(),
  numero_processo: z.number().int().nullable().optional(),
  ano_processo: z.number().int().nullable().optional(),
  // Número do acórdão/decisão colegiada; tipo: "A" = Acórdão, "D" = Decisão.
  numero_acordao: z.string().nullable().optional(),
  ano_acordao: z.string().nullable().optional(),
  tipo_acordao: z.string().nullable().optional(),
  data_extracao: z.string().datetime({ offset: true }).nullable().optional(),
  multas: z.number().int(),
  obrigacoes: z.number().int(),
  recomendacoes: z.number().int(),
  ressarcimentos: z.number().int(),
  claimed_by: z.string().nullable().optional(),
  claimed_at: z.string().datetime({ offset: true }).nullable().optional(),
});
export type DecisaoListItem = z.infer<typeof decisaoListItemSchema>;

// Mirrors DecisaoListPage in backend schemas.
export const decisaoListPageSchema = z.object({
  items: z.array(decisaoListItemSchema),
  page: z.number().int(),
  page_size: z.number().int(),
  total: z.number().int(),
});
export type DecisaoListPage = z.infer<typeof decisaoListPageSchema>;

// Mirrors EntidadeOut in backend schemas.
export const entidadeOutSchema = z.object({
  tipo: tipoEntidadeSchema,
  id_ner: z.number().int(),
  descricao: z.string(),
  status: reviewStatusSchema,
  campos: z.record(z.string(), z.unknown()),
  reviewer: z.string().nullable().optional(),
  reviewed_at: z.string().datetime({ offset: true }).nullable().optional(),
  observacoes: z.string().nullable().optional(),
});
export type EntidadeOut = z.infer<typeof entidadeOutSchema>;

// Mirrors DecisaoDetail in backend schemas.
export const decisaoDetailSchema = z.object({
  id: z.number().int(),
  id_processo: z.number().int(),
  id_composicao_pauta: z.number().int(),
  id_voto_pauta: z.number().int(),
  data_extracao: z.string().datetime({ offset: true }).nullable().optional(),
  claimed_by: z.string().nullable().optional(),
  claimed_at: z.string().datetime({ offset: true }).nullable().optional(),
  revisado_por: z.string().nullable().optional(),
  data_revisao: z.string().datetime({ offset: true }).nullable().optional(),
  entidades: z.array(entidadeOutSchema),
  proximo_id: z.number().int().nullable().optional(),
});
export type DecisaoDetail = z.infer<typeof decisaoDetailSchema>;

// Mirrors EntidadeSpan in backend schemas.
export const entidadeSpanSchema = z.object({
  id_ner: z.number().int(),
  tipo: tipoEntidadeSchema,
  char_start: z.number().int().nullable().optional(),
  char_end: z.number().int().nullable().optional(),
  match_status: spanMatchStatusSchema,
});
export type EntidadeSpan = z.infer<typeof entidadeSpanSchema>;

// Mirrors DecisaoTexto in backend schemas.
export const decisaoTextoSchema = z.object({
  texto_acordao: z.string().nullable().optional(),
  numero_processo: z.number().int().nullable().optional(),
  ano_processo: z.number().int().nullable().optional(),
  numero_acordao: z.string().nullable().optional(),
  ano_acordao: z.string().nullable().optional(),
  tipo_acordao: z.string().nullable().optional(),
  pessoas: z.array(pessoaSchema).default([]),
  relatorio: z.string().nullable().optional(),
  fundamentacao_voto: z.string().nullable().optional(),
  conclusao: z.string().nullable().optional(),
  orgao_responsavel: z.string().nullable().optional(),
  orgao_origem: z.string().nullable().optional(),
  interessado: z.string().nullable().optional(),
  spans: z.array(entidadeSpanSchema).default([]),
});
export type DecisaoTexto = z.infer<typeof decisaoTextoSchema>;

// Mirrors AwaitingDispatchItem in backend schemas.
export const awaitingDispatchItemSchema = z.object({
  id: z.number().int(),
  tipo: tipoEntidadeSchema,
  id_processo: z.number().int(),
  numero_processo: z.number().int().nullable().optional(),
  ano_processo: z.number().int().nullable().optional(),
  descricao: z.string(),
  reviewer: z.string().nullable().optional(),
  reviewed_at: z.string().datetime({ offset: true }).nullable().optional(),
});
export type AwaitingDispatchItem = z.infer<typeof awaitingDispatchItemSchema>;

// Mirrors AwaitingDispatchPage in backend schemas.
export const awaitingDispatchPageSchema = z.object({
  items: z.array(awaitingDispatchItemSchema),
  page: z.number().int(),
  page_size: z.number().int(),
  total: z.number().int(),
});
export type AwaitingDispatchPage = z.infer<typeof awaitingDispatchPageSchema>;

// Mirrors ClaimResponse in backend schemas.
export const claimResponseSchema = z.object({
  claimed_by: z.string(),
  claimed_at: z.string().datetime({ offset: true }),
});
export type ClaimResponse = z.infer<typeof claimResponseSchema>;

// ----- UI labels --------------------------------------------------------------

export const TIPO_LABEL: Record<TipoEntidade, string> = {
  multa: "Multa",
  obrigacao: "Obrigação",
  recomendacao: "Recomendação",
  ressarcimento: "Ressarcimento",
};
