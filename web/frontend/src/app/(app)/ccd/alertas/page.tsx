"use client";

import { SortableHead, useClientSort } from "@/components/sortable-table";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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

      {data && data.tipos.length > 0 ? (
        <Tabs defaultValue={data.tipos[0]?.tipo} className="w-full">
          <TabsList>
            {data.tipos.map((info) => (
              <TabsTrigger key={info.tipo} value={info.tipo}>
                {info.titulo}
                <Badge variant={info.quantidade > 0 ? "warning" : "success"} className="ml-2">
                  {info.quantidade.toLocaleString("pt-BR")}
                </Badge>
              </TabsTrigger>
            ))}
          </TabsList>

          {data.tipos.map((info) => (
            <TabsContent key={info.tipo} value={info.tipo} className="flex flex-col gap-3">
              <div className="flex items-start justify-between gap-3">
                <p className="text-sm text-muted-foreground">{info.descricao}</p>
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
              <AlertaTabela
                tipo={info.tipo}
                items={data.items.filter((it) => it.tipo === info.tipo)}
              />
            </TabsContent>
          ))}
        </Tabs>
      ) : null}
    </div>
  );
}

type AlertaSortKey =
  | "processo"
  | "relator"
  | "data_marcador"
  | "situacao"
  | "data_cancelamento"
  | "parcelas_pagas";

const GETTERS: Record<AlertaSortKey, (a: Alerta) => string | number | null | undefined> = {
  processo: (a) => a.processo,
  relator: (a) => a.relator,
  data_marcador: (a) => a.data_marcador,
  situacao: (a) => a.detalhe.situacao_descricao ?? a.detalhe.situacao,
  data_cancelamento: (a) => a.detalhe.data_cancelamento,
  parcelas_pagas: (a) => a.detalhe.parcelas_pagas,
};

function AlertaTabela({ tipo, items }: { tipo: TipoAlerta; items: Alerta[] }) {
  const { sorted, sort, toggle } = useClientSort<Alerta, AlertaSortKey>(items, GETTERS);

  if (tipo !== "parcelamento_cancelado") return null;

  return (
    <div className="rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            <SortableHead label="Processo" col="processo" sort={sort} onClick={toggle} />
            <SortableHead label="Relator" col="relator" sort={sort} onClick={toggle} />
            <SortableHead label="Marcador desde" col="data_marcador" sort={sort} onClick={toggle} />
            <SortableHead label="Último parcelamento" col="situacao" sort={sort} onClick={toggle} />
            <SortableHead
              label="Cancelado em"
              col="data_cancelamento"
              sort={sort}
              onClick={toggle}
            />
            <SortableHead
              label="Parcelas pagas"
              col="parcelas_pagas"
              sort={sort}
              onClick={toggle}
              align="right"
            />
          </TableRow>
        </TableHeader>
        <TableBody>
          {sorted.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} className="py-8 text-center text-muted-foreground">
                Nenhum alerta.
              </TableCell>
            </TableRow>
          ) : (
            sorted.map((alerta) => {
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
                  <TableCell className="whitespace-nowrap text-right">
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
