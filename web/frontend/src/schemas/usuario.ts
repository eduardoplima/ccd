import { z } from "zod";

import { permissaoItemSchema } from "@/schemas/auth";

const papelSchema = z.enum(["user", "admin", "restrito"]);
export type Papel = z.infer<typeof papelSchema>;

export const usuarioSchema = z.object({
  idUsuario: z.number(),
  login: z.string(),
  email: z.string().email(),
  nomeCompleto: z.string(),
  papel: papelSchema,
  ativo: z.boolean(),
  dataCriacao: z.string(),
  dataAtualizacao: z.string(),
  permissoes: z.array(permissaoItemSchema).default([]),
});
export type Usuario = z.infer<typeof usuarioSchema>;

export const usuarioListResponseSchema = z.object({
  items: z.array(usuarioSchema),
  total: z.number(),
  page: z.number(),
  size: z.number(),
});
export type UsuarioListResponse = z.infer<typeof usuarioListResponseSchema>;

export const usuarioCreateInputSchema = z.object({
  login: z
    .string()
    .min(3, "mínimo 3 caracteres")
    .max(64, "máximo 64 caracteres")
    .regex(/^[a-z0-9][a-z0-9._-]{1,63}$/, "use letras minúsculas, dígitos, ., _ ou -"),
  email: z.string().email("e-mail inválido"),
  nomeCompleto: z.string().min(1, "informe o nome").max(255),
  papel: papelSchema,
});
export type UsuarioCreateInput = z.infer<typeof usuarioCreateInputSchema>;

export const usuarioCreateResponseSchema = z.object({
  usuario: usuarioSchema,
  senhaTemporaria: z.string(),
});
export type UsuarioCreateResponse = z.infer<typeof usuarioCreateResponseSchema>;

export const usuarioUpdateInputSchema = z.object({
  nomeCompleto: z.string().min(1).max(255).optional(),
  papel: papelSchema.optional(),
  ativo: z.boolean().optional(),
  permissoes: z.array(permissaoItemSchema).optional(),
});
export type UsuarioUpdateInput = z.infer<typeof usuarioUpdateInputSchema>;

export const resetSenhaResponseSchema = z.object({
  senhaTemporaria: z.string(),
});
export type ResetSenhaResponse = z.infer<typeof resetSenhaResponseSchema>;

export const trocarSenhaInputSchema = z
  .object({
    senhaAtual: z.string().min(1, "informe a senha atual").max(72),
    senhaNova: z.string().min(8, "mínimo 8 caracteres").max(72),
    confirmacao: z.string().min(1),
  })
  .refine((d) => d.senhaNova === d.confirmacao, {
    message: "as senhas não conferem",
    path: ["confirmacao"],
  });
export type TrocarSenhaInput = z.infer<typeof trocarSenhaInputSchema>;
