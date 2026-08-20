"use client";

import { useMemo, useRef, useState } from "react";

import { cn } from "@/lib/utils";
import { LABELS, Label, Span } from "@/schemas/dataset";

// Mesma paleta do annotation-canvas, copiada de propósito: aquele componente é
// de edição e este é só leitura — acoplar os dois por 4 linhas não compensa.
const LABEL_CLASS: Record<Label, string> = {
  MULTA: "bg-amber-100 text-amber-950 dark:bg-amber-950 dark:text-amber-100",
  OBRIGACAO: "bg-sky-100 text-sky-950 dark:bg-sky-950 dark:text-sky-100",
  RESSARCIMENTO: "bg-emerald-100 text-emerald-950 dark:bg-emerald-950 dark:text-emerald-100",
  RECOMENDACAO: "bg-violet-100 text-violet-950 dark:bg-violet-950 dark:text-violet-100",
};

type Anotacao = { anotador: string; spans: Span[] };

type Pedaco = { start: number; end: number; porAnotador: (Label | null)[] };

function fatiar(textLength: number, anotacoes: Anotacao[]): Pedaco[] {
  const pontos = new Set<number>([0, textLength]);
  for (const { spans } of anotacoes) {
    for (const s of spans) {
      pontos.add(Math.max(0, s.start));
      pontos.add(Math.min(textLength, s.end));
    }
  }
  const ordenados = [...pontos].sort((a, b) => a - b);
  const pedacos: Pedaco[] = [];
  for (let i = 0; i < ordenados.length - 1; i++) {
    const start = ordenados[i];
    const end = ordenados[i + 1];
    if (start === end) continue;
    pedacos.push({
      start,
      end,
      porAnotador: anotacoes.map(
        ({ spans }) => spans.find((s) => s.start <= start && s.end >= end)?.label ?? null,
      ),
    });
  }
  return pedacos;
}

/** Rótulo mais marcado no pedaço (desempate pela ordem dos anotadores). */
function majoritario(labels: (Label | null)[]): Label | null {
  const marcados = labels.filter((l): l is Label => l !== null);
  if (marcados.length === 0) return null;
  return [...marcados].sort(
    (a, b) => marcados.filter((l) => l === b).length - marcados.filter((l) => l === a).length,
  )[0];
}

type Tooltip = { top: number; left: number; linhas: { anotador: string; label: Label | null }[] };

export function MultiAnnotatorCanvas({ text, anotacoes }: { text: string; anotacoes: Anotacao[] }) {
  const pedacos = useMemo(() => fatiar(text.length, anotacoes), [text.length, anotacoes]);
  const [tooltip, setTooltip] = useState<Tooltip | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  function mostrar(e: React.MouseEvent, p: Pedaco) {
    const base = containerRef.current!.getBoundingClientRect();
    setTooltip({
      top: e.clientY - base.top + 18,
      left: Math.max(8, Math.min(e.clientX - base.left, base.width - 220)),
      linhas: anotacoes.map((a, i) => ({ anotador: a.anotador, label: p.porAnotador[i] })),
    });
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2 text-xs">
        {LABELS.map((label) => (
          <span key={label} className={cn("rounded-sm px-2 py-0.5", LABEL_CLASS[label])}>
            {label}
          </span>
        ))}
        <span className="rounded-sm px-2 py-0.5 ring-2 ring-red-400">
          anel vermelho = divergência (passe o mouse para ver quem marcou o quê)
        </span>
      </div>

      <div ref={containerRef} className="relative">
        <div className="prose prose-sm max-w-none whitespace-pre-wrap rounded-md border bg-card p-6 font-serif text-base leading-relaxed">
          {pedacos.map((p) => {
            const chunk = text.slice(p.start, p.end);
            if (!chunk) return null;
            const label = majoritario(p.porAnotador);
            if (!label) {
              return <span key={p.start}>{chunk}</span>;
            }
            const consenso = p.porAnotador.every((l) => l === label);
            return (
              <span
                key={p.start}
                className={cn(
                  "rounded-sm",
                  LABEL_CLASS[label],
                  !consenso && "ring-2 ring-red-400 ring-offset-1",
                )}
                onMouseEnter={(e) => mostrar(e, p)}
                onMouseMove={(e) => mostrar(e, p)}
                onMouseLeave={() => setTooltip(null)}
              >
                {chunk}
              </span>
            );
          })}
        </div>

        {tooltip && (
          <div
            className="pointer-events-none absolute z-10 min-w-40 rounded-md border bg-card p-2 text-sm shadow-md"
            style={{ top: tooltip.top, left: tooltip.left }}
          >
            {tooltip.linhas.map((l) => (
              <div key={l.anotador} className="flex items-center justify-between gap-3">
                <span className="text-muted-foreground">{l.anotador}</span>
                {l.label ? (
                  <span className={cn("rounded-sm px-1.5 py-0.5 text-xs", LABEL_CLASS[l.label])}>
                    {l.label}
                  </span>
                ) : (
                  <span className="text-xs text-muted-foreground">—</span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
