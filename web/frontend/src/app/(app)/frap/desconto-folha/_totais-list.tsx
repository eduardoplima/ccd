"use client";

import { Table, TableBody, TableCell, TableHeader, TableRow } from "@/components/ui/table";
import { useFasesDebitosNotificados, useFasesTotais } from "@/hooks/use-fases";
import { formatBRL } from "@/lib/format";
import type { DebitoFase, DebitosFaseResumo } from "@/schemas/fases";

import { SortableHead, useClientSort } from "./_sortable";

type DebitoSortKey =
  | "idDebito"
  | "processoOrigem"
  | "processoExecucao"
  | "valorOriginal"
  | "valorAtualizado"
  | "tipoDebito"
  | "statusDivida";

function processoKey(numero: string | null | undefined, ano: string | null | undefined): string {
  if (!numero || !ano) return "";
  return `${ano}/${numero}`;
}

function formatProcesso(numero: string | null | undefined, ano: string | null | undefined): string {
  if (numero && ano) return `${numero}/${ano}`;
  return "—";
}

const GETTERS: Record<DebitoSortKey, (d: DebitoFase) => string | number | null | undefined> = {
  idDebito: (d) => d.idDebito,
  processoOrigem: (d) => processoKey(d.numeroProcessoOrigem, d.anoProcessoOrigem),
  processoExecucao: (d) => processoKey(d.numeroProcessoExecucao, d.anoProcessoExecucao),
  valorOriginal: (d) => d.valorOriginal,
  valorAtualizado: (d) => d.valorAtualizado,
  tipoDebito: (d) => d.tipoDebito ?? "",
  statusDivida: (d) => d.statusDivida ?? "",
};

export function TotaisList({ cpfCnpj }: { cpfCnpj: string }) {
  const { data, isFetching } = useFasesTotais(cpfCnpj, true);
  return <DebitosTable data={data} isFetching={isFetching} />;
}

export function DebitosNotificadosList({ cpfCnpj }: { cpfCnpj: string }) {
  const { data, isFetching } = useFasesDebitosNotificados(cpfCnpj, true);
  return <DebitosTable data={data} isFetching={isFetching} />;
}

function DebitosTable({
  data,
  isFetching,
}: {
  data: DebitosFaseResumo | undefined;
  isFetching: boolean;
}) {
  const items = data?.debitos ?? [];
  const { sorted, sort, toggle } = useClientSort<DebitoFase, DebitoSortKey>(items, GETTERS);

  if (isFetching && !data) {
    return (
      <p className="text-xs text-muted-foreground">Carregando débitos (valor atualizado)...</p>
    );
  }
  if (!data) return null;
  return (
    <div className="rounded border">
      <Table>
        <TableHeader>
          <TableRow>
            <SortableHead label="Id Débito" col="idDebito" sort={sort} onClick={toggle} />
            <SortableHead
              label="Processo Origem"
              col="processoOrigem"
              sort={sort}
              onClick={toggle}
            />
            <SortableHead
              label="Processo Execução"
              col="processoExecucao"
              sort={sort}
              onClick={toggle}
            />
            <SortableHead
              label="Original"
              col="valorOriginal"
              sort={sort}
              onClick={toggle}
              align="right"
            />
            <SortableHead
              label="Atualizado"
              col="valorAtualizado"
              sort={sort}
              onClick={toggle}
              align="right"
            />
            <SortableHead label="Tipo" col="tipoDebito" sort={sort} onClick={toggle} />
            <SortableHead label="Status" col="statusDivida" sort={sort} onClick={toggle} />
          </TableRow>
        </TableHeader>
        <TableBody>
          {sorted.length === 0 ? (
            <TableRow>
              <TableCell colSpan={7} className="py-6 text-center text-xs text-muted-foreground">
                Nenhum débito.
              </TableCell>
            </TableRow>
          ) : (
            sorted.map((d) => (
              <TableRow key={d.idDebito}>
                <TableCell className="font-mono text-xs">{d.idDebito}</TableCell>
                <TableCell className="font-mono text-xs">
                  {formatProcesso(d.numeroProcessoOrigem, d.anoProcessoOrigem)}
                </TableCell>
                <TableCell className="font-mono text-xs">
                  {formatProcesso(d.numeroProcessoExecucao, d.anoProcessoExecucao)}
                </TableCell>
                <TableCell className="text-right font-mono text-xs">
                  {formatBRL(d.valorOriginal)}
                </TableCell>
                <TableCell className="text-right font-mono text-xs">
                  {d.valorAtualizado != null ? formatBRL(d.valorAtualizado) : "—"}
                </TableCell>
                <TableCell className="text-xs">{d.tipoDebito ?? "—"}</TableCell>
                <TableCell className="text-xs">{d.statusDivida ?? "—"}</TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
}
