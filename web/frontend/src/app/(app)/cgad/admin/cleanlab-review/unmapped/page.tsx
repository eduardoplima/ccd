"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useMemo, useState } from "react";

import { ConfidenceFilter } from "@/components/dataset-corrections/confidence-filter";
import { UnmappedDecisionBar } from "@/components/dataset-corrections/decision-bar";
import { FallbackWindow } from "@/components/dataset-corrections/fallback-window";
import { Button } from "@/components/ui/button";
import { useUnmapped } from "@/hooks/use-dataset-corrections";
import { useMinConfidence } from "@/hooks/use-min-confidence";

const PAGE_SIZE = 25;

export default function UnmappedPage() {
  const [page, setPage] = useState(1);
  const [selectedRowId, setSelectedRowId] = useState<number | null>(null);
  const { fraction: minConfidence, percentage } = useMinConfidence();
  const data = useUnmapped({ page, pageSize: PAGE_SIZE, minConfidence });
  const searchParams = useSearchParams();
  const backToListHref = useMemo(() => {
    const sp = new URLSearchParams(searchParams.toString());
    const qs = sp.toString();
    return qs ? `/cgad/admin/cleanlab-review?${qs}` : "/cgad/admin/cleanlab-review";
  }, [searchParams]);

  const items = data.data?.items ?? [];
  const selected = items.find((e) => e.row_id === selectedRowId) ?? items[0] ?? null;
  const selectedIndex = selected
    ? items.findIndex((e) => e.row_id === selected.row_id)
    : -1;

  function moveNext() {
    if (items.length === 0) return;
    const next = items[(selectedIndex + 1) % items.length];
    setSelectedRowId(next.row_id);
  }
  function movePrev() {
    if (items.length === 0) return;
    const prev = items[(selectedIndex - 1 + items.length) % items.length];
    setSelectedRowId(prev.row_id);
  }

  const totalPages = data.data
    ? Math.max(1, Math.ceil(data.data.total / PAGE_SIZE))
    : 1;

  return (
    <main className="mx-auto flex w-full max-w-screen-2xl flex-col gap-4 p-6">
      <div>
        <Link
          href={backToListHref}
          className="text-xs text-muted-foreground hover:underline"
        >
          ← Voltar
        </Link>
        <h1 className="mt-1 text-xl font-semibold">Erros sem documento</h1>
        <p className="text-sm text-muted-foreground">
          Tokens flagrados cuja sentença não foi localizada em um documento do
          dataset. Use o contexto do cleanlab para decidir.
          {percentage > 0 ? ` · filtrando confiança ≥ ${percentage}%` : null}
        </p>
      </div>

      <ConfidenceFilter />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
        <div className="flex flex-col gap-3">
          {data.isLoading ? (
            <div className="text-sm text-muted-foreground">Carregando…</div>
          ) : null}
          {!data.isLoading && items.length === 0 ? (
            <div className="rounded-md border bg-white p-6 text-sm text-muted-foreground">
              Tudo certo: nenhum erro sem documento.
            </div>
          ) : null}
          {items.map((e) => {
            const isSel = e.row_id === selected?.row_id;
            return (
              <button
                key={e.row_id}
                type="button"
                onClick={() => setSelectedRowId(e.row_id)}
                className={`text-left transition-shadow ${
                  isSel ? "ring-2 ring-blue-500" : "hover:ring-1 hover:ring-muted"
                } rounded-md`}
              >
                <FallbackWindow error={e} />
              </button>
            );
          })}
        </div>
        <div>
          <UnmappedDecisionBar
            error={selected ?? null}
            onMoveNext={moveNext}
            onMovePrev={movePrev}
          />
        </div>
      </div>

      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>
          Página {page} de {totalPages}
          {data.data ? ` · ${data.data.total} erros` : null}
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
