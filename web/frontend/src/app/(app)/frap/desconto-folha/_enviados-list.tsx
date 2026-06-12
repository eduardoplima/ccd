"use client";

import { Table, TableBody, TableCell, TableHeader, TableRow } from "@/components/ui/table";
import { useFasesEnviados } from "@/hooks/use-fases";
import { formatDate } from "@/lib/format";
import { SortableHead, useClientSort } from "@/components/sortable-table";
import type { NotificacaoEnviada } from "@/schemas/fases";

type EnviadoSortKey = "processo" | "idDebito" | "idEventoCcd" | "dataPublicacaoCcd" | "resumoCcd";

const GETTERS: Record<
  EnviadoSortKey,
  (n: NotificacaoEnviada) => string | number | null | undefined
> = {
  processo: (n) => `${n.anoProcesso}/${n.numeroProcesso}`,
  idDebito: (n) => n.idDebito,
  idEventoCcd: (n) => n.idEventoCcd,
  dataPublicacaoCcd: (n) => n.dataPublicacaoCcd,
  resumoCcd: (n) => n.resumoCcd ?? "",
};

export function EnviadosList({ cpfCnpj }: { cpfCnpj: string }) {
  const { data, isFetching } = useFasesEnviados(cpfCnpj, true);
  const items = data?.items ?? [];
  const { sorted, sort, toggle } = useClientSort<NotificacaoEnviada, EnviadoSortKey>(
    items,
    GETTERS,
  );

  if (isFetching && !data) {
    return <p className="text-xs text-muted-foreground">Carregando notificações CCD...</p>;
  }
  if (!data) return null;
  if (data.items.length === 0) {
    return (
      <p className="rounded border border-dashed p-3 text-xs text-muted-foreground">
        Nenhuma notificação CCD escaneada para os débitos desta pessoa. Rode{" "}
        <code className="font-mono">frap scan-notificacoes-ccd</code>.
      </p>
    );
  }
  return (
    <div className="rounded border">
      <Table>
        <TableHeader>
          <TableRow>
            <SortableHead label="Processo" col="processo" sort={sort} onClick={toggle} />
            <SortableHead label="Id Débito" col="idDebito" sort={sort} onClick={toggle} />
            <SortableHead label="Evento CCD" col="idEventoCcd" sort={sort} onClick={toggle} />
            <SortableHead
              label="Data publicação"
              col="dataPublicacaoCcd"
              sort={sort}
              onClick={toggle}
            />
            <SortableHead label="Resumo" col="resumoCcd" sort={sort} onClick={toggle} />
          </TableRow>
        </TableHeader>
        <TableBody>
          {sorted.map((n) => (
            <TableRow key={n.idNotif}>
              <TableCell className="font-mono text-xs">
                {n.numeroProcesso}/{n.anoProcesso}
              </TableCell>
              <TableCell className="font-mono text-xs">{n.idDebito ?? "—"}</TableCell>
              <TableCell className="font-mono text-xs">{n.idEventoCcd}</TableCell>
              <TableCell className="font-mono text-xs">
                {formatDate(n.dataPublicacaoCcd?.split("T")[0] ?? null)}
              </TableCell>
              <TableCell className="max-w-[300px] truncate" title={n.resumoCcd ?? ""}>
                {n.resumoCcd ?? "—"}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
