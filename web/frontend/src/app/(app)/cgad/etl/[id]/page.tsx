"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useCurrentUser } from "@/hooks/use-current-user";
import {
  useDecisoesExtracao,
  useExtracao,
  useExtracaoEventos,
} from "@/hooks/use-etl";
import {
  DecisaoExtraidaItem,
  DecisaoItemRow,
  ExtracaoEventoOut,
  ExtracaoOut,
  RunStatus,
} from "@/schemas/etl";

const PAGE_SIZE = 20;

function formatDate(iso: string): string {
  const [y, m, d] = iso.split("-");
  if (!y || !m || !d) return iso;
  return `${d}/${m}/${y}`;
}

function formatDateTime(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

const STATUS_LABEL: Record<RunStatus, string> = {
  queued: "na fila",
  running: "em andamento",
  done: "concluída",
  error: "erro",
};

const STATUS_TONE: Record<RunStatus, string> = {
  queued: "bg-muted text-muted-foreground",
  running: "bg-blue-500/15 text-blue-700 dark:text-blue-300",
  done: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300",
  error: "bg-red-500/15 text-red-700 dark:text-red-300",
};

function StatusBadge({ status }: { status: RunStatus }) {
  return (
    <span
      className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_TONE[status]}`}
    >
      {STATUS_LABEL[status]}
    </span>
  );
}

const ITEM_STATUS_LABEL: Record<DecisaoItemRow["status"], string> = {
  pending: "pendente",
  approved: "aprovado",
  rejected: "rejeitado",
};

const ITEM_STATUS_TONE: Record<DecisaoItemRow["status"], string> = {
  pending: "bg-amber-500/15 text-amber-700 dark:text-amber-300",
  approved: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300",
  rejected: "bg-red-500/15 text-red-700 dark:text-red-300",
};

function ItemStatusBadge({ status }: { status: DecisaoItemRow["status"] }) {
  return (
    <span
      className={`rounded px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide ${ITEM_STATUS_TONE[status]}`}
    >
      {ITEM_STATUS_LABEL[status]}
    </span>
  );
}

export default function ExtracaoDetailPage() {
  const router = useRouter();
  const params = useParams<{ id: string }>();
  const id = Number(params.id);
  const idValid = Number.isFinite(id) && id > 0;

  const { data: me, isLoading: meLoading } = useCurrentUser();
  useEffect(() => {
    if (!meLoading && me && me.papel !== "admin") {
      router.replace("/cgad/reviews");
    }
  }, [me, meLoading, router]);

  useEffect(() => {
    if (!idValid) router.replace("/cgad/etl");
  }, [idValid, router]);

  if (!idValid || !me || me.papel !== "admin") return null;

  return <Detail id={id} />;
}

function Detail({ id }: { id: number }) {
  const router = useRouter();
  const { data: extracao, isLoading } = useExtracao(id);
  const { events } = useExtracaoEventos(id, extracao?.status);

  if (isLoading || !extracao) {
    return (
      <main className="mx-auto flex w-full max-w-screen-2xl flex-col gap-4 p-6">
        <p className="text-sm text-muted-foreground">Carregando extração...</p>
      </main>
    );
  }

  return (
    <main className="mx-auto flex w-full max-w-screen-2xl flex-col gap-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Extração #{extracao.id}</h1>
          <p className="text-sm text-muted-foreground">
            Período {formatDate(extracao.data_inicio)} a{" "}
            {formatDate(extracao.data_fim)} · disparada em{" "}
            {formatDateTime(extracao.data_execucao)}
          </p>
        </div>
        <Button variant="outline" onClick={() => router.push("/cgad/etl")}>
          Voltar
        </Button>
      </div>

      <Summary extracao={extracao} />

      <Card>
        <CardHeader>
          <CardTitle>Atividade ao vivo</CardTitle>
          <CardDescription>
            {extracao.status === "queued" || extracao.status === "running"
              ? "Atualizando a cada 1,5s enquanto a extração está em execução."
              : "Histórico completo dos eventos desta extração."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ActivityFeed events={events} />
        </CardContent>
      </Card>

      <DecisoesPanel id={id} />
    </main>
  );
}

function Summary({ extracao }: { extracao: ExtracaoOut }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Resumo</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
          <Stat label="Status">
            <StatusBadge status={extracao.status} />
          </Stat>
          <Stat label="Etapa atual" value={extracao.etapa_atual} />
          <Stat
            label="Decisões processadas"
            value={extracao.decisoes_processadas}
          />
          <Stat
            label="Obrigações geradas"
            value={extracao.obrigacoes_geradas}
          />
          <Stat
            label="Recomendações geradas"
            value={extracao.recomendacoes_geradas}
          />
        </div>
        {extracao.status === "error" && extracao.mensagem_erro ? (
          <p className="mt-4 rounded border border-red-500/30 bg-red-500/5 p-3 text-sm text-red-700 dark:text-red-300">
            {extracao.mensagem_erro}
          </p>
        ) : null}
      </CardContent>
    </Card>
  );
}

function Stat({
  label,
  value,
  children,
}: {
  label: string;
  value?: string | number;
  children?: React.ReactNode;
}) {
  return (
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-base font-medium">
        {children ?? (value !== undefined ? value : "—")}
      </p>
    </div>
  );
}

function ActivityFeed({ events }: { events: ExtracaoEventoOut[] }) {
  // Newest at the top — feed reads top-to-bottom, but most recent first.
  const ordered = useMemo(() => [...events].reverse(), [events]);

  if (ordered.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        Aguardando eventos. Eles aparecem aqui assim que a extração começar a
        processar decisões.
      </p>
    );
  }

  return (
    <ol className="max-h-96 space-y-2 overflow-y-auto pr-2">
      {ordered.map((e) => (
        <li
          key={e.id}
          className="flex items-start gap-3 rounded border bg-background/50 p-2 text-sm"
        >
          <span className="shrink-0 font-mono text-xs text-muted-foreground">
            {formatDateTime(e.timestamp)}
          </span>
          <span className="flex-1">{describeEvent(e)}</span>
        </li>
      ))}
    </ol>
  );
}

function describeEvent(e: ExtracaoEventoOut): React.ReactNode {
  const p = (e.payload ?? {}) as Record<string, unknown>;
  switch (e.tipo) {
    case "stage_started":
      return (
        <span>
          <Badge variant="outline" className="mr-2">
            etapa
          </Badge>
          Iniciando <strong>{String(p.stage ?? "?")}</strong>.
        </span>
      );
    case "stage_progress":
      return (
        <span>
          Total a processar nesta etapa: <strong>{Number(p.total ?? 0)}</strong>{" "}
          decisões.
        </span>
      );
    case "stage_done":
      return (
        <span>
          <Badge variant="outline" className="mr-2">
            etapa concluída
          </Badge>
          <strong>{String(p.stage ?? "?")}</strong>
          {" — "}
          {Object.entries(p)
            .filter(([k]) => k !== "stage")
            .map(([k, v]) => `${k}=${String(v)}`)
            .join(" · ")}
        </span>
      );
    case "decision_done":
      return (
        <span>
          Decisão {String(p.id_processo ?? "?")}/
          {String(p.id_voto_pauta ?? "?")} processada (
          <strong>
            {Number(p.processed ?? 0)}/{Number(p.total ?? 0)}
          </strong>
          )
        </span>
      );
    case "obrigacao_extracted":
      return (
        <span>
          Obrigação extraída — id {String(p.id_obrigacao ?? "?")} (processo{" "}
          {String(p.id_processo ?? "?")})
        </span>
      );
    case "recomendacao_extracted":
      return (
        <span>
          Recomendação extraída — id {String(p.id_recomendacao ?? "?")}{" "}
          (processo {String(p.id_processo ?? "?")})
        </span>
      );
    case "obrigacao_skipped":
    case "recomendacao_skipped":
      return (
        <span className="text-muted-foreground">
          {e.tipo.replace("_", " ")} — já processado em execução anterior
        </span>
      );
    case "error":
      return (
        <span className="text-red-700 dark:text-red-300">
          Erro: {String(p.message ?? "sem mensagem")}
        </span>
      );
    default:
      return <span className="text-muted-foreground">{e.tipo}</span>;
  }
}

function DecisoesPanel({ id }: { id: number }) {
  const [page, setPage] = useState(1);
  const { data, isLoading } = useDecisoesExtracao(id, {
    page,
    pageSize: PAGE_SIZE,
  });
  const [activeTab, setActiveTab] = useState<"obrigacoes" | "recomendacoes">(
    "obrigacoes",
  );

  const total = data?.total ?? 0;
  const items = data?.items ?? [];
  const lastPage = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Decisões extraídas</CardTitle>
        <CardDescription>
          NERDecisões geradas por esta extração e os itens
          (obrigações/recomendações) que delas saíram. Clique em um item para
          abri-lo na fila de revisão.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Tabs
          value={activeTab}
          onValueChange={(v) => setActiveTab(v as typeof activeTab)}
        >
          <TabsList>
            <TabsTrigger value="obrigacoes">Obrigações</TabsTrigger>
            <TabsTrigger value="recomendacoes">Recomendações</TabsTrigger>
          </TabsList>
        </Tabs>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Decisão</TableHead>
              <TableHead>Itens</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && items.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={2}
                  className="text-center text-muted-foreground"
                >
                  Carregando...
                </TableCell>
              </TableRow>
            ) : items.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={2}
                  className="text-center text-muted-foreground"
                >
                  Esta extração ainda não emitiu decisões com vínculo (ou foi
                  disparada antes do tracking de RunId).
                </TableCell>
              </TableRow>
            ) : (
              items.map((decisao) => (
                <DecisaoRow
                  key={decisao.id_ner_decisao}
                  decisao={decisao}
                  kind={activeTab}
                />
              ))
            )}
          </TableBody>
        </Table>

        {total > PAGE_SIZE ? (
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>
              Página {page} de {lastPage} — {total} decisões
            </span>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                Anterior
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={page >= lastPage}
                onClick={() => setPage((p) => Math.min(lastPage, p + 1))}
              >
                Próxima
              </Button>
            </div>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}

function DecisaoRow({
  decisao,
  kind,
}: {
  decisao: DecisaoExtraidaItem;
  kind: "obrigacoes" | "recomendacoes";
}) {
  const items =
    kind === "obrigacoes" ? decisao.obrigacoes : decisao.recomendacoes;
  const reviewKind = kind === "obrigacoes" ? "obrigacao" : "recomendacao";

  return (
    <TableRow>
      <TableCell className="align-top">
        <div className="font-medium">
          Processo {decisao.id_processo}/{decisao.id_voto_pauta}
        </div>
        <div className="text-xs text-muted-foreground">
          Pauta {decisao.id_composicao_pauta}/{decisao.id_voto_pauta} · NER #
          {decisao.id_ner_decisao}
        </div>
      </TableCell>
      <TableCell>
        {items.length === 0 ? (
          <span className="text-xs text-muted-foreground">
            Nenhuma {kind === "obrigacoes" ? "obrigação" : "recomendação"}{" "}
            gerada.
          </span>
        ) : (
          <ul className="space-y-1">
            {items.map((item) => (
              <li key={item.id} className="flex items-start gap-2 text-sm">
                <ItemStatusBadge status={item.status} />
                <Link
                  href={`/cgad/reviews/${reviewKind}/${item.id}`}
                  className="flex-1 hover:underline"
                  title={item.descricao}
                >
                  {item.descricao.length > 160
                    ? `${item.descricao.slice(0, 157)}…`
                    : item.descricao}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </TableCell>
    </TableRow>
  );
}
