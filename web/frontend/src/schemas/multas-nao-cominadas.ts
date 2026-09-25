import { z } from "zod";

// mirrors backend app/cgad/multas_nao_cominadas/schemas.py MultaNaoCominada
export const multaNaoCominadaSchema = z.object({
  id: z.number().int(),
  id_processo: z.number().int(),
  numero_processo: z.number().int().nullable().optional(),
  ano_processo: z.number().int().nullable().optional(),
  id_decisao: z.number().int().nullable().optional(),
  descricao: z.string(),
  prazo: z.string().nullable().optional(),
  data_cumprimento: z.string().nullable().optional(),
  orgao: z.string().nullable().optional(),
  responsavel: z.string().nullable().optional(),
  documento: z.string().nullable().optional(),
  valor_dia: z.number().nullable().optional(),
  periodo: z.string().nullable().optional(),
  status: z.enum(["approved", "dispatched"]),
  revisor: z.string().nullable().optional(),
  data_revisao: z.string().datetime({ offset: true }).nullable().optional(),
});
export type MultaNaoCominada = z.infer<typeof multaNaoCominadaSchema>;

// mirrors backend MultasNaoCominadas
export const multasNaoCominadasSchema = z.object({
  total_obrigacoes: z.number().int(),
  total_processos: z.number().int(),
  items: z.array(multaNaoCominadaSchema),
});
export type MultasNaoCominadas = z.infer<typeof multasNaoCominadasSchema>;
