"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { Button, buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useMultasNaoCominadas } from "@/hooks/use-multas-nao-cominadas";
import { messageForError } from "@/lib/error-messages";
import { formatCurrencyBRL, formatDate, formatProcesso } from "@/lib/format";
import { cn } from "@/lib/utils";

const PAGE_SIZE = 25;

function truncate(value: string, max: number): string {
  return value.length > max ? `${value.slice(0, max - 1)}…` : value;
}

function formatDataHora(iso: string | null | undefined): string {
  return iso ? new Date(iso).toLocaleDateString("pt-BR") : "—";
}

export default function MultasNaoCominadasPage() {
  const { data, isLoading, isError, error } = useMultasNaoCominadas();
  const [page, setPage] = useState(1);

  useEffect(() => {
    if (isError) {
      toast.error(messageForError(error, "Erro ao carregar as multas não cominadas."));
    }
  }, [isError, error]);

  const items = data?.items ?? [];
  const totalPages = Math.max(1, Math.ceil(items.length / PAGE_SIZE));
  const pagina = items.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <main className="mx-auto flex w-full max-w-screen-2xl flex-col gap-6 p-6">
      <div>
        <h1 className="text-2xl font-semibold">Multas não cominadas</h1>
        <p className="text-sm text-muted-foreground">
          Obrigações revisadas e aprovadas com multa cominatória prevista na decisão, cujo processo
          não tem nenhum débito do tipo multa cominatória cadastrado no sistema de execução.
        </p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-center gap-3">
            <CardTitle className="section-heading text-base">Obrigações</CardTitle>
            {data && (
              <span className="text-sm text-muted-foreground">
                {data.total_obrigacoes} obrigações em {data.total_processos} processos
              </span>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Processo</TableHead>
                <TableHead>Obrigação</TableHead>
                <TableHead>Responsável pela multa</TableHead>
                <TableHead className="text-right">Valor/dia</TableHead>
                <TableHead>Prazo</TableHead>
                <TableHead>Cumprimento</TableHead>
                <TableHead>Revisão</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell
                    colSpan={8}
                    className="py-10 text-center text-sm text-muted-foreground"
                  >
                    Carregando...
                  </TableCell>
                </TableRow>
              ) : pagina.length === 0 ? (
                <TableRow>
                  <TableCell
                    colSpan={8}
                    className="py-10 text-center text-sm text-muted-foreground"
                  >
                    Nenhuma obrigação.
                  </TableCell>
                </TableRow>
              ) : (
                pagina.map((m) => (
                  <TableRow key={m.id}>
                    <TableCell className="font-mono">
                      {formatProcesso(m.numero_processo, m.ano_processo, m.id_processo)}
                    </TableCell>
                    <TableCell className="max-w-md">
                      <span title={m.descricao}>{truncate(m.descricao, 90)}</span>
                      {m.orgao && <div className="text-xs text-muted-foreground">{m.orgao}</div>}
                    </TableCell>
                    <TableCell>
                      {m.responsavel ?? <span className="text-muted-foreground">—</span>}
                      {m.documento && (
                        <div className="font-mono text-xs text-muted-foreground">{m.documento}</div>
                      )}
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {formatCurrencyBRL(m.valor_dia)}
                      {m.periodo && (
                        <div className="text-xs text-muted-foreground">{m.periodo}</div>
                      )}
                    </TableCell>
                    <TableCell className="max-w-xs">
                      <span title={m.prazo ?? undefined}>
                        {m.prazo ? truncate(m.prazo, 40) : "—"}
                      </span>
                    </TableCell>
                    <TableCell>{formatDate(m.data_cumprimento)}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <div>
                          <div>{m.revisor ?? <span className="text-muted-foreground">—</span>}</div>
                          <div className="text-xs text-muted-foreground">
                            {formatDataHora(m.data_revisao)}
                          </div>
                        </div>
                        {m.id_decisao != null && (
                          <Link
                            href={`/cgad/reviews/decisao/${m.id_decisao}/visualizar?voltar=/cgad/multas-nao-cominadas`}
                            className={buttonVariants({ size: "sm", variant: "outline" })}
                          >
                            Ver
                          </Link>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <span
                        className={cn(
                          "rounded px-1.5 py-0.5 text-xs font-medium",
                          m.status === "dispatched"
                            ? "bg-emerald-100 text-emerald-950"
                            : "bg-amber-100 text-amber-950",
                        )}
                      >
                        {m.status === "dispatched" ? "Enviado" : "Aprovado"}
                      </span>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>

          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>
              Página {page} de {totalPages}
            </span>
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => setPage(page - 1)}
                disabled={page <= 1}
              >
                Anterior
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => setPage(page + 1)}
                disabled={page >= totalPages}
              >
                Próxima
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </main>
  );
}
