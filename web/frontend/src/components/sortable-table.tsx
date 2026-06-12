"use client";

import { useMemo, useState } from "react";

import { TableHead } from "@/components/ui/table";

export type SortDir = "asc" | "desc";

export interface SortState<K extends string> {
  key: K | null;
  dir: SortDir;
}

export function useClientSort<T, K extends string>(
  items: readonly T[],
  getters: Record<K, (item: T) => string | number | null | undefined>,
  initial: SortState<K> = { key: null, dir: "asc" },
): { sorted: T[]; sort: SortState<K>; toggle: (key: K) => void } {
  const [sort, setSort] = useState<SortState<K>>(initial);

  function toggle(key: K) {
    setSort((prev) => {
      if (prev.key !== key) return { key, dir: "asc" };
      if (prev.dir === "asc") return { key, dir: "desc" };
      return { key: null, dir: "asc" };
    });
  }

  const sorted = useMemo(() => {
    if (sort.key === null) return [...items];
    const getter = getters[sort.key];
    const mult = sort.dir === "asc" ? 1 : -1;
    return [...items].sort((a, b) => {
      const va = getter(a);
      const vb = getter(b);
      // null/undefined sempre no fim
      if (va == null && vb == null) return 0;
      if (va == null) return 1;
      if (vb == null) return -1;
      if (typeof va === "number" && typeof vb === "number") return (va - vb) * mult;
      return String(va).localeCompare(String(vb), "pt-BR", { numeric: true }) * mult;
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [items, sort]);

  return { sorted, sort, toggle };
}

export function SortableHead<K extends string>({
  label,
  col,
  sort,
  onClick,
  align,
}: {
  label: string;
  col: K;
  sort: SortState<K>;
  onClick: (col: K) => void;
  align?: "right";
}) {
  const active = sort.key === col;
  const arrow = active ? (sort.dir === "asc" ? "↑" : "↓") : "↕";
  return (
    <TableHead
      onClick={() => onClick(col)}
      className={`cursor-pointer select-none ${align === "right" ? "text-right" : ""}`}
    >
      <span className="inline-flex items-center gap-1">
        {label}
        <span className={active ? "text-foreground" : "text-muted-foreground/40"}>{arrow}</span>
      </span>
    </TableHead>
  );
}
