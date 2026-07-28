"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { Button, buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAwaitingDispatch, useDecisoes } from "@/hooks/use-reviews";
import { messageForError } from "@/lib/error-messages";
import { formatAcordao, formatProcesso } from "@/lib/format";
import { cn } from "@/lib/utils";
import { AwaitingDispatchItem, DecisaoListItem, TIPO_LABEL, TipoEntidade } from "@/schemas/review";

const PAGE_SIZE = 20;

type Tab = "pendentes" | "awaiting-dispatch";

const BADGE_CLASS: Record<TipoEntidade, string> = {
  multa: "bg-amber-100 text-amber-950",
  obrigacao: "bg-sky-100 text-sky-950",
  ressarcimento: "bg-emerald-100 text-emerald-950",
  recomendacao: "bg-violet-100 text-violet-950",
};

const TIPO_PLURAL: Record<TipoEntidade, string> = {
  multa: "multas",
  obrigacao: "obrigações",
  recomendacao: "recomendações",
  ressarcimento: "ressarcimentos",
};

export default function ReviewsPage() {
  const [tab, setTab] = useState<Tab>("pendentes");
  const [page, setPage] = useState(1);
  const [processoInput, setProcessoInput] = useState("");
  const [processo, setProcesso] = useState("");

  const isAwaiting = tab === "awaiting-dispatch";

  const decisoes = useDecisoes({
    page,
    pageSize: PAGE_SIZE,
    processo,
    enabled: !isAwaiting,
  });
  const awaiting = useAwaitingDispatch({
    page,
    pageSize: PAGE_SIZE,
    enabled: isAwaiting,
  });

  const isLoading = isAwaiting ? awaiting.isLoading : decisoes.isLoading;
  const isError = isAwaiting ? awaiting.isError : decisoes.isError;
  const error = isAwaiting ? awaiting.error : decisoes.error;

  useEffect(() => {
    if (!isError) return;
    toast.error(
      messageForError(
        error,
        isAwaiting
          ? "Erro ao carregar itens aguardando envio."
          : "Erro ao carregar decisões pendentes.",
      ),
    );
  }, [isError, error, isAwaiting]);

  return (
    <main className="mx-auto flex w-full max-w-screen-2xl flex-col gap-4 p-6">
      <div>
        <h1 className="text-2xl font-semibold">
          {isAwaiting ? "Aguardando envio" : "Decisões pendentes"}
        </h1>
        <p className="text-sm text-muted-foreground">
          {isAwaiting
            ? "Entidades aprovadas, ainda não enviadas."
            : "Revise cada decisão: edite, rejeite ou adicione as entidades extraídas do acórdão."}
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
          <TabsTrigger value="pendentes">Pendentes</TabsTrigger>
          <TabsTrigger value="awaiting-dispatch">Aguardando envio</TabsTrigger>
        </TabsList>
      </Tabs>

      {!isAwaiting && (
        <form
          className="flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            setProcesso(processoInput.trim());
            setPage(1);
          }}
        >
          <Input
            value={processoInput}
            onChange={(e) => setProcessoInput(e.target.value)}
            placeholder="Buscar por processo (ex.: 123/2026)"
            className="max-w-xs"
            inputMode="numeric"
          />
          <Button type="submit" variant="outline">
            Buscar
          </Button>
          {processo && (
            <Button
              type="button"
              variant="ghost"
              onClick={() => {
                setProcessoInput("");
                setProcesso("");
                setPage(1);
              }}
            >
              Limpar
            </Button>
          )}
        </form>
      )}

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
        <DecisoesTable
          items={decisoes.data?.items ?? []}
          total={decisoes.data?.total ?? 0}
          page={page}
          pageSize={PAGE_SIZE}
          onPageChange={setPage}
          isLoading={isLoading}
        />
      )}
    </main>
  );
}

function CountBadges({ item }: { item: DecisaoListItem }) {
  const counts: [TipoEntidade, number][] = [
    ["multa", item.multas],
    ["obrigacao", item.obrigacoes],
    ["recomendacao", item.recomendacoes],
    ["ressarcimento", item.ressarcimentos],
  ];
  return (
    <div className="flex flex-wrap gap-1">
      {counts
        .filter(([, n]) => n > 0)
        .map(([tipo, n]) => (
          <span
            key={tipo}
            className={cn("rounded px-1.5 py-0.5 text-xs font-medium", BADGE_CLASS[tipo])}
          >
            {n} {n > 1 ? TIPO_PLURAL[tipo] : TIPO_LABEL[tipo].toLowerCase()}
          </span>
        ))}
    </div>
  );
}

function Pagination({
  page,
  totalPages,
  total,
  onPageChange,
  isLoading,
}: {
  page: number;
  totalPages: number;
  total: number;
  onPageChange: (page: number) => void;
  isLoading: boolean;
}) {
  return (
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
  );
}

function DecisoesTable({
  items,
  total,
  page,
  pageSize,
  onPageChange,
  isLoading,
}: {
  items: DecisaoListItem[];
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
            <TableHead>Acórdão</TableHead>
            <TableHead>Entidades</TableHead>
            <TableHead>Reservado por</TableHead>
            <TableHead>Extraído em</TableHead>
            <TableHead className="w-0" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoading ? (
            <TableRow>
              <TableCell colSpan={6} className="py-10 text-center text-sm text-muted-foreground">
                Carregando...
              </TableCell>
            </TableRow>
          ) : items.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} className="py-10 text-center text-sm text-muted-foreground">
                Nenhuma decisão pendente.
              </TableCell>
            </TableRow>
          ) : (
            items.map((item) => (
              <TableRow key={item.id}>
                <TableCell className="font-mono">
                  {formatProcesso(item.numero_processo, item.ano_processo, item.id_processo)}
                </TableCell>
                <TableCell>
                  {formatAcordao(item.numero_acordao, item.ano_acordao, item.tipo_acordao)}
                </TableCell>
                <TableCell>
                  <CountBadges item={item} />
                </TableCell>
                <TableCell>
                  {item.claimed_by ?? <span className="text-muted-foreground">—</span>}
                </TableCell>
                <TableCell>
                  {item.data_extracao ? (
                    new Date(item.data_extracao).toLocaleDateString("pt-BR")
                  ) : (
                    <span className="text-muted-foreground">—</span>
                  )}
                </TableCell>
                <TableCell>
                  <Link
                    href={`/cgad/reviews/decisao/${item.id}`}
                    className={buttonVariants({ size: "sm" })}
                  >
                    Revisar
                  </Link>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>

      <Pagination
        page={page}
        totalPages={totalPages}
        total={total}
        onPageChange={onPageChange}
        isLoading={isLoading}
      />
    </div>
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
  items: AwaitingDispatchItem[];
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
              <TableRow key={`${item.tipo}-${item.id}`}>
                <TableCell className="font-mono">
                  {formatProcesso(item.numero_processo, item.ano_processo, item.id_processo)}
                </TableCell>
                <TableCell>
                  <span
                    className={cn(
                      "rounded px-1.5 py-0.5 text-xs font-medium",
                      BADGE_CLASS[item.tipo],
                    )}
                  >
                    {TIPO_LABEL[item.tipo]}
                  </span>
                </TableCell>
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

      <Pagination
        page={page}
        totalPages={totalPages}
        total={total}
        onPageChange={onPageChange}
        isLoading={isLoading}
      />
    </div>
  );
}
