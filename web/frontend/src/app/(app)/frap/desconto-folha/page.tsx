"use client";

import { useRouter } from "next/navigation";
import { parseAsInteger, parseAsString, parseAsStringEnum, useQueryState } from "nuqs";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useOrgaos, usePessoas } from "@/hooks/use-desconto-folha";
import type { PessoasSortKey } from "@/lib/api/desconto-folha";
import { formatBRL } from "@/lib/format";

import { TipologiasTab } from "./_tipologias-tab";

const SIZE = 50;

const SORT_KEYS = [
  "nome",
  "cpf",
  "orgao",
  "valor_atualizado",
  "qtd_notificacoes",
  "qtd_debitos_notificados",
  "valor_debitos_notificados",
  "esperado",
] as const satisfies readonly PessoasSortKey[];

const ORIGEM_LABEL: Record<string, string> = {
  P: "Planilha",
  M: "Manual",
  S: "Rubrica",
  C: "Notificação",
};

function formatOrigens(codes: readonly string[]): string {
  if (codes.length === 0) return "—";
  return codes.map((c) => ORIGEM_LABEL[c] ?? c).join(", ");
}

export default function DescontoFolhaPage() {
  const router = useRouter();

  const [tab, setTab] = useQueryState("tab", parseAsString.withDefault("pessoas"));
  const [page, setPage] = useQueryState("page", parseAsInteger.withDefault(1));
  const [q, setQ] = useQueryState("q", parseAsString.withDefault(""));

  function abrirPessoa(cpfCnpj: string) {
    void router.push(`/frap/desconto-folha/${encodeURIComponent(cpfCnpj)}`);
  }

  function abrirOrgao(idOrgao: number) {
    void router.push(`/frap/desconto-folha/orgao/${idOrgao}`);
  }

  const placeholder =
    tab === "orgaos" ? "Buscar órgão..." : "Buscar pessoa, CPF/CNPJ ou órgão...";

  return (
    <div className="flex flex-col gap-6">
      <h1 className="section-heading text-2xl">Desconto em Folha</h1>

      <Tabs value={tab} onValueChange={(v) => void setTab(v)}>
        <TabsList>
          <TabsTrigger value="pessoas">Por pessoa</TabsTrigger>
          <TabsTrigger value="orgaos">Por órgão</TabsTrigger>
          <TabsTrigger value="tipologias">Tipologias</TabsTrigger>
        </TabsList>

        {tab !== "tipologias" ? (
          <div className="pt-4">
            <Input
              value={q}
              onChange={(e) => {
                void setQ(e.target.value);
                void setPage(1);
              }}
              placeholder={placeholder}
              className="max-w-md"
            />
          </div>
        ) : null}

        <TabsContent value="pessoas" className="pt-4">
          <PessoasTab
            q={q || undefined}
            page={page}
            setPage={(p) => void setPage(p)}
            onSelect={abrirPessoa}
          />
        </TabsContent>

        <TabsContent value="orgaos" className="pt-4">
          <OrgaosTab
            q={q || undefined}
            page={page}
            setPage={(p) => void setPage(p)}
            onSelect={abrirOrgao}
          />
        </TabsContent>

        <TabsContent value="tipologias" className="pt-4">
          <TipologiasTab onAbrirPessoa={abrirPessoa} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Tab: Por pessoa
// ---------------------------------------------------------------------------

function PessoasTab({
  q,
  page,
  setPage,
  onSelect,
}: {
  q: string | undefined;
  page: number;
  setPage: (p: number) => void;
  onSelect: (cpf: string) => void;
}) {
  const [sortBy, setSortBy] = useQueryState(
    "sortBy",
    parseAsStringEnum<PessoasSortKey>([...SORT_KEYS]).withDefault("qtd_notificacoes"),
  );
  const [sortDir, setSortDir] = useQueryState(
    "sortDir",
    parseAsStringEnum<"asc" | "desc">(["asc", "desc"]).withDefault("desc"),
  );

  function toggleSort(coluna: PessoasSortKey) {
    if (sortBy !== coluna) {
      void setSortBy(coluna);
      void setSortDir("desc");
      return;
    }
    if (sortDir === "desc") {
      void setSortDir("asc");
      return;
    }
    void setSortBy("qtd_notificacoes");
    void setSortDir("desc");
  }

  const { data, isFetching } = usePessoas({
    q,
    page,
    size: SIZE,
    sortBy: sortBy ?? undefined,
    sortDir,
  });
  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / SIZE));

  return (
    <div className="flex flex-col gap-3">
      <p className="text-xs text-muted-foreground">
        {total.toLocaleString("pt-BR")} pessoas · página {page} de {totalPages}
      </p>
      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <SortableHead
                label="Nome"
                col="nome"
                sortBy={sortBy}
                sortDir={sortDir}
                onClick={toggleSort}
              />
              <SortableHead
                label="CPF/CNPJ"
                col="cpf"
                sortBy={sortBy}
                sortDir={sortDir}
                onClick={toggleSort}
              />
              <SortableHead
                label="Órgão notificado"
                col="orgao"
                sortBy={sortBy}
                sortDir={sortDir}
                onClick={toggleSort}
              />
              <TableHead>Origem Informação</TableHead>
              <TableHead className="text-right">Parcelas Conciliadas</TableHead>
              <SortableHead
                label="Total Multas em Aberto"
                col="valor_atualizado"
                sortBy={sortBy}
                sortDir={sortDir}
                onClick={toggleSort}
                align="right"
              />
              <SortableHead
                label="Total notificações"
                col="qtd_notificacoes"
                sortBy={sortBy}
                sortDir={sortDir}
                onClick={toggleSort}
                align="right"
              />
              <SortableHead
                label="Débitos notificados"
                col="qtd_debitos_notificados"
                sortBy={sortBy}
                sortDir={sortDir}
                onClick={toggleSort}
                align="right"
              />
              <SortableHead
                label="Valor Débitos Notificados"
                col="valor_debitos_notificados"
                sortBy={sortBy}
                sortDir={sortDir}
                onClick={toggleSort}
                align="right"
              />
              <SortableHead
                label="Agendado"
                col="esperado"
                sortBy={sortBy}
                sortDir={sortDir}
                onClick={toggleSort}
                align="right"
              />
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.items.length === 0 && !isFetching ? (
              <TableRow>
                <TableCell colSpan={10} className="py-8 text-center text-muted-foreground">
                  Nenhum registro.
                </TableCell>
              </TableRow>
            ) : (
              data?.items.map((p) => (
                <TableRow
                  key={p.cpfCnpj ?? "?"}
                  className="cursor-pointer hover:bg-muted/40"
                  onClick={() => p.cpfCnpj && onSelect(p.cpfCnpj)}
                >
                  <TableCell>{p.nomePessoa ?? "—"}</TableCell>
                  <TableCell className="font-mono text-xs">{p.cpfCnpj ?? "—"}</TableCell>
                  <TableCell className="text-xs">
                    {p.nomeOrgaoNotificado ?? (
                      <span className="text-muted-foreground italic">sem órgão</span>
                    )}
                  </TableCell>
                  <TableCell className="text-xs">{formatOrigens(p.origens)}</TableCell>
                  <TableCell className="text-right">
                    {p.qtdConciliadas} / {p.qtdParcelas}
                  </TableCell>
                  <TableCell className="text-right">{formatBRL(p.valorAtualizadoTotal)}</TableCell>
                  <TableCell className="text-right">{p.qtdProcessosNotificados}</TableCell>
                  <TableCell className="text-right">{p.qtdDebitosNotificados}</TableCell>
                  <TableCell className="text-right">
                    {formatBRL(p.valorDebitosNotificadosTotal)}
                  </TableCell>
                  <TableCell className="text-right">{formatBRL(p.totalEsperado)}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
      <Paginacao page={page} totalPages={totalPages} setPage={setPage} disabled={isFetching} />
    </div>
  );
}

function SortableHead({
  label,
  col,
  sortBy,
  sortDir,
  onClick,
  align,
}: {
  label: string;
  col: PessoasSortKey;
  sortBy: PessoasSortKey | null;
  sortDir: "asc" | "desc";
  onClick: (c: PessoasSortKey) => void;
  align?: "right";
}) {
  const active = sortBy === col;
  const arrow = active ? (sortDir === "desc" ? "↓" : "↑") : "↕";
  return (
    <TableHead
      onClick={() => onClick(col)}
      className={`cursor-pointer select-none ${align === "right" ? "text-right" : ""}`}
    >
      <span className="inline-flex items-center gap-1">
        {label}
        <span className={active ? "text-foreground" : "text-muted-foreground/40"}>{arrow}</span>
      </span>
    </TableHead>
  );
}

// ---------------------------------------------------------------------------
// Tab: Por órgão
// ---------------------------------------------------------------------------

function OrgaosTab({
  q,
  page,
  setPage,
  onSelect,
}: {
  q: string | undefined;
  page: number;
  setPage: (p: number) => void;
  onSelect: (id: number) => void;
}) {
  const { data, isFetching } = useOrgaos({ q, page, size: SIZE });
  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / SIZE));

  return (
    <div className="flex flex-col gap-3">
      <p className="text-xs text-muted-foreground">
        {total.toLocaleString("pt-BR")} órgãos · página {page} de {totalPages}
      </p>
      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Órgão</TableHead>
              <TableHead className="text-right">Pessoas</TableHead>
              <TableHead className="text-right">Parcelas</TableHead>
              <TableHead className="text-right">Parcelas Conciliadas</TableHead>
              <TableHead className="text-right">Esperado</TableHead>
              <TableHead className="text-right">Quitado</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.items.length === 0 && !isFetching ? (
              <TableRow>
                <TableCell colSpan={6} className="py-8 text-center text-muted-foreground">
                  Nenhum registro.
                </TableCell>
              </TableRow>
            ) : (
              data?.items.map((o) => (
                <TableRow
                  key={o.idOrgao ?? "null"}
                  className="cursor-pointer hover:bg-muted/40"
                  onClick={() => onSelect(o.idOrgao ?? 0)}
                >
                  <TableCell>
                    {o.nomeOrgao ?? (
                      <span className="text-muted-foreground italic">Sem órgão notificado</span>
                    )}
                  </TableCell>
                  <TableCell className="text-right">{o.qtdPessoas}</TableCell>
                  <TableCell className="text-right">{o.qtdParcelas}</TableCell>
                  <TableCell className="text-right">{o.qtdConciliadas}</TableCell>
                  <TableCell className="text-right">{formatBRL(o.totalEsperado)}</TableCell>
                  <TableCell className="text-right">{formatBRL(o.totalQuitado)}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
      <Paginacao page={page} totalPages={totalPages} setPage={setPage} disabled={isFetching} />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Paginação
// ---------------------------------------------------------------------------

function Paginacao({
  page,
  totalPages,
  setPage,
  disabled,
}: {
  page: number;
  totalPages: number;
  setPage: (p: number) => void;
  disabled?: boolean;
}) {
  return (
    <div className="flex items-center justify-end gap-2">
      <Button
        variant="outline"
        size="sm"
        disabled={page <= 1 || disabled}
        onClick={() => setPage(Math.max(1, page - 1))}
      >
        Anterior
      </Button>
      <Button
        variant="outline"
        size="sm"
        disabled={page >= totalPages || disabled}
        onClick={() => setPage(page + 1)}
      >
        Próxima
      </Button>
    </div>
  );
}
