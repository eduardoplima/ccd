"use client";

import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { TIPO_LABEL, TipoEntidade } from "@/schemas/review";

// Same palette as dataset-corrections/document-canvas.tsx (NER_LABEL_CLASS),
// keyed by the review tipo instead of the uppercase NER label.
export const TIPO_SPAN_CLASS: Record<TipoEntidade, string> = {
  multa: "bg-amber-100 text-amber-950",
  obrigacao: "bg-sky-100 text-sky-950",
  ressarcimento: "bg-emerald-100 text-emerald-950",
  recomendacao: "bg-violet-100 text-violet-950",
};

export type CanvasSpan = {
  key: string;
  tipo: TipoEntidade;
  charStart: number;
  charEnd: number;
  rejected?: boolean;
};

type Range = {
  start: number;
  end: number;
  span: CanvasSpan | null;
};

// Boundary-points algorithm from dataset-corrections/document-canvas.tsx:
// collect all span edges, sort, emit non-overlapping segments.
function buildRanges(textLength: number, spans: CanvasSpan[]): Range[] {
  const points = new Set<number>([0, textLength]);
  for (const s of spans) {
    points.add(Math.max(0, s.charStart));
    points.add(Math.min(textLength, s.charEnd));
  }
  const sorted = [...points].sort((a, b) => a - b);
  const ranges: Range[] = [];
  for (let i = 0; i < sorted.length - 1; i++) {
    const start = sorted[i];
    const end = sorted[i + 1];
    if (start === end) continue;
    const span = spans.find((s) => s.charStart <= start && s.charEnd >= end) ?? null;
    ranges.push({ start, end, span });
  }
  return ranges;
}

type DecisionCanvasProps = {
  text: string;
  spans: CanvasSpan[];
  selectedKey: string | null;
  onSelect: (key: string) => void;
  onAddEntity: (tipo: TipoEntidade, trecho: string) => void;
  disabled?: boolean;
};

export function DecisionCanvas({
  text,
  spans,
  selectedKey,
  onSelect,
  onAddEntity,
  disabled,
}: DecisionCanvasProps) {
  const [pendingSelection, setPendingSelection] = useState<string | null>(null);

  const ranges = useMemo(() => buildRanges(text.length, spans), [text, spans]);

  // Only strings cross the boundary — offsets of new entities are re-derived
  // via indexOf by the caller, matching the backend's read-time alignment.
  function handleMouseUp() {
    if (disabled) return;
    const selection = window.getSelection()?.toString().trim() ?? "";
    if (selection.length >= 10 && text.includes(selection)) {
      setPendingSelection(selection);
    }
  }

  return (
    <div className="space-y-2">
      {pendingSelection && (
        <div className="sticky top-2 z-10 flex flex-wrap items-center gap-2 rounded-md border bg-card p-2 text-sm shadow-sm">
          <span className="text-muted-foreground">Adicionar trecho selecionado como:</span>
          {(Object.keys(TIPO_LABEL) as TipoEntidade[]).map((tipo) => (
            <Button
              key={tipo}
              size="sm"
              variant="outline"
              className={TIPO_SPAN_CLASS[tipo]}
              onClick={() => {
                onAddEntity(tipo, pendingSelection);
                setPendingSelection(null);
                window.getSelection()?.removeAllRanges();
              }}
            >
              {TIPO_LABEL[tipo]}
            </Button>
          ))}
          <Button size="sm" variant="ghost" onClick={() => setPendingSelection(null)}>
            Cancelar
          </Button>
        </div>
      )}

      <div
        className="max-h-[70vh] overflow-y-auto whitespace-pre-wrap rounded-md border bg-card p-6 font-serif text-base leading-relaxed"
        onMouseUp={handleMouseUp}
      >
        {ranges.map((r, i) => {
          const chunk = text.slice(r.start, r.end);
          if (!chunk) return null;
          if (!r.span) return <span key={i}>{chunk}</span>;
          const isSelected = r.span.key === selectedKey;
          const span = r.span;
          return (
            <span
              key={i}
              role="button"
              tabIndex={0}
              className={cn(
                "cursor-pointer rounded-sm transition-all",
                TIPO_SPAN_CLASS[span.tipo],
                span.rejected && "line-through opacity-50",
                isSelected && "ring-2 ring-offset-1",
              )}
              title={TIPO_LABEL[span.tipo]}
              onClick={() => onSelect(span.key)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  onSelect(span.key);
                }
              }}
            >
              {chunk}
            </span>
          );
        })}
      </div>
    </div>
  );
}
