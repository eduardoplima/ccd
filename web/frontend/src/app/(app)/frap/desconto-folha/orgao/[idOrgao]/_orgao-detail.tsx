"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Fragment, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  useDepositosOrgao,
  useDepositosOrgaoLancamentos,
  useParcelasPessoa,
  usePessoasDoOrgao,
} from "@/hooks/use-desconto-folha";
import { formatBRL, formatDate } from "@/lib/format";

import { ParcelasTable } from "../../[cpfcnpj]/_pessoa-detail";

export function OrgaoDetail({ idOrgao }: { idOrgao: number }) {
  const router = useRouter();
  const { data: pessoas, isFetching: loadingPessoas } = usePessoasDoOrgao(idOrgao);
  const { data: depositos } = useDepositosOrgao(idOrgao > 0 ? idOrgao : null);
  const [expandedCpfCnpj, setExpandedCpfCnpj] = useState<string | null>(null);

  const nomeOrgao =
    pessoas?.nomeOrgao ?? (idOrgao <= 0 ? "Sem órgão notificado" : `Órgão #${idOrgao}`);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          ← Voltar
        </Button>
        <div>
          <h1 className="section-heading text-2xl">{nomeOrgao}</h1>
          {depositos?.cnpj ? (
            <p className="font-mono text-xs text-muted-foreground">CNPJ {depositos.cnpj}</p>
          ) : null}
        </div>
      </div>

      <DepositosCard idOrgao={idOrgao} />

      <div className="flex flex-col gap-3">
        <h2 className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
          Pessoas associadas{" "}
          {pessoas ? (
            <span className="font-normal normal-case">
              ({pessoas.pessoas.length.toLocaleString("pt-BR")})
            </span>
          ) : null}
        </h2>
        <div className="rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>CPF/CNPJ</TableHead>
                <TableHead className="text-right">Parcelas</TableHead>
                <TableHead className="text-right">Conciliadas</TableHead>
                <TableHead className="text-right">Esperado</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loadingPessoas && !pessoas ? (
                <TableRow>
                  <TableCell colSpan={5} className="py-8 text-center text-muted-foreground">
                    Carregando...
                  </TableCell>
                </TableRow>
              ) : !pessoas || pessoas.pessoas.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="py-8 text-center text-muted-foreground">
                    Nenhuma pessoa associada.
                  </TableCell>
                </TableRow>
              ) : (
                pessoas.pessoas.map((p) => {
                  const isExpanded = !!p.cpfCnpj && expandedCpfCnpj === p.cpfCnpj;
                  return (
                    <Fragment key={p.cpfCnpj ?? "?"}>
                      <TableRow
                        className={
                          (p.cpfCnpj ? "cursor-pointer hover:bg-muted/40 " : "") +
                          (isExpanded ? "bg-muted/30 " : "")
                        }
                        onClick={() => {
                          if (!p.cpfCnpj) return;
                          setExpandedCpfCnpj(isExpanded ? null : p.cpfCnpj);
                        }}
                      >
                        <TableCell>{p.nomePessoa ?? "—"}</TableCell>
                        <TableCell className="font-mono text-xs">{p.cpfCnpj ?? "—"}</TableCell>
                        <TableCell className="text-right">{p.qtdParcelas}</TableCell>
                        <TableCell className="text-right">{p.qtdConciliadas}</TableCell>
                        <TableCell className="text-right">{formatBRL(p.totalEsperado)}</TableCell>
                      </TableRow>
                      {isExpanded && p.cpfCnpj ? (
                        <TableRow className="bg-muted/20 hover:bg-muted/20">
                          <TableCell colSpan={5} className="p-0">
                            <ParcelasInline cpfCnpj={p.cpfCnpj} />
                          </TableCell>
                        </TableRow>
                      ) : null}
                    </Fragment>
                  );
                })
              )}
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  );
}

function ParcelasInline({ cpfCnpj }: { cpfCnpj: string }) {
  const { data, isFetching } = useParcelasPessoa(cpfCnpj);
  return (
    <div className="border-l-4 border-[var(--brand-accent)] bg-background/60 p-4">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h4 className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Parcelas {data?.nomePessoa ? `· ${data.nomePessoa}` : ""}
        </h4>
        <Link
          href={`/frap/desconto-folha/${encodeURIComponent(cpfCnpj)}`}
          className="text-xs text-yellow-700 hover:underline"
          onClick={(e) => e.stopPropagation()}
        >
          Abrir página da pessoa →
        </Link>
      </div>
      {isFetching && !data ? (
        <p className="text-xs text-muted-foreground">Carregando...</p>
      ) : !data || data.parcelas.length === 0 ? (
        <p className="text-xs text-muted-foreground">Nenhuma parcela.</p>
      ) : (
        <ParcelasTable
          parcelas={data.parcelas}
          isAdmin={false}
          selecionadas={new Set()}
          onToggle={() => {}}
        />
      )}
    </div>
  );
}

function DepositosCard({ idOrgao }: { idOrgao: number }) {
  const [expanded, setExpanded] = useState(false);
  const { data: depositos, isFetching: loadingDepositos } = useDepositosOrgao(
    idOrgao > 0 ? idOrgao : null,
  );
  const podeExpandir = idOrgao > 0 && !!depositos?.cnpj && (depositos?.qtd ?? 0) > 0;
  const { data: lancs, isFetching: loadingLancs } = useDepositosOrgaoLancamentos(
    expanded && podeExpandir ? idOrgao : null,
  );

  return (
    <Card
      className={podeExpandir ? "cursor-pointer transition-colors hover:bg-muted/30" : undefined}
      onClick={() => {
        if (podeExpandir) setExpanded((v) => !v);
      }}
      aria-expanded={podeExpandir ? expanded : undefined}
    >
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center justify-between gap-3 text-sm font-medium uppercase tracking-wide text-muted-foreground">
          <span>
            Depósitos em contas FRAP
            {depositos?.isEstadual ? (
              <span className="ml-2 normal-case text-muted-foreground/70">
                (Depósitos do Estado)
              </span>
            ) : null}
          </span>
          {podeExpandir ? (
            <span className="text-xs normal-case text-muted-foreground/80">
              {expanded ? "▲ ocultar lançamentos" : "▼ ver lançamentos"}
            </span>
          ) : null}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {idOrgao <= 0 ? (
          <p className="text-sm text-muted-foreground">Não aplicável a “sem órgão notificado”.</p>
        ) : loadingDepositos && !depositos ? (
          <p className="text-sm text-muted-foreground">Carregando...</p>
        ) : depositos && depositos.cnpj ? (
          <div className="flex flex-wrap items-baseline gap-x-8 gap-y-1">
            <span className="font-mono text-2xl font-semibold">{formatBRL(depositos.total)}</span>
            <span className="text-sm text-muted-foreground">
              {depositos.qtd.toLocaleString("pt-BR")} lançamento{depositos.qtd === 1 ? "" : "s"} de
              crédito
            </span>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">
            CNPJ do órgão não encontrado em <code>Bdc.dbo.vw_Gen_Orgao</code> — não é possível
            calcular depósitos por CNPJ.
          </p>
        )}

        {expanded && podeExpandir ? (
          <div
            className="mt-4 rounded-lg border bg-background/60"
            onClick={(e) => e.stopPropagation()}
          >
            {loadingLancs && !lancs ? (
              <p className="p-4 text-sm text-muted-foreground">Carregando lançamentos...</p>
            ) : !lancs || lancs.items.length === 0 ? (
              <p className="p-4 text-sm text-muted-foreground">Nenhum lançamento encontrado.</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Data</TableHead>
                    <TableHead>Conta</TableHead>
                    <TableHead>Histórico</TableHead>
                    <TableHead>Documento</TableHead>
                    <TableHead>Descrição</TableHead>
                    <TableHead>Origem</TableHead>
                    <TableHead className="text-right">Valor</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {lancs.items.map((l) => (
                    <TableRow key={l.idLancamento}>
                      <TableCell className="whitespace-nowrap font-mono text-xs">
                        {formatDate(l.dtMovimento ?? null)}
                      </TableCell>
                      <TableCell className="font-mono text-xs">{l.conta}</TableCell>
                      <TableCell>{l.historico}</TableCell>
                      <TableCell className="font-mono text-xs">{l.documento ?? "—"}</TableCell>
                      <TableCell className="max-w-[260px] truncate" title={l.descricao ?? ""}>
                        {l.descricao ?? "—"}
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {l.viaCnpj ? <Badge variant="outline">CNPJ</Badge> : null}
                          {l.viaInferencia ? <Badge variant="outline">Inferência</Badge> : null}
                        </div>
                      </TableCell>
                      <TableCell className="whitespace-nowrap text-right font-mono text-emerald-700">
                        {formatBRL(l.valor)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
