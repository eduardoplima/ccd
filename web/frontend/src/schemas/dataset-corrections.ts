import { z } from "zod";

// Mirrors DTOs in backend/app/dataset_corrections/schemas.py.
// Field names and types must stay one-to-one with the Pydantic source.

export const decisionStatusSchema = z.enum(["pending", "accept", "reject", "custom", "mixed"]);
export type DecisionStatus = z.infer<typeof decisionStatusSchema>;

export const decisionKindSchema = z.enum(["accept", "reject", "custom"]);
export type DecisionKind = z.infer<typeof decisionKindSchema>;

export const nerSpanSchema = z.object({
  char_start: z.number().int(),
  char_end: z.number().int(),
  label: z.string(),
});
export type NerSpan = z.infer<typeof nerSpanSchema>;

export const tokenInGroupSchema = z.object({
  token_idx_in_doc: z.number().int(),
  text: z.string(),
  char_start: z.number().int(),
  char_end: z.number().int(),
  bio_original: z.string(),
  label_sugerido: z.string().nullable().optional(),
  confianca: z.number().nullable().optional(),
  row_id: z.number().int().nullable().optional(),
  is_flagged: z.boolean(),
});
export type TokenInGroup = z.infer<typeof tokenInGroupSchema>;

export const entityGroupSchema = z.object({
  group_id: z.string(),
  document_id: z.number().int(),
  first_token_idx: z.number().int(),
  last_token_idx: z.number().int(),
  char_start: z.number().int(),
  char_end: z.number().int(),
  gold_entity_label: z.string().nullable().optional(),
  tokens: z.array(tokenInGroupSchema),
  flagged_row_ids: z.array(z.number().int()),
  status: decisionStatusSchema,
  entity_label_final: z.string().nullable().optional(),
  decided_by: z.string().nullable().optional(),
  decided_at: z.string().nullable().optional(),
});
export type EntityGroup = z.infer<typeof entityGroupSchema>;

export const documentListItemSchema = z.object({
  document_id: z.number().int(),
  text_preview: z.string(),
  group_count: z.number().int(),
  decided_group_count: z.number().int(),
});
export type DocumentListItem = z.infer<typeof documentListItemSchema>;

export const documentListPageSchema = z.object({
  items: z.array(documentListItemSchema),
  page: z.number().int(),
  page_size: z.number().int(),
  total: z.number().int(),
});
export type DocumentListPage = z.infer<typeof documentListPageSchema>;

export const documentTokenSchema = z.object({
  token_idx_in_doc: z.number().int(),
  text: z.string(),
  char_start: z.number().int(),
  char_end: z.number().int(),
  bio: z.string(),
});
export type DocumentToken = z.infer<typeof documentTokenSchema>;

export const documentDetailSchema = z.object({
  document_id: z.number().int(),
  text: z.string(),
  ner_spans: z.array(nerSpanSchema),
  groups: z.array(entityGroupSchema),
  tokens: z.array(documentTokenSchema),
});
export type DocumentDetail = z.infer<typeof documentDetailSchema>;

export const groupDecisionRequestSchema = z.object({
  decision: decisionKindSchema,
  entity_label: z.string().nullable().optional(),
  first_token_idx: z.number().int().nullable().optional(),
  last_token_idx: z.number().int().nullable().optional(),
});
export type GroupDecisionRequest = z.infer<typeof groupDecisionRequestSchema>;

export const groupDecisionResponseSchema = z.object({
  group_id: z.string(),
  status: decisionStatusSchema,
  entity_label_final: z.string().nullable(),
  decided_by: z.string().nullable(),
  decided_at: z.string().nullable(),
});
export type GroupDecisionResponse = z.infer<typeof groupDecisionResponseSchema>;

export const unmappedErrorSchema = z.object({
  row_id: z.number().int(),
  sentenca_idx: z.number().int(),
  token: z.string(),
  contexto: z.string(),
  label_original: z.string(),
  label_sugerido: z.string(),
  confianca: z.number(),
  status: decisionStatusSchema,
  label_final: z.string().nullable().optional(),
  decided_by: z.string().nullable().optional(),
  decided_at: z.string().nullable().optional(),
});
export type UnmappedError = z.infer<typeof unmappedErrorSchema>;

export const unmappedListPageSchema = z.object({
  items: z.array(unmappedErrorSchema),
  page: z.number().int(),
  page_size: z.number().int(),
  total: z.number().int(),
});
export type UnmappedListPage = z.infer<typeof unmappedListPageSchema>;

export const unmappedDecisionRequestSchema = z.object({
  decision: decisionKindSchema,
  label_final: z.string().nullable().optional(),
});
export type UnmappedDecisionRequest = z.infer<typeof unmappedDecisionRequestSchema>;

export const unmappedDecisionResponseSchema = z.object({
  row_id: z.number().int(),
  status: decisionStatusSchema,
  label_final: z.string().nullable(),
  decided_by: z.string().nullable(),
  decided_at: z.string().nullable(),
});
export type UnmappedDecisionResponse = z.infer<typeof unmappedDecisionResponseSchema>;

export const progressSchema = z.object({
  total: z.number().int(),
  decided: z.number().int(),
  accept: z.number().int(),
  reject: z.number().int(),
  custom: z.number().int(),
  mixed: z.number().int(),
  unmapped_total: z.number().int(),
  unmapped_decided: z.number().int(),
});
export type Progress = z.infer<typeof progressSchema>;

export const labelsResponseSchema = z.object({
  labels: z.array(z.string()),
  entity_labels: z.array(z.string()),
});
export type LabelsResponse = z.infer<typeof labelsResponseSchema>;
