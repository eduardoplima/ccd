import { apiClient } from "@/lib/api-client";
import {
  resetSenhaResponseSchema,
  usuarioCreateResponseSchema,
  usuarioListResponseSchema,
  usuarioSchema,
  type ResetSenhaResponse,
  type Usuario,
  type UsuarioCreateInput,
  type UsuarioCreateResponse,
  type UsuarioListResponse,
  type UsuarioUpdateInput,
} from "@/schemas/usuario";

export interface UsuariosFilters {
  papel?: "user" | "admin";
  ativo?: boolean;
  q?: string;
  page: number;
  size: number;
}

export async function listUsuarios(f: UsuariosFilters): Promise<UsuarioListResponse> {
  const params: Record<string, string | number | boolean> = { page: f.page, size: f.size };
  if (f.papel) params.papel = f.papel;
  if (f.ativo !== undefined) params.ativo = f.ativo;
  if (f.q) params.q = f.q;
  const { data } = await apiClient.get("/api/v1/usuarios", { params });
  return usuarioListResponseSchema.parse(data);
}

export async function createUsuario(input: UsuarioCreateInput): Promise<UsuarioCreateResponse> {
  const { data } = await apiClient.post("/api/v1/usuarios", input);
  return usuarioCreateResponseSchema.parse(data);
}

export async function updateUsuario(id: number, input: UsuarioUpdateInput): Promise<Usuario> {
  const { data } = await apiClient.patch(`/api/v1/usuarios/${id}`, input);
  return usuarioSchema.parse(data);
}

export async function resetSenha(id: number): Promise<ResetSenhaResponse> {
  const { data } = await apiClient.post(`/api/v1/usuarios/${id}/reset-senha`);
  return resetSenhaResponseSchema.parse(data);
}

export async function trocarSenha(senhaAtual: string, senhaNova: string): Promise<void> {
  await apiClient.post("/api/v1/auth/trocar-senha", { senhaAtual, senhaNova });
}
