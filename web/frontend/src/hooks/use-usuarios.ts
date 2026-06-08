"use client";

import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createUsuario,
  listUsuarios,
  resetSenha,
  trocarSenha,
  updateUsuario,
  type UsuariosFilters,
} from "@/lib/api/usuarios";
import type { UsuarioCreateInput, UsuarioUpdateInput } from "@/schemas/usuario";

export function useUsuarios(filters: UsuariosFilters) {
  return useQuery({
    queryKey: ["usuarios", filters],
    queryFn: () => listUsuarios(filters),
    staleTime: 30_000,
    placeholderData: keepPreviousData,
  });
}

export function useCreateUsuario() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input: UsuarioCreateInput) => createUsuario(input),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["usuarios"] }),
  });
}

export function useUpdateUsuario() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, input }: { id: number; input: UsuarioUpdateInput }) =>
      updateUsuario(id, input),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["usuarios"] }),
  });
}

export function useResetSenha() {
  return useMutation({ mutationFn: (id: number) => resetSenha(id) });
}

export function useTrocarSenha() {
  return useMutation({
    mutationFn: ({ senhaAtual, senhaNova }: { senhaAtual: string; senhaNova: string }) =>
      trocarSenha(senhaAtual, senhaNova),
  });
}
