"use client";

import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useMemo } from "react";
import { toast } from "sonner";

import { ConfidenceFilter } from "@/components/dataset-corrections/confidence-filter";
import { GroupDecisionBar } from "@/components/dataset-corrections/decision-bar";
import { DocumentCanvas } from "@/components/dataset-corrections/document-canvas";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  useDocumentDetail,
  useDocuments,
} from "@/hooks/use-dataset-corrections";
import { useMinConfidence } from "@/hooks/use-min-confidence";
import { EntityGroup } from "@/schemas/dataset-corrections";

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

export default function DocumentReviewPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const docId = Number(params?.docId);
  const { fraction: minConfidence, percentage } = useMinConfidence();

  const detail = useDocumentDetail(docId, { minConfidence });
  const docList = useDocuments({
    page: 1,
    pageSize: 1000,
    onlyPending: false,
    minConfidence,
  });

  const groups = useMemo(
    () => detail.data?.groups ?? [],
    [detail.data?.groups],
  );

  const selectedGroupId = (() => {
    const raw = searchParams.get("group");
    if (raw == null) return groups[0]?.group_id ?? null;
    return groups.find((g) => g.group_id === raw)?.group_id
      ?? groups[0]?.group_id
      ?? null;
  })();
  const selected =
    groups.find((g) => g.group_id === selectedGroupId) ?? null;
  const selectedIndex = selected
    ? groups.findIndex((g) => g.group_id === selected.group_id)
    : -1;

  const setSelectedGroup = useCallback(
    (groupId: string | null) => {
      const sp = new URLSearchParams(searchParams.toString());
      if (groupId == null) sp.delete("group");
      else sp.set("group", groupId);
      router.replace(`?${sp.toString()}`, { scroll: false });
    },
    [router, searchParams],
  );

  const onMoveNext = useCallback(() => {
    if (groups.length === 0) return;
    const next = (selectedIndex + 1 + groups.length) % groups.length;
    setSelectedGroup(groups[next].group_id);
  }, [groups, selectedIndex, setSelectedGroup]);

  const onMovePrev = useCallback(() => {
    if (groups.length === 0) return;
    const prev = (selectedIndex - 1 + groups.length) % groups.length;
    setSelectedGroup(groups[prev].group_id);
  }, [groups, selectedIndex, setSelectedGroup]);

  const adjacentDocs = useMemo(() => {
    if (!docList.data) return { prev: null as number | null, next: null as number | null };
    const ids = docList.data.items.map((x) => x.document_id);
    const idx = ids.indexOf(docId);
    return {
      prev: idx > 0 ? ids[idx - 1] : null,
      next: idx >= 0 && idx < ids.length - 1 ? ids[idx + 1] : null,
    };
  }, [docList.data, docId]);

  // For auto-advance after deciding everything in this doc: jump to the
  // next document that still has pending entities. Walks forward from the
  // current position and wraps to the start of the list, so the user
  // doesn't get "all done" prematurely just because the current doc sits
  // at the tail of the (id-sorted) list.
  const nextPendingDocId = useMemo(() => {
    if (!docList.data) return null;
    const items = docList.data.items;
    if (items.length === 0) return null;
    const startIdx = Math.max(0, items.findIndex((d) => d.document_id === docId));
    for (let offset = 1; offset <= items.length; offset++) {
      const target = items[(startIdx + offset) % items.length];
      if (target.document_id === docId) continue;
      if (target.decided_group_count < target.group_count) {
        return target.document_id;
      }
    }
    return null;
  }, [docList.data, docId]);

  const backToListHref = useMemo(() => {
    const sp = new URLSearchParams(searchParams.toString());
    sp.delete("group");
    const qs = sp.toString();
    return qs ? `/cgad/admin/cleanlab-review?${qs}` : "/cgad/admin/cleanlab-review";
  }, [searchParams]);

  const goToDoc = useCallback(
    (targetDoc: number | null) => {
      if (targetDoc == null) return;
      const sp = new URLSearchParams(searchParams.toString());
      sp.delete("group");
      const qs = sp.toString();
      router.push(
        qs
          ? `/cgad/admin/cleanlab-review/documents/${targetDoc}?${qs}`
          : `/cgad/admin/cleanlab-review/documents/${targetDoc}`,
      );
    },
    [router, searchParams],
  );

  const onAfterDecide = useCallback(
    (decidedGroupId: string) => {
      // ``groups`` reflects state before the refetch, so the just-decided
      // group still appears as pending. Manually exclude it from the
      // pending count.
      const remainingPending = groups.filter(
        (g) => g.status === "pending" && g.group_id !== decidedGroupId,
      );
      if (remainingPending.length === 0) {
        if (nextPendingDocId != null) {
          goToDoc(nextPendingDocId);
          toast.success("Documento concluído. Indo para o próximo.");
        } else {
          toast.success("Nada mais pendente neste filtro.");
        }
        return;
      }
      // Otherwise: prefer the next pending group after the current; fall
      // back to the first pending group if we're past the last one.
      const decidedIdx = groups.findIndex(
        (g) => g.group_id === decidedGroupId,
      );
      const after = groups
        .slice(decidedIdx + 1)
        .find((g) => g.status === "pending");
      const target = after ?? remainingPending[0];
      setSelectedGroup(target.group_id);
    },
    [groups, nextPendingDocId, goToDoc, setSelectedGroup],
  );

  if (detail.isLoading) {
    return (
      <main className="mx-auto w-full max-w-screen-2xl p-6 text-sm text-muted-foreground">
        Carregando documento…
      </main>
    );
  }
  if (detail.isError || !detail.data) {
    return (
      <main className="mx-auto w-full max-w-screen-2xl p-6 text-sm text-muted-foreground">
        Documento não encontrado.
        <div className="mt-4">
          <Link href={backToListHref} className="underline">
            Voltar à lista
          </Link>
        </div>
      </main>
    );
  }

  const decidedCount = groups.filter((g) => g.status !== "pending").length;

  return (
    <main className="mx-auto flex w-full max-w-screen-2xl flex-col gap-4 p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <Link
            href={backToListHref}
            className="text-xs text-muted-foreground hover:underline"
          >
            ← Voltar
          </Link>
          <h1 className="mt-1 text-xl font-semibold">
            Documento {detail.data.document_id}
          </h1>
          <p className="text-xs text-muted-foreground">
            {decidedCount} / {groups.length} entidades decididas neste documento
            {percentage > 0 ? ` · confiança ≥ ${percentage}%` : null}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={adjacentDocs.prev == null}
            onClick={() => goToDoc(adjacentDocs.prev)}
            title="Atalho: H"
          >
            ← Doc anterior
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={adjacentDocs.next == null}
            onClick={() => goToDoc(adjacentDocs.next)}
            title="Atalho: L"
          >
            Doc próximo →
          </Button>
        </div>
      </div>

      <ConfidenceFilter />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_420px]">
        <DocumentCanvas
          text={detail.data.text}
          nerSpans={detail.data.ner_spans}
          groups={groups}
          selectedGroupId={selectedGroupId}
          onSelectGroup={setSelectedGroup}
        />
        <div className="flex flex-col gap-4">
          <GroupDecisionBar
            group={selected}
            documentId={docId}
            docTokens={detail.data.tokens}
            onMoveNext={onMoveNext}
            onMovePrev={onMovePrev}
            onAfterDecide={onAfterDecide}
          />

          <div className="rounded-md border bg-white p-4">
            <div className="mb-2 text-xs uppercase tracking-wide text-muted-foreground">
              Outras entidades neste documento
            </div>
            <ul className="flex flex-col gap-1.5 text-sm">
              {groups.map((g) => {
                const isSel = g.group_id === selectedGroupId;
                const summary =
                  g.gold_entity_label ?? "(livre)";
                return (
                  <li key={g.group_id}>
                    <button
                      type="button"
                      onClick={() => setSelectedGroup(g.group_id)}
                      className={`flex w-full items-center justify-between gap-2 rounded px-2 py-1 text-left ${
                        isSel ? "bg-muted" : "hover:bg-muted/50"
                      }`}
                    >
                      <span className="truncate">
                        <span className="font-mono text-xs">{summary}</span>
                        <span className="ml-2 text-xs text-muted-foreground">
                          {g.tokens.length} tokens · {g.flagged_row_ids.length}{" "}
                          flagrado(s)
                        </span>
                      </span>
                      {g.status !== "pending" ? (
                        <Badge variant={statusBadgeVariant(g.status)}>
                          ✓
                        </Badge>
                      ) : null}
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      </div>
    </main>
  );
}
