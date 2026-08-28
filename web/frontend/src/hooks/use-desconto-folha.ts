"use client";

import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  atribuirOrgaoPessoa,
  atualizarCadastro,
  atualizarMonitoramento,
  atualizarParcela,
  criarCadastro,
  criarMatchManual,
  criarMonitoramento,
  criarParcela,
  deletarCadastro,
  deletarMatchManual,
  deletarMonitoramento,
  deletarParcela,
  getCadastro,
  getDepositosOrgao,
  getDepositosOrgaoLancamentos,
  getMonitoramentoResumo,
  getParcelasPessoa,
  getPessoasProcesso,
  getPessoasDoOrgao,
  getTipologiaAtrasoSistemico,
  getTipologiaCpfSemSiai,
  getTipologiaParcelaDuplicada,
  getTipologiaRepasseMulti,
  listCadastros,
  listMonitoramento,
  listOrgaos,
  listOrgaosDisponiveis,
  listPessoas,
  type MonitoramentoFilters,
  type OrgaosFilters,
  type PessoasFilters,
  type RepasseMultiFilters,
} from "@/lib/api/desconto-folha";
import type {
  CadastroManualUpdate,
  GrupoMonitoramento,
  MonitoramentoPayload,
  ParcelaManualInput,
  ParcelaManualUpdate,
} from "@/schemas/desconto-folha";

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

export function useCadastro(idDescontoFolha: number | null) {
  return useQuery({
    queryKey: [KEY, "cadastro", idDescontoFolha],
    queryFn: () => getCadastro(idDescontoFolha!),
    enabled: idDescontoFolha !== null,
    staleTime: 10_000,
  });
}

export function useAtualizarCadastro() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, input }: { id: number; input: CadastroManualUpdate }) =>
      atualizarCadastro(id, input),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useCriarParcela() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, input }: { id: number; input: ParcelaManualInput }) =>
      criarParcela(id, input),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useAtualizarParcela() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      idParcela,
      input,
    }: {
      id: number;
      idParcela: number;
      input: ParcelaManualUpdate;
    }) => atualizarParcela(id, idParcela, input),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useDeletarParcela() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, idParcela }: { id: number; idParcela: number }) =>
      deletarParcela(id, idParcela),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useMonitoramento(filters: MonitoramentoFilters) {
  return useQuery({
    queryKey: [KEY, "monitoramento", filters],
    queryFn: () => listMonitoramento(filters),
    staleTime: 30_000,
    placeholderData: keepPreviousData,
  });
}

export function useMonitoramentoResumo(grupo?: GrupoMonitoramento) {
  return useQuery({
    queryKey: [KEY, "monitoramento-resumo", grupo],
    queryFn: () => getMonitoramentoResumo(grupo),
    staleTime: 30_000,
  });
}

export function useCriarMonitoramento() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: criarMonitoramento,
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function useAtualizarMonitoramento() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: MonitoramentoPayload }) =>
      atualizarMonitoramento(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });
}

export function usePessoasProcesso(processo: string) {
  const proc = processo.trim();
  return useQuery({
    queryKey: [KEY, "monitoramento-pessoas", proc],
    queryFn: () => getPessoasProcesso(proc),
    enabled: /^\d{1,6}\s*\/\s*\d{4}$/.test(proc),
    staleTime: 5 * 60_000,
  });
}

export function useDeletarMonitoramento() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: deletarMonitoramento,
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
