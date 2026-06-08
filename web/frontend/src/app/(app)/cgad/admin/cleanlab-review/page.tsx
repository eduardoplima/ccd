"use client";

import Link from "next/link";
import { useState } from "react";

import { ConfidenceFilter } from "@/components/dataset-corrections/confidence-filter";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  useDocuments,
  useProgress,
} from "@/hooks/use-dataset-corrections";
import { useMinConfidence } from "@/hooks/use-min-confidence";
import { exportUrl } from "@/lib/dataset-corrections-api";
import { getAccessToken } from "@/lib/auth";

const PAGE_SIZE = 25;

export default function CleanlabReviewPage() {
  const [page, setPage] = useState(1);
  const [onlyPending, setOnlyPending] = useState(true);
  const { fraction: minConfidence, percentage } = useMinConfidence();

  const documents = useDocuments({
    page,
    pageSize: PAGE_SIZE,
    onlyPending,
    minConfidence,
  });
  const progress = useProgress();

  function handleExport() {
    // Export is a GET, so we open it in a new tab with the access token
    // appended via fetch + blob (the simple <a download> would skip auth).
    const token = getAccessToken();
    fetch(exportUrl(), {
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    })
      .then(async (res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "dataset-corrections.json";
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
      })
      .catch(() => {
        // Toast suppressed here; the user will see it didn't download.
      });
  }

  const totalPages = documents.data
    ? Math.max(1, Math.ceil(documents.data.total / PAGE_SIZE))
    : 1;

  return (
    <main className="mx-auto flex w-full max-w-screen-2xl flex-col gap-4 p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Revisão cleanlab</h1>
          <p className="text-sm text-muted-foreground">
            Erros de anotação detectados pelo cleanlab no dataset DeciContas.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {progress.data?.unmapped_total ? (
            <Link
              href="/cgad/admin/cleanlab-review/unmapped"
              className="rounded-md border px-3 py-1.5 text-sm text-muted-foreground hover:bg-muted"
            >
              Sem documento ({progress.data.unmapped_total})
            </Link>
          ) : null}
          <Button variant="outline" onClick={handleExport}>
            Exportar JSON
          </Button>
        </div>
      </div>

      {progress.data ? (
        <div className="flex flex-wrap items-center gap-3 rounded-md border bg-white p-4">
          <div className="flex flex-col">
            <span className="text-xs uppercase tracking-wide text-muted-foreground">
              Progresso
            </span>
            <span className="text-lg font-semibold">
              {progress.data.decided} / {progress.data.total}
            </span>
          </div>
          <div className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
            <div
              className="h-full bg-emerald-500 transition-all"
              style={{
                width: `${
                  progress.data.total === 0
                    ? 0
                    : (progress.data.decided / progress.data.total) * 100
                }%`,
              }}
            />
          </div>
          <div className="flex gap-3 text-sm">
            <Badge variant="default">A {progress.data.accept}</Badge>
            <Badge variant="secondary">R {progress.data.reject}</Badge>
            <Badge variant="outline">C {progress.data.custom}</Badge>
          </div>
        </div>
      ) : null}

      <ConfidenceFilter />

      <div className="flex items-center gap-2">
        <Checkbox
          id="only-pending"
          checked={onlyPending}
          onCheckedChange={(v) => {
            setOnlyPending(Boolean(v));
            setPage(1);
          }}
        />
        <label htmlFor="only-pending" className="text-sm">
          Mostrar apenas documentos com entidades pendentes
        </label>
        {percentage > 0 ? (
          <span className="ml-3 text-xs text-muted-foreground">
            Filtrando para confiança ≥ {percentage}%
          </span>
        ) : null}
      </div>

      <div className="rounded-md border bg-white">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-24">Doc ID</TableHead>
              <TableHead>Trecho</TableHead>
              <TableHead className="w-32 text-right">Entidades</TableHead>
              <TableHead className="w-40 text-right">Decididas</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {documents.isLoading ? (
              <TableRow>
                <TableCell colSpan={4} className="py-8 text-center text-muted-foreground">
                  Carregando…
                </TableCell>
              </TableRow>
            ) : null}
            {documents.isError ? (
              <TableRow>
                <TableCell
                  colSpan={4}
                  className="py-8 text-center text-rose-700"
                >
                  Erro ao carregar documentos. Reinicie o backend para
                  garantir o código mais recente, ou abra o devtools para
                  ver o erro de schema.
                </TableCell>
              </TableRow>
            ) : null}
            {documents.data?.items.map((d) => {
              const allDone = d.decided_group_count >= d.group_count;
              return (
                <TableRow key={d.document_id}>
                  <TableCell className="font-mono">
                    <Link
                      href={`/cgad/admin/cleanlab-review/documents/${d.document_id}`}
                      className="hover:underline"
                    >
                      {d.document_id}
                    </Link>
                  </TableCell>
                  <TableCell className="max-w-xl truncate">
                    <Link
                      href={`/cgad/admin/cleanlab-review/documents/${d.document_id}`}
                      className="hover:underline"
                    >
                      {d.text_preview}
                    </Link>
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {d.group_count}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {allDone ? (
                      <Badge variant="default">
                        {d.decided_group_count}/{d.group_count}
                      </Badge>
                    ) : (
                      <span className="text-muted-foreground">
                        {d.decided_group_count}/{d.group_count}
                      </span>
                    )}
                  </TableCell>
                </TableRow>
              );
            })}
            {!documents.isLoading && documents.data?.items.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="py-8 text-center text-muted-foreground">
                  Nada por aqui.
                </TableCell>
              </TableRow>
            ) : null}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>
          Página {page} de {totalPages}
          {documents.data ? ` · ${documents.data.total} documentos` : null}
          {progress.data ? ` · ${progress.data.total} entidades no total` : null}
        </span>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
          >
            Anterior
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
          >
            Próxima
          </Button>
        </div>
      </div>
    </main>
  );
}
