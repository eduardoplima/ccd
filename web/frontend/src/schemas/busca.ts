// mirrors backend app/busca/schemas.py
import { z } from "zod";

const decimalNullable = z
  .union([z.string(), z.number()])
  .nullable()
  .optional()
  .transform((v) => (v === null || v === undefined ? null : Number(v)));

export const pessoaItemSchema = z.object({
  idPessoa: z.number().int(),
  cpfcnpj: z.string().nullable().optional(),
  nome: z.string(),
  qtdDebitos: z.number().int(),
});
export type PessoaItem = z.infer<typeof pessoaItemSchema>;

export const pessoaListResponseSchema = z.object({
  items: z.array(pessoaItemSchema),
  total: z.number().int(),
});
export type PessoaListResponse = z.infer<typeof pessoaListResponseSchema>;

export const processoHeaderSchema = z.object({
  idProcesso: z.number().int(),
  numeroProcesso: z.string(),
  anoProcesso: z.string(),
  assunto: z.string().nullable().optional(),
  interessado: z.string().nullable().optional(),
  valor: decimalNullable,
});
export type ProcessoHeader = z.infer<typeof processoHeaderSchema>;

export const processoResultadoSchema = z.object({
  processo: processoHeaderSchema,
  tipo: z.enum(["origem", "execucao"]),
  pessoas: z.array(pessoaItemSchema),
});
export type ProcessoResultado = z.infer<typeof processoResultadoSchema>;

export const debitoPessoaItemSchema = z.object({
  idDebito: z.number().int(),
  idProcessoOrigem: z.number().int().nullable().optional(),
  idProcessoExecucao: z.number().int().nullable().optional(),
  valorOriginalDebito: decimalNullable,
  valorPago: decimalNullable,
  dataAto: z.string().nullable().optional(),
  dataBaixa: z.string().nullable().optional(),
  matchesPessoa: z.number().int(),
  matchesGuia: z.number().int(),
});
export type DebitoPessoaItem = z.infer<typeof debitoPessoaItemSchema>;

export const debitoPessoaListResponseSchema = z.object({
  items: z.array(debitoPessoaItemSchema),
  total: z.number().int(),
});
export type DebitoPessoaListResponse = z.infer<typeof debitoPessoaListResponseSchema>;
