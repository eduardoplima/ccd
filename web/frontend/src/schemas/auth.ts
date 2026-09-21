import { z } from "zod";

// mirrors backend LoginRequest
export const loginSchema = z.object({
  login: z.string().min(1, "informe o login").max(64, "login excede 64 caracteres"),
  senha: z.string().min(1, "informe a senha").max(72, "senha excede 72 caracteres"),
});
export type LoginInput = z.infer<typeof loginSchema>;

// mirrors backend TokenPair
export const tokenPairSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
  token_type: z.string(),
  expires_in: z.number(),
});
export type TokenPair = z.infer<typeof tokenPairSchema>;

// mirrors backend PermissaoItem
export const permissaoItemSchema = z.object({
  modulo: z.string(),
  ver: z.boolean().default(true),
  editar: z.boolean(),
});
export type PermissaoItem = z.infer<typeof permissaoItemSchema>;

// mirrors backend UserOut
export const userOutSchema = z.object({
  idUsuario: z.number(),
  login: z.string(),
  email: z.string().nullable(),
  nomeCompleto: z.string(),
  papel: z.string(),
  ativo: z.boolean(),
  deveTrocarSenha: z.boolean(),
  dataCriacao: z.string(),
  permissoes: z.array(permissaoItemSchema).default([]),
});
export type UserOut = z.infer<typeof userOutSchema>;
