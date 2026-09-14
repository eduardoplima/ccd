import { z } from "zod";

// Espelha backend/app/ccd/desconto_folha/schemas.py (JSON em camelCase).

export const statusExtracaoSchema = z.enum(["PENDENTE", "OK", "SEM_RESPOSTA", "ERRO"]);
export type StatusExtracao = z.infer<typeof statusExtracaoSchema>;

// mirrors backend NotificacaoOut
export const notificacaoSchema = z.object({
  numero: z.string().nullable().optional(),
  data: z.string().nullable().optional(),
});

// mirrors backend ArOut
export const arSchema = z.object({
  numeroPostagem: z.string().nullable().optional(),
  data: z.string().nullable().optional(),
});

// mirrors backend RespostaOut
export const respostaSchema = z.object({
  processo: z.string().nullable().optional(),
  evento: z.number().int().nullable().optional(),
  data: z.string().nullable().optional(),
});

// mirrors backend CadastroListItem
export const cadastroListItemSchema = z.object({
  id: z.number().int(),
  idProcesso: z.number().int(),
  processo: z.string(),
  idDebito: z.number().int().nullable().optional(),
  idPessoa: z.number().int().nullable().optional(),
  cpfCnpj: z.string().nullable().optional(),
  responsavel: z.string().nullable().optional(),
  idOrgao: z.number().int().nullable().optional(),
  orgao: z.string().nullable().optional(),
  notificacao: notificacaoSchema,
  ar: arSchema,
  resposta: respostaSchema,
  statusExtracao: statusExtracaoSchema,
  valorTotal: z.number().nullable().optional(),
  parcelado: z.boolean(),
  qtdValores: z.number().int(),
  qtdMatches: z.number().int(),
});
export type CadastroListItem = z.infer<typeof cadastroListItemSchema>;

// mirrors backend CadastroListResponse
export const cadastroListResponseSchema = z.object({
  items: z.array(cadastroListItemSchema),
  total: z.number().int(),
  page: z.number().int(),
  size: z.number().int(),
});
export type CadastroListResponse = z.infer<typeof cadastroListResponseSchema>;

// mirrors backend LancamentoOut
export const lancamentoSchema = z.object({
  idLancamento: z.number().int(),
  dtMovimento: z.string().nullable().optional(),
  documento: z.string().nullable().optional(),
  historico: z.string().nullable().optional(),
  valor: z.number(),
});
export type Lancamento = z.infer<typeof lancamentoSchema>;

// mirrors backend MatchOut
export const matchSchema = z.object({
  idMatch: z.number().int(),
  lancamento: lancamentoSchema,
  automatico: z.boolean(),
  dataMatch: z.string().nullable().optional(),
  observacao: z.string().nullable().optional(),
});
export type Match = z.infer<typeof matchSchema>;

// mirrors backend ValorOut
export const valorSchema = z.object({
  idValor: z.number().int(),
  numeroParcela: z.number().int(),
  mes: z.number().int().nullable().optional(),
  ano: z.number().int().nullable().optional(),
  valor: z.number(),
  origem: z.enum(["L", "M"]),
  match: matchSchema.nullable().optional(),
  candidatos: z.array(lancamentoSchema).default([]),
});
export type Valor = z.infer<typeof valorSchema>;

// mirrors backend CadastroDetalhe
export const cadastroDetalheSchema = cadastroListItemSchema.extend({
  trechoResposta: z.string().nullable().optional(),
  arquivoResposta: z.string().nullable().optional(),
  dataExtracao: z.string().nullable().optional(),
  observacoes: z.string().nullable().optional(),
  valores: z.array(valorSchema).default([]),
});
export type CadastroDetalhe = z.infer<typeof cadastroDetalheSchema>;

// mirrors backend DebitoLookup
export const debitoLookupSchema = z.object({
  idDebito: z.number().int(),
  valorOriginal: z.number().nullable().optional(),
  tipo: z.string().nullable().optional(),
  status: z.string().nullable().optional(),
  cancelado: z.boolean(),
  idPessoa: z.number().int().nullable().optional(),
  nomePessoa: z.string().nullable().optional(),
  documento: z.string().nullable().optional(),
});
export type DebitoLookup = z.infer<typeof debitoLookupSchema>;

// mirrors backend ProcessoLookup
export const processoLookupSchema = z.object({
  idProcesso: z.number().int(),
  processo: z.string(),
  orgao: z.string().nullable().optional(),
  debitos: z.array(debitoLookupSchema),
});
export type ProcessoLookup = z.infer<typeof processoLookupSchema>;

// mirrors backend CadastroInput
export type CadastroInput = {
  idProcesso: number;
  idDebito?: number | null;
  idPessoa?: number | null;
  nomeOrgao?: string | null;
  observacoes?: string | null;
};

// mirrors backend ValorInput
export type ValorInput = {
  numeroParcela: number;
  mes?: number | null;
  ano?: number | null;
  valor: number;
};

// mirrors backend MatchAutomaticoResultado
export const matchAutomaticoResultadoSchema = z.object({ vinculados: z.number().int() });
