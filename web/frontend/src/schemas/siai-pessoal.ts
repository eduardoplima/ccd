import { z } from "zod";

// mirrors backend ItemContrachequeOut
export const itemContrachequeSchema = z.object({
  codigo: z.string().nullable().optional(),
  descricao: z.string(),
  tipo: z.enum(["V", "D"]),
  valor: z.number(),
  tce: z.boolean().default(false),
});
export type ItemContracheque = z.infer<typeof itemContrachequeSchema>;

// mirrors backend FolhaContrachequeOut
export const folhaContrachequeSchema = z.object({
  idContracheque: z.number().int(),
  tipoFolha: z.string(),
  idOrgao: z.number().int().nullable().optional(),
  orgao: z.string().nullable().optional(),
  matricula: z.string().nullable().optional(),
  cargo: z.string().nullable().optional(),
  lotacao: z.string().nullable().optional(),
  totalVantagens: z.number().nullable().optional(),
  totalDescontos: z.number().nullable().optional(),
  remessas: z.number().int().default(1),
  itens: z.array(itemContrachequeSchema).default([]),
});
export type FolhaContracheque = z.infer<typeof folhaContrachequeSchema>;

// mirrors backend ContrachequeMes
export const contrachequeMesSchema = z.object({
  cpf: z.string(),
  nome: z.string().nullable().optional(),
  ano: z.number().int(),
  mes: z.number().int(),
  folhas: z.array(folhaContrachequeSchema).default([]),
});
export type ContrachequeMes = z.infer<typeof contrachequeMesSchema>;

export type ContrachequeParams = { cpf: string; ano: number; mes: number; processo?: string };
