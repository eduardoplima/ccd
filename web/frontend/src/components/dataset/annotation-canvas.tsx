"use client";

import { useCallback, useMemo, useRef, useState } from "react";

import { cn } from "@/lib/utils";
import { LABELS, Label, Span } from "@/schemas/dataset";

const LABEL_CLASS: Record<Label, string> = {
  MULTA: "bg-amber-100 text-amber-950",
  OBRIGACAO: "bg-sky-100 text-sky-950",
  RESSARCIMENTO: "bg-emerald-100 text-emerald-950",
  RECOMENDACAO: "bg-violet-100 text-violet-950",
};

const LABEL_BUTTON: Record<Label, string> = {
  MULTA: "bg-amber-500 hover:bg-amber-600",
  OBRIGACAO: "bg-sky-500 hover:bg-sky-600",
  RESSARCIMENTO: "bg-emerald-500 hover:bg-emerald-600",
  RECOMENDACAO: "bg-violet-500 hover:bg-violet-600",
};

type Pedaco = { start: number; end: number; span: Span | null };

function fatiar(textLength: number, spans: Span[]): Pedaco[] {
  const pontos = new Set<number>([0, textLength]);
  for (const s of spans) {
    pontos.add(Math.max(0, s.start));
    pontos.add(Math.min(textLength, s.end));
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
      span: spans.find((s) => s.start <= start && s.end >= end) ?? null,
    });
  }
  return pedacos;
}

/** Offset absoluto de um ponto da seleção nativa, a partir do `data-start` do
 * pedaço que o contém. Evita ter que espelhar o texto em nós de token. */
function offsetAbsoluto(node: Node | null, offset: number): number | null {
  let el: HTMLElement | null =
    node?.nodeType === Node.TEXT_NODE ? node.parentElement : (node as HTMLElement | null);
  while (el && el.dataset?.start === undefined) el = el.parentElement;
  if (!el) return null;
  return Number(el.dataset.start) + offset;
}

/** Encolhe a seleção para não incluir espaço nas bordas — arrastar com o mouse
 * quase sempre pega um espaço a mais e isso desalinharia o span dos tokens. */
function aparar(text: string, start: number, end: number): [number, number] {
  while (start < end && /\s/.test(text[start])) start += 1;
  while (end > start && /\s/.test(text[end - 1])) end -= 1;
  return [start, end];
}

export function AnnotationCanvas({
  text,
  spans,
  onChange,
  readOnly = false,
}: {
  text: string;
  spans: Span[];
  onChange: (spans: Span[]) => void;
  readOnly?: boolean;
}) {
  const [pendente, setPendente] = useState<{ start: number; end: number } | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const pedacos = useMemo(() => fatiar(text.length, spans), [text.length, spans]);

  const aoSoltar = useCallback(() => {
    if (readOnly) return;
    const sel = window.getSelection();
    if (!sel || sel.isCollapsed) {
      setPendente(null);
      return;
    }
    const a = offsetAbsoluto(sel.anchorNode, sel.anchorOffset);
    const b = offsetAbsoluto(sel.focusNode, sel.focusOffset);
    if (a === null || b === null) return;

    const [start, end] = aparar(text, Math.min(a, b), Math.max(a, b));
    if (end <= start) {
      setPendente(null);
      return;
    }
    // Sobreposição com span existente: remover primeiro (o backend rejeita).
    if (spans.some((s) => start < s.end && end > s.start)) {
      setPendente(null);
      sel.removeAllRanges();
      return;
    }
    setPendente({ start, end });
  }, [readOnly, spans, text]);

  function rotular(label: Label) {
    if (!pendente) return;
    onChange([...spans, { ...pendente, label }].sort((x, y) => x.start - y.start));
    setPendente(null);
    window.getSelection()?.removeAllRanges();
  }

  function remover(alvo: Span) {
    onChange(spans.filter((s) => s !== alvo));
  }

  return (
    <div className="space-y-3">
      <div
        ref={containerRef}
        onMouseUp={aoSoltar}
        className="prose prose-sm max-w-none whitespace-pre-wrap rounded-md border bg-white p-6 font-serif text-base leading-relaxed select-text"
      >
        {pedacos.map((p) => {
          const chunk = text.slice(p.start, p.end);
          if (!chunk) return null;
          if (!p.span) {
            return (
              <span key={p.start} data-start={p.start}>
                {chunk}
              </span>
            );
          }
          const span = p.span;
          return (
            <span
              key={p.start}
              data-start={p.start}
              className={cn(
                "rounded-sm ring-2 ring-offset-1",
                LABEL_CLASS[span.label],
                readOnly ? "ring-transparent" : "cursor-pointer ring-current/30",
              )}
              title={readOnly ? span.label : `${span.label} — clique para remover`}
              onClick={() => !readOnly && remover(span)}
            >
              {chunk}
            </span>
          );
        })}
      </div>

      {pendente && (
        <div className="flex flex-wrap items-center gap-2 rounded-md border bg-zinc-50 p-3">
          <span className="text-sm text-zinc-600">
            &ldquo;{text.slice(pendente.start, pendente.end).slice(0, 80)}
            {pendente.end - pendente.start > 80 ? "…" : ""}&rdquo; é:
          </span>
          {LABELS.map((label) => (
            <button
              key={label}
              type="button"
              onClick={() => rotular(label)}
              className={cn(
                "rounded-md px-3 py-1.5 text-sm font-medium text-white transition-colors",
                LABEL_BUTTON[label],
              )}
            >
              {label}
            </button>
          ))}
          <button
            type="button"
            onClick={() => {
              setPendente(null);
              window.getSelection()?.removeAllRanges();
            }}
            className="rounded-md px-3 py-1.5 text-sm text-zinc-600 hover:bg-zinc-200"
          >
            Cancelar
          </button>
        </div>
      )}
    </div>
  );
}
