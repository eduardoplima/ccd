"use client";

import { ChevronDown, ChevronsUpDown, ChevronUp } from "lucide-react";
import { parseAsInteger, parseAsString, parseAsStringLiteral, useQueryState } from "nuqs";

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
import { useFiltrosCCD, useProcessosCCD } from "@/hooks/use-ccd-processos";
import { marcadorColor } from "@/lib/marcador-color";
import { cn } from "@/lib/utils";
import type { ProcessoCCD } from "@/schemas/ccd";

const SIZE = 100;

// valor-sentinela do dropdown para "processos sem marcador CCD"
const SEM_MARCADOR = "__sem_marcador__";

const COLUMNS = [
  { key: "processo", label: "Processo" },
  { key: "marcador", label: "Marcador" },
  { key: "origem", label: "Origem" },
  { key: "relator", label: "Relator" },
  { key: "tipo", label: "Tipo" },
  { key: "assunto", label: "Assunto" },
] as const;

const SORT_KEYS = COLUMNS.map((c) => c.key);
const ORDERS = ["asc", "desc"] as const;

export default function CcdInicioPage() {
  const [marcador, setMarcador] = useQueryState("marcador", parseAsString.withDefault(""));
  const [relator, setRelator] = useQueryState("relator", parseAsString.withDefault(""));
  const [assunto, setAssunto] = useQueryState("assunto", parseAsString.withDefault(""));
  const [sort, setSort] = useQueryState(
    "sort",
    parseAsStringLiteral(SORT_KEYS).withDefault("processo"),
  );
  const [order, setOrder] = useQueryState("order", parseAsStringLiteral(ORDERS).withDefault("asc"));
  const [page, setPage] = useQueryState("page", parseAsInteger.withDefault(1));

  const { data: filtros } = useFiltrosCCD();
  const semMarcador = marcador === SEM_MARCADOR;
  const { data, isFetching, isError, error } = useProcessosCCD({
    marcador: semMarcador ? undefined : marcador || undefined,
    semMarcador: semMarcador || undefined,
    relator: relator || undefined,
    assunto: assunto || undefined,
    sort,
    order,
    page,
    size: SIZE,
  });

  function toggleSort(key: (typeof SORT_KEYS)[number]) {
    if (sort === key) {
      void setOrder(order === "asc" ? "desc" : "asc");
    } else {
      void setSort(key);
      void setOrder("asc");
    }
    void setPage(1);
  }

  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / SIZE));
  const inicio = total === 0 ? 0 : (page - 1) * SIZE + 1;
  const fim = Math.min(page * SIZE, total);

  function resetFilters() {
    void setMarcador("");
    void setRelator("");
    void setAssunto("");
    void setSort("processo");
    void setOrder("asc");
    void setPage(1);
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="section-heading text-2xl">Início — Processos na CCD</h1>

      <div className="grid gap-3 md:grid-cols-3">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="f-marcador">Marcador</Label>
          <SelectNative
            id="f-marcador"
            value={marcador}
            style={marcador && marcador !== SEM_MARCADOR ? marcadorColor(marcador) : undefined}
            onChange={(e) => {
              void setMarcador(e.target.value);
              void setPage(1);
            }}
          >
            <option value="">Todos</option>
            {filtros ? (
              <option value={SEM_MARCADOR}>Sem marcador ({filtros.sem_marcador})</option>
            ) : null}
            {filtros?.marcadores.map((m) => (
              <option key={m.descricao} value={m.descricao} style={marcadorColor(m.descricao)}>
                {m.descricao} ({m.quantidade})
              </option>
            ))}
          </SelectNative>
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="f-relator">Relator</Label>
          <SelectNative
            id="f-relator"
            value={relator}
            onChange={(e) => {
              void setRelator(e.target.value);
              void setPage(1);
            }}
          >
            <option value="">Todos</option>
            {filtros?.relatores.map((r) => (
              <option key={r.codigo} value={r.codigo}>
                {r.nome}
              </option>
            ))}
          </SelectNative>
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="f-assunto">Assunto</Label>
          <Input
            id="f-assunto"
            placeholder="buscar no assunto"
            value={assunto}
            onChange={(e) => {
              void setAssunto(e.target.value);
              void setPage(1);
            }}
          />
        </div>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {isFetching ? "Carregando..." : `${total.toLocaleString("pt-BR")} processos`}
        </p>
        <Button variant="outline" size="sm" onClick={resetFilters}>
          Limpar filtros
        </Button>
      </div>

      {isError ? (
        <p className="text-sm text-destructive">Erro ao carregar: {(error as Error).message}</p>
      ) : null}

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              {COLUMNS.map((col) => {
                const active = sort === col.key;
                const Icon = !active ? ChevronsUpDown : order === "asc" ? ChevronUp : ChevronDown;
                return (
                  <TableHead key={col.key}>
                    <button
                      type="button"
                      onClick={() => toggleSort(col.key)}
                      className={cn(
                        "-ml-1 inline-flex items-center gap-1 rounded px-1 py-0.5 transition-colors hover:text-foreground",
                        active ? "text-foreground" : "text-muted-foreground",
                      )}
                    >
                      {col.label}
                      <Icon className={cn("size-3.5", active ? "opacity-100" : "opacity-40")} />
                    </button>
                  </TableHead>
                );
              })}
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.items.length === 0 && !isFetching ? (
              <TableRow>
                <TableCell colSpan={6} className="py-8 text-center text-muted-foreground">
                  Nenhum processo encontrado.
                </TableCell>
              </TableRow>
            ) : (
              data?.items.map((row) => <ProcessoRow key={row.processo} row={row} />)
            )}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {total === 0
            ? "—"
            : `${inicio.toLocaleString("pt-BR")}–${fim.toLocaleString("pt-BR")} de ${total.toLocaleString("pt-BR")}`}
        </p>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">
            Página {page} de {totalPages}
          </span>
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
    </div>
  );
}

function ProcessoRow({ row }: { row: ProcessoCCD }) {
  return (
    <TableRow>
      <TableCell className="whitespace-nowrap font-mono text-xs font-medium">
        {row.processo}
      </TableCell>
      <TableCell>
        {row.marcador ? (
          <Badge
            variant="outline"
            className="whitespace-nowrap border"
            style={marcadorColor(row.marcador)}
          >
            {row.marcador}
          </Badge>
        ) : (
          <span className="text-xs text-muted-foreground">—</span>
        )}
      </TableCell>
      <TableCell className="max-w-[200px] truncate" title={row.origem ?? ""}>
        {row.origem ?? "—"}
      </TableCell>
      <TableCell className="whitespace-nowrap">{row.relator ?? "—"}</TableCell>
      <TableCell>{row.tipo ?? "—"}</TableCell>
      <TableCell className="max-w-[280px] truncate" title={row.assunto ?? ""}>
        {row.assunto ?? "—"}
      </TableCell>
    </TableRow>
  );
}
