"use client";

import { Fragment, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { SortableHead, useClientSort } from "@/components/sortable-table";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useMonitoramentosCCD } from "@/hooks/use-ccd-monitoramentos";
import type { Monitoramento, Urgencia } from "@/schemas/ccd-monitoramentos";

const URGENCIAS: {
  valor: Urgencia;
  label: string;
  variant: "destructive" | "warning" | "secondary";
}[] = [
  { valor: "alta", label: "Alta", variant: "destructive" },
  { valor: "media", label: "Média", variant: "warning" },
  { valor: "baixa", label: "Baixa", variant: "secondary" },
];
const ORDEM_URGENCIA: Record<Urgencia, number> = { alta: 0, media: 1, baixa: 2 };

type Filtro = Urgencia | "todas";
type SortKey = "processo" | "tipo" | "relator" | "urgencia" | "dias_ccd" | "ultima_peca";

const GETTERS: Record<SortKey, (m: Monitoramento) => string | number | null | undefined> = {
  processo: (m) => m.processo.split("/").reverse().join("/"),
  tipo: (m) => m.tipo,
  relator: (m) => m.relator,
  urgencia: (m) => (m.urgencia ? ORDEM_URGENCIA[m.urgencia] : 9),
  dias_ccd: (m) => m.dias_ccd,
  ultima_peca: (m) => m.ultima_peca_data,
};

function formatarData(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? "—" : d.toLocaleDateString("pt-BR");
}

function UrgenciaBadge({ urgencia }: { urgencia: Urgencia | null }) {
  const u = URGENCIAS.find((x) => x.valor === urgencia);
  return u ? <Badge variant={u.variant}>{u.label}</Badge> : <span>—</span>;
}

export default function MonitoramentosPage() {
  const { data, isFetching, isError, error } = useMonitoramentosCCD();
  const [filtro, setFiltro] = useState<Filtro>("todas");
  const items = (data?.items ?? []).filter((m) => filtro === "todas" || m.urgencia === filtro);
  const contar = (u: Filtro) =>
    (data?.items ?? []).filter((m) => u === "todas" || m.urgencia === u).length;

  return (
    <div className="flex flex-col gap-6">
      <h1 className="section-heading text-2xl">Monitoramentos</h1>
      <p className="text-sm text-muted-foreground">
        Processos MON e de outros tipos com o marcador “Monitorar obrigação de fazer” no setor CCD,
        com a natureza e o próximo passo. O job diário reanalisa só os processos com peça nova.
        {data?.calculado_em
          ? ` Atualizado em ${new Date(data.calculado_em).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" })}.`
          : null}
      </p>

      {isError ? (
        <p className="text-sm text-destructive">Erro ao carregar: {(error as Error).message}</p>
      ) : null}
      {isFetching && !data ? <p className="text-sm text-muted-foreground">Carregando...</p> : null}

      {data ? (
        <>
          <Tabs value={filtro} onValueChange={(v) => setFiltro(v as Filtro)}>
            <TabsList>
              {[{ valor: "todas" as Filtro, label: "Todas" }, ...URGENCIAS].map((u) => (
                <TabsTrigger key={u.valor} value={u.valor}>
                  {u.label}
                  <Badge variant="outline" className="ml-2">
                    {contar(u.valor)}
                  </Badge>
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>
          <MonitoramentosTabela items={items} />
        </>
      ) : null}
    </div>
  );
}

function MonitoramentosTabela({ items }: { items: Monitoramento[] }) {
  const { sorted, sort, toggle } = useClientSort<Monitoramento, SortKey>(items, GETTERS);
  const [aberto, setAberto] = useState<string | null>(null);

  return (
    <div className="rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            <SortableHead label="Processo" col="processo" sort={sort} onClick={toggle} />
            <SortableHead label="Tipo" col="tipo" sort={sort} onClick={toggle} />
            <SortableHead label="Relator" col="relator" sort={sort} onClick={toggle} />
            <TableCell className="font-medium">Jurisdicionado · natureza</TableCell>
            <TableCell className="font-medium">Próximo passo</TableCell>
            <SortableHead label="Urgência" col="urgencia" sort={sort} onClick={toggle} />
            <SortableHead
              label="Dias na CCD"
              col="dias_ccd"
              sort={sort}
              onClick={toggle}
              align="right"
            />
            <SortableHead label="Última peça" col="ultima_peca" sort={sort} onClick={toggle} />
          </TableRow>
        </TableHeader>
        <TableBody>
          {sorted.length === 0 ? (
            <TableRow>
              <TableCell colSpan={8} className="py-8 text-center text-muted-foreground">
                Nenhum processo.
              </TableCell>
            </TableRow>
          ) : (
            sorted.map((m) => (
              <Fragment key={m.processo}>
                <TableRow
                  className="cursor-pointer align-top"
                  onClick={() => setAberto(aberto === m.processo ? null : m.processo)}
                >
                  <TableCell className="whitespace-nowrap font-mono text-xs font-medium">
                    {m.processo}
                  </TableCell>
                  <TableCell>{m.tipo ?? "—"}</TableCell>
                  <TableCell className="max-w-40 text-xs">{m.relator ?? "—"}</TableCell>
                  <TableCell className="max-w-md text-xs">
                    <div className="font-medium">{m.jurisdicionado ?? m.assunto ?? "—"}</div>
                    <div className="text-muted-foreground">{m.natureza ?? "Sem análise."}</div>
                  </TableCell>
                  <TableCell className="max-w-md text-xs">
                    {m.proximo_passo ?? "—"}
                    {m.desatualizada ? (
                      <Badge variant="warning" className="ml-2">
                        peça nova
                      </Badge>
                    ) : null}
                  </TableCell>
                  <TableCell>
                    <UrgenciaBadge urgencia={m.urgencia} />
                  </TableCell>
                  <TableCell className="text-right">{m.dias_ccd ?? "—"}</TableCell>
                  <TableCell className="whitespace-nowrap text-xs">
                    {m.ultima_peca_evento !== null ? `Ev. ${m.ultima_peca_evento} · ` : ""}
                    {formatarData(m.ultima_peca_data)}
                  </TableCell>
                </TableRow>
                {aberto === m.processo ? (
                  <TableRow className="bg-muted/30 hover:bg-muted/30">
                    <TableCell colSpan={8} className="whitespace-normal">
                      <div className="flex flex-col gap-3 p-2">
                        <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                          <span>
                            Análise{" "}
                            {m.fonte === "manual"
                              ? "manual"
                              : m.fonte === "llm"
                                ? "automática (LLM)"
                                : "pendente"}
                            {m.analisado_em ? ` em ${formatarData(m.analisado_em)}` : ""}
                          </span>
                          {m.marcadores.map((mc) => (
                            <Badge key={mc} variant="outline">
                              {mc}
                            </Badge>
                          ))}
                        </div>
                        {m.ficha_md ? (
                          <div className="prose prose-sm prose-neutral max-w-none dark:prose-invert">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.ficha_md}</ReactMarkdown>
                          </div>
                        ) : (
                          <p className="text-sm text-muted-foreground">Sem ficha.</p>
                        )}
                        {m.ultima_peca_resumo ? (
                          <p className="text-xs text-muted-foreground">
                            Última peça: {m.ultima_peca_resumo}
                          </p>
                        ) : null}
                      </div>
                    </TableCell>
                  </TableRow>
                ) : null}
              </Fragment>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
}
