import { z } from "zod";

// mirrors backend MatchResumo
export const matchResumoSchema = z.object({
  matcher: z.enum(["OB", "PESSOA", "GUIA", "DESCONTO_FOLHA"]),
  status: z.string(),
  quantidade: z.number(),
});
export type MatchResumo = z.infer<typeof matchResumoSchema>;

// mirrors backend LancamentoListItem
export const lancamentoSchema = z.object({
  idLancamento: z.number(),
  conta: z.string(),
  periodo: z.string(),
  dtMovimento: z.string(),
  dtBalancete: z.string().nullable().optional(),
  agOrigem: z.string().nullable().optional(),
  lote: z.string().nullable().optional(),
  historico: z.string(),
  documento: z.string().nullable().optional(),
  docData: z.string().nullable().optional(),
  valor: z.union([z.string(), z.number()]).transform((v) => Number(v)),
  valorDC: z.enum(["C", "D"]),
  descricao: z.string().nullable().optional(),
  categoria: z.string(),
  cpfcnpjDepositante: z.string().nullable().optional(),
  matchesResumo: z.array(matchResumoSchema).default([]),
});
export type Lancamento = z.infer<typeof lancamentoSchema>;

// mirrors backend LancamentoListResponse
export const lancamentoListResponseSchema = z.object({
  items: z.array(lancamentoSchema),
  total: z.number(),
  page: z.number(),
  size: z.number(),
});
export type LancamentoListResponse = z.infer<typeof lancamentoListResponseSchema>;

export const CATEGORIAS = [
  "OB_RECEBIDA",
  "GUIA_RECEBIMENTO",
  "TRANSFERENCIA",
  "APLICACAO_RESGATE",
  "SALDO",
  "OUTROS",
] as const;
export type Categoria = (typeof CATEGORIAS)[number];

export const CONTAS = ["700000-6", "600000-2"] as const;
export type Conta = (typeof CONTAS)[number];

// ---------- Detalhe ----------

const matchBase = z.object({
  idMatch: z.number(),
  status: z.string(),
  statusDescricao: z.string().nullable().optional(),
});

const decimalLike = z.union([z.string(), z.number()]).transform((v) => Number(v));

export const matchOBSchema = matchBase.extend({
  matcher: z.literal("OB"),
  anoSigef: z.number().nullable().optional(),
  cdUnidadeGestora: z.number().nullable().optional(),
  cdGestao: z.number().nullable().optional(),
  nuOrdemBancaria: z.string().nullable().optional(),
  dataPagamento: z.string().nullable().optional(),
  valorOB: decimalLike.nullable().optional(),
  cdCredor: z.string().nullable().optional(),
  nmCredor: z.string().nullable().optional(),
  nuPreparacaoPagamento: z.string().nullable().optional(),
  nuNotaEmpenho: z.string().nullable().optional(),
});

export const matchPessoaSchema = matchBase.extend({
  matcher: z.literal("PESSOA"),
  idDebito: z.number().nullable().optional(),
  idProcessoExecucao: z.number().nullable().optional(),
  cpfcnpj: z.string().nullable().optional(),
  nomePessoa: z.string().nullable().optional(),
  valorPago: decimalLike.nullable().optional(),
  valorAPagar: decimalLike.nullable().optional(),
  valorOriginalDebito: decimalLike.nullable().optional(),
  valorCasadoEm: z.string().nullable().optional(),
});

export const matchGuiaSchema = matchBase.extend({
  matcher: z.literal("GUIA"),
  idBoleto: z.number().nullable().optional(),
  idDebito: z.number().nullable().optional(),
  idProcessoExecucao: z.number().nullable().optional(),
  codigoBarras: z.string().nullable().optional(),
  dataPagamento: z.string().nullable().optional(),
  valorPago: decimalLike.nullable().optional(),
  nomePessoa: z.string().nullable().optional(),
  cpfcnpj: z.string().nullable().optional(),
});

export const matchDescontoFolhaSchema = matchBase.extend({
  matcher: z.literal("DESCONTO_FOLHA"),
  idParcela: z.number().nullable().optional(),
  numeroParcela: z.number().nullable().optional(),
  mesReferencia: z.number().nullable().optional(),
  anoReferencia: z.number().nullable().optional(),
  valorEsperado: decimalLike.nullable().optional(),
  cpfcnpj: z.string().nullable().optional(),
  nomePessoa: z.string().nullable().optional(),
  idContrachequeItem: z.number().nullable().optional(),
  valorContracheque: decimalLike.nullable().optional(),
});

export const matchSchema = z.discriminatedUnion("matcher", [
  matchOBSchema,
  matchPessoaSchema,
  matchGuiaSchema,
  matchDescontoFolhaSchema,
]);
export type Match = z.infer<typeof matchSchema>;
export type MatchOB = z.infer<typeof matchOBSchema>;
export type MatchPessoa = z.infer<typeof matchPessoaSchema>;
export type MatchGuia = z.infer<typeof matchGuiaSchema>;
export type MatchDescontoFolha = z.infer<typeof matchDescontoFolhaSchema>;

// mirrors backend LancamentoDetail
export const lancamentoDetailSchema = lancamentoSchema.omit({ matchesResumo: true }).extend({
  cpfcnpjAmbiguo: z.boolean(),
  nomeArquivo: z.string().nullable().optional(),
  matches: z.array(matchSchema).default([]),
});
export type LancamentoDetail = z.infer<typeof lancamentoDetailSchema>;

export const MATCHER_LABEL: Record<MatchResumo["matcher"], string> = {
  OB: "OB",
  PESSOA: "Pessoa",
  GUIA: "Guia",
  DESCONTO_FOLHA: "Desconto-Folha",
};
