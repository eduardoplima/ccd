// mirrors backend app/desconto_folha/schemas.py
import { z } from "zod";

const decimalLike = z.union([z.string(), z.number()]).transform((v) => Number(v));
const decimalNullable = z
  .union([z.string(), z.number()])
  .nullable()
  .optional()
  .transform((v) => (v === null || v === undefined ? null : Number(v)));

// ---------------------------------------------------------------------------
// Por pessoa
// ---------------------------------------------------------------------------

export const pessoaAgregadaItemSchema = z.object({
  cpfCnpj: z.string().nullable().optional(),
  nomePessoa: z.string().nullable().optional(),
  idOrgaoNotificado: z.number().nullable().optional(),
  nomeOrgaoNotificado: z.string().nullable().optional(),
  qtdParcelas: z.number().int(),
  qtdConciliadas: z.number().int().default(0),
  origens: z.array(z.string()).default([]),
  valorAtualizadoTotal: decimalLike,
  qtdProcessosNotificados: z.number().int(),
  qtdDebitosNotificados: z.number().int(),
  valorDebitosNotificadosTotal: decimalLike,
  totalEsperado: decimalLike,
  totalQuitado: decimalLike,
  saldoAberto: decimalLike,
});
export type PessoaAgregadaItem = z.infer<typeof pessoaAgregadaItemSchema>;

export const depositosOrgaoResponseSchema = z.object({
  idOrgao: z.number().int(),
  cnpj: z.string().nullable().optional(),
  qtd: z.number().int(),
  total: decimalLike,
  isEstadual: z.boolean().default(false),
});
export type DepositosOrgaoResponse = z.infer<typeof depositosOrgaoResponseSchema>;

export const lancamentoDoOrgaoItemSchema = z.object({
  idLancamento: z.number().int(),
  dtMovimento: z.string().nullable().optional(),
  conta: z.string(),
  valor: decimalLike,
  historico: z.string(),
  documento: z.string().nullable().optional(),
  descricao: z.string().nullable().optional(),
  cpfCnpjDepositante: z.string().nullable().optional(),
  viaCnpj: z.boolean(),
  viaInferencia: z.boolean(),
});
export type LancamentoDoOrgaoItem = z.infer<typeof lancamentoDoOrgaoItemSchema>;

export const lancamentosDoOrgaoResponseSchema = z.object({
  idOrgao: z.number().int(),
  items: z.array(lancamentoDoOrgaoItemSchema),
});
export type LancamentosDoOrgaoResponse = z.infer<typeof lancamentosDoOrgaoResponseSchema>;

export const pessoaAgregadaListResponseSchema = z.object({
  items: z.array(pessoaAgregadaItemSchema),
  total: z.number().int(),
  page: z.number().int(),
  size: z.number().int(),
});
export type PessoaAgregadaListResponse = z.infer<typeof pessoaAgregadaListResponseSchema>;

export const parcelaPessoaItemSchema = z.object({
  idParcela: z.number().int().nullable().optional(),
  idDescontoFolha: z.number().int(),
  origem: z.string(),
  numeroParcela: z.number().int().nullable().optional(),
  mesReferencia: z.number().int().nullable().optional(),
  anoReferencia: z.number().int().nullable().optional(),
  valorEsperado: decimalLike,
  dataVencimento: z.string().nullable().optional(),
  dataPagamento: z.string().nullable().optional(),
  situacaoParcela: z.string().nullable().optional(),
  tipoBaixa: z.number().int().nullable().optional(),
  statusCodigo: z.string().nullable().optional(),
  statusDescricao: z.string().nullable().optional(),
  isManual: z.boolean(),
  valorContracheque: decimalNullable,
  idLancamentoFrap: z.number().int().nullable().optional(),
  idMatch: z.number().int().nullable().optional(),
  observacao: z.string().nullable().optional(),
});
export type ParcelaPessoaItem = z.infer<typeof parcelaPessoaItemSchema>;

export const parcelasPessoaResponseSchema = z.object({
  cpfCnpj: z.string().nullable().optional(),
  nomePessoa: z.string().nullable().optional(),
  idOrgaoNotificado: z.number().int().nullable().optional(),
  nomeOrgaoNotificado: z.string().nullable().optional(),
  parcelas: z.array(parcelaPessoaItemSchema),
});
export type ParcelasPessoaResponse = z.infer<typeof parcelasPessoaResponseSchema>;

export const atribuirOrgaoResultadoSchema = z.object({
  qtdAtualizados: z.number().int(),
  idOrgao: z.number().int(),
  nomeOrgao: z.string(),
});
export type AtribuirOrgaoResultado = z.infer<typeof atribuirOrgaoResultadoSchema>;

// ---------------------------------------------------------------------------
// Por órgão
// ---------------------------------------------------------------------------

export const orgaoAgregadoItemSchema = z.object({
  idOrgao: z.number().int().nullable().optional(),
  nomeOrgao: z.string().nullable().optional(),
  qtdPessoas: z.number().int(),
  qtdParcelas: z.number().int(),
  qtdConciliadas: z.number().int(),
  totalEsperado: decimalLike,
  totalQuitado: decimalLike,
});
export type OrgaoAgregadoItem = z.infer<typeof orgaoAgregadoItemSchema>;

export const orgaoAgregadoListResponseSchema = z.object({
  items: z.array(orgaoAgregadoItemSchema),
  total: z.number().int(),
  page: z.number().int(),
  size: z.number().int(),
});
export type OrgaoAgregadoListResponse = z.infer<typeof orgaoAgregadoListResponseSchema>;

export const pessoaDoOrgaoItemSchema = z.object({
  cpfCnpj: z.string().nullable().optional(),
  nomePessoa: z.string().nullable().optional(),
  qtdParcelas: z.number().int(),
  qtdConciliadas: z.number().int(),
  totalEsperado: decimalLike,
});
export type PessoaDoOrgaoItem = z.infer<typeof pessoaDoOrgaoItemSchema>;

export const pessoasDoOrgaoResponseSchema = z.object({
  idOrgao: z.number().int(),
  nomeOrgao: z.string().nullable().optional(),
  pessoas: z.array(pessoaDoOrgaoItemSchema),
});
export type PessoasDoOrgaoResponse = z.infer<typeof pessoasDoOrgaoResponseSchema>;

// ---------------------------------------------------------------------------
// Cadastro manual
// ---------------------------------------------------------------------------

export const cadastroManualItemSchema = z.object({
  idDescontoFolha: z.number().int(),
  cpfCnpj: z.string().nullable().optional(),
  nomePessoa: z.string().nullable().optional(),
  idOrgaoNotificado: z.number().int().nullable().optional(),
  nomeOrgaoNotificado: z.string().nullable().optional(),
  qtdParcelas: z.number().int(),
  valorTotal: decimalLike,
  dataInclusao: z.string().nullable().optional(),
});
export type CadastroManualItem = z.infer<typeof cadastroManualItemSchema>;

export const cadastroManualListResponseSchema = z.object({
  items: z.array(cadastroManualItemSchema),
  total: z.number().int(),
  page: z.number().int(),
  size: z.number().int(),
});
export type CadastroManualListResponse = z.infer<typeof cadastroManualListResponseSchema>;

// Input do form de cadastro
export const parcelaManualInputSchema = z.object({
  numeroParcela: z.number().int().min(1),
  mesReferencia: z.number().int().min(1).max(12),
  anoReferencia: z.number().int().min(2000).max(2100),
  valorEsperado: z.number().positive(),
  dataVencimento: z.string().nullable().optional(),
});
export type ParcelaManualInput = z.infer<typeof parcelaManualInputSchema>;

export const cadastroManualInputSchema = z.object({
  cpfCnpj: z.string().min(11).max(14),
  nomePessoa: z.string().min(1).max(200),
  idOrgaoNotificado: z.number().int(),
  nomeOrgaoNotificado: z.string().min(1).max(200),
  parcelas: z.array(parcelaManualInputSchema).min(1),
  observacao: z.string().max(500).nullable().optional(),
});
export type CadastroManualInput = z.infer<typeof cadastroManualInputSchema>;

// ---------------------------------------------------------------------------
// Match manual
// ---------------------------------------------------------------------------

export const matchManualInputSchema = z.object({
  idLancamentoFrap: z.number().int(),
  idsParcela: z.array(z.number().int()).min(1),
  observacao: z.string().max(500).nullable().optional(),
});
export type MatchManualInput = z.infer<typeof matchManualInputSchema>;

export const matchManualResultadoSchema = z.object({
  matchesCriados: z.number().int(),
  idsMatch: z.array(z.number().int()),
});
export type MatchManualResultado = z.infer<typeof matchManualResultadoSchema>;

// ---------------------------------------------------------------------------
// Órgãos disponíveis (dropdown)
// ---------------------------------------------------------------------------

export const orgaoDisponivelSchema = z.object({
  idOrgao: z.number().int(),
  nomeOrgao: z.string(),
});
export type OrgaoDisponivel = z.infer<typeof orgaoDisponivelSchema>;

// ---------------------------------------------------------------------------
// Tipologias de análise
// ---------------------------------------------------------------------------

export const candidatoRepasseMultiSchema = z.object({
  idsParcela: z.array(z.number().int()),
  somaCandidata: decimalLike,
  descricaoCombinacao: z.string(),
});
export type CandidatoRepasseMulti = z.infer<typeof candidatoRepasseMultiSchema>;

export const repasseMultiParcelaItemSchema = z.object({
  idLancamento: z.number().int(),
  dtMovimento: z.string(),
  valor: decimalLike,
  historico: z.string().nullable().optional(),
  cpfCnpj: z.string().nullable().optional(),
  nomePessoa: z.string().nullable().optional(),
  candidatos: z.array(candidatoRepasseMultiSchema),
});
export type RepasseMultiParcelaItem = z.infer<typeof repasseMultiParcelaItemSchema>;

export const repasseMultiParcelaResponseSchema = z.object({
  items: z.array(repasseMultiParcelaItemSchema),
});
export type RepasseMultiParcelaResponse = z.infer<typeof repasseMultiParcelaResponseSchema>;

export const cpfSemSiaiItemSchema = z.object({
  idDescontoFolha: z.number().int(),
  cpfCnpj: z.string().nullable().optional(),
  nomePessoa: z.string().nullable().optional(),
  origem: z.string(),
  qtdParcelas: z.number().int(),
  nomeOrgaoNotificado: z.string().nullable().optional(),
});
export type CpfSemSiaiItem = z.infer<typeof cpfSemSiaiItemSchema>;

export const cpfSemSiaiResponseSchema = z.object({
  items: z.array(cpfSemSiaiItemSchema),
});
export type CpfSemSiaiResponse = z.infer<typeof cpfSemSiaiResponseSchema>;

export const parcelaDuplicadaItemSchema = z.object({
  idDescontoFolha: z.number().int(),
  cpfCnpj: z.string().nullable().optional(),
  nomePessoa: z.string().nullable().optional(),
  numeroParcela: z.number().int(),
  mesReferencia: z.number().int(),
  anoReferencia: z.number().int(),
  valorEsperado: decimalLike,
  qtd: z.number().int(),
  idsParcela: z.array(z.number().int()),
});
export type ParcelaDuplicadaItem = z.infer<typeof parcelaDuplicadaItemSchema>;

export const parcelaDuplicadaResponseSchema = z.object({
  items: z.array(parcelaDuplicadaItemSchema),
});
export type ParcelaDuplicadaResponse = z.infer<typeof parcelaDuplicadaResponseSchema>;

export const atrasoSistemicoMesSchema = z.object({
  ano: z.number().int(),
  mes: z.number().int(),
  pctAtraso: z.number(),
  qtdParcelas: z.number().int(),
  qtdEmAtraso: z.number().int(),
});
export type AtrasoSistemicoMes = z.infer<typeof atrasoSistemicoMesSchema>;

export const atrasoSistemicoItemSchema = z.object({
  idOrgao: z.number().int().nullable().optional(),
  nomeOrgao: z.string().nullable().optional(),
  qtdMesesConsecutivos: z.number().int(),
  pctMedio: z.number(),
  detalheMeses: z.array(atrasoSistemicoMesSchema),
});
export type AtrasoSistemicoItem = z.infer<typeof atrasoSistemicoItemSchema>;

export const atrasoSistemicoResponseSchema = z.object({
  items: z.array(atrasoSistemicoItemSchema),
});
export type AtrasoSistemicoResponse = z.infer<typeof atrasoSistemicoResponseSchema>;
