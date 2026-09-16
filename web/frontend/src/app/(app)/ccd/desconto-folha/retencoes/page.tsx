"use client";

import Link from "next/link";
import { parseAsString, useQueryState } from "nuqs";

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
import { useMapaRetencoes } from "@/hooks/use-desconto-folha";
import { messageForError } from "@/lib/error-messages";
import { formatCpf, formatCurrencyBRL } from "@/lib/format";
import type { MesRetencao } from "@/schemas/desconto-folha";

import { formatData } from "../_shared";

function competencia(m: MesRetencao): string {
  return `${String(m.mes).padStart(2, "0")}/${m.ano}`;
}

export default function MapaRetencoesPage() {
  const [cpf] = useQueryState("cpf", parseAsString.withDefault(""));
  const { data, isPending, isError, error } = useMapaRetencoes(cpf || null);

  return (
    <main className="mx-auto flex w-full max-w-screen-xl flex-col gap-4 p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Mapa de retenções</h1>
          <p className="text-sm text-muted-foreground">
            {data?.nome ?? "Responsável"} ({formatCpf(cpf)}) · rubricas TCE/FRAP no SIAI Pessoal
          </p>
        </div>
        <Link
          href="/ccd/desconto-folha"
          className={buttonVariants({ variant: "outline", size: "sm" })}
        >
          Voltar
        </Link>
      </div>

      {data && (
        <div className="flex flex-wrap gap-x-8 gap-y-2 rounded-lg border px-4 py-3">
          {(
            [
              ["Total retido", formatCurrencyBRL(data.totalRetido)],
              ["Conciliado no FRAP", formatCurrencyBRL(data.totalConciliado)],
              ["Meses com retenção", String(data.meses.length)],
            ] as const
          ).map(([rotulo, valor]) => (
            <div key={rotulo}>
              <div className="text-xs text-muted-foreground">{rotulo}</div>
              <div className="text-lg font-semibold">{valor}</div>
            </div>
          ))}
        </div>
      )}

      {!cpf && <p className="text-sm text-muted-foreground">Informe o CPF na URL (cpf).</p>}
      {cpf && isPending && <p className="text-sm text-muted-foreground">Carregando…</p>}
      {isError && (
        <p className="text-sm text-destructive">
          {messageForError(error, "Erro ao consultar as retenções.")}
        </p>
      )}
      {data && data.meses.length === 0 && (
        <p className="text-sm text-muted-foreground">
          Nenhuma retenção TCE/FRAP no SIAI Pessoal para este CPF.
        </p>
      )}

      {data && data.meses.length > 0 && (
        <div className="rounded-lg border">
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
              {data.meses.flatMap((m) =>
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
                    <TableCell className="text-right font-medium">
                      {formatCurrencyBRL(r.valor)}
                    </TableCell>
                    <TableCell className="text-sm">
                      {idx === 0 ? <ConciliacaoMes m={m} /> : null}
                    </TableCell>
                    <TableCell>
                      {idx === 0 && (
                        <Link
                          href={`/ccd/siai-pessoal/contracheque?${new URLSearchParams({
                            cpf,
                            ano: String(m.ano),
                            mes: String(m.mes),
                          }).toString()}`}
                          className={buttonVariants({ variant: "ghost", size: "sm" })}
                        >
                          Contracheque
                        </Link>
                      )}
                    </TableCell>
                  </TableRow>
                )),
              )}
            </TableBody>
          </Table>
        </div>
      )}
    </main>
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
