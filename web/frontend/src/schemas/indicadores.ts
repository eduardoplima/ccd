import { z } from "zod";

// mirrors backend app/ccd/indicadores/schemas.py
export const indicadorSchema = z.object({
  chave: z.string(),
  titulo: z.string(),
  unidade: z.enum(["brl", "pct", "dias", "qtd"]),
  sentido: z.enum(["maior", "menor"]),
  ref_dpg: z.string(),
  valores: z.record(z.string(), z.number().nullable()),
  atual: z.number().nullable(),
  linha_base: z.number().nullable(),
  detalhe: z.string().nullable(),
});
export type Indicador = z.infer<typeof indicadorSchema>;

export const painelSchema = z.object({
  ano: z.number(),
  anos: z.array(z.number()),
  indicadores: z.array(indicadorSchema),
});
export type Painel = z.infer<typeof painelSchema>;
