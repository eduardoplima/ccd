"use client";

import Link from "next/link";
import { parseAsInteger, parseAsString, useQueryState } from "nuqs";

import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useContracheque } from "@/hooks/use-siai-pessoal";
import { messageForError } from "@/lib/error-messages";
import { formatCpf, formatCurrencyBRL } from "@/lib/format";
import type { FolhaContracheque } from "@/schemas/siai-pessoal";

function competencia(ano: number, mes: number): string {
  return `${String(mes).padStart(2, "0")}/${ano}`;
}

function mesRelativo(ano: number, mes: number, delta: number): { ano: number; mes: number } {
  const idx = ano * 12 + (mes - 1) + delta;
  return { ano: Math.floor(idx / 12), mes: (idx % 12) + 1 };
}

export default function ContrachequePage() {
  const [cpf] = useQueryState("cpf", parseAsString.withDefault(""));
  const [ano] = useQueryState("ano", parseAsInteger.withDefault(new Date().getFullYear()));
  const [mes] = useQueryState("mes", parseAsInteger.withDefault(new Date().getMonth() + 1));
  const [processo] = useQueryState("processo", parseAsString.withDefault(""));
  const [cadastro] = useQueryState("cadastro", parseAsInteger);

  const params = cpf ? { cpf, ano, mes, processo: processo || undefined } : null;
  const { data, isPending, isError, error } = useContracheque(params);

  const linkMes = (delta: number) => {
    const p = mesRelativo(ano, mes, delta);
    const qs = new URLSearchParams({ cpf, ano: String(p.ano), mes: String(p.mes) });
    if (processo) qs.set("processo", processo);
    if (cadastro != null) qs.set("cadastro", String(cadastro));
    return `/ccd/siai-pessoal/contracheque?${qs.toString()}`;
  };

  if (!cpf) {
    return (
      <main className="mx-auto flex w-full max-w-screen-lg flex-col gap-4 p-6">
        <h1 className="text-2xl font-semibold">Contracheque SIAI Pessoal</h1>
        <p className="text-sm text-muted-foreground">Informe o CPF na URL (cpf, ano e mes).</p>
      </main>
    );
  }

  return (
    <main className="mx-auto flex w-full max-w-screen-lg flex-col gap-4 p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">
            Contracheque SIAI Pessoal{" "}
            <span className="ml-2 rounded-md bg-primary px-3 py-1 font-mono text-primary-foreground">
              {competencia(ano, mes)}
            </span>
          </h1>
          <p className="text-sm text-muted-foreground">
            {data?.nome ?? "Servidor"} ({formatCpf(cpf)})
            {processo && (
              <>
                {" "}
                · processo <span className="font-mono">{processo}</span>
              </>
            )}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {cadastro != null && (
            <Link
              href={`/ccd/desconto-folha/${cadastro}`}
              className={buttonVariants({ variant: "outline", size: "sm" })}
            >
              Voltar ao cadastro
            </Link>
          )}
          <Link href={linkMes(-1)} className={buttonVariants({ variant: "outline", size: "sm" })}>
            ← Mês anterior
          </Link>
          <Link href={linkMes(1)} className={buttonVariants({ variant: "outline", size: "sm" })}>
            Mês seguinte →
          </Link>
        </div>
      </div>

      {isPending && <p className="text-sm text-muted-foreground">Carregando…</p>}
      {isError && (
        <p className="text-sm text-destructive">
          {messageForError(error, "Erro ao consultar o SIAI Pessoal.")}
        </p>
      )}
      {data && data.folhas.length === 0 && (
        <p className="text-sm text-muted-foreground">
          Nenhuma folha no SIAI Pessoal para {competencia(ano, mes)}.
        </p>
      )}
      {data?.folhas.map((f) => (
        <FolhaCard key={f.idContracheque} folha={f} />
      ))}
    </main>
  );
}

function FolhaCard({ folha: f }: { folha: FolhaContracheque }) {
  const vantagens = f.itens.filter((i) => i.tipo === "V").reduce((s, i) => s + i.valor, 0);
  const descontos = f.itens.filter((i) => i.tipo === "D").reduce((s, i) => s + i.valor, 0);
  const totalV = f.totalVantagens ?? vantagens;
  const totalD = f.totalDescontos ?? descontos;
  const detalhes = [f.matricula && `matrícula ${f.matricula}`, f.cargo, f.lotacao].filter(Boolean);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex flex-wrap items-center gap-2 text-base">
          {f.orgao ?? (f.idOrgao != null ? `Órgão ${f.idOrgao}` : "Órgão não informado")} ·{" "}
          {f.tipoFolha}
          {f.remessas > 1 && (
            <Badge
              variant="outline"
              title="Folha reenviada em remessas retificadoras; exibida a última"
            >
              {f.remessas} remessas
            </Badge>
          )}
        </CardTitle>
        {detalhes.length > 0 && (
          <p className="text-sm text-muted-foreground">{detalhes.join(" · ")}</p>
        )}
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-24">Código</TableHead>
              <TableHead>Rubrica</TableHead>
              <TableHead className="w-28">Tipo</TableHead>
              <TableHead className="w-36 text-right">Valor</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {f.itens.map((i, idx) => (
              <TableRow key={idx} className={i.tce ? "bg-amber-50" : undefined}>
                <TableCell className="font-mono">{i.codigo ?? "—"}</TableCell>
                <TableCell>
                  {i.descricao}
                  {i.tce && (
                    <Badge variant="warning" className="ml-2">
                      TCE/FRAP
                    </Badge>
                  )}
                </TableCell>
                <TableCell>
                  <Badge variant={i.tipo === "D" ? "destructive" : "success"}>
                    {i.tipo === "D" ? "Desconto" : "Vantagem"}
                  </Badge>
                </TableCell>
                <TableCell className="text-right font-medium">
                  {formatCurrencyBRL(i.valor)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <dl className="flex flex-wrap justify-end gap-x-8 gap-y-1 text-sm">
          <div>
            <dt className="inline text-muted-foreground">Total vantagens: </dt>
            <dd className="inline font-medium">{formatCurrencyBRL(totalV)}</dd>
          </div>
          <div>
            <dt className="inline text-muted-foreground">Total descontos: </dt>
            <dd className="inline font-medium">{formatCurrencyBRL(totalD)}</dd>
          </div>
          <div>
            <dt className="inline text-muted-foreground">Líquido: </dt>
            <dd className="inline font-semibold">{formatCurrencyBRL(totalV - totalD)}</dd>
          </div>
        </dl>
      </CardContent>
    </Card>
  );
}
