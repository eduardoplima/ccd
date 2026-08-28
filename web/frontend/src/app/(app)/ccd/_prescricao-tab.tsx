"use client";

import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHeader, TableRow } from "@/components/ui/table";
import { SortableHead, useClientSort } from "@/components/sortable-table";
import { usePrescricaoCCD } from "@/hooks/use-ccd-processos";
import { formatBRL, formatDate } from "@/lib/format";
import type { PrescricaoCCD } from "@/schemas/ccd";

const CATEGORIA: Record<
  PrescricaoCCD["categoria"],
  { label: string; variant: "destructive" | "warning" | "outline" }
> = {
  prescrito: { label: "Prescrito", variant: "destructive" },
  risco: { label: "Risco", variant: "warning" },
  ok: { label: "Ok", variant: "outline" },
  sem_referencia: { label: "Sem referência", variant: "outline" },
};

const FONTE_LABEL: Record<string, string> = {
  citação: "Citação",
  trânsito: "Trânsito",
};

type SortKey =
  | "processo"
  | "categoria"
  | "responsaveis"
  | "data_base"
  | "data_prescricao"
  | "dias"
  | "debitos"
  | "valor"
  | "assunto";

export function PrescricaoTab({ ocultarPermanencia }: { ocultarPermanencia: boolean }) {
  const { data, isFetching, isError, error } = usePrescricaoCCD(ocultarPermanencia);

  const items = data?.items ?? [];
  // sem sort inicial: preserva a ordem do servidor (mais urgente primeiro)
  const { sorted, sort, toggle } = useClientSort<PrescricaoCCD, SortKey>(items, {
    processo: (i) => `${i.ano_processo}${i.numero_processo}`,
    categoria: (i) => i.categoria,
    responsaveis: (i) => i.responsaveis,
    data_base: (i) => i.data_base,
    data_prescricao: (i) => i.data_prescricao,
    dias: (i) => i.dias_decorridos,
    debitos: (i) => i.qtd_debitos,
    valor: (i) => i.valor_total,
    assunto: (i) => i.assunto,
  });

  return (
    <div className="flex flex-col gap-4">
      <p className="text-sm text-muted-foreground">
        {isFetching
          ? "Carregando..."
          : `${items.length.toLocaleString("pt-BR")} processos com débito em aberto — prazo de 5 anos da citação ou, na falta, do trânsito em julgado (STF Tema 899)`}
      </p>

      {isError ? (
        <p className="text-sm text-destructive">Erro ao carregar: {(error as Error).message}</p>
      ) : null}

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <SortableHead label="Processo" col="processo" sort={sort} onClick={toggle} />
              <SortableHead label="Situação" col="categoria" sort={sort} onClick={toggle} />
              <SortableHead label="Responsáveis" col="responsaveis" sort={sort} onClick={toggle} />
              <SortableHead label="Base" col="data_base" sort={sort} onClick={toggle} />
              <SortableHead
                label="Prescreve em"
                col="data_prescricao"
                sort={sort}
                onClick={toggle}
              />
              <SortableHead label="Dias" col="dias" sort={sort} onClick={toggle} align="right" />
              <SortableHead
                label="Débitos"
                col="debitos"
                sort={sort}
                onClick={toggle}
                align="right"
              />
              <SortableHead
                label="Valor em aberto"
                col="valor"
                sort={sort}
                onClick={toggle}
                align="right"
              />
              <SortableHead label="Assunto" col="assunto" sort={sort} onClick={toggle} />
            </TableRow>
          </TableHeader>
          <TableBody>
            {items.length === 0 && !isFetching ? (
              <TableRow>
                <TableCell colSpan={9} className="py-8 text-center text-muted-foreground">
                  Nenhum processo encontrado.
                </TableCell>
              </TableRow>
            ) : (
              sorted.map((row) => {
                const cat = CATEGORIA[row.categoria];
                return (
                  <TableRow key={row.processo}>
                    <TableCell className="whitespace-nowrap font-mono text-xs font-medium">
                      {row.processo}
                    </TableCell>
                    <TableCell>
                      <Badge variant={cat.variant} className="whitespace-nowrap">
                        {cat.label}
                      </Badge>
                    </TableCell>
                    <TableCell className="max-w-[240px] truncate" title={row.responsaveis ?? ""}>
                      {row.responsaveis ?? "—"}
                    </TableCell>
                    <TableCell className="whitespace-nowrap">
                      {row.fonte_base
                        ? `${FONTE_LABEL[row.fonte_base] ?? row.fonte_base} ${formatDate(row.data_base?.split("T")[0])}`
                        : "—"}
                    </TableCell>
                    <TableCell className="whitespace-nowrap">
                      {formatDate(row.data_prescricao)}
                    </TableCell>
                    <TableCell className="text-right tabular-nums">
                      {row.dias_decorridos != null
                        ? row.dias_decorridos.toLocaleString("pt-BR")
                        : "—"}
                    </TableCell>
                    <TableCell className="text-right tabular-nums">{row.qtd_debitos}</TableCell>
                    <TableCell className="text-right tabular-nums whitespace-nowrap">
                      {formatBRL(row.valor_total)}
                    </TableCell>
                    <TableCell className="max-w-[280px] truncate" title={row.assunto ?? ""}>
                      {row.assunto ?? "—"}
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
