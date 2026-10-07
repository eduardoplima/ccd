"use client";

import Link from "next/link";
import { parseAsString, useQueryState } from "nuqs";

import { buttonVariants } from "@/components/ui/button";
import { useMapaRetencoes } from "@/hooks/use-desconto-folha";
import { messageForError } from "@/lib/error-messages";
import { formatCpf, formatCurrencyBRL } from "@/lib/format";

import { RetencoesTabela } from "../_retencoes-tabela";

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
          <RetencoesTabela cpf={cpf} meses={data.meses} />
        </div>
      )}
    </main>
  );
}
