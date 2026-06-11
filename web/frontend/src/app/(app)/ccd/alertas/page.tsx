"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useAlertasCCD } from "@/hooks/use-ccd-alertas";
import { marcadorColor } from "@/lib/marcador-color";
import type { Alerta, TipoAlerta } from "@/schemas/ccd-alertas";

const MARCADOR_PARCELAMENTO = "PARCELAMENTO EM CURSO";

// Situações que representam parcelamento encerrado/cancelado (Badge destrutivo).
const SITUACOES_CANCELADAS = new Set(["3", "5"]);

function formatarData(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? "—" : d.toLocaleDateString("pt-BR");
}

export default function AlertasPage() {
  const { data, isFetching, isError, error } = useAlertasCCD();

  return (
    <div className="flex flex-col gap-6">
      <h1 className="section-heading text-2xl">Alertas</h1>
      <p className="text-sm text-muted-foreground">
        Inconsistências entre marcadores e a situação real dos processos no setor CCD, para a equipe
        revisar e dar a devida providência.
      </p>

      {isError ? (
        <p className="text-sm text-destructive">Erro ao carregar: {(error as Error).message}</p>
      ) : null}

      {isFetching && !data ? <p className="text-sm text-muted-foreground">Carregando...</p> : null}

      {data?.tipos.map((info) => {
        const items = data.items.filter((it) => it.tipo === info.tipo);
        return (
          <Card key={info.tipo}>
            <CardHeader>
              <div className="flex items-start justify-between gap-3">
                <div className="flex flex-col gap-1.5">
                  <CardTitle className="flex items-center gap-2 text-base">
                    {info.titulo}
                    <Badge variant={info.quantidade > 0 ? "warning" : "success"}>
                      {info.quantidade.toLocaleString("pt-BR")}
                    </Badge>
                  </CardTitle>
                  <CardDescription>{info.descricao}</CardDescription>
                </div>
                {info.tipo === "parcelamento_cancelado" ? (
                  <Badge
                    variant="outline"
                    className="whitespace-nowrap border"
                    style={marcadorColor(MARCADOR_PARCELAMENTO)}
                  >
                    {MARCADOR_PARCELAMENTO}
                  </Badge>
                ) : null}
              </div>
            </CardHeader>
            <CardContent>
              <AlertaTabela tipo={info.tipo} items={items} />
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}

function AlertaTabela({ tipo, items }: { tipo: TipoAlerta; items: Alerta[] }) {
  if (tipo !== "parcelamento_cancelado") return null;
  return (
    <div className="rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Processo</TableHead>
            <TableHead>Relator</TableHead>
            <TableHead>Marcador desde</TableHead>
            <TableHead>Último parcelamento</TableHead>
            <TableHead>Cancelado em</TableHead>
            <TableHead>Parcelas pagas</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {items.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} className="py-8 text-center text-muted-foreground">
                Nenhum alerta.
              </TableCell>
            </TableRow>
          ) : (
            items.map((alerta) => {
              const d = alerta.detalhe;
              const nuncaParcelado = d.id_parcelamento === null;
              const cancelado = d.situacao !== null && SITUACOES_CANCELADAS.has(d.situacao);
              return (
                <TableRow key={alerta.processo}>
                  <TableCell className="whitespace-nowrap font-mono text-xs font-medium">
                    {alerta.processo}
                  </TableCell>
                  <TableCell className="whitespace-nowrap">{alerta.relator ?? "—"}</TableCell>
                  <TableCell className="whitespace-nowrap">
                    {formatarData(alerta.data_marcador)}
                  </TableCell>
                  <TableCell>
                    {nuncaParcelado ? (
                      <span className="text-xs text-muted-foreground">Nunca parcelado</span>
                    ) : (
                      <Badge variant={cancelado ? "destructive" : "secondary"}>
                        {d.situacao_descricao ?? d.situacao ?? "—"}
                      </Badge>
                    )}
                  </TableCell>
                  <TableCell className="whitespace-nowrap">
                    {formatarData(d.data_cancelamento)}
                  </TableCell>
                  <TableCell className="whitespace-nowrap">
                    {d.numero_parcelas === null
                      ? "—"
                      : `${d.parcelas_pagas ?? 0}/${d.numero_parcelas}`}
                  </TableCell>
                </TableRow>
              );
            })
          )}
        </TableBody>
      </Table>
    </div>
  );
}
