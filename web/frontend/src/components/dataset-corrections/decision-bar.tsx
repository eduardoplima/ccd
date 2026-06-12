"use client";

import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { RangeAdjuster } from "@/components/dataset-corrections/range-adjuster";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useDecideGroup, useDecideUnmapped, useLabels } from "@/hooks/use-dataset-corrections";
import { messageForError } from "@/lib/error-messages";
import { cn } from "@/lib/utils";
import {
  DecisionKind,
  DocumentToken,
  EntityGroup,
  UnmappedError,
} from "@/schemas/dataset-corrections";

function statusLabel(status: EntityGroup["status"]): string {
  switch (status) {
    case "accept":
      return "Aceita";
    case "reject":
      return "Rejeitada";
    case "custom":
      return "Customizada";
    case "mixed":
      return "Mista";
    default:
      return "Pendente";
  }
}

function statusBadgeVariant(
  status: EntityGroup["status"],
): "default" | "secondary" | "destructive" | "outline" {
  switch (status) {
    case "accept":
      return "default";
    case "reject":
      return "secondary";
    case "custom":
      return "outline";
    case "mixed":
      return "destructive";
    default:
      return "destructive";
  }
}

function maxConfidence(group: EntityGroup): number {
  let max = 0;
  for (const t of group.tokens) {
    if (t.is_flagged && t.confianca != null && t.confianca > max) {
      max = t.confianca;
    }
  }
  return max;
}

function commonSuggestion(group: EntityGroup): string | null {
  const sugs = group.tokens
    .filter((t) => t.is_flagged && t.label_sugerido)
    .map((t) => t.label_sugerido as string);
  if (sugs.length === 0) return null;
  return sugs.every((s) => s === sugs[0]) ? sugs[0] : null;
}

export function GroupDecisionBar({
  group,
  documentId,
  docTokens,
  onMoveNext,
  onMovePrev,
  onAfterDecide,
}: {
  group: EntityGroup | null;
  documentId: number | null;
  docTokens: DocumentToken[];
  onMoveNext?: () => void;
  onMovePrev?: () => void;
  /** Called after a successful decision. If provided, replaces the
   * post-decide ``onMoveNext`` so the page can decide whether to advance
   * within the current document or jump to the next one. */
  onAfterDecide?: (groupId: string) => void;
}) {
  const decideMutation = useDecideGroup(documentId);
  const labelsQuery = useLabels();
  const [customLabel, setCustomLabel] = useState<string>("");
  const [customFirst, setCustomFirst] = useState<number>(0);
  const [customLast, setCustomLast] = useState<number>(0);
  const customSelectRef = useRef<HTMLSelectElement | null>(null);

  useEffect(() => {
    if (group?.status === "custom" && group.entity_label_final) {
      setCustomLabel(group.entity_label_final);
    } else {
      setCustomLabel("");
    }
    if (group) {
      setCustomFirst(group.first_token_idx);
      setCustomLast(group.last_token_idx);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    group?.group_id,
    group?.status,
    group?.entity_label_final,
    group?.first_token_idx,
    group?.last_token_idx,
  ]);

  function fireDecide(decision: DecisionKind, entityLabel?: string | null) {
    if (!group) return;
    const decidedId = group.group_id;
    const isCustomWithRange =
      decision === "custom" &&
      (customFirst !== group.first_token_idx || customLast !== group.last_token_idx);
    decideMutation.mutate(
      {
        groupId: decidedId,
        body: {
          decision,
          entity_label: entityLabel ?? null,
          first_token_idx: isCustomWithRange ? customFirst : null,
          last_token_idx: isCustomWithRange ? customLast : null,
        },
      },
      {
        onSuccess: () => {
          toast.success(
            decision === "accept"
              ? "Sugestão aceita."
              : decision === "reject"
                ? "Original mantido."
                : `Entidade marcada como ${entityLabel}.`,
          );
          if (onAfterDecide) {
            onAfterDecide(decidedId);
          } else {
            onMoveNext?.();
          }
        },
        onError: (err) => {
          toast.error(messageForError(err, "Não foi possível salvar a decisão."));
        },
      },
    );
  }

  useEffect(() => {
    function handler(ev: KeyboardEvent) {
      if (!group) return;
      const target = ev.target as HTMLElement | null;
      if (target && ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName)) {
        return;
      }
      if (ev.key.toLowerCase() === "a") {
        ev.preventDefault();
        fireDecide("accept");
      } else if (ev.key.toLowerCase() === "r") {
        ev.preventDefault();
        fireDecide("reject");
      } else if (ev.key.toLowerCase() === "c") {
        ev.preventDefault();
        customSelectRef.current?.focus();
      } else if (ev.key === "ArrowRight" || ev.key.toLowerCase() === "k") {
        ev.preventDefault();
        onMoveNext?.();
      } else if (ev.key === "ArrowLeft" || ev.key.toLowerCase() === "j") {
        ev.preventDefault();
        onMovePrev?.();
      }
    }
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [group?.group_id]);

  if (!group) {
    return (
      <aside className="rounded-md border bg-muted/30 p-4 text-sm text-muted-foreground">
        Selecione uma entidade destacada no documento.
      </aside>
    );
  }

  const entityLabels = labelsQuery.data?.entity_labels ?? [];
  const conf = Math.round(maxConfidence(group) * 100);
  const isPending = decideMutation.isPending;
  const sharedSug = commonSuggestion(group);
  const flaggedTokens = group.tokens.filter((t) => t.is_flagged);

  return (
    <aside className="flex flex-col gap-4 rounded-md border bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="text-xs uppercase tracking-wide text-muted-foreground">
          Entidade {group.gold_entity_label ?? "(livre)"} · {group.tokens.length} tokens ·{" "}
          {flaggedTokens.length} flagrado(s)
        </div>
        <Badge variant={statusBadgeVariant(group.status)}>
          {statusLabel(group.status)}
          {group.status === "custom" && group.entity_label_final
            ? ` → ${group.entity_label_final}`
            : ""}
        </Badge>
      </div>

      <div className="rounded border bg-muted/40 p-3">
        <div className="flex items-center justify-between text-xs uppercase tracking-wide text-muted-foreground">
          <span>Tokens flagrados</span>
          <span>conf. máx {conf}%</span>
        </div>
        <ul className="mt-2 flex max-h-40 flex-col gap-1 overflow-auto text-sm">
          {flaggedTokens.map((tok) => (
            <li key={tok.token_idx_in_doc} className="flex items-center justify-between gap-2">
              <span className="font-mono">{tok.text}</span>
              <span className="flex items-center gap-1 text-xs text-muted-foreground">
                <span className="font-mono">{tok.bio_original}</span>
                <span>→</span>
                <span className="font-mono">{tok.label_sugerido}</span>
                {tok.confianca != null ? (
                  <span className="ml-2">{Math.round(tok.confianca * 100)}%</span>
                ) : null}
              </span>
            </li>
          ))}
        </ul>
      </div>

      <div className="flex flex-col gap-2">
        <Button
          variant="default"
          disabled={isPending}
          onClick={() => fireDecide("accept")}
          title="Atalho: A"
        >
          Aceitar sugestão
          {sharedSug ? ` (todos → ${sharedSug})` : " (por token)"}
        </Button>
        <Button
          variant="secondary"
          disabled={isPending}
          onClick={() => fireDecide("reject")}
          title="Atalho: R"
        >
          Manter original
        </Button>

        <RangeAdjuster
          docTokens={docTokens}
          naturalFirst={group.first_token_idx}
          naturalLast={group.last_token_idx}
          firstIdx={customFirst}
          lastIdx={customLast}
          onChange={(first, last) => {
            setCustomFirst(first);
            setCustomLast(last);
          }}
        />

        <div className="flex items-center gap-2 pt-2">
          <select
            ref={customSelectRef}
            value={customLabel}
            onChange={(e) => setCustomLabel(e.target.value)}
            className="flex-1 rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm"
          >
            <option value="">Marcar como…</option>
            {entityLabels.map((l) => (
              <option key={l} value={l}>
                {l === "O" ? "Não-entidade (O)" : l}
              </option>
            ))}
          </select>
          <Button
            variant="outline"
            disabled={isPending || !customLabel}
            onClick={() => fireDecide("custom", customLabel)}
          >
            Salvar
          </Button>
        </div>
        <p className="text-xs text-muted-foreground">
          “Marcar como” reescreve o BIO da faixa selecionada ({customLast - customFirst + 1}{" "}
          tokens). Primeiro token vira <code className="font-mono">B-…</code>, demais{" "}
          <code className="font-mono">I-…</code>.
        </p>
      </div>

      <div className="flex items-center justify-between border-t pt-3 text-xs text-muted-foreground">
        <button
          type="button"
          className="hover:underline disabled:opacity-50"
          onClick={onMovePrev}
          disabled={!onMovePrev}
        >
          ← Anterior (J)
        </button>
        <button
          type="button"
          className="hover:underline disabled:opacity-50"
          onClick={onMoveNext}
          disabled={!onMoveNext}
        >
          Próximo (K) →
        </button>
      </div>
    </aside>
  );
}

// ---------- Unmapped (single-row) decision bar -----------------------------

export function UnmappedDecisionBar({
  error,
  onMoveNext,
  onMovePrev,
}: {
  error: UnmappedError | null;
  onMoveNext?: () => void;
  onMovePrev?: () => void;
}) {
  const decideMutation = useDecideUnmapped();
  const labelsQuery = useLabels();
  const [customLabel, setCustomLabel] = useState<string>("");
  const customSelectRef = useRef<HTMLSelectElement | null>(null);

  useEffect(() => {
    if (error?.status === "custom" && error.label_final) {
      setCustomLabel(error.label_final);
    } else {
      setCustomLabel("");
    }
  }, [error?.row_id, error?.status, error?.label_final]);

  function fireDecide(decision: DecisionKind, labelFinal?: string | null) {
    if (!error) return;
    decideMutation.mutate(
      {
        rowId: error.row_id,
        body: { decision, label_final: labelFinal ?? null },
      },
      {
        onSuccess: () => {
          toast.success(
            decision === "accept"
              ? "Sugestão aceita."
              : decision === "reject"
                ? "Original mantido."
                : "Label customizado salvo.",
          );
          onMoveNext?.();
        },
        onError: (err) => {
          toast.error(messageForError(err, "Não foi possível salvar a decisão."));
        },
      },
    );
  }

  if (!error) {
    return (
      <aside className="rounded-md border bg-muted/30 p-4 text-sm text-muted-foreground">
        Selecione um erro à esquerda.
      </aside>
    );
  }

  const labels = labelsQuery.data?.labels ?? [];
  const conf = Math.round(error.confianca * 100);
  const isPending = decideMutation.isPending;

  return (
    <aside className="flex flex-col gap-4 rounded-md border bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="text-xs uppercase tracking-wide text-muted-foreground">
          Erro #{error.row_id}
        </div>
        <Badge variant={error.status === "pending" ? "destructive" : "default"}>
          {statusLabel(error.status)}
        </Badge>
      </div>

      <div>
        <div className="text-xs text-muted-foreground">Token</div>
        <div className="font-mono text-base">{error.token}</div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="rounded border bg-muted/40 p-3">
          <div className="text-xs uppercase tracking-wide text-muted-foreground">Original</div>
          <div className="mt-1 font-mono text-sm">{error.label_original}</div>
        </div>
        <div className="rounded border bg-muted/40 p-3">
          <div className="text-xs uppercase tracking-wide text-muted-foreground">
            Sugestão cleanlab
          </div>
          <div className="mt-1 font-mono text-sm">{error.label_sugerido}</div>
          <div className="mt-2 flex items-center gap-2">
            <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted">
              <div
                className={cn(
                  "h-full",
                  conf > 80 ? "bg-rose-500" : conf > 50 ? "bg-amber-500" : "bg-emerald-500",
                )}
                style={{ width: `${conf}%` }}
              />
            </div>
            <span className="text-xs text-muted-foreground">{conf}%</span>
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <Button variant="default" disabled={isPending} onClick={() => fireDecide("accept")}>
          Aceitar sugestão ({error.label_sugerido})
        </Button>
        <Button variant="secondary" disabled={isPending} onClick={() => fireDecide("reject")}>
          Manter original ({error.label_original})
        </Button>
        <div className="flex items-center gap-2 pt-2">
          <select
            ref={customSelectRef}
            value={customLabel}
            onChange={(e) => setCustomLabel(e.target.value)}
            className="flex-1 rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm"
          >
            <option value="">Outro label BIO…</option>
            {labels.map((l) => (
              <option key={l} value={l}>
                {l}
              </option>
            ))}
          </select>
          <Button
            variant="outline"
            disabled={isPending || !customLabel}
            onClick={() => fireDecide("custom", customLabel)}
          >
            Salvar
          </Button>
        </div>
      </div>

      <div className="flex items-center justify-between border-t pt-3 text-xs text-muted-foreground">
        <button
          type="button"
          className="hover:underline disabled:opacity-50"
          onClick={onMovePrev}
          disabled={!onMovePrev}
        >
          ← Anterior
        </button>
        <button
          type="button"
          className="hover:underline disabled:opacity-50"
          onClick={onMoveNext}
          disabled={!onMoveNext}
        >
          Próximo →
        </button>
      </div>
    </aside>
  );
}
