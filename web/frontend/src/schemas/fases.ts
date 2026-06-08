// mirrors backend app/desconto_folha/schemas.py — 4 fases
import { z } from "zod";

const decimalLike = z.union([z.string(), z.number()]).transform((v) => Number(v));
const decimalNullable = z
  .union([z.string(), z.number()])
  .nullable()
  .optional()
  .transform((v) => (v === null || v === undefined ? null : Number(v)));

export const faseStatsSchema = z.object({
  qtd: z.number().int(),
  total: decimalNullable,
});
export type FaseStats = z.infer<typeof faseStatsSchema>;

export const fasesResumoSchema = z.object({
  totais: faseStatsSchema,
  debitosNotificados: faseStatsSchema,
  enviados: faseStatsSchema,
  agendados: faseStatsSchema,
  pagos: faseStatsSchema,
});
export type FasesResumo = z.infer<typeof fasesResumoSchema>;

export const debitoFaseSchema = z.object({
  idDebito: z.number().int(),
  idProcessoOrigem: z.number().int().nullable().optional(),
  numeroProcessoOrigem: z.string().nullable().optional(),
  anoProcessoOrigem: z.string().nullable().optional(),
  idProcessoExecucao: z.number().int().nullable().optional(),
  numeroProcessoExecucao: z.string().nullable().optional(),
  anoProcessoExecucao: z.string().nullable().optional(),
  valorOriginal: decimalLike,
  valorAtualizado: decimalNullable,
  tipoDebito: z.string().nullable().optional(),
  statusDivida: z.string().nullable().optional(),
});
export type DebitoFase = z.infer<typeof debitoFaseSchema>;

export const debitosFaseResumoSchema = z.object({
  qtdDebitos: z.number().int(),
  valorOriginalTotal: decimalLike,
  debitos: z.array(debitoFaseSchema),
});
export type DebitosFaseResumo = z.infer<typeof debitosFaseResumoSchema>;

export const notificacaoEnviadaSchema = z.object({
  idNotif: z.number().int(),
  numeroProcesso: z.string(),
  anoProcesso: z.string(),
  idDebito: z.number().int().nullable().optional(),
  idEventoCcd: z.number().int(),
  dataPublicacaoCcd: z.string().nullable().optional(),
  resumoCcd: z.string().nullable().optional(),
});
export type NotificacaoEnviada = z.infer<typeof notificacaoEnviadaSchema>;

export const enviadosListResponseSchema = z.object({
  items: z.array(notificacaoEnviadaSchema),
});
export type EnviadosListResponse = z.infer<typeof enviadosListResponseSchema>;
