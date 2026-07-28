"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { toast } from "sonner";

import { ClaimBanner } from "@/components/review/claim-banner";
import { CanvasSpan, DecisionCanvas } from "@/components/review/decision-canvas";
import { EntityDraft, EntityPanel } from "@/components/review/entity-panel";
import { Button } from "@/components/ui/button";
import { useCurrentUser } from "@/hooks/use-current-user";
import {
  useApproveDecisao,
  useClaim,
  useDecisao,
  useDecisaoTexto,
  useRelease,
} from "@/hooks/use-reviews";
import { messageForError } from "@/lib/error-messages";
import { formatAcordao, formatProcesso } from "@/lib/format";
import {
  DecisaoDetail,
  DecisaoReviewPayload,
  DecisaoTexto,
  EntidadeReview,
  TIPO_LABEL,
  TipoEntidade,
  fieldsSchemaByTipo,
} from "@/schemas/review";

export default function DecisaoReviewPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const id = Number(params.id);
  const idValid = Number.isFinite(id) && id > 0;

  useEffect(() => {
    if (!idValid) router.replace("/cgad/reviews");
  }, [idValid, router]);

  if (!idValid) return null;

  return <Detail id={id} />;
}

function draftKey(tipo: TipoEntidade, idNer: number): string {
  return `${tipo}-${idNer}`;
}

function initDrafts(detail: DecisaoDetail): EntityDraft[] {
  return detail.entidades.map((e) => ({
    key: draftKey(e.tipo, e.id_ner),
    tipo: e.tipo,
    idNer: e.id_ner,
    serverStatus: e.status,
    reviewer: e.reviewer,
    serverObservacoes: e.observacoes,
    descricao: e.descricao,
    spanMissing: false,
    rejected: false,
    motivo: "",
    campos: { ...e.campos },
  }));
}

function descricaoOf(draft: EntityDraft): string {
  const field = `descricao_${draft.tipo}`;
  const value = draft.campos[field];
  return typeof value === "string" ? value : "";
}

function Detail({ id }: { id: number }) {
  const router = useRouter();
  const { data: me } = useCurrentUser();
  const query = useDecisao(id);
  const textoQuery = useDecisaoTexto(id);
  const claim = useClaim(id);
  const release = useRelease(id);
  const approve = useApproveDecisao(id);

  const [drafts, setDrafts] = useState<EntityDraft[] | null>(null);
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const newCounter = useRef(0);

  const detail = query.data;
  const texto = textoQuery.data ?? null;

  // Claim on mount, release on unmount + tab close.
  useEffect(() => {
    claim.mutate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    return () => {
      // Best-effort release. sendBeacon can't set the JWT header, so we
      // just fire the mutation; the backend's 15-min TTL covers missed
      // releases.
      release.mutate();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (detail && drafts === null) setDrafts(initDrafts(detail));
  }, [detail, drafts]);

  if (query.isError) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 p-10">
        <p className="text-sm">
          {messageForError(query.error, "Não foi possível carregar a decisão.")}
        </p>
        <Button variant="outline" onClick={() => router.push("/cgad/reviews")}>
          Voltar para a lista
        </Button>
      </div>
    );
  }

  if (query.isLoading || !detail || drafts === null) {
    return (
      <div className="flex flex-1 items-center justify-center p-10 text-sm text-muted-foreground">
        Carregando decisão...
      </div>
    );
  }

  const holdsClaim = !!detail.claimed_by && !!me && detail.claimed_by === me.login;
  const formDisabled = !holdsClaim || !!detail.revisado_por;

  function updateDraft(key: string, patch: Partial<EntityDraft>) {
    setDrafts((prev) => prev!.map((d) => (d.key === key ? { ...d, ...patch } : d)));
  }

  function updateCampos(key: string, patch: Record<string, unknown>) {
    setDrafts((prev) =>
      prev!.map((d) => (d.key === key ? { ...d, campos: { ...d.campos, ...patch } } : d)),
    );
  }

  function removeDraft(key: string) {
    setDrafts((prev) => prev!.filter((d) => d.key !== key));
    if (selectedKey === key) setSelectedKey(null);
  }

  function addEntity(tipo: TipoEntidade, trecho: string) {
    newCounter.current += 1;
    const key = `new-${tipo}-${newCounter.current}`;
    const draft: EntityDraft = {
      key,
      tipo,
      idNer: null,
      serverStatus: "pending",
      descricao: trecho,
      spanMissing: false,
      rejected: false,
      motivo: "",
      campos: { [`descricao_${tipo}`]: trecho },
    };
    setDrafts((prev) => [...(prev ?? []), draft]);
    selectCard(key);
  }

  function selectCard(key: string) {
    setSelectedKey(key);
    // O card pode ainda não estar montado (entidade recém-adicionada).
    setTimeout(() => {
      document
        .getElementById(`entity-card-${key}`)
        ?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }, 50);
  }

  function handleApprove() {
    const pendentes = drafts!.filter((d) => d.serverStatus === "pending");
    const entidades: EntidadeReview[] = [];

    for (const draft of pendentes) {
      const label = `${TIPO_LABEL[draft.tipo]}${draft.idNer !== null ? ` #${draft.idNer}` : " (nova)"}`;
      if (draft.rejected) {
        if (draft.motivo.trim().length < 10) {
          selectCard(draft.key);
          toast.error(`${label}: informe o motivo da rejeição (mínimo 10 caracteres).`);
          return;
        }
        entidades.push({
          tipo: draft.tipo,
          id_ner: draft.idNer,
          resultado: "rejected",
          observacoes: draft.motivo.trim(),
        });
        continue;
      }
      const parsed = fieldsSchemaByTipo[draft.tipo].safeParse(draft.campos);
      if (!parsed.success) {
        selectCard(draft.key);
        const issue = parsed.error.issues[0];
        toast.error(`${label}: ${issue?.message ?? "campos inválidos."}`);
        return;
      }
      entidades.push({
        tipo: draft.tipo,
        id_ner: draft.idNer,
        resultado: "approved",
        campos: { ...parsed.data, tipo: draft.tipo },
      });
    }

    const payload: DecisaoReviewPayload = { entidades };
    approve.mutate(payload, {
      onSuccess: () => {
        toast.success("Decisão aprovada.");
        router.replace("/cgad/reviews");
      },
      onError: (err) => toast.error(messageForError(err, "Erro ao aprovar a decisão.")),
    });
  }

  return (
    <DecisaoBody
      detail={detail}
      texto={texto}
      textoLoading={textoQuery.isLoading}
      drafts={drafts}
      selectedKey={selectedKey}
      onSelect={selectCard}
      onUpdate={updateDraft}
      onUpdateCampos={updateCampos}
      onRemove={removeDraft}
      onAddEntity={addEntity}
      formDisabled={formDisabled}
      currentUsername={me?.login ?? null}
      onApprove={handleApprove}
      approveSubmitting={approve.isPending}
      onReclaim={() =>
        claim.mutate(undefined, {
          onError: (err) => toast.error(messageForError(err, "Não foi possível reservar.")),
        })
      }
      reclaimSubmitting={claim.isPending}
      onBackToList={() => router.push("/cgad/reviews")}
    />
  );
}

type DecisaoBodyProps = {
  detail: DecisaoDetail;
  texto: DecisaoTexto | null;
  textoLoading: boolean;
  drafts: EntityDraft[];
  selectedKey: string | null;
  onSelect: (key: string) => void;
  onUpdate: (key: string, patch: Partial<EntityDraft>) => void;
  onUpdateCampos: (key: string, patch: Record<string, unknown>) => void;
  onRemove: (key: string) => void;
  onAddEntity: (tipo: TipoEntidade, trecho: string) => void;
  formDisabled: boolean;
  currentUsername: string | null;
  onApprove: () => void;
  approveSubmitting: boolean;
  onReclaim: () => void;
  reclaimSubmitting: boolean;
  onBackToList: () => void;
};

function DecisaoBody({
  detail,
  texto,
  textoLoading,
  drafts,
  selectedKey,
  onSelect,
  onUpdate,
  onUpdateCampos,
  onRemove,
  onAddEntity,
  formDisabled,
  currentUsername,
  onApprove,
  approveSubmitting,
  onReclaim,
  reclaimSubmitting,
  onBackToList,
}: DecisaoBodyProps) {
  const textoAcordao = texto?.texto_acordao ?? "";

  const notFoundKeys = useMemo(
    () =>
      new Set(
        (texto?.spans ?? [])
          .filter((s) => s.match_status === "not_found")
          .map((s) => draftKey(s.tipo, s.id_ner)),
      ),
    [texto],
  );

  const canvasSpans = useMemo<CanvasSpan[]>(() => {
    if (!textoAcordao) return [];
    const byKey = new Map(drafts.map((d) => [d.key, d]));
    const spans: CanvasSpan[] = [];
    for (const s of texto?.spans ?? []) {
      if (s.char_start == null || s.char_end == null) continue;
      const key = draftKey(s.tipo, s.id_ner);
      const draft = byKey.get(key);
      spans.push({
        key,
        tipo: s.tipo,
        charStart: s.char_start,
        charEnd: s.char_end,
        rejected: draft ? draft.rejected || draft.serverStatus === "rejected" : false,
      });
    }
    // Entidades adicionadas pelo revisor: o destaque é derivado no cliente
    // por indexOf (primeira ocorrência), como no SpanEditor antigo.
    for (const draft of drafts) {
      if (draft.idNer !== null) continue;
      const descricao = descricaoOf(draft);
      if (!descricao) continue;
      const idx = textoAcordao.indexOf(descricao);
      if (idx === -1) continue;
      spans.push({
        key: draft.key,
        tipo: draft.tipo,
        charStart: idx,
        charEnd: idx + descricao.length,
        rejected: false,
      });
    }
    return spans;
  }, [drafts, texto, textoAcordao]);

  const draftsComSpan = useMemo(
    () => drafts.map((d) => ({ ...d, spanMissing: notFoundKeys.has(d.key) })),
    [drafts, notFoundKeys],
  );

  return (
    <main className="mx-auto flex w-full max-w-screen-2xl flex-col gap-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">
            {texto?.numero_acordao
              ? formatAcordao(texto.numero_acordao, texto.ano_acordao, texto.tipo_acordao)
              : "Decisão"}{" "}
            · Processo{" "}
            {formatProcesso(texto?.numero_processo, texto?.ano_processo, detail.id_processo)}
          </h1>
          <p className="text-xs text-muted-foreground">
            Decisão #{detail.id} · Pauta {detail.id_composicao_pauta}/{detail.id_voto_pauta} ·{" "}
            {drafts.length} entidade{drafts.length === 1 ? "" : "s"}
          </p>
        </div>
        <Button variant="outline" onClick={onBackToList}>
          Voltar
        </Button>
      </div>

      <ClaimBanner
        currentUsername={currentUsername}
        claimedBy={detail.claimed_by ?? null}
        claimedAt={detail.claimed_at ?? null}
        onReclaim={onReclaim}
        onBack={onBackToList}
        isReclaiming={reclaimSubmitting}
      />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div>
          <h2 className="mb-2 text-sm font-medium">
            Texto do acórdão
            <span className="ml-2 font-normal text-muted-foreground">
              (selecione um trecho para adicionar uma entidade)
            </span>
          </h2>
          {textoLoading && !texto ? (
            <div className="rounded-md border bg-muted/30 p-4 text-sm text-muted-foreground">
              Carregando texto do acórdão...
            </div>
          ) : !textoAcordao ? (
            <div className="rounded-md border bg-muted/30 p-4 text-sm text-muted-foreground">
              Texto do acórdão indisponível.
            </div>
          ) : (
            <DecisionCanvas
              text={textoAcordao}
              spans={canvasSpans}
              selectedKey={selectedKey}
              onSelect={onSelect}
              onAddEntity={onAddEntity}
              disabled={formDisabled}
            />
          )}
        </div>

        <div>
          <h2 className="mb-2 text-sm font-medium">Entidades</h2>
          <EntityPanel
            drafts={draftsComSpan}
            pessoas={texto?.pessoas ?? []}
            selectedKey={selectedKey}
            onSelect={onSelect}
            onUpdate={onUpdate}
            onUpdateCampos={onUpdateCampos}
            onRemove={onRemove}
            disabled={formDisabled}
          />

          <div className="mt-4 flex justify-end border-t pt-4">
            <Button
              onClick={onApprove}
              disabled={formDisabled || approveSubmitting}
              data-testid="approve-decisao-button"
            >
              {approveSubmitting ? "Aprovando..." : "Aprovar decisão"}
            </Button>
          </div>
        </div>
      </div>

      <section>
        <h2 className="mb-2 text-sm font-medium">Informações Adicionais</h2>
        {textoLoading && !texto ? (
          <div className="rounded-md border bg-muted/30 p-4 text-sm text-muted-foreground">
            Carregando informações adicionais...
          </div>
        ) : (
          <div className="divide-y rounded-md border">
            <AccordionItem title="Voto">
              <LabeledText label="Relatório" value={texto?.relatorio} />
              <LabeledText label="Fundamentação" value={texto?.fundamentacao_voto} />
              <LabeledText label="Conclusão" value={texto?.conclusao} />
              {!texto?.relatorio && !texto?.fundamentacao_voto && !texto?.conclusao && (
                <p className="text-sm text-muted-foreground">Indisponível.</p>
              )}
            </AccordionItem>
            <AccordionItem title="Pessoas">
              {texto?.pessoas.length ? (
                <ul className="space-y-1 text-sm">
                  {texto.pessoas.map((p) => (
                    <li key={`${p.documento ?? p.nome}`}>
                      {p.nome}
                      {p.documento ? (
                        <span className="text-muted-foreground"> · {p.documento}</span>
                      ) : null}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-muted-foreground">Indisponível.</p>
              )}
            </AccordionItem>
            <AccordionItem title="Órgãos">
              <LabeledText label="Órgão envolvido" value={texto?.orgao_responsavel} />
              <LabeledText label="Órgão de origem" value={texto?.orgao_origem} />
              <LabeledText label="Interessado" value={texto?.interessado} />
              {!texto?.orgao_responsavel && !texto?.orgao_origem && !texto?.interessado && (
                <p className="text-sm text-muted-foreground">Indisponível.</p>
              )}
            </AccordionItem>
          </div>
        )}
      </section>
    </main>
  );
}

function AccordionItem({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <details className="group">
      <summary className="flex cursor-pointer items-center justify-between p-4 text-sm font-medium hover:bg-muted/30">
        {title}
        <span className="text-muted-foreground transition-transform group-open:rotate-180">▾</span>
      </summary>
      <div className="space-y-3 px-4 pb-4">{children}</div>
    </details>
  );
}

function LabeledText({ label, value }: { label: string; value: string | null | undefined }) {
  if (!value) return null;
  return (
    <div>
      <p className="text-xs font-medium text-muted-foreground">{label}</p>
      <p className="whitespace-pre-wrap text-sm">{value}</p>
    </div>
  );
}
