"use client";

import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatCurrencyBRL } from "@/lib/format";
import type { MesRetencao } from "@/schemas/desconto-folha";

import { formatData } from "./_shared";

function competencia(m: MesRetencao): string {
  return `${String(m.mes).padStart(2, "0")}/${m.ano}`;
}

export function RetencoesTabela({
  cpf,
  meses,
  processo,
  cadastro,
}: {
  cpf: string;
  meses: MesRetencao[];
  processo?: string;
  cadastro?: number;
}) {
  const linkContracheque = (m: MesRetencao) => {
    const qs = new URLSearchParams({ cpf, ano: String(m.ano), mes: String(m.mes) });
    if (processo) qs.set("processo", processo);
    if (cadastro != null) qs.set("cadastro", String(cadastro));
    return `/ccd/siai-pessoal/contracheque?${qs.toString()}`;
  };

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-28">Competência</TableHead>
          <TableHead>Órgão</TableHead>
          <TableHead>Rubrica</TableHead>
          <TableHead className="text-right">Valor retido</TableHead>
          <TableHead>Conciliação FRAP</TableHead>
          <TableHead className="w-0" />
        </TableRow>
      </TableHeader>
      <TableBody>
        {meses.flatMap((m) =>
          m.retencoes.map((r, idx) => (
            <TableRow key={`${m.ano}-${m.mes}-${idx}`}>
              <TableCell className={idx === 0 ? "font-semibold" : "text-muted-foreground"}>
                {competencia(m)}
              </TableCell>
              <TableCell className="max-w-[260px] truncate" title={r.orgao ?? undefined}>
                {r.orgao ?? "—"}
              </TableCell>
              <TableCell>
                {r.codigo && <span className="mr-1 font-mono text-xs">{r.codigo}</span>}
                {r.rubrica}
              </TableCell>
              <TableCell className="text-right font-medium">{formatCurrencyBRL(r.valor)}</TableCell>
              <TableCell className="text-sm">
                {idx === 0 ? <ConciliacaoMes m={m} /> : null}
              </TableCell>
              <TableCell>
                {idx === 0 && (
                  <Link
                    href={linkContracheque(m)}
                    className={buttonVariants({ variant: "ghost", size: "sm" })}
                  >
                    Contracheque
                  </Link>
                )}
              </TableCell>
            </TableRow>
          )),
        )}
        <TableRow className="bg-muted/40 font-semibold">
          <TableCell colSpan={3}>Total</TableCell>
          <TableCell className="text-right">
            {formatCurrencyBRL(meses.reduce((s, m) => s + m.totalRetido, 0))}
          </TableCell>
          <TableCell colSpan={2} />
        </TableRow>
      </TableBody>
    </Table>
  );
}

function ConciliacaoMes({ m }: { m: MesRetencao }) {
  if (m.parcelas.length === 0) {
    return <Badge variant="outline">sem parcela no mês</Badge>;
  }
  return (
    <div className="flex flex-col gap-1">
      <div className="flex flex-wrap items-center gap-2">
        {m.conciliado ? (
          <Badge variant="success">conciliado · {formatCurrencyBRL(m.totalConciliado)}</Badge>
        ) : (
          <Badge variant="warning">parcela sem crédito</Badge>
        )}
        {m.totalConciliado > m.totalRetido + 0.01 && (
          <Badge
            variant="warning"
            title="Créditos vinculados somam mais que a retenção do mês no SIAI: conferir a conciliação"
          >
            acima do retido
          </Badge>
        )}
      </div>
      <ul className="space-y-0.5 text-xs">
        {m.parcelas.map((p) => (
          <li key={`${p.idCadastro}-${p.numeroParcela}`}>
            <Link
              href={`/ccd/desconto-folha/${p.idCadastro}`}
              className="font-mono text-primary underline-offset-2 hover:underline"
            >
              {p.processo}
            </Link>{" "}
            · parcela {p.numeroParcela} · {formatCurrencyBRL(p.valor)}
            {p.lancamento
              ? ` · crédito ${formatData(p.lancamento.dtMovimento)} ${formatCurrencyBRL(p.lancamento.valor)}`
              : " · sem crédito vinculado"}
            {p.creditoCompartilhado && (
              <Badge variant="warning" className="ml-1">
                mesma OB em outro processo
              </Badge>
            )}
            {p.competenciaInferida && (
              <span
                className="ml-1 text-muted-foreground"
                title="Parcela sem mês na resposta; mês anterior ao crédito"
              >
                (mês pelo crédito)
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
