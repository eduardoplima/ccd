"use client";

import { UnmappedError } from "@/schemas/dataset-corrections";

/**
 * Renders the cleanlab CSV's `contexto` window with the flagged token
 * underlined. Used for errors whose document couldn't be located, where
 * the document-level canvas isn't available.
 */
export function FallbackWindow({ error }: { error: UnmappedError }) {
  const ctx = error.contexto || "";
  const idx = ctx.indexOf(error.token);
  const before = idx >= 0 ? ctx.slice(0, idx) : "";
  const hit = idx >= 0 ? ctx.slice(idx, idx + error.token.length) : error.token;
  const after = idx >= 0 ? ctx.slice(idx + error.token.length) : ctx;

  return (
    <div className="rounded-md border bg-white p-4 font-mono text-sm leading-relaxed">
      <div className="mb-2 text-xs uppercase tracking-wide text-muted-foreground">
        Sentença #{error.sentenca_idx} · contexto cleanlab
      </div>
      <span>{before}</span>
      <span className="rounded bg-amber-100 px-0.5 ring-2 ring-red-500">
        {hit}
      </span>
      <span>{after}</span>
    </div>
  );
}
