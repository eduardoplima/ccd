"use client";

import { parseAsString, parseAsStringEnum, useQueryState } from "nuqs";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useCurrentUser } from "@/hooks/use-current-user";
import {
  useBeneficiosResumo,
  useDispararDeteccaoBeneficios,
  useExportarBeneficios,
} from "@/hooks/use-beneficios";
import { formatBRL } from "@/lib/format";
import { podeEditar } from "@/lib/permissoes";
import { ORIGENS_BENEFICIO, type BeneficioItem, type OrigemBeneficio } from "@/schemas/beneficios";

import { BeneficioDetalhe } from "./_beneficio-detalhe";
import { BeneficiosLista } from "./_beneficios-lista";
import { SerieTemporal } from "./_serie-temporal";

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border p-3">
      <div className="text-muted-foreground text-xs">{label}</div>
      <div className="text-lg font-semibold">{value}</div>
    </div>
  );
}

export default function BeneficiosPage() {
  const [de, setDe] = useQueryState("de", parseAsString.withDefault(""));
  const [ate, setAte] = useQueryState("ate", parseAsString.withDefault(""));
  const [q, setQ] = useQueryState("q", parseAsString.withDefault(""));
  const [origem, setOrigem] = useQueryState(
    "origem",
    parseAsStringEnum<OrigemBeneficio>([...ORIGENS_BENEFICIO]),
  );
  const recorte = {
    q: q || undefined,
    origem: origem ?? undefined,
    dataDe: de || undefined,
    dataAte: ate || undefined,
  };
  const temPeriodo = !!(de || ate);
  const { data: user } = useCurrentUser();
  const { data: resumo } = useBeneficiosResumo(recorte);
  const exportar = useExportarBeneficios();
  const detectar = useDispararDeteccaoBeneficios();
  const [detalhe, setDetalhe] = useState<BeneficioItem | null>(null);

  const canEdit = podeEditar(user, "ccd.beneficios");

  async function dispararDeteccao() {
    try {
      const job = await detectar.mutateAsync();
      toast.success(`Detecção enfileirada (job ${job.idJob}).`);
    } catch (err) {
      const resp = (err as { response?: { status?: number; data?: { detail?: string } } }).response;
      if (resp?.status === 503)
        toast.error("Fila de tarefas indisponível — o Redis não está rodando.");
      else if (resp?.status === 403) toast.error("Apenas administradores disparam a detecção.");
      else toast.error(resp?.data?.detail ?? "Falha ao enfileirar a detecção.");
    }
  }

  async function exportarRecorte(formato: "csv" | "json") {
    try {
      await exportar.mutateAsync({ formato, recorte });
      toast.success("Exportado.");
    } catch (err) {
      const status = (err as { response?: { status?: number } }).response?.status;
      if (status === 404) toast.error("Nenhum benefício no recorte.");
      else toast.error("Falha ao exportar.");
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h1 className="section-heading text-2xl">Benefícios (SisBenefícios)</h1>
        <div className="flex gap-2">
          {canEdit ? (
            <Button variant="outline" onClick={() => void dispararDeteccao()}>
              Detectar candidatos
            </Button>
          ) : null}
          <Button disabled={exportar.isPending} onClick={() => void exportarRecorte("csv")}>
            Exportar CSV
          </Button>
          <Button
            variant="outline"
            disabled={exportar.isPending}
            onClick={() => void exportarRecorte("json")}
          >
            Exportar JSON
          </Button>
        </div>
      </div>

      <SerieTemporal
        de={de}
        ate={ate}
        onChange={(d, a) => {
          void setDe(d);
          void setAte(a);
        }}
      />

      <div className="flex flex-wrap items-end gap-2">
        <div className="flex flex-col gap-1">
          <label htmlFor="periodo-de" className="text-muted-foreground text-xs">
            Ocorrência de
          </label>
          <Input
            id="periodo-de"
            type="date"
            value={de}
            max={ate || undefined}
            onChange={(e) => void setDe(e.target.value || null)}
          />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="periodo-ate" className="text-muted-foreground text-xs">
            até
          </label>
          <Input
            id="periodo-ate"
            type="date"
            value={ate}
            min={de || undefined}
            onChange={(e) => void setAte(e.target.value || null)}
          />
        </div>
        {temPeriodo ? (
          <Button
            variant="ghost"
            onClick={() => {
              void setDe(null);
              void setAte(null);
            }}
          >
            Limpar
          </Button>
        ) : null}
        <span className="text-muted-foreground pb-2 text-xs">
          Data do fato gerador; propostas usam a data de inclusão. O export leva o recorte atual.
        </span>
      </div>

      {resumo ? (
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          <StatCard label="Total" value={String(resumo.total)} />
          <StatCard label="Potenciais" value={String(resumo.qtdPotencial)} />
          <StatCard label="Efetivos" value={String(resumo.qtdEfetivo)} />
          <StatCard
            label="Valor efetivo"
            value={resumo.valorEfetivo ? formatBRL(Number(resumo.valorEfetivo)) : "—"}
          />
        </div>
      ) : null}

      <BeneficiosLista
        q={q}
        origem={origem}
        dataDe={recorte.dataDe}
        dataAte={recorte.dataAte}
        onQ={(v) => void setQ(v || null)}
        onOrigem={(v) => void setOrigem(v)}
        onVer={setDetalhe}
      />

      <BeneficioDetalhe item={detalhe} onClose={() => setDetalhe(null)} />
    </div>
  );
}
