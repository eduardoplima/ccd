"use client";

import { parseAsString, useQueryState } from "nuqs";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useCurrentUser } from "@/hooks/use-current-user";
import {
  useBeneficiosResumo,
  useDispararDeteccaoBeneficios,
  useExportarBeneficios,
} from "@/hooks/use-beneficios";
import { formatBRL } from "@/lib/format";
import type { BeneficioItem } from "@/schemas/beneficios";

import { BeneficioFormDialog } from "./_beneficio-dialog";
import { BeneficiosTab } from "./_beneficios-tab";

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border p-3">
      <div className="text-muted-foreground text-xs">{label}</div>
      <div className="text-lg font-semibold">{value}</div>
    </div>
  );
}

export default function BeneficiosPage() {
  const [tab, setTab] = useQueryState("tab", parseAsString.withDefault("rascunhos"));
  const { data: user } = useCurrentUser();
  const { data: resumo } = useBeneficiosResumo();
  const exportar = useExportarBeneficios();
  const detectar = useDispararDeteccaoBeneficios();

  const [criarOpen, setCriarOpen] = useState(false);
  const [editando, setEditando] = useState<BeneficioItem | null>(null);
  const [selecao, setSelecao] = useState<Set<number>>(new Set());

  const isAdmin = user?.papel === "admin";

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

  async function exportarLote(formato: "xlsx" | "json") {
    try {
      await exportar.mutateAsync({ formato, ids: [...selecao] });
      setSelecao(new Set());
      toast.success("Lote exportado e marcado como enviado.");
    } catch (err) {
      const status = (err as { response?: { status?: number } }).response?.status;
      if (status === 404) toast.error("Nenhum benefício validado para exportar.");
      else toast.error("Falha ao exportar.");
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h1 className="section-heading text-2xl">Benefícios (SisBenefícios)</h1>
        <div className="flex gap-2">
          {isAdmin ? (
            <Button variant="outline" onClick={() => void dispararDeteccao()}>
              Detectar candidatos
            </Button>
          ) : null}
          <Button onClick={() => setCriarOpen(true)}>Novo benefício</Button>
        </div>
      </div>

      {resumo ? (
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4 xl:grid-cols-8">
          <StatCard label="Total" value={String(resumo.total)} />
          <StatCard label="Rascunhos" value={String(resumo.qtdRascunho)} />
          <StatCard label="Validados" value={String(resumo.qtdValidado)} />
          <StatCard label="Enviados" value={String(resumo.qtdEnviado)} />
          <StatCard label="Descartados" value={String(resumo.qtdDescartado)} />
          <StatCard label="Potenciais" value={String(resumo.qtdPotencial)} />
          <StatCard label="Efetivos" value={String(resumo.qtdEfetivo)} />
          <StatCard
            label="Valor efetivo"
            value={resumo.valorEfetivo ? formatBRL(Number(resumo.valorEfetivo)) : "—"}
          />
        </div>
      ) : null}

      <Tabs value={tab} onValueChange={(v) => void setTab(v)}>
        <TabsList>
          <TabsTrigger value="propostas">Propostas</TabsTrigger>
          <TabsTrigger value="rascunhos">Rascunhos</TabsTrigger>
          <TabsTrigger value="validados">Validados</TabsTrigger>
          <TabsTrigger value="enviados">Enviados</TabsTrigger>
          <TabsTrigger value="descartados">Descartados</TabsTrigger>
        </TabsList>

        <TabsContent value="propostas" className="pt-4">
          <p className="text-muted-foreground mb-3 text-sm">
            Propostas de benefício aprovadas pelas UTCEs no SisBenefícios, importadas para a CCD
            gerenciar a conversão em potencial/efetivo. As demais abas mostram só a carteira
            detectada e os cadastros manuais.
          </p>
          <BeneficiosTab
            fonte="propostas"
            selecao={selecao}
            onSelecao={setSelecao}
            onEditar={setEditando}
          />
        </TabsContent>
        <TabsContent value="rascunhos" className="pt-4">
          <BeneficiosTab status="RASCUNHO" fonte="carteira" onEditar={setEditando} />
        </TabsContent>
        <TabsContent value="validados" className="pt-4">
          <div className="mb-3 flex items-center gap-2">
            <Button
              size="sm"
              disabled={exportar.isPending}
              onClick={() => void exportarLote("xlsx")}
            >
              Exportar XLSX{selecao.size > 0 ? ` (${selecao.size})` : " (todos)"}
            </Button>
            <Button
              size="sm"
              variant="outline"
              disabled={exportar.isPending}
              onClick={() => void exportarLote("json")}
            >
              Exportar JSON{selecao.size > 0 ? ` (${selecao.size})` : " (todos)"}
            </Button>
            <span className="text-muted-foreground text-sm">
              O export marca os registros como enviados à SECEX.
            </span>
          </div>
          <BeneficiosTab
            status="VALIDADO"
            fonte="carteira"
            selecao={selecao}
            onSelecao={setSelecao}
            onEditar={setEditando}
          />
        </TabsContent>
        <TabsContent value="enviados" className="pt-4">
          <BeneficiosTab status="ENVIADO" fonte="carteira" onEditar={setEditando} />
        </TabsContent>
        <TabsContent value="descartados" className="pt-4">
          <BeneficiosTab status="DESCARTADO" fonte="carteira" onEditar={setEditando} />
        </TabsContent>
      </Tabs>

      <BeneficioFormDialog open={criarOpen} item={null} onOpenChange={setCriarOpen} />
      <BeneficioFormDialog
        open={editando !== null}
        item={editando}
        onOpenChange={(open) => {
          if (!open) setEditando(null);
        }}
      />
    </div>
  );
}
