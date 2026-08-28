"use client";

import { Button } from "@/components/ui/button";

export function Paginacao({
  page,
  totalPages,
  setPage,
  disabled,
}: {
  page: number;
  totalPages: number;
  setPage: (p: number) => void;
  disabled?: boolean;
}) {
  return (
    <div className="flex items-center justify-end gap-2">
      <Button
        variant="outline"
        size="sm"
        disabled={page <= 1 || disabled}
        onClick={() => setPage(Math.max(1, page - 1))}
      >
        Anterior
      </Button>
      <Button
        variant="outline"
        size="sm"
        disabled={page >= totalPages || disabled}
        onClick={() => setPage(page + 1)}
      >
        Próxima
      </Button>
    </div>
  );
}
