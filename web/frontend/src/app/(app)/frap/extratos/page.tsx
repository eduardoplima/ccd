"use client";

import { parseAsInteger, parseAsString, parseAsStringLiteral, useQueryState } from "nuqs";
import { useState } from "react";

import { LancamentoDetailSheet } from "@/components/app/lancamento-detail-sheet";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { SelectNative } from "@/components/ui/select-native";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useLancamentos } from "@/hooks/use-lancamentos";
import { cn } from "@/lib/utils";
import {
  formatBRDecimal,
  formatBRL,
  formatDate,
  matchStatusVariant,
  parseBRDecimal,
} from "@/lib/format";
import { CATEGORIAS, CONTAS, MATCHER_LABEL, type Lancamento } from "@/schemas/lancamento";

const VALOR_MODOS = ["exato", "faixa"] as const;
type ValorModo = (typeof VALOR_MODOS)[number];

const SIZE = 50;

export default function ExtratosPage() {
  const [conta, setConta] = useQueryState("conta", parseAsString.withDefault(""));
  const [dtInicio, setDtInicio] = useQueryState("dt_inicio", parseAsString.withDefault(""));
  const [dtFim, setDtFim] = useQueryState("dt_fim", parseAsString.withDefault(""));
  const [categoria, setCategoria] = useQueryState("categoria", parseAsString.withDefault(""));
  const [valorDc, setValorDc] = useQueryState("vdc", parseAsString.withDefault(""));
  const [valorModo, setValorModo] = useQueryState<ValorModo>(
    "vmodo",
    parseAsStringLiteral(VALOR_MODOS).withDefault("exato"),
  );
  const [valorExato, setValorExato] = useQueryState("valor", parseAsString.withDefault(""));
  const [valorMin, setValorMin] = useQueryState("valor_min", parseAsString.withDefault(""));
  const [valorMax, setValorMax] = useQueryState("valor_max", parseAsString.withDefault(""));
  const [q, setQ] = useQueryState("q", parseAsString.withDefault(""));
  const [page, setPage] = useQueryState("page", parseAsInteger.withDefault(1));
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const valorMinNum = parseBRDecimal(valorMin);
  const valorMaxNum = parseBRDecimal(valorMax);
  const valorExatoNum = parseBRDecimal(valorExato);

  const valorRangeInvalid =
    valorModo === "faixa" &&
    valorMinNum !== null &&
    valorMaxNum !== null &&
    Number(valorMinNum) > Number(valorMaxNum);

  const apiValorMin =
    valorModo === "exato"
      ? (valorExatoNum ?? undefined)
      : !valorRangeInvalid
        ? (valorMinNum ?? undefined)
        : undefined;
  const apiValorMax =
    valorModo === "exato"
      ? (valorExatoNum ?? undefined)
      : !valorRangeInvalid
        ? (valorMaxNum ?? undefined)
        : undefined;

  const { data, isFetching, isError, error } = useLancamentos({
    conta: conta || undefined,
    dtInicio: dtInicio || undefined,
    dtFim: dtFim || undefined,
    categoria: categoria || undefined,
    valorDc: valorDc === "C" || valorDc === "D" ? valorDc : undefined,
    valorMin: apiValorMin,
    valorMax: apiValorMax,
    q: q || undefined,
    page,
    size: SIZE,
  });

  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / SIZE));

  function resetFilters() {
    void setConta("");
    void setDtInicio("");
    void setDtFim("");
    void setCategoria("");
    void setValorDc("");
    void setValorModo("exato");
    void setValorExato("");
    void setValorMin("");
    void setValorMax("");
    void setQ("");
    void setPage(1);
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="section-heading text-2xl">Extratos</h1>

      <div className="flex flex-col gap-3">
        <div className="grid gap-3 md:grid-cols-3">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="f-conta">Conta</Label>
            <SelectNative
              id="f-conta"
              value={conta}
              onChange={(e) => {
                void setConta(e.target.value);
                void setPage(1);
              }}
            >
              <option value="">Todas</option>
              {CONTAS.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </SelectNative>
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="f-categoria">Categoria</Label>
            <SelectNative
              id="f-categoria"
              value={categoria}
              onChange={(e) => {
                void setCategoria(e.target.value);
                void setPage(1);
              }}
            >
              <option value="">Todas</option>
              {CATEGORIAS.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </SelectNative>
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="f-vdc">C/D</Label>
            <SelectNative
              id="f-vdc"
              value={valorDc}
              onChange={(e) => {
                void setValorDc(e.target.value);
                void setPage(1);
              }}
            >
              <option value="">C/D</option>
              <option value="C">Crédito</option>
              <option value="D">Débito</option>
            </SelectNative>
          </div>
        </div>

        <div className="grid gap-3 md:grid-cols-4">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="f-dt-inicio">Data início</Label>
            <Input
              id="f-dt-inicio"
              type="date"
              value={dtInicio}
              max={dtFim || undefined}
              onChange={(e) => {
                void setDtInicio(e.target.value);
                void setPage(1);
              }}
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="f-dt-fim">Data fim</Label>
            <Input
              id="f-dt-fim"
              type="date"
              value={dtFim}
              min={dtInicio || undefined}
              onChange={(e) => {
                void setDtFim(e.target.value);
                void setPage(1);
              }}
            />
          </div>

          <div className="flex flex-col gap-1.5 md:col-span-2">
            <Label>Valor</Label>
            <div className="flex items-center gap-2">
              {valorModo === "exato" ? (
                <Input
                  id="f-valor"
                  type="text"
                  inputMode="decimal"
                  placeholder="0,00"
                  value={valorExato}
                  onChange={(e) => {
                    void setValorExato(e.target.value);
                    void setPage(1);
                  }}
                  onBlur={(e) => void setValorExato(formatBRDecimal(e.target.value))}
                />
              ) : (
                <div className="grid flex-1 grid-cols-2 gap-2">
                  <Input
                    id="f-valor-min"
                    type="text"
                    inputMode="decimal"
                    placeholder="mín"
                    value={valorMin}
                    aria-invalid={valorRangeInvalid || undefined}
                    onChange={(e) => {
                      void setValorMin(e.target.value);
                      void setPage(1);
                    }}
                    onBlur={(e) => void setValorMin(formatBRDecimal(e.target.value))}
                  />
                  <Input
                    id="f-valor-max"
                    type="text"
                    inputMode="decimal"
                    placeholder="máx"
                    value={valorMax}
                    aria-invalid={valorRangeInvalid || undefined}
                    onChange={(e) => {
                      void setValorMax(e.target.value);
                      void setPage(1);
                    }}
                    onBlur={(e) => void setValorMax(formatBRDecimal(e.target.value))}
                  />
                </div>
              )}
              <div className="inline-flex h-9 shrink-0 rounded-md border bg-muted p-0.5 text-xs">
                {VALOR_MODOS.map((modo) => (
                  <button
                    key={modo}
                    type="button"
                    className={cn(
                      "rounded px-2 capitalize transition-colors",
                      valorModo === modo
                        ? "bg-background text-foreground shadow-sm"
                        : "text-muted-foreground hover:text-foreground",
                    )}
                    onClick={() => {
                      void setValorModo(modo);
                      void setPage(1);
                    }}
                  >
                    {modo}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="f-q">Busca livre</Label>
          <Input
            id="f-q"
            placeholder="histórico, descrição ou documento"
            value={q}
            onChange={(e) => {
              void setQ(e.target.value);
              void setPage(1);
            }}
          />
        </div>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {isFetching ? "Carregando..." : `${total.toLocaleString("pt-BR")} lançamentos`}
        </p>
        <Button variant="outline" size="sm" onClick={resetFilters}>
          Limpar filtros
        </Button>
      </div>

      {valorRangeInvalid ? (
        <p className="text-sm text-destructive">Valor mín. deve ser menor ou igual ao máx.</p>
      ) : null}

      {isError ? (
        <p className="text-sm text-destructive">Erro ao carregar: {(error as Error).message}</p>
      ) : null}

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Data</TableHead>
              <TableHead>Conta</TableHead>
              <TableHead>Histórico</TableHead>
              <TableHead>Documento</TableHead>
              <TableHead>Descrição</TableHead>
              <TableHead className="text-right">Valor</TableHead>
              <TableHead>Categoria</TableHead>
              <TableHead>Matches</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.items.length === 0 && !isFetching ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center text-muted-foreground py-8">
                  Nenhum lançamento encontrado.
                </TableCell>
              </TableRow>
            ) : (
              data?.items.map((row) => (
                <LancamentoRow
                  key={row.idLancamento}
                  row={row}
                  onSelect={() => setSelectedId(row.idLancamento)}
                />
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Página {page} de {totalPages}
        </p>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1 || isFetching}
            onClick={() => setPage(Math.max(1, page - 1))}
          >
            Anterior
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= totalPages || isFetching}
            onClick={() => setPage(page + 1)}
          >
            Próxima
          </Button>
        </div>
      </div>

      <LancamentoDetailSheet
        idLancamento={selectedId}
        onOpenChange={(open) => {
          if (!open) setSelectedId(null);
        }}
      />
    </div>
  );
}

function LancamentoRow({ row, onSelect }: { row: Lancamento; onSelect: () => void }) {
  return (
    <TableRow className="cursor-pointer" onClick={onSelect}>
      <TableCell className="whitespace-nowrap font-mono text-xs">
        {formatDate(row.dtMovimento)}
      </TableCell>
      <TableCell className="font-mono text-xs">{row.conta}</TableCell>
      <TableCell>{row.historico}</TableCell>
      <TableCell className="font-mono text-xs">{row.documento ?? "—"}</TableCell>
      <TableCell className="max-w-[260px] truncate" title={row.descricao ?? ""}>
        {row.descricao ?? "—"}
      </TableCell>
      <TableCell
        className={
          "whitespace-nowrap text-right font-mono " +
          (row.valorDC === "C" ? "text-emerald-700" : "text-destructive")
        }
      >
        {row.valorDC === "D" ? "−" : ""}
        {formatBRL(row.valor)}
      </TableCell>
      <TableCell>
        <Badge variant="outline">{row.categoria}</Badge>
      </TableCell>
      <TableCell>
        <div className="flex flex-wrap gap-1">
          {row.matchesResumo.length === 0 ? (
            <span className="text-xs text-muted-foreground">—</span>
          ) : (
            row.matchesResumo.map((m, i) => (
              <Badge
                key={`${m.matcher}-${i}`}
                variant={matchStatusVariant(m.status)}
                title={`${MATCHER_LABEL[m.matcher]}: ${m.status}${m.quantidade > 1 ? ` (×${m.quantidade})` : ""}`}
              >
                {MATCHER_LABEL[m.matcher]}
              </Badge>
            ))
          )}
        </div>
      </TableCell>
    </TableRow>
  );
}
