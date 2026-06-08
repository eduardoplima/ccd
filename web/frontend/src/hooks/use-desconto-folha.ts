"use client";

import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  atribuirOrgaoPessoa,
  criarCadastro,
  criarMatchManual,
  deletarCadastro,
  deletarMatchManual,
  getDepositosOrgao,
  getDepositosOrgaoLancamentos,
  getParcelasPessoa,
  getPessoasDoOrgao,
  getTipologiaAtrasoSistemico,
  getTipologiaCpfSemSiai,
  getTipologiaParcelaDuplicada,
  getTipologiaRepasseMulti,
  listCadastros,
  listOrgaos,
  listOrgaosDisponiveis,
  listPessoas,
  type OrgaosFilters,
  type PessoasFilters,
  type RepasseMultiFilters,
} from "@/lib/api/desconto-folha";

const KEY = "desconto-folha";

export function usePessoas(filters: PessoasFilters) {
  return useQuery({
    queryKey: [KEY, "pessoas", filters],
    queryFn: () => listPessoas(filters),
    staleTime: 30_000,
    placeholderData: keepPreviousData,
  });
}

export function useParcelasPessoa(cpfCnpj: string | null, ano?: number) {
  return useQuery({
    queryKey: [KEY, "parcelas", cpfCnpj, ano],
    queryFn: () => getParcelasPessoa(cpfCnpj!, ano),
    enabled: !!cpfCnpj,
    staleTime: 30_000,
  });
}

export function useOrgaos(filters: OrgaosFilters) {
  return useQuery({
    queryKey: [KEY, "orgaos", filters],
    queryFn: () => listOrgaos(filters),
    staleTime: 30_000,
    placeholderData: keepPreviousData,
  });
}

export function usePessoasDoOrgao(idOrgao: number | null, ano?: number, mes?: number) {
  return useQuery({
    queryKey: [KEY, "orgao-pessoas", idOrgao, ano, mes],
    queryFn: () => getPessoasDoOrgao(idOrgao!, ano, mes),
    enabled: idOrgao !== null,
    staleTime: 30_000,
  });
}

export function useDepositosOrgao(idOrgao: number | null) {
  return useQuery({
    queryKey: [KEY, "depositos-orgao", idOrgao],
    queryFn: () => getDepositosOrgao(idOrgao!),
    enabled: idOrgao !== null,
    staleTime: 5 * 60_000,
  });
}

export function useDepositosOrgaoLancamentos(idOrgao: number | null) {
  return useQuery({
    queryKey: [KEY, "depositos-orgao-lancamentos", idOrgao],
    queryFn: () => getDepositosOrgaoLancamentos(idOrgao!),
    enabled: idOrgao !== null,
    staleTime: 5 * 60_000,
  });
}

export function useOrgaosDisponiveis(busca: string) {
  return useQuery({
    queryKey: [KEY, "orgaos-disponiveis", busca],
    queryFn: () => listOrgaosDisponiveis(busca || undefined),
    staleTime: 5 * 60_000,
    enabled: busca.length >= 2,
  });
}

export function useCadastros(q: string, page: number, size: number) {
  return useQuery({
    queryKey: [KEY, "cadastros", q, page, size],
    queryFn: () => listCadastros(q || undefined, page, size),
    staleTime: 30_000,
    placeholderData: keepPreviousData,
  });
}

export function useCriarCadastro() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: criarCadastro,
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useDeletarCadastro() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: deletarCadastro,
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useCriarMatchManual() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: criarMatchManual,
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useAtribuirOrgaoPessoa() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ cpfCnpj, idOrgao }: { cpfCnpj: string; idOrgao: number }) =>
      atribuirOrgaoPessoa(cpfCnpj, idOrgao),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useDeletarMatchManual() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: deletarMatchManual,
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useTipologiaRepasseMulti(filters: RepasseMultiFilters, enabled = true) {
  return useQuery({
    queryKey: [KEY, "tipologia-repasse-multi", filters],
    queryFn: () => getTipologiaRepasseMulti(filters),
    staleTime: 60_000,
    enabled,
  });
}

export function useTipologiaCpfSemSiai(enabled = true) {
  return useQuery({
    queryKey: [KEY, "tipologia-cpf-sem-siai"],
    queryFn: () => getTipologiaCpfSemSiai(),
    staleTime: 5 * 60_000,
    enabled,
  });
}

export function useTipologiaParcelaDuplicada(
  ano: number | undefined,
  mes: number | undefined,
  enabled = true,
) {
  return useQuery({
    queryKey: [KEY, "tipologia-parcela-duplicada", ano, mes],
    queryFn: () => getTipologiaParcelaDuplicada(ano, mes),
    staleTime: 60_000,
    enabled,
  });
}

export function useTipologiaAtrasoSistemico(
  ano: number | undefined,
  mesesConsecutivos: number,
  pctMinimo: number,
  enabled = true,
) {
  return useQuery({
    queryKey: [KEY, "tipologia-atraso-sistemico", ano, mesesConsecutivos, pctMinimo],
    queryFn: () => getTipologiaAtrasoSistemico(ano, mesesConsecutivos, pctMinimo),
    staleTime: 60_000,
    enabled,
  });
}
