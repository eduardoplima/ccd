import { z } from "zod";

// All schemas in this file mirror DTOs in backend/app/dashboards/schemas.py.

export const kpiBlockSchema = z.object({
  pendentes_obrigacao: z.number().int(),
  pendentes_recomendacao: z.number().int(),
  revisadas_periodo: z.number().int(),
  aprovadas_periodo: z.number().int(),
  percent_aprovacao: z.number(), // 0.0 – 1.0
  obrigacoes_com_multa: z.number().int(),
  ticket_medio_multa: z.number().nullable().optional(),
});
export type KpiBlock = z.infer<typeof kpiBlockSchema>;

export const orgaoBucketSchema = z.object({
  nome: z.string(),
  obrigacoes: z.number().int(),
  recomendacoes: z.number().int(),
  total: z.number().int(),
});
export type OrgaoBucket = z.infer<typeof orgaoBucketSchema>;

export const pessoaBucketSchema = z.object({
  nome: z.string(),
  documento: z.string().nullable().optional(),
  obrigacoes: z.number().int(),
  recomendacoes: z.number().int(),
  total: z.number().int(),
});
export type PessoaBucket = z.infer<typeof pessoaBucketSchema>;

export const dashboardSummarySchema = z.object({
  kpis: kpiBlockSchema,
  top_orgaos: z.array(orgaoBucketSchema),
  top_pessoas: z.array(pessoaBucketSchema),
});
export type DashboardSummary = z.infer<typeof dashboardSummarySchema>;
