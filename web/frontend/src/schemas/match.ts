import { z } from "zod";

const decimal = z.union([z.string(), z.number()]).transform((v) => Number(v));

const lancamentoCtx = {
  idLancamento: z.number().nullable().optional(),
  dtMovimento: z.string().nullable().optional(),
  valorLancamento: decimal.nullable().optional(),
  valorDC: z.string().nullable().optional(),
  historico: z.string().nullable().optional(),
  documentoExtrato: z.string().nullable().optional(),
};

const common = {
  idMatch: z.number(),
  status: z.string(),
  statusDescricao: z.string().nullable().optional(),
  conta: z.string(),
  periodo: z.string(),
};

export const matchOBListItemSchema = z.object({
  matcher: z.literal("OB"),
  ...common,
  ...lancamentoCtx,
  anoSigef: z.number(),
  nuOrdemBancaria: z.string().nullable().optional(),
  cdUnidadeGestora: z.number().nullable().optional(),
  dataPagamento: z.string().nullable().optional(),
  valorOB: decimal.nullable().optional(),
  cdCredor: z.string().nullable().optional(),
  nmCredor: z.string().nullable().optional(),
});
export type MatchOBListItem = z.infer<typeof matchOBListItemSchema>;

export const matchPessoaListItemSchema = z.object({
  matcher: z.literal("PESSOA"),
  ...common,
  ...lancamentoCtx,
  idDebito: z.number().nullable().optional(),
  cpfcnpj: z.string().nullable().optional(),
  nomePessoa: z.string().nullable().optional(),
  valorPago: decimal.nullable().optional(),
  valorAPagar: decimal.nullable().optional(),
  valorCasadoEm: z.string().nullable().optional(),
});
export type MatchPessoaListItem = z.infer<typeof matchPessoaListItemSchema>;

export const matchGuiaListItemSchema = z.object({
  matcher: z.literal("GUIA"),
  ...common,
  ...lancamentoCtx,
  idBoleto: z.number().nullable().optional(),
  idDebito: z.number().nullable().optional(),
  codigoBarras: z.string().nullable().optional(),
  dataPagamento: z.string().nullable().optional(),
  valorPago: decimal.nullable().optional(),
  nomePessoa: z.string().nullable().optional(),
  cpfcnpj: z.string().nullable().optional(),
});
export type MatchGuiaListItem = z.infer<typeof matchGuiaListItemSchema>;

export const matchDescontoFolhaListItemSchema = z.object({
  matcher: z.literal("DESCONTO_FOLHA"),
  idMatch: z.number(),
  status: z.string(),
  statusDescricao: z.string().nullable().optional(),
  idParcela: z.number().nullable().optional(),
  numeroParcela: z.number().nullable().optional(),
  mesReferencia: z.number().nullable().optional(),
  anoReferencia: z.number().nullable().optional(),
  valorEsperado: decimal.nullable().optional(),
  cpfcnpj: z.string().nullable().optional(),
  nomePessoa: z.string().nullable().optional(),
  valorContracheque: decimal.nullable().optional(),
  idLancamento: z.number().nullable().optional(),
  dtMovimento: z.string().nullable().optional(),
  valorLancamento: decimal.nullable().optional(),
});
export type MatchDescontoFolhaListItem = z.infer<typeof matchDescontoFolhaListItemSchema>;

const responseSchema = <T extends z.ZodTypeAny>(item: T) =>
  z.object({ items: z.array(item), total: z.number(), page: z.number(), size: z.number() });

export const matchOBListResponseSchema = responseSchema(matchOBListItemSchema);
export const matchPessoaListResponseSchema = responseSchema(matchPessoaListItemSchema);
export const matchGuiaListResponseSchema = responseSchema(matchGuiaListItemSchema);
export const matchDescontoFolhaListResponseSchema = responseSchema(
  matchDescontoFolhaListItemSchema,
);

export type MatchOBListResponse = z.infer<typeof matchOBListResponseSchema>;
export type MatchPessoaListResponse = z.infer<typeof matchPessoaListResponseSchema>;
export type MatchGuiaListResponse = z.infer<typeof matchGuiaListResponseSchema>;
export type MatchDescontoFolhaListResponse = z.infer<typeof matchDescontoFolhaListResponseSchema>;
