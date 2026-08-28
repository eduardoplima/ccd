"use client";

import { HelpCircle } from "lucide-react";
import { parseAsBoolean, parseAsString, useQueryState } from "nuqs";

import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import { PrescricaoTab } from "./_prescricao-tab";
import { TempoTab } from "./_tempo-tab";
import { TodosTab } from "./_todos-tab";

// espelha MARCADORES_PERMANENCIA de web/backend/app/ccd/service.py
const MARCADORES_PERMANENCIA: { grupo: string; itens: string[] }[] = [
  {
    grupo: "Cobrança em andamento",
    itens: [
      "PARCELAMENTO EM CURSO",
      "DESCONTO EM FOLHA - ACOMPANHAMENTO",
      "DESCONTO EM FOLHA - Acompanhamento Nereu",
      "PROTESTO - Confirmação de envio",
      "PROTESTO - Enviado",
      "Protesto Efetivo Junho/2026",
      "Protesto Efetivo Julho/2026",
    ],
  },
  {
    grupo: "Sobrestados / decisão judicial",
    itens: [
      "Nereu - SOBRESTADO",
      "SOBRESTADO - Decisão judicial",
      "DECISÃO JUDICIAL - Acompanhamento",
      "DECISÃO JUDICIAL - Suspender os efeitos do Acórdão",
    ],
  },
  {
    grupo: "Aguardando terceiros / encerramento",
    itens: [
      "EXECUÇÃO - aguardando determinações ou impedimentos",
      "Chamados abertos aguardando solução",
      "PAGAMENTO INTEGRAL",
    ],
  },
];

export default function CcdInicioPage() {
  const [tab, setTab] = useQueryState("tab", parseAsString.withDefault("tempo"));
  const [ocultarPermanencia, setOcultarPermanencia] = useQueryState(
    "permanencia",
    parseAsBoolean.withDefault(true),
  );

  return (
    <div className="flex flex-col gap-6">
      <h1 className="section-heading text-2xl">Início — Processos na CCD</h1>

      <Tabs value={tab} onValueChange={(v) => void setTab(v)}>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <TabsList>
            <TabsTrigger value="tempo">Tempo na CCD</TabsTrigger>
            <TabsTrigger value="prescricao">Risco de prescrição</TabsTrigger>
            <TabsTrigger value="todos">Todos</TabsTrigger>
          </TabsList>
          {tab !== "todos" ? (
            <div className="flex items-center gap-2">
              <Checkbox
                id="f-permanencia"
                checked={ocultarPermanencia}
                onCheckedChange={(c) => void setOcultarPermanencia(c === true)}
              />
              <Label htmlFor="f-permanencia" className="cursor-pointer font-normal">
                Ocultar marcadores de permanência
              </Label>
              <Dialog>
                <DialogTrigger asChild>
                  <button
                    type="button"
                    aria-label="O que são marcadores de permanência?"
                    className="text-muted-foreground transition-colors hover:text-foreground"
                  >
                    <HelpCircle className="size-4" />
                  </button>
                </DialogTrigger>
                <DialogContent className="max-h-[80vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>Marcadores de permanência</DialogTitle>
                    <DialogDescription>
                      Marcadores que indicam que o processo está na CCD por um motivo legítimo —
                      aguardando um evento externo, com cobrança em andamento ou sobrestado — e por
                      isso não precisa de instrução agora. Com o filtro ligado, processos com
                      qualquer um destes marcadores ativos saem das filas de tempo e de prescrição.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="flex flex-col gap-4 text-sm">
                    {MARCADORES_PERMANENCIA.map((g) => (
                      <div key={g.grupo}>
                        <p className="mb-1 font-medium">{g.grupo}</p>
                        <ul className="list-disc space-y-0.5 pl-5 text-muted-foreground">
                          {g.itens.map((m) => (
                            <li key={m}>{m}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                    <p className="text-xs text-muted-foreground">
                      Obs.: parcelamento em curso e sobrestamento também suspendem a prescrição —
                      por isso esses processos não aparecem na aba de risco com o filtro ligado.
                    </p>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          ) : null}
        </div>

        <TabsContent value="tempo" className="mt-4">
          <TempoTab ocultarPermanencia={ocultarPermanencia} />
        </TabsContent>
        <TabsContent value="prescricao" className="mt-4">
          <PrescricaoTab ocultarPermanencia={ocultarPermanencia} />
        </TabsContent>
        <TabsContent value="todos" className="mt-4">
          <TodosTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
