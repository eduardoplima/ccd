"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { useFasesResumo } from "@/hooks/use-fases";
import { formatBRL } from "@/lib/format";

import { DebitosNotificadosList, TotaisList } from "./_totais-list";
import { EnviadosList } from "./_enviados-list";

type Aberto = "totais" | "notificados" | "enviados" | null;

export function FasesSummary({ cpfCnpj }: { cpfCnpj: string }) {
  const { data, isFetching } = useFasesResumo(cpfCnpj);
  const [aberto, setAberto] = useState<Aberto>(null);

  if (isFetching && !data) {
    return <p className="text-xs text-muted-foreground">Carregando fases...</p>;
  }
  if (!data) return null;

  return (
    <div className="flex flex-col gap-4">
      <div className="rounded-lg border p-3">
        <div className="mb-3 text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Fases do desconto em folha
        </div>
        <div className="grid grid-cols-1 gap-2 md:grid-cols-3">
          <FaseCard
            titulo="Totais"
            qtd={data.totais.qtd}
            unidade="débitos"
            total={data.totais.total}
            ativo={aberto === "totais"}
            onClick={() => setAberto(aberto === "totais" ? null : "totais")}
          />
          <FaseCard
            titulo="Débitos notificados"
            qtd={data.debitosNotificados.qtd}
            unidade="débitos"
            total={data.debitosNotificados.total}
            ativo={aberto === "notificados"}
            onClick={() => setAberto(aberto === "notificados" ? null : "notificados")}
          />
          <FaseCard
            titulo="Enviados"
            qtd={data.enviados.qtd}
            unidade="notificações"
            total={null}
            ativo={aberto === "enviados"}
            onClick={() => setAberto(aberto === "enviados" ? null : "enviados")}
          />
        </div>

        {aberto === "totais" ? (
          <div className="mt-4">
            <TotaisList cpfCnpj={cpfCnpj} />
          </div>
        ) : null}
        {aberto === "notificados" ? (
          <div className="mt-4">
            <DebitosNotificadosList cpfCnpj={cpfCnpj} />
          </div>
        ) : null}
        {aberto === "enviados" ? (
          <div className="mt-4">
            <EnviadosList cpfCnpj={cpfCnpj} />
          </div>
        ) : null}
      </div>

      <div className="flex flex-wrap items-baseline gap-x-8 gap-y-1 px-1 text-base">
        <span>
          <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Agendados:
          </span>{" "}
          <span className="font-semibold">{data.agendados.qtd.toLocaleString("pt-BR")}</span>{" "}
          <span className="text-sm text-muted-foreground">parcelas</span>
          {data.agendados.total != null ? (
            <span className="ml-2 font-mono text-sm text-muted-foreground">
              {formatBRL(data.agendados.total)}
            </span>
          ) : null}
        </span>
        <span>
          <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Pagos:
          </span>{" "}
          <span className="font-semibold">{data.pagos.qtd.toLocaleString("pt-BR")}</span>{" "}
          <span className="text-sm text-muted-foreground">conciliadas</span>
          {data.pagos.total != null ? (
            <span className="ml-2 font-mono text-sm text-muted-foreground">
              {formatBRL(data.pagos.total)}
            </span>
          ) : null}
        </span>
      </div>
    </div>
  );
}

function FaseCard({
  titulo,
  qtd,
  unidade,
  total,
  ativo,
  onClick,
}: {
  titulo: string;
  qtd: number;
  unidade: string;
  total: number | null;
  ativo?: boolean;
  onClick?: () => void;
}) {
  const clicavel = onClick !== undefined;
  return (
    <Button
      type="button"
      variant={ativo ? "default" : "outline"}
      onClick={onClick}
      disabled={!clicavel}
      className="flex h-auto flex-col items-start gap-1 p-3 text-left whitespace-normal"
    >
      <span className="text-[10px] font-medium uppercase tracking-wide">{titulo}</span>
      <span className="text-lg font-semibold">
        {qtd.toLocaleString("pt-BR")} <span className="text-xs font-normal">{unidade}</span>
      </span>
      {total != null ? (
        <span className="font-mono text-xs opacity-80">{formatBRL(total)}</span>
      ) : null}
    </Button>
  );
}
