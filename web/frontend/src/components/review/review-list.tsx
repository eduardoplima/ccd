"use client";

import { useQueryClient } from "@tanstack/react-query";
import { ChevronDown, ChevronUp } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { reviewKeys } from "@/hooks/use-reviews";
import { messageForError } from "@/lib/error-messages";
import { formatProcesso } from "@/lib/format";
import { claimReview, rejectReview } from "@/lib/reviews-api";
import { ReviewKind, ReviewListItem } from "@/schemas/review";

function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleDateString("pt-BR");
}

type ReviewListProps = {
  items: ReviewListItem[];
  kind: ReviewKind;
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
  isLoading?: boolean;
};

export function ReviewList({
  items,
  kind,
  page,
  pageSize,
  total,
  onPageChange,
  isLoading,
}: ReviewListProps) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const queryClient = useQueryClient();

  const [expanded, setExpanded] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Clear selection when collapsing, changing page, or switching tab.
  useEffect(() => {
    if (!expanded) setSelectedIds(new Set());
  }, [expanded]);
  useEffect(() => {
    setSelectedIds(new Set());
  }, [page, kind]);

  const toggleSelected = (id: number) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const selectedSorted = Array.from(selectedIds).sort((a, b) => a - b);
  const keepId = selectedSorted[0];
  const rejectId = selectedSorted[1];

  async function confirmDuplicate() {
    if (keepId === undefined || rejectId === undefined) return;
    setSubmitting(true);
    try {
      await claimReview({ kind, id: rejectId });
      await rejectReview({ kind, id: rejectId }, `duplicado de #${keepId}`);
      toast.success(
        `Item #${rejectId} marcado como duplicado de #${keepId}.`,
      );
      setSelectedIds(new Set());
      setConfirmOpen(false);
      queryClient.invalidateQueries({ queryKey: reviewKeys.all });
    } catch (err) {
      toast.error(messageForError(err, "Erro ao marcar como duplicado."));
    } finally {
      setSubmitting(false);
    }
  }

  const colSpan = expanded ? 6 : 5;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setExpanded((v) => !v)}
        >
          {expanded ? (
            <>
              <ChevronUp className="mr-1 h-4 w-4" /> Recolher descrições
            </>
          ) : (
            <>
              <ChevronDown className="mr-1 h-4 w-4" /> Expandir descrições
            </>
          )}
        </Button>
        {expanded && selectedIds.size > 0 ? (
          <div className="flex items-center gap-3 text-sm">
            <span className="text-muted-foreground">
              {selectedIds.size} selecionado{selectedIds.size > 1 ? "s" : ""}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setSelectedIds(new Set())}
            >
              Limpar
            </Button>
            <Button
              variant="destructive"
              size="sm"
              disabled={selectedIds.size !== 2}
              onClick={() => setConfirmOpen(true)}
            >
              Marcar como duplicadas
            </Button>
          </div>
        ) : null}
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            {expanded ? <TableHead className="w-24">Duplicado?</TableHead> : null}
            <TableHead>Processo</TableHead>
            <TableHead>Descrição</TableHead>
            <TableHead>Reservado por</TableHead>
            <TableHead>Extraído em</TableHead>
            <TableHead className="w-0" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoading ? (
            <TableRow>
              <TableCell
                colSpan={colSpan}
                className="py-10 text-center text-sm text-muted-foreground"
              >
                Carregando...
              </TableCell>
            </TableRow>
          ) : items.length === 0 ? (
            <TableRow>
              <TableCell
                colSpan={colSpan}
                className="py-10 text-center text-sm text-muted-foreground"
              >
                Nenhum item pendente.
              </TableCell>
            </TableRow>
          ) : (
            items.map((item) => (
              <TableRow key={`${item.kind}-${item.id}`}>
                {expanded ? (
                  <TableCell>
                    <Checkbox
                      checked={selectedIds.has(item.id)}
                      onCheckedChange={() => toggleSelected(item.id)}
                      aria-label={`Selecionar item ${item.id} como duplicado`}
                    />
                  </TableCell>
                ) : null}
                <TableCell className="font-mono align-top">
                  {formatProcesso(
                    item.numero_processo,
                    item.ano_processo,
                    item.id_processo,
                  )}
                </TableCell>
                <TableCell
                  className={
                    expanded
                      ? "max-w-xl whitespace-pre-wrap break-words align-top"
                      : "max-w-xl truncate"
                  }
                  title={expanded ? undefined : item.descricao}
                >
                  {item.descricao}
                </TableCell>
                <TableCell className="align-top">
                  {item.claimed_by ? (
                    <Badge variant="secondary">{item.claimed_by}</Badge>
                  ) : (
                    <span className="text-muted-foreground">—</span>
                  )}
                </TableCell>
                <TableCell className="align-top">
                  {formatDate(item.reviewed_at)}
                </TableCell>
                <TableCell className="align-top">
                  <Link
                    href={`/cgad/reviews/${kind}/${item.id}`}
                    className={buttonVariants({
                      size: "sm",
                      variant: "outline",
                    })}
                  >
                    Revisar
                  </Link>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>

      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>
          Página {page} de {totalPages} · {total} itens
        </span>
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1 || isLoading}
          >
            Anterior
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages || isLoading}
          >
            Próxima
          </Button>
        </div>
      </div>

      <Dialog open={confirmOpen} onOpenChange={setConfirmOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirmar duplicidade</DialogTitle>
            <DialogDescription>
              Os dois itens selecionados são realmente duplicados?
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2 text-sm">
            <p>
              <strong>Manter:</strong> item #{keepId} (id menor)
            </p>
            <p>
              <strong>Rejeitar:</strong> item #{rejectId} — receberá a nota{" "}
              <span className="font-mono">duplicado de #{keepId}</span>.
            </p>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => setConfirmOpen(false)}
              disabled={submitting}
            >
              Cancelar
            </Button>
            <Button
              type="button"
              variant="destructive"
              onClick={confirmDuplicate}
              disabled={submitting}
            >
              {submitting ? "Marcando..." : "Confirmar"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
