"use client";

import { useMemo } from "react";

import { cn } from "@/lib/utils";
import { EntityGroup, NerSpan } from "@/schemas/dataset-corrections";

const NER_LABEL_CLASS: Record<string, string> = {
  MULTA: "bg-amber-100 text-amber-950",
  OBRIGACAO: "bg-sky-100 text-sky-950",
  RESSARCIMENTO: "bg-emerald-100 text-emerald-950",
  RECOMENDACAO: "bg-violet-100 text-violet-950",
};

function nerClass(label: string | null): string {
  if (!label) return "";
  return NER_LABEL_CLASS[label] ?? "bg-gray-100 text-gray-900";
}

function groupRingClass(status: EntityGroup["status"], selected: boolean): string {
  const ring = (() => {
    switch (status) {
      case "accept":
        return "ring-emerald-500";
      case "reject":
        return "ring-zinc-400";
      case "custom":
        return "ring-blue-500";
      case "mixed":
        return "ring-orange-500";
      default:
        return "ring-red-500";
    }
  })();
  return cn(
    "ring-2 rounded cursor-pointer transition-all",
    ring,
    selected && "ring-4 ring-offset-1 ring-offset-white",
  );
}

type Range = {
  start: number;
  end: number;
  nerLabel: string | null;
  group: EntityGroup | null;
};

function buildRanges(textLength: number, nerSpans: NerSpan[], groups: EntityGroup[]): Range[] {
  const points = new Set<number>([0, textLength]);
  for (const s of nerSpans) {
    points.add(Math.max(0, s.char_start));
    points.add(Math.min(textLength, s.char_end));
  }
  for (const g of groups) {
    points.add(Math.max(0, g.char_start));
    points.add(Math.min(textLength, g.char_end));
  }
  const sorted = [...points].sort((a, b) => a - b);
  const ranges: Range[] = [];
  for (let i = 0; i < sorted.length - 1; i++) {
    const start = sorted[i];
    const end = sorted[i + 1];
    if (start === end) continue;
    const ner = nerSpans.find((s) => s.char_start <= start && s.char_end >= end);
    const group = groups.find((g) => g.char_start <= start && g.char_end >= end) ?? null;
    ranges.push({ start, end, nerLabel: ner?.label ?? null, group });
  }
  return ranges;
}

export function DocumentCanvas({
  text,
  nerSpans,
  groups,
  selectedGroupId,
  onSelectGroup,
}: {
  text: string;
  nerSpans: NerSpan[];
  groups: EntityGroup[];
  selectedGroupId: string | null;
  onSelectGroup: (groupId: string) => void;
}) {
  const ranges = useMemo(
    () => buildRanges(text.length, nerSpans, groups),
    [text.length, nerSpans, groups],
  );

  return (
    <div className="prose prose-sm max-w-none whitespace-pre-wrap rounded-md border bg-white p-6 font-serif text-base leading-relaxed">
      {ranges.map((r, i) => {
        const chunk = text.slice(r.start, r.end);
        if (!chunk) return null;
        const ner = nerClass(r.nerLabel);
        const isSelected = r.group != null && r.group.group_id === selectedGroupId;

        const className = cn(
          "rounded-sm",
          ner,
          r.group && groupRingClass(r.group.status, isSelected),
        );
        if (r.group) {
          const group = r.group;
          return (
            <span
              key={i}
              className={className}
              role="button"
              tabIndex={0}
              data-group-id={group.group_id}
              onClick={() => onSelectGroup(group.group_id)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  onSelectGroup(group.group_id);
                }
              }}
              title={
                group.gold_entity_label
                  ? `Entidade ${group.gold_entity_label} (${group.flagged_row_ids.length} flagrado(s))`
                  : `Grupo livre (${group.flagged_row_ids.length} flagrado(s))`
              }
            >
              {chunk}
            </span>
          );
        }
        if (r.nerLabel) {
          return (
            <span key={i} className={className} title={r.nerLabel}>
              {chunk}
            </span>
          );
        }
        return <span key={i}>{chunk}</span>;
      })}
    </div>
  );
}
