"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useDocumentos, useProgresso } from "@/hooks/use-dataset";
import { messageForError } from "@/lib/error-messages";

const PAGE_SIZE = 20;

type Tab = "pending" | "done" | "entidades" | "vazios";

const FILTROS: Record<Tab, { status?: string; comEntidades?: boolean }> = {
  pending: { status: "pending" },
  done: { status: "done" },
  entidades: { comEntidades: true },
  vazios: { comEntidades: false },
};

export default function DatasetPage() {
  const [tab, setTab] = useState<Tab>("pending");
  const [page, setPage] = useState(1);

  const documentos = useDocumentos({ page, pageSize: PAGE_SIZE, ...FILTROS[tab] });
  const progresso = useProgresso();

  useEffect(() => {
    if (!documentos.isError) return;
    toast.error(messageForError(documentos.error, "Erro ao carregar o conjunto de dados."));
  }, [documentos.isError, documentos.error]);

  const data = documentos.data;
  const totalPages = Math.max(1, Math.ceil((data?.total ?? 0) / PAGE_SIZE));

  return (
    <main className="mx-auto flex w-full max-w-screen-2xl flex-col gap-4 p-6">
      <div>
        <h1 className="text-2xl font-semibold">Conjunto de dados</h1>
        <p className="text-sm text-muted-foreground">
          Anote no texto do acórdão as multas, obrigações, recomendações e ressarcimentos. Cada
          anotador trabalha de forma independente — você não vê a anotação dos demais.
        </p>
        <p className="text-sm text-muted-foreground">
          As duas últimas abas são uma triagem por probabilidade: um documento cai em{" "}
          <strong>Probabilidade de ter entidades</strong> quando a anotação de referência ou o
          modelo encontraram alguma multa, obrigação, recomendação ou ressarcimento nele. É só uma
          estimativa — nenhuma marcação é mostrada na tela de anotação, e os dois lados erram.
        </p>
      </div>

      <div className="flex flex-wrap gap-3">
        <Cartao titulo="Pendentes" valor={data?.pendentes ?? 0} />
        <Cartao titulo="Concluídos" valor={data?.concluidos ?? 0} />
        <Cartao titulo="Prob. de ter entidades" valor={data?.com_entidades ?? 0} />
        <Cartao
          titulo="Prob. de ser vazio"
          valor={data ? Math.max(0, data.pendentes + data.concluidos - data.com_entidades) : 0}
        />
        <Cartao titulo="Documentos no conjunto" valor={progresso.data?.documentos ?? 0} />
      </div>

      <Tabs
        value={tab}
        onValueChange={(v) => {
          setTab(v as Tab);
          setPage(1);
        }}
      >
        <TabsList>
          <TabsTrigger value="pending">Pendentes</TabsTrigger>
          <TabsTrigger value="done">Concluídos</TabsTrigger>
          <TabsTrigger value="entidades">Probabilidade de ter entidades</TabsTrigger>
          <TabsTrigger value="vazios">Probabilidade de ser vazio</TabsTrigger>
        </TabsList>
      </Tabs>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-24">Processo</TableHead>
            <TableHead className="w-16">Tipo</TableHead>
            <TableHead>Trecho</TableHead>
            <TableHead className="w-20 text-right">Spans</TableHead>
            <TableHead className="w-24" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {documentos.isLoading && (
            <TableRow>
              <TableCell colSpan={5} className="text-center text-muted-foreground">
                Carregando…
              </TableCell>
            </TableRow>
          )}
          {!documentos.isLoading && (data?.items.length ?? 0) === 0 && (
            <TableRow>
              <TableCell colSpan={5} className="text-center text-muted-foreground">
                Nada por aqui.
              </TableCell>
            </TableRow>
          )}
          {data?.items.map((item) => (
            <TableRow key={item.id}>
              <TableCell className="font-medium">{item.processo ?? "—"}</TableCell>
              <TableCell className="text-muted-foreground">
                {item.codigo_tipo_processo ?? "—"}
              </TableCell>
              <TableCell className="max-w-xl truncate text-sm text-muted-foreground">
                {item.trecho}
              </TableCell>
              <TableCell className="text-right">{item.total_spans}</TableCell>
              <TableCell>
                <Link
                  href={`/cgad/dataset/${item.id}`}
                  className="text-sm font-medium text-primary hover:underline"
                >
                  {item.status === "done" ? "Rever" : "Anotar"}
                </Link>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>
          Página {page} de {totalPages} · {data?.total ?? 0} itens
        </span>
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => setPage(page - 1)}
            disabled={page <= 1 || documentos.isLoading}
          >
            Anterior
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => setPage(page + 1)}
            disabled={page >= totalPages || documentos.isLoading}
          >
            Próxima
          </Button>
        </div>
      </div>

      {progresso.data && progresso.data.anotadores.length > 0 && (
        <section className="space-y-2 rounded-md border bg-white p-4">
          <h2 className="text-sm font-semibold">Progresso da equipe</h2>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Anotador</TableHead>
                <TableHead className="text-right">Concluídos</TableHead>
                <TableHead className="text-right">Atribuídos</TableHead>
                <TableHead className="text-right">Spans</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {progresso.data.anotadores.map((a) => (
                <TableRow key={a.anotador}>
                  <TableCell className="font-medium">{a.anotador}</TableCell>
                  <TableCell className="text-right">{a.concluidos}</TableCell>
                  <TableCell className="text-right">{a.total}</TableCell>
                  <TableCell className="text-right">{a.spans}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {progresso.data.concordancia.some((c) => c.documentos_comuns > 0) && (
            <p className="pt-2 text-sm text-muted-foreground">
              Concordância (F1 de span, IoU ≥ 0,5):{" "}
              {progresso.data.concordancia
                .filter((c) => c.f1 !== null)
                .map(
                  (c) => `${c.a}×${c.b} ${(c.f1! * 100).toFixed(1)}% (${c.documentos_comuns} docs)`,
                )
                .join(" · ")}
            </p>
          )}
        </section>
      )}
    </main>
  );
}

function Cartao({ titulo, valor }: { titulo: string; valor: number }) {
  return (
    <div className="rounded-md border bg-white px-4 py-3">
      <div className="text-xs text-muted-foreground">{titulo}</div>
      <div className="text-2xl font-semibold">{valor}</div>
    </div>
  );
}
