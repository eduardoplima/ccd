import { z } from "zod";

// mirrors backend app/ccd/beneficios/schemas.py

export const ORIGENS_BENEFICIO = [
  "MANUAL",
  "DEBITO",
  "BOLETO",
  "PGE",
  "FOLHA",
  "DIVIDA_ATIVA",
  "FRAP",
  "PROPOSTA",
] as const;
export type OrigemBeneficio = (typeof ORIGENS_BENEFICIO)[number];

const decimalNullable = z
  .union([z.string(), z.number()])
  .nullable()
  .optional()
  .transform((v) => (v === null || v === undefined ? null : String(v)));

// mirrors backend BeneficioItem
export const beneficioItemSchema = z.object({
  idBeneficio: z.number(),
  descricao: z.string(),
  origem: z.enum(ORIGENS_BENEFICIO),
  chaveOrigem: z.string().nullable().optional(),
  idDebitoExecucao: z.number().nullable().optional(),
  dataInclusao: z.string().nullable().optional(),
  dataAtualizacao: z.string().nullable().optional(),
  memoriaCalculo: z.string().nullable().optional(),
  valorQuantidade: decimalNullable,
  justificativa: z.string().nullable().optional(),
  idSituacaoEfetivacao: z.number().nullable().optional(),
  idAreaTematica: z.number().nullable().optional(),
  idCaracterizacao: z.number().nullable().optional(),
  idUnidadeMedida: z.number().nullable().optional(),
  idSituacao: z.number().nullable().optional(),
  idTipo: z.number().nullable().optional(),
  idSubtipo: z.number().nullable().optional(),
  numeroProcessoDecisao: z.string().nullable().optional(),
  anoProcessoDecisao: z.number().nullable().optional(),
  idProcessoDecisao: z.number().nullable().optional(),
  descricaoMotivo: z.string().nullable().optional(),
  idBeneficioPotencial: z.number().nullable().optional(),
  cpfCnpj: z.string().nullable().optional(),
  nomePessoa: z.string().nullable().optional(),
  dataOcorrencia: z.string().nullable().optional(),
});
export type BeneficioItem = z.infer<typeof beneficioItemSchema>;

// mirrors backend BeneficioListResponse
export const beneficioListResponseSchema = z.object({
  items: z.array(beneficioItemSchema),
  total: z.number(),
  page: z.number(),
  size: z.number(),
});
export type BeneficioListResponse = z.infer<typeof beneficioListResponseSchema>;

// mirrors backend BeneficioResumo
export const beneficioResumoSchema = z.object({
  total: z.number(),
  qtdPotencial: z.number(),
  qtdEfetivo: z.number(),
  valorPotencial: decimalNullable,
  valorEfetivo: decimalNullable,
});
export type BeneficioResumo = z.infer<typeof beneficioResumoSchema>;

// mirrors backend MesSerie
export const mesSerieSchema = z.object({ ano: z.number(), mes: z.number(), qtd: z.number() });
export type MesSerie = z.infer<typeof mesSerieSchema>;

// mirrors backend DominioItem / DominiosResponse
export const dominioItemSchema = z.object({ id: z.number(), descricao: z.string() });
export type DominioItem = z.infer<typeof dominioItemSchema>;

export const dominiosResponseSchema = z.object({
  tipos: z.array(dominioItemSchema),
  subtipos: z.array(dominioItemSchema),
  tipoSubtipos: z.record(z.string(), z.array(z.number())),
  areasTematicas: z.array(dominioItemSchema),
  caracterizacoes: z.array(dominioItemSchema),
  situacoes: z.array(dominioItemSchema),
  situacoesEfetivacao: z.array(dominioItemSchema),
  unidadesMedida: z.array(dominioItemSchema),
});
export type DominiosResponse = z.infer<typeof dominiosResponseSchema>;
