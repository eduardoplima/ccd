import { z } from "zod";

// Espelha backend/app/ccd/desconto_folha/schemas.py (JSON em camelCase).

export const statusExtracaoSchema = z.enum(["PENDENTE", "OK", "SEM_RESPOSTA", "ERRO"]);
export type StatusExtracao = z.infer<typeof statusExtracaoSchema>;

export const tipoNotificacaoSchema = z.enum(["E", "F"]);
export type TipoNotificacao = z.infer<typeof tipoNotificacaoSchema>;
export const tipoRecebimentoSchema = z.enum(["E", "T", "AR", "DE"]);
export type TipoRecebimento = z.infer<typeof tipoRecebimentoSchema>;

// mirrors backend NotificacaoOut
export const notificacaoSchema = z.object({
  numero: z.string().nullable().optional(),
  data: z.string().nullable().optional(),
  tipo: tipoNotificacaoSchema.nullable().optional(),
  evento: z.number().int().nullable().optional(),
  url: z.string().nullable().optional(),
});

// mirrors backend ArOut (recebimento da notificação; a chave JSON continua `ar`)
export const arSchema = z.object({
  numeroPostagem: z.string().nullable().optional(),
  data: z.string().nullable().optional(),
  tipo: tipoRecebimentoSchema.nullable().optional(),
  evento: z.number().int().nullable().optional(),
  url: z.string().nullable().optional(),
});

// mirrors backend RespostaOut
export const respostaSchema = z.object({
  processo: z.string().nullable().optional(),
  evento: z.number().int().nullable().optional(),
  data: z.string().nullable().optional(),
  url: z.string().nullable().optional(),
});

// mirrors backend RetencoesOut
export const retencoesSchema = z.object({
  cpf: z.string(),
  total: z.number(),
  competencias: z.number().int(),
  ultimoAno: z.number().int().nullable().optional(),
  ultimoMes: z.number().int().nullable().optional(),
});
export type Retencoes = z.infer<typeof retencoesSchema>;

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
// mirrors backend TotaisOut
export const totaisSchema = z.object({
  cadastros: z.number().int(),
  processos: z.number().int(),
  pessoas: z.number().int(),
  valorEsperado: z.number(),
  valorRecebido: z.number(),
  valorAReceber: z.number(),
});
export type Totais = z.infer<typeof totaisSchema>;

export const cadastroListResponseSchema = z.object({
  items: z.array(cadastroListItemSchema),
  total: z.number().int(),
  page: z.number().int(),
  size: z.number().int(),
  totais: totaisSchema,
});
export type CadastroListResponse = z.infer<typeof cadastroListResponseSchema>;

// mirrors backend SugestoesOut
export const sugestoesSchema = z.object({
  pessoas: z.array(
    z.object({ cpf: z.string(), nome: z.string().nullable().optional(), qtd: z.number().int() }),
  ),
  orgaos: z.array(z.object({ nome: z.string(), qtd: z.number().int() })),
});
export type Sugestoes = z.infer<typeof sugestoesSchema>;

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
  valorSiai: z.number().nullable().optional(),
  match: matchSchema.nullable().optional(),
  candidatos: z.array(lancamentoSchema).default([]),
});
export type Valor = z.infer<typeof valorSchema>;

// mirrors backend MapaRetencoesOut
export const mesRetencaoSchema = z.object({
  ano: z.number().int(),
  mes: z.number().int(),
  retencoes: z.array(
    z.object({
      orgao: z.string().nullable().optional(),
      codigo: z.string().nullable().optional(),
      rubrica: z.string(),
      valor: z.number(),
    }),
  ),
  totalRetido: z.number(),
  parcelas: z.array(
    z.object({
      idCadastro: z.number().int(),
      processo: z.string(),
      numeroParcela: z.number().int(),
      valor: z.number(),
      conciliado: z.boolean(),
      competenciaInferida: z.boolean().default(false),
      creditoCompartilhado: z.boolean().default(false),
      lancamento: lancamentoSchema.nullable().optional(),
    }),
  ),
  totalConciliado: z.number(),
  conciliado: z.boolean(),
});
export type MesRetencao = z.infer<typeof mesRetencaoSchema>;

export const mapaRetencoesSchema = z.object({
  cpf: z.string(),
  nome: z.string().nullable().optional(),
  totalRetido: z.number(),
  totalConciliado: z.number(),
  meses: z.array(mesRetencaoSchema),
});
export type MapaRetencoes = z.infer<typeof mapaRetencoesSchema>;

// mirrors backend CreditoFrapOut / CreditosFrapResponse (busca FRAP-first)
export const creditoFrapSchema = lancamentoSchema.extend({
  descricao: z.string().nullable().optional(),
  idCadastroVinculado: z.number().int().nullable().optional(),
});
export type CreditoFrap = z.infer<typeof creditoFrapSchema>;

export const creditosFrapResponseSchema = z.object({
  texto: z.string().nullable().optional(),
  desde: z.string().nullable().optional(),
  valor: z.number().nullable().optional(),
  aviso: z.string().nullable().optional(),
  items: z.array(creditoFrapSchema).default([]),
});
export type CreditosFrapResponse = z.infer<typeof creditosFrapResponseSchema>;

export type CreditosFrapParams = { texto?: string; valor?: number; desde?: string };

// mirrors backend EventoRespostaOut
export const eventoRespostaSchema = z.object({
  processo: z.string().nullable().optional(),
  idEvento: z.number().int(),
  evento: z.number().int(),
  nome: z.string().nullable().optional(),
  data: z.string().nullable().optional(),
  url: z.string(),
});
export type EventoResposta = z.infer<typeof eventoRespostaSchema>;

// mirrors backend CadastroDetalhe
export const cadastroDetalheSchema = cadastroListItemSchema.extend({
  trechoResposta: z.string().nullable().optional(),
  arquivoResposta: z.string().nullable().optional(),
  dataExtracao: z.string().nullable().optional(),
  observacoes: z.string().nullable().optional(),
  valores: z.array(valorSchema).default([]),
  eventosResposta: z.array(eventoRespostaSchema).default([]),
});
export type CadastroDetalhe = z.infer<typeof cadastroDetalheSchema>;

// mirrors backend DebitoLookup
export const debitoLookupSchema = z.object({
  idDebito: z.number().int(),
  valorOriginal: z.number().nullable().optional(),
  tipo: z.string().nullable().optional(),
  status: z.string().nullable().optional(),
  cancelado: z.boolean(),
  desdobrado: z.boolean().default(false),
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
