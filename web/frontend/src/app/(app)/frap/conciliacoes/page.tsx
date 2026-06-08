"use client";

import { parseAsInteger, parseAsString, useQueryState } from "nuqs";

import { Badge } from "@/components/ui/badge";
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
import {
  useMatchesDescontoFolha,
  useMatchesGuia,
  useMatchesOB,
  useMatchesPessoa,
} from "@/hooks/use-matches";
import type { MatchesFilters } from "@/lib/api/matches";
import { formatBRL, formatDate, matchStatusVariant } from "@/lib/format";

const SIZE = 50;

function placeholderPorTab(tab: string): string {
  if (tab === "ob") return "Buscar credor ou NU OB...";
  return "Buscar pessoa ou CPF...";
}

export default function ConciliacoesPage() {
  const [tab, setTab] = useQueryState("tab", parseAsString.withDefault("guia"));
  const [q, setQ] = useQueryState("q", parseAsString.withDefault(""));
  const [page, setPage] = useQueryState("page", parseAsInteger.withDefault(1));

  const filters: MatchesFilters = {
    q: q || undefined,
    page,
    size: SIZE,
  };

  return (
    <div className="flex flex-col gap-6">
      <h1 className="section-heading text-2xl">Conciliações</h1>
      <p className="text-sm text-muted-foreground -mt-3">
        Lista apenas matches bem-sucedidos por matcher.
      </p>

      <Input
        value={q}
        onChange={(e) => {
          void setQ(e.target.value);
          void setPage(1);
        }}
        placeholder={placeholderPorTab(tab)}
        className="max-w-md"
      />

      <Tabs
        value={tab}
        onValueChange={(v) => {
          void setTab(v);
          void setPage(1);
        }}
      >
        <TabsList>
          <TabsTrigger value="guia">Guia</TabsTrigger>
          <TabsTrigger value="pessoa">Pessoa</TabsTrigger>
          <TabsTrigger value="ob">OB (SIGEF)</TabsTrigger>
          <TabsTrigger value="desconto">Desconto-Folha</TabsTrigger>
        </TabsList>

        <TabsContent value="guia">
          <GuiaTable filters={filters} page={page} setPage={setPage} />
        </TabsContent>
        <TabsContent value="pessoa">
          <PessoaTable filters={filters} page={page} setPage={setPage} />
        </TabsContent>
        <TabsContent value="ob">
          <ObTable filters={filters} page={page} setPage={setPage} />
        </TabsContent>
        <TabsContent value="desconto">
          <DescontoFolhaTable filters={filters} page={page} setPage={setPage} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

interface PageProps {
  filters: MatchesFilters;
  page: number;
  setPage: (n: number) => Promise<URLSearchParams>;
}

function PaginationFooter({
  total,
  page,
  setPage,
  isFetching,
}: {
  total: number;
  page: number;
  setPage: PageProps["setPage"];
  isFetching: boolean;
}) {
  const totalPages = Math.max(1, Math.ceil(total / SIZE));
  return (
    <div className="mt-4 flex items-center justify-between">
      <p className="text-sm text-muted-foreground">
        {total.toLocaleString("pt-BR")} resultados — página {page} de {totalPages}
      </p>
      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          disabled={page <= 1 || isFetching}
          onClick={() => void setPage(Math.max(1, page - 1))}
        >
          Anterior
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={page >= totalPages || isFetching}
          onClick={() => void setPage(page + 1)}
        >
          Próxima
        </Button>
      </div>
    </div>
  );
}

function ObTable({ filters, page, setPage }: PageProps) {
  const { data, isFetching } = useMatchesOB(filters);
  return (
    <div className="rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Status</TableHead>
            <TableHead>Conta</TableHead>
            <TableHead>Data extrato</TableHead>
            <TableHead className="text-right">Valor extrato</TableHead>
            <TableHead>NU OB</TableHead>
            <TableHead>Data pgto</TableHead>
            <TableHead className="text-right">Valor OB</TableHead>
            <TableHead>Credor</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data?.items.length === 0 && !isFetching ? (
            <TableRow>
              <TableCell colSpan={8} className="py-8 text-center text-muted-foreground">
                Nenhum match.
              </TableCell>
            </TableRow>
          ) : (
            data?.items.map((m) => (
              <TableRow key={m.idMatch}>
                <TableCell>
                  <Badge variant={matchStatusVariant(m.status)}>{m.status}</Badge>
                </TableCell>
                <TableCell className="font-mono text-xs">{m.conta}</TableCell>
                <TableCell className="font-mono text-xs">{formatDate(m.dtMovimento)}</TableCell>
                <TableCell className="text-right font-mono text-xs">
                  {m.valorLancamento != null ? formatBRL(m.valorLancamento) : "—"}
                </TableCell>
                <TableCell className="font-mono text-xs">{m.nuOrdemBancaria ?? "—"}</TableCell>
                <TableCell className="font-mono text-xs">{formatDate(m.dataPagamento)}</TableCell>
                <TableCell className="text-right font-mono text-xs">
                  {m.valorOB != null ? formatBRL(m.valorOB) : "—"}
                </TableCell>
                <TableCell className="max-w-[220px] truncate" title={m.nmCredor ?? ""}>
                  {m.nmCredor ?? "—"}
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
      <div className="px-3 py-2">
        <PaginationFooter
          total={data?.total ?? 0}
          page={page}
          setPage={setPage}
          isFetching={isFetching}
        />
      </div>
    </div>
  );
}

function PessoaTable({ filters, page, setPage }: PageProps) {
  const { data, isFetching } = useMatchesPessoa(filters);
  return (
    <div className="rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Status</TableHead>
            <TableHead>Conta</TableHead>
            <TableHead>Data</TableHead>
            <TableHead>CPF/CNPJ</TableHead>
            <TableHead>Nome</TableHead>
            <TableHead className="text-right">Valor extrato</TableHead>
            <TableHead className="text-right">Pago</TableHead>
            <TableHead>Casou em</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data?.items.length === 0 && !isFetching ? (
            <TableRow>
              <TableCell colSpan={8} className="py-8 text-center text-muted-foreground">
                Nenhum match.
              </TableCell>
            </TableRow>
          ) : (
            data?.items.map((m) => (
              <TableRow key={m.idMatch}>
                <TableCell>
                  <Badge variant={matchStatusVariant(m.status)}>{m.status}</Badge>
                </TableCell>
                <TableCell className="font-mono text-xs">{m.conta}</TableCell>
                <TableCell className="font-mono text-xs">{formatDate(m.dtMovimento)}</TableCell>
                <TableCell className="font-mono text-xs">{m.cpfcnpj ?? "—"}</TableCell>
                <TableCell className="max-w-[220px] truncate" title={m.nomePessoa ?? ""}>
                  {m.nomePessoa ?? "—"}
                </TableCell>
                <TableCell className="text-right font-mono text-xs">
                  {m.valorLancamento != null ? formatBRL(m.valorLancamento) : "—"}
                </TableCell>
                <TableCell className="text-right font-mono text-xs">
                  {m.valorPago != null ? formatBRL(m.valorPago) : "—"}
                </TableCell>
                <TableCell className="text-xs">{m.valorCasadoEm ?? "—"}</TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
      <div className="px-3 py-2">
        <PaginationFooter
          total={data?.total ?? 0}
          page={page}
          setPage={setPage}
          isFetching={isFetching}
        />
      </div>
    </div>
  );
}

function GuiaTable({ filters, page, setPage }: PageProps) {
  const { data, isFetching } = useMatchesGuia(filters);
  return (
    <div className="rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Status</TableHead>
            <TableHead>Conta</TableHead>
            <TableHead>Data extrato</TableHead>
            <TableHead className="text-right">Valor extrato</TableHead>
            <TableHead>Cód. barras</TableHead>
            <TableHead>Data pgto</TableHead>
            <TableHead className="text-right">Valor pago</TableHead>
            <TableHead>Pessoa</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data?.items.length === 0 && !isFetching ? (
            <TableRow>
              <TableCell colSpan={8} className="py-8 text-center text-muted-foreground">
                Nenhum match.
              </TableCell>
            </TableRow>
          ) : (
            data?.items.map((m) => (
              <TableRow key={m.idMatch}>
                <TableCell>
                  <Badge variant={matchStatusVariant(m.status)}>{m.status}</Badge>
                </TableCell>
                <TableCell className="font-mono text-xs">{m.conta}</TableCell>
                <TableCell className="font-mono text-xs">{formatDate(m.dtMovimento)}</TableCell>
                <TableCell className="text-right font-mono text-xs">
                  {m.valorLancamento != null ? formatBRL(m.valorLancamento) : "—"}
                </TableCell>
                <TableCell className="max-w-[180px] truncate font-mono text-xs">
                  {m.codigoBarras ?? "—"}
                </TableCell>
                <TableCell className="font-mono text-xs">{formatDate(m.dataPagamento)}</TableCell>
                <TableCell className="text-right font-mono text-xs">
                  {m.valorPago != null ? formatBRL(m.valorPago) : "—"}
                </TableCell>
                <TableCell className="max-w-[180px] truncate" title={m.nomePessoa ?? ""}>
                  {m.nomePessoa ?? "—"}
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
      <div className="px-3 py-2">
        <PaginationFooter
          total={data?.total ?? 0}
          page={page}
          setPage={setPage}
          isFetching={isFetching}
        />
      </div>
    </div>
  );
}

function DescontoFolhaTable({ filters, page, setPage }: PageProps) {
  const { data, isFetching } = useMatchesDescontoFolha(filters);
  return (
    <div className="rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Status</TableHead>
            <TableHead>Parcela</TableHead>
            <TableHead>Mês/Ano ref.</TableHead>
            <TableHead>CPF</TableHead>
            <TableHead>Pessoa</TableHead>
            <TableHead className="text-right">Esperado</TableHead>
            <TableHead className="text-right">Contracheque</TableHead>
            <TableHead className="text-right">Crédito FRAP</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data?.items.length === 0 && !isFetching ? (
            <TableRow>
              <TableCell colSpan={8} className="py-8 text-center text-muted-foreground">
                Nenhum match.
              </TableCell>
            </TableRow>
          ) : (
            data?.items.map((m) => (
              <TableRow key={m.idMatch}>
                <TableCell>
                  <Badge variant={matchStatusVariant(m.status)}>{m.status}</Badge>
                </TableCell>
                <TableCell className="font-mono text-xs">{m.numeroParcela ?? "—"}</TableCell>
                <TableCell className="font-mono text-xs">
                  {m.mesReferencia != null && m.anoReferencia != null
                    ? `${String(m.mesReferencia).padStart(2, "0")}/${m.anoReferencia}`
                    : "—"}
                </TableCell>
                <TableCell className="font-mono text-xs">{m.cpfcnpj ?? "—"}</TableCell>
                <TableCell className="max-w-[200px] truncate" title={m.nomePessoa ?? ""}>
                  {m.nomePessoa ?? "—"}
                </TableCell>
                <TableCell className="text-right font-mono text-xs">
                  {m.valorEsperado != null ? formatBRL(m.valorEsperado) : "—"}
                </TableCell>
                <TableCell className="text-right font-mono text-xs">
                  {m.valorContracheque != null ? formatBRL(m.valorContracheque) : "—"}
                </TableCell>
                <TableCell className="text-right font-mono text-xs">
                  {m.valorLancamento != null ? formatBRL(m.valorLancamento) : "—"}
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
      <div className="px-3 py-2">
        <PaginationFooter
          total={data?.total ?? 0}
          page={page}
          setPage={setPage}
          isFetching={isFetching}
        />
      </div>
    </div>
  );
}
