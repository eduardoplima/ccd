"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";

import { MultiAnnotatorCanvas } from "@/components/dataset/multi-annotator-canvas";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useDivergenciaDetail, useDivergencias } from "@/hooks/use-dataset";
import { messageForError } from "@/lib/error-messages";
import { cn } from "@/lib/utils";
import { LABELS, Label, TIPOS_DIVERGENCIA, TipoDivergencia } from "@/schemas/dataset";

const TIPO_NOME: Record<TipoDivergencia, string> = {
  rotulo: "Rótulo trocado",
  fronteira: "Fronteira",
  ausente: "Span ausente",
};

export function DivergenciasTab() {
  const [selecionado, setSelecionado] = useState<number | null>(null);
  const [filtroLabel, setFiltroLabel] = useState<Label | null>(null);
  const [filtroTipo, setFiltroTipo] = useState<TipoDivergencia | null>(null);

  const divergencias = useDivergencias();
  const detalhe = useDivergenciaDetail(selecionado);

  useEffect(() => {
    if (!divergencias.isError) return;
    toast.error(messageForError(divergencias.error, "Erro ao carregar as divergências."));
  }, [divergencias.isError, divergencias.error]);

  const data = divergencias.data;
  const documentos = (data?.documentos ?? []).filter(
    (d) =>
      (filtroLabel === null || d.rotulos.includes(filtroLabel)) &&
      (filtroTipo === null || d.tipos.includes(filtroTipo)),
  );

  return (
    <div className="flex flex-col gap-4">
      <p className="text-sm text-muted-foreground">
        Onde {data?.anotadores.join(", ") ?? "os anotadores"} mais discordam, par a par: rótulo
        trocado (mesmo trecho, classes diferentes), fronteira (mesmo rótulo, limites diferentes) e
        span ausente (um marcou, o outro não).
      </p>

      <div className="flex flex-wrap gap-3">
        <Cartao titulo="Documentos comuns" valor={data?.documentos_comuns ?? 0} />
        <Cartao titulo="Docs com divergência" valor={data?.documentos.length ?? 0} />
        <Cartao
          titulo="Divergências (pares)"
          valor={data?.por_tipo.reduce((soma, t) => soma + t.total, 0) ?? 0}
        />
        {data?.por_tipo.map((t) => (
          <Cartao key={t.tipo} titulo={TIPO_NOME[t.tipo]} valor={t.total} />
        ))}
      </div>

      {data && (
        <section className="rounded-md border bg-card p-4">
          <h2 className="mb-2 text-sm font-semibold">Por rótulo</h2>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Rótulo</TableHead>
                <TableHead className="text-right">Acertos</TableHead>
                <TableHead className="text-right">Divergências</TableHead>
                <TableHead className="text-right">Concordância</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.por_rotulo.map((r) => (
                <TableRow key={r.label}>
                  <TableCell className="font-medium">{r.label}</TableCell>
                  <TableCell className="text-right">{r.acertos}</TableCell>
                  <TableCell className="text-right">{r.divergencias}</TableCell>
                  <TableCell className="text-right">
                    {r.f1 === null ? "—" : `${(r.f1 * 100).toFixed(1)}%`}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </section>
      )}

      <div className="flex flex-wrap items-center gap-2 text-sm">
        <span className="text-muted-foreground">Filtrar:</span>
        {LABELS.map((label) => (
          <Chip
            key={label}
            ativo={filtroLabel === label}
            onClick={() => setFiltroLabel(filtroLabel === label ? null : label)}
          >
            {label}
          </Chip>
        ))}
        <span className="mx-1 text-muted-foreground">·</span>
        {TIPOS_DIVERGENCIA.map((tipo) => (
          <Chip
            key={tipo}
            ativo={filtroTipo === tipo}
            onClick={() => setFiltroTipo(filtroTipo === tipo ? null : tipo)}
          >
            {TIPO_NOME[tipo]}
          </Chip>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-[400px_minmax(0,1fr)]">
        <section className="max-h-[70vh] overflow-y-auto rounded-md border bg-card">
          {divergencias.isLoading && (
            <p className="p-4 text-sm text-muted-foreground">Carregando…</p>
          )}
          {!divergencias.isLoading && documentos.length === 0 && (
            <p className="p-4 text-sm text-muted-foreground">Nenhum documento divergente.</p>
          )}
          {documentos.map((d) => (
            <button
              key={d.id}
              type="button"
              onClick={() => setSelecionado(d.id)}
              className={cn(
                "flex w-full flex-col gap-1 border-b px-4 py-3 text-left transition-colors last:border-b-0 hover:bg-muted/60",
                selecionado === d.id && "bg-muted",
              )}
            >
              <div className="flex items-baseline justify-between gap-2">
                <span className="text-sm font-medium">{d.processo ?? `doc ${d.id}`}</span>
                <span className="text-xs text-muted-foreground">
                  {d.divergencias} div. · {(d.score * 100).toFixed(0)}%
                </span>
              </div>
              <div className="text-xs text-muted-foreground">
                {Object.entries(d.spans_por_anotador)
                  .map(([nome, n]) => `${nome} ${n}`)
                  .join(" · ")}
              </div>
              <div className="flex flex-wrap gap-1 text-xs text-muted-foreground">
                {d.tipos.map((t) => (
                  <span key={t} className="rounded-sm bg-muted px-1.5 py-0.5">
                    {TIPO_NOME[t]}
                  </span>
                ))}
                {d.rotulos.map((r) => (
                  <span key={r} className="rounded-sm bg-muted px-1.5 py-0.5">
                    {r}
                  </span>
                ))}
              </div>
            </button>
          ))}
        </section>

        <section>
          {selecionado === null && (
            <p className="rounded-md border bg-card p-6 text-sm text-muted-foreground">
              Selecione um documento na lista para ver as três anotações sobrepostas.
            </p>
          )}
          {detalhe.isLoading && (
            <p className="rounded-md border bg-card p-6 text-sm text-muted-foreground">
              Carregando…
            </p>
          )}
          {detalhe.data && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold">
                  {detalhe.data.processo ?? `Documento ${detalhe.data.id}`}
                  {detalhe.data.codigo_tipo_processo && (
                    <span className="ml-2 text-sm font-normal text-muted-foreground">
                      {detalhe.data.codigo_tipo_processo}
                    </span>
                  )}
                </h2>
                <span className="text-sm text-muted-foreground">
                  {detalhe.data.anotacoes
                    .map((a) => `${a.anotador}: ${a.spans.length} spans`)
                    .join(" · ")}
                </span>
              </div>
              <MultiAnnotatorCanvas text={detalhe.data.texto} anotacoes={detalhe.data.anotacoes} />
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

function Cartao({ titulo, valor }: { titulo: string; valor: number }) {
  return (
    <div className="rounded-md border bg-card px-4 py-3">
      <div className="text-xs text-muted-foreground">{titulo}</div>
      <div className="text-2xl font-semibold">{valor}</div>
    </div>
  );
}

function Chip({
  ativo,
  onClick,
  children,
}: {
  ativo: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <Button size="sm" variant={ativo ? "default" : "outline"} onClick={onClick}>
      {children}
    </Button>
  );
}
