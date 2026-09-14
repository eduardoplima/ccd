import { z } from "zod";

// All schemas in this file mirror DTOs in backend/app/cgad/dashboards/schemas.py.

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

// mirrors backend TreemapBucket
export const treemapBucketSchema = z.object({
  nome: z.string(),
  total: z.number().int(),
});
export type TreemapBucket = z.infer<typeof treemapBucketSchema>;

// mirrors backend TreemapSet
export const treemapSetSchema = z.object({
  por_orgao: z.array(treemapBucketSchema),
  por_tipo: z.array(treemapBucketSchema),
  por_relator: z.array(treemapBucketSchema),
});
export type TreemapSet = z.infer<typeof treemapSetSchema>;

// mirrors backend EntidadeCadastrada
export const entidadeCadastradaSchema = z.object({
  tipo: z.enum(["obrigacao", "recomendacao"]),
  id: z.number().int(),
  id_processo: z.number().int(),
  numero_processo: z.number().int().nullable().optional(),
  ano_processo: z.number().int().nullable().optional(),
  id_decisao: z.number().int().nullable().optional(),
  descricao: z.string(),
  status: z.enum(["approved", "dispatched"]),
  revisor: z.string().nullable().optional(),
  data_revisao: z.string().datetime({ offset: true }).nullable().optional(),
  data_envio: z.string().datetime({ offset: true }).nullable().optional(),
  orgao: z.string(),
  tipo_processo: z.string(),
  relator: z.string(),
  pessoa: z.string().nullable().optional(),
});
export type EntidadeCadastrada = z.infer<typeof entidadeCadastradaSchema>;

export const dashboardSummarySchema = z.object({
  top_orgaos: z.array(orgaoBucketSchema),
  top_pessoas: z.array(pessoaBucketSchema),
  treemap_obrigacao: treemapSetSchema,
  treemap_recomendacao: treemapSetSchema,
  entidades: z.array(entidadeCadastradaSchema),
});
export type DashboardSummary = z.infer<typeof dashboardSummarySchema>;
