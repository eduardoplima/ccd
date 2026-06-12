"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";

import { ReviewList } from "@/components/review/review-list";
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
import { useAwaitingDispatch, useReviews } from "@/hooks/use-reviews";
import { messageForError } from "@/lib/error-messages";
import { formatProcesso } from "@/lib/format";
import { ReviewKind } from "@/schemas/review";

const PAGE_SIZE = 20;

type Tab = ReviewKind | "awaiting-dispatch";

export default function ReviewsPage() {
  const [tab, setTab] = useState<Tab>("obrigacao");
  const [page, setPage] = useState(1);

  const isAwaiting = tab === "awaiting-dispatch";

  const reviews = useReviews({
    kind: isAwaiting ? "obrigacao" : (tab as ReviewKind),
    status: "pending",
    page,
    pageSize: PAGE_SIZE,
    enabled: !isAwaiting,
  });
  const awaiting = useAwaitingDispatch({
    page,
    pageSize: PAGE_SIZE,
    enabled: isAwaiting,
  });

  const isLoading = isAwaiting ? awaiting.isLoading : reviews.isLoading;
  const isError = isAwaiting ? awaiting.isError : reviews.isError;
  const error = isAwaiting ? awaiting.error : reviews.error;

  useEffect(() => {
    if (!isError) return;
    toast.error(
      messageForError(
        error,
        isAwaiting
          ? "Erro ao carregar itens aguardando envio."
          : "Erro ao carregar itens pendentes.",
      ),
    );
  }, [isError, error, isAwaiting]);

  return (
    <main className="mx-auto flex w-full max-w-screen-2xl flex-col gap-4 p-6">
      <div>
        <h1 className="text-2xl font-semibold">
          {isAwaiting ? "Aguardando envio" : "Itens pendentes"}
        </h1>
        <p className="text-sm text-muted-foreground">
          {isAwaiting
            ? "Obrigações e recomendações aprovadas, ainda não enviadas."
            : "Aprove, edite ou rejeite obrigações e recomendações extraídas."}
        </p>
      </div>

      <Tabs
        value={tab}
        onValueChange={(v) => {
          setTab(v as Tab);
          setPage(1);
        }}
      >
        <TabsList>
          <TabsTrigger value="obrigacao">Obrigações</TabsTrigger>
          <TabsTrigger value="recomendacao">Recomendações</TabsTrigger>
          <TabsTrigger value="awaiting-dispatch">Aguardando envio</TabsTrigger>
        </TabsList>
      </Tabs>

      {isAwaiting ? (
        <AwaitingDispatchTable
          items={awaiting.data?.items ?? []}
          total={awaiting.data?.total ?? 0}
          page={page}
          pageSize={PAGE_SIZE}
          onPageChange={setPage}
          isLoading={isLoading}
        />
      ) : (
        <ReviewList
          kind={tab as ReviewKind}
          items={reviews.data?.items ?? []}
          page={page}
          pageSize={PAGE_SIZE}
          total={reviews.data?.total ?? 0}
          onPageChange={setPage}
          isLoading={isLoading}
        />
      )}
    </main>
  );
}

function AwaitingDispatchTable({
  items,
  total,
  page,
  pageSize,
  onPageChange,
  isLoading,
}: {
  items: ReturnType<typeof useAwaitingDispatch>["data"] extends infer D
    ? D extends { items: infer I }
      ? I
      : never
    : never;
  total: number;
  page: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  isLoading: boolean;
}) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="space-y-3">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Processo</TableHead>
            <TableHead>Tipo</TableHead>
            <TableHead>Descrição</TableHead>
            <TableHead>Revisado por</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoading ? (
            <TableRow>
              <TableCell colSpan={4} className="py-10 text-center text-sm text-muted-foreground">
                Carregando...
              </TableCell>
            </TableRow>
          ) : items.length === 0 ? (
            <TableRow>
              <TableCell colSpan={4} className="py-10 text-center text-sm text-muted-foreground">
                Nenhum item aguardando envio.
              </TableCell>
            </TableRow>
          ) : (
            items.map((item) => (
              <TableRow key={`${item.kind}-${item.id}`}>
                <TableCell className="font-mono">
                  {formatProcesso(item.numero_processo, item.ano_processo, item.id_processo)}
                </TableCell>
                <TableCell>{item.kind === "obrigacao" ? "Obrigação" : "Recomendação"}</TableCell>
                <TableCell className="max-w-xl truncate" title={item.descricao}>
                  {item.descricao}
                </TableCell>
                <TableCell>
                  {item.reviewer ?? <span className="text-muted-foreground">—</span>}
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>

      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>
          Página {page} de {totalPages} · {total} itens
        </span>
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1 || isLoading}
          >
            Anterior
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages || isLoading}
          >
            Próxima
          </Button>
        </div>
      </div>
    </div>
  );
}
