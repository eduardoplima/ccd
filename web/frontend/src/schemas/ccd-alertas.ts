import { z } from "zod";

// mirrors backend TipoAlerta
export const tipoAlertaSchema = z.enum(["parcelamento_cancelado"]);
export type TipoAlerta = z.infer<typeof tipoAlertaSchema>;

// mirrors backend ParcelamentoCanceladoDetalhe
export const parcelamentoCanceladoDetalheSchema = z.object({
  id_parcelamento: z.number().nullable(),
  situacao: z.string().nullable(),
  situacao_descricao: z.string().nullable(),
  data_cancelamento: z.string().nullable(),
  numero_parcelas: z.number().nullable(),
  parcelas_pagas: z.number().nullable(),
});
export type ParcelamentoCanceladoDetalhe = z.infer<
  typeof parcelamentoCanceladoDetalheSchema
>;

// mirrors backend AlertaParcelamentoCancelado
export const alertaParcelamentoCanceladoSchema = z.object({
  tipo: z.literal("parcelamento_cancelado"),
  processo: z.string(),
  numero_processo: z.string(),
  ano_processo: z.string(),
  relator: z.string().nullable(),
  data_marcador: z.string().nullable(),
  detalhe: parcelamentoCanceladoDetalheSchema,
});

// mirrors backend AlertaOut (discriminated union pronta para novos tipos)
export const alertaSchema = z.discriminatedUnion("tipo", [
  alertaParcelamentoCanceladoSchema,
]);
export type Alerta = z.infer<typeof alertaSchema>;

// mirrors backend TipoAlertaInfo
export const tipoAlertaInfoSchema = z.object({
  tipo: tipoAlertaSchema,
  titulo: z.string(),
  descricao: z.string(),
  quantidade: z.number(),
});
export type TipoAlertaInfo = z.infer<typeof tipoAlertaInfoSchema>;

// mirrors backend AlertasResponse
export const alertasResponseSchema = z.object({
  tipos: z.array(tipoAlertaInfoSchema),
  items: z.array(alertaSchema),
  total: z.number(),
});
export type AlertasResponse = z.infer<typeof alertasResponseSchema>;
