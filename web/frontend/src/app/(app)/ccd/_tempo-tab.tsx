"use client";

import { parseAsInteger, useQueryState } from "nuqs";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useProcessosCCD } from "@/hooks/use-ccd-processos";
import { formatDate } from "@/lib/format";
import { marcadorColor } from "@/lib/marcador-color";

const SIZE = 100;

export function TempoTab({ ocultarPermanencia }: { ocultarPermanencia: boolean }) {
  const [page, setPage] = useQueryState("pagina_tempo", parseAsInteger.withDefault(1));

  const { data, isFetching, isError, error } = useProcessosCCD({
    sort: "dias_ccd",
    order: "desc",
    ocultarPermanencia,
    page,
    size: SIZE,
  });

  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / SIZE));

  return (
    <div className="flex flex-col gap-4">
      <p className="text-sm text-muted-foreground">
        {isFetching
          ? "Carregando..."
          : `${total.toLocaleString("pt-BR")} processos, os mais antigos na CCD primeiro`}
      </p>

      {isError ? (
        <p className="text-sm text-destructive">Erro ao carregar: {(error as Error).message}</p>
      ) : null}

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Processo</TableHead>
              <TableHead className="text-right">Dias na CCD</TableHead>
              <TableHead>Entrada</TableHead>
              <TableHead>Marcador</TableHead>
              <TableHead>Relator</TableHead>
              <TableHead>Assunto</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.items.length === 0 && !isFetching ? (
              <TableRow>
                <TableCell colSpan={6} className="py-8 text-center text-muted-foreground">
                  Nenhum processo encontrado.
                </TableCell>
              </TableRow>
            ) : (
              data?.items.map((row) => (
                <TableRow key={row.processo}>
                  <TableCell className="whitespace-nowrap font-mono text-xs font-medium">
                    {row.processo}
                  </TableCell>
                  <TableCell className="text-right font-medium tabular-nums">
                    {row.dias_ccd != null ? row.dias_ccd.toLocaleString("pt-BR") : "—"}
                  </TableCell>
                  <TableCell className="whitespace-nowrap">
                    {formatDate(row.entrada_ccd?.split("T")[0])}
                  </TableCell>
                  <TableCell>
                    {row.marcador ? (
                      <Badge
                        variant="outline"
                        className="whitespace-nowrap border"
                        style={marcadorColor(row.marcador)}
                      >
                        {row.marcador}
                      </Badge>
                    ) : (
                      <span className="text-xs text-muted-foreground">—</span>
                    )}
                  </TableCell>
                  <TableCell className="whitespace-nowrap">{row.relator ?? "—"}</TableCell>
                  <TableCell className="max-w-[280px] truncate" title={row.assunto ?? ""}>
                    {row.assunto ?? "—"}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-end gap-2">
        <span className="text-sm text-muted-foreground">
          Página {page} de {totalPages}
        </span>
        <Button
          variant="outline"
          size="sm"
          disabled={page <= 1 || isFetching}
          onClick={() => setPage(Math.max(1, page - 1))}
        >
          Anterior
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={page >= totalPages || isFetching}
          onClick={() => setPage(page + 1)}
        >
          Próxima
        </Button>
      </div>
    </div>
  );
}
