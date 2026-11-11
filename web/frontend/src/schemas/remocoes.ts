import { z } from "zod";

export const tipoItemSchema = z.enum(["obrigacao", "recomendacao"]);
export type TipoItem = z.infer<typeof tipoItemSchema>;

// mirrors backend Acordao
export const acordaoSchema = z.object({
  id_composicao_pauta: z.number().int(),
  numero: z.string().nullable().optional(),
  ano: z.string().nullable().optional(),
  tipo: z.string().nullable().optional(),
  data_sessao: z.string().nullable().optional(),
});
export type Acordao = z.infer<typeof acordaoSchema>;

// mirrors backend ItemCurado
export const itemCuradoSchema = z.object({
  tipo: tipoItemSchema,
  id: z.number().int(),
  id_composicao_pauta: z.number().int(),
  descricao: z.string(),
  orgao: z.string().nullable().optional(),
  status: z.enum(["approved", "dispatched", "removed"]),
  id_composicao_pauta_remocao: z.number().int().nullable().optional(),
  justificativa_remocao: z.string().nullable().optional(),
  removido_por: z.string().nullable().optional(),
  data_remocao: z.string().datetime({ offset: true }).nullable().optional(),
});
export type ItemCurado = z.infer<typeof itemCuradoSchema>;

// mirrors backend Consulta
export const consultaRemocaoSchema = z.object({
  id_processo: z.number().int(),
  processo: z.string(),
  acordaos: z.array(acordaoSchema),
  itens: z.array(itemCuradoSchema),
});
export type ConsultaRemocao = z.infer<typeof consultaRemocaoSchema>;

// mirrors backend RemocaoPayload
export type RemocaoPayload = {
  id_processo: number;
  id_composicao_pauta_remocao: number;
  justificativa: string;
  itens: { tipo: TipoItem; id: number }[];
};

// mirrors backend RemocaoResultado
export const remocaoResultadoSchema = z.object({ removidos: z.number().int() });
