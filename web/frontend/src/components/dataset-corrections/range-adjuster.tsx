"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { DocumentToken } from "@/schemas/dataset-corrections";

const PREVIEW_PAD = 4;

/**
 * Lets the reviewer extend or shrink the persisted entity range before
 * committing a "custom" group decision. Backed by the doc's full token
 * list so we can show a few neighbouring tokens on each side.
 */
export function RangeAdjuster({
  docTokens,
  naturalFirst,
  naturalLast,
  firstIdx,
  lastIdx,
  onChange,
}: {
  docTokens: DocumentToken[];
  naturalFirst: number;
  naturalLast: number;
  firstIdx: number;
  lastIdx: number;
  onChange: (first: number, last: number) => void;
}) {
  const minIdx = 0;
  const maxIdx = docTokens.length - 1;
  const dirty = firstIdx !== naturalFirst || lastIdx !== naturalLast;

  const previewStart = Math.max(minIdx, firstIdx - PREVIEW_PAD);
  const previewEnd = Math.min(maxIdx, lastIdx + PREVIEW_PAD);

  function adjust(deltaFirst: number, deltaLast: number) {
    const next = {
      first: Math.min(maxIdx, Math.max(minIdx, firstIdx + deltaFirst)),
      last: Math.min(maxIdx, Math.max(minIdx, lastIdx + deltaLast)),
    };
    if (next.first > next.last) return;
    onChange(next.first, next.last);
  }

  return (
    <div className="rounded border bg-muted/40 p-3">
      <div className="flex items-center justify-between text-xs uppercase tracking-wide text-muted-foreground">
        <span>
          Faixa da entidade · tokens {firstIdx}–{lastIdx} (
          {lastIdx - firstIdx + 1})
        </span>
        {dirty ? (
          <button
            type="button"
            onClick={() => onChange(naturalFirst, naturalLast)}
            className="text-blue-600 hover:underline"
          >
            Resetar ({naturalFirst}–{naturalLast})
          </button>
        ) : null}
      </div>

      <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
        <div className="flex items-center justify-between gap-1">
          <span className="text-muted-foreground">Início:</span>
          <div className="flex gap-1">
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={firstIdx <= minIdx}
              onClick={() => adjust(-1, 0)}
              title="Incluir token anterior"
            >
              ← +1
            </Button>
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={firstIdx >= lastIdx}
              onClick={() => adjust(+1, 0)}
              title="Excluir primeiro token"
            >
              +1 →
            </Button>
          </div>
        </div>
        <div className="flex items-center justify-between gap-1">
          <span className="text-muted-foreground">Fim:</span>
          <div className="flex gap-1">
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={lastIdx <= firstIdx}
              onClick={() => adjust(0, -1)}
              title="Excluir último token"
            >
              ← -1
            </Button>
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={lastIdx >= maxIdx}
              onClick={() => adjust(0, +1)}
              title="Incluir token seguinte"
            >
              -1 →
            </Button>
          </div>
        </div>
      </div>

      <div className="mt-3 max-h-24 overflow-auto rounded border bg-white p-2 font-mono text-xs leading-relaxed">
        {docTokens.slice(previewStart, previewEnd + 1).map((tok) => {
          const inRange =
            tok.token_idx_in_doc >= firstIdx && tok.token_idx_in_doc <= lastIdx;
          return (
            <span
              key={tok.token_idx_in_doc}
              className={cn(
                "rounded-sm px-0.5",
                inRange ? "bg-amber-100 text-amber-950" : "text-muted-foreground",
              )}
              title={`#${tok.token_idx_in_doc} · ${tok.bio}`}
            >
              {tok.text}{" "}
            </span>
          );
        })}
      </div>
    </div>
  );
}
