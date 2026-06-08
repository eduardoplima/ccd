"use client";

import { useMemo, useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { SelectNative } from "@/components/ui/select-native";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useCurrentUser } from "@/hooks/use-current-user";
import {
  useCancelarJob,
  useDeletarFinalizados,
  useDeletarJob,
  useDispararConciliar,
  useDispararConciliarTodos,
  useDispararParse,
  useJobs,
  useUploadExtrato,
} from "@/hooks/use-jobs";
import { formatDate } from "@/lib/format";
import { CONTAS } from "@/schemas/lancamento";
import type { Job, JobStatus } from "@/schemas/job";

const SIZE = 50;

const STATUS_VARIANT: Record<JobStatus, "success" | "warning" | "destructive" | "outline"> = {
  pending: "outline",
  running: "warning",
  done: "success",
  failed: "destructive",
  cancelled: "outline",
};

const EM_ANDAMENTO: ReadonlySet<JobStatus> = new Set(["pending", "running"]);

export default function JobsPage() {
  const { data: me } = useCurrentUser();
  const [page, setPage] = useState(1);
  const [ano, setAno] = useState<number>(new Date().getFullYear());
  const [mes, setMes] = useState<number>(1);
  const [selecionado, setSelecionado] = useState<Job | null>(null);
  const [marcados, setMarcados] = useState<Set<number>>(new Set());

  const { data, isFetching } = useJobs(page, SIZE);
  const parse = useDispararParse();
  const conciliar = useDispararConciliar();
  const conciliarTodos = useDispararConciliarTodos();
  const upload = useUploadExtrato();
  const cancelar = useCancelarJob();
  const deletar = useDeletarJob();
  const limpar = useDeletarFinalizados();

  const isAdmin = me?.papel === "admin";
  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / SIZE));

  const jobsPagina = useMemo(() => data?.items ?? [], [data]);
  const idsPagina = useMemo(() => jobsPagina.map((j) => j.idJob), [jobsPagina]);
  const marcadosPagina = useMemo(
    () => idsPagina.filter((id) => marcados.has(id)),
    [idsPagina, marcados],
  );
  const marcadosJobs = useMemo(
    () => jobsPagina.filter((j) => marcados.has(j.idJob)),
    [jobsPagina, marcados],
  );
  const cabecalhoEstado: boolean | "indeterminate" =
    idsPagina.length > 0 && marcadosPagina.length === idsPagina.length
      ? true
      : marcadosPagina.length > 0
        ? "indeterminate"
        : false;
  const podeCancelar = marcadosJobs.filter((j) => EM_ANDAMENTO.has(j.status)).length;
  const podeExcluir = marcadosJobs.filter((j) => !EM_ANDAMENTO.has(j.status)).length;
  const ocupado = cancelar.isPending || deletar.isPending || limpar.isPending;

  function alternarMarcado(id: number, alvo: boolean) {
    setMarcados((prev) => {
      const next = new Set(prev);
      if (alvo) next.add(id);
      else next.delete(id);
      return next;
    });
  }

  function alternarTodos(alvo: boolean) {
    setMarcados((prev) => {
      const next = new Set(prev);
      if (alvo) idsPagina.forEach((id) => next.add(id));
      else idsPagina.forEach((id) => next.delete(id));
      return next;
    });
  }

  async function executarEmLote(
    jobs: Job[],
    fn: (id: number) => Promise<unknown>,
    rotuloAcao: string,
  ) {
    if (jobs.length === 0) return;
    if (!confirm(`${rotuloAcao} ${jobs.length} job(s)?`)) return;
    const resultados = await Promise.allSettled(jobs.map((j) => fn(j.idJob)));
    const ok = resultados.filter((r) => r.status === "fulfilled").length;
    const ko = resultados.length - ok;
    setMarcados((prev) => {
      const next = new Set(prev);
      jobs.forEach((j, i) => {
        if (resultados[i].status === "fulfilled") next.delete(j.idJob);
      });
      return next;
    });
    if (ko === 0) toast.success(`${ok} job(s) processados.`);
    else if (ok === 0) toast.error(`Falha em ${ko} job(s).`);
    else toast.warning(`${ok} ok, ${ko} com falha.`);
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="section-heading text-2xl">Extrações</h1>
      <p className="text-sm text-muted-foreground">
        Disparar parse e conciliação assincronamente. Os jobs rodam no worker ARQ (precisa do
        Redis). A tabela atualiza automaticamente a cada 5s.
      </p>

      {!isAdmin ? (
        <p className="text-sm text-destructive">Disparar jobs e upload requerem papel admin.</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Parse + Publicar</CardTitle>
              <CardDescription>
                Lê os <code>.txt</code> em <code>docs/extratos_frap/</code> e publica em
                <code> FRAPLancamento</code>.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                disabled={parse.isPending}
                onClick={async () => {
                  try {
                    await parse.mutateAsync();
                    toast.success("Parse enfileirado.");
                  } catch (err: unknown) {
                    toast.error(_msgErro(err));
                  }
                }}
              >
                {parse.isPending ? "Disparando..." : "Disparar parse"}
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Conciliar mês</CardTitle>
              <CardDescription>4 matchers + publicação em FRAPMatch*.</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-3">
              <div className="grid grid-cols-2 gap-2">
                <Input type="number" value={ano} onChange={(e) => setAno(Number(e.target.value))} />
                <SelectNative value={mes} onChange={(e) => setMes(Number(e.target.value))}>
                  {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
                    <option key={m} value={m}>
                      {String(m).padStart(2, "0")}
                    </option>
                  ))}
                </SelectNative>
              </div>
              <Button
                disabled={conciliar.isPending}
                onClick={async () => {
                  try {
                    await conciliar.mutateAsync({ ano, mes });
                    toast.success("Conciliação enfileirada.");
                  } catch (err: unknown) {
                    toast.error(_msgErro(err));
                  }
                }}
              >
                {conciliar.isPending ? "Disparando..." : "Conciliar"}
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Conciliar ano todo</CardTitle>
              <CardDescription>
                Enfileira 12 jobs (jan→dez) do ano em <code>FRAPJob</code>.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-3">
              <Input type="number" value={ano} onChange={(e) => setAno(Number(e.target.value))} />
              <Button
                variant="outline"
                disabled={conciliarTodos.isPending}
                onClick={async () => {
                  if (!confirm(`Disparar conciliação dos 12 meses de ${ano}?`)) return;
                  try {
                    const res = await conciliarTodos.mutateAsync(ano);
                    toast.success(`${res.jobs.length} jobs enfileirados.`);
                  } catch (err: unknown) {
                    toast.error(_msgErro(err));
                  }
                }}
              >
                {conciliarTodos.isPending ? "Enfileirando..." : `Conciliar ${ano} inteiro`}
              </Button>
            </CardContent>
          </Card>

          <UploadCard upload={upload} />
        </div>
      )}

      <Card>
        <CardHeader className="flex flex-row items-start justify-between gap-3">
          <div>
            <CardTitle className="text-base">Histórico</CardTitle>
            <CardDescription>
              {total.toLocaleString("pt-BR")} jobs · página {page} de {totalPages} ·{" "}
              {isFetching ? "atualizando" : "auto-refresh 5s"}
              {marcados.size > 0 ? <> · {marcados.size} selecionado(s)</> : null}
            </CardDescription>
          </div>
          {isAdmin ? (
            <div className="flex flex-wrap items-center gap-2">
              {marcados.size > 0 ? (
                <>
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={ocupado || podeCancelar === 0}
                    onClick={() =>
                      executarEmLote(
                        marcadosJobs.filter((j) => EM_ANDAMENTO.has(j.status)),
                        (id) => cancelar.mutateAsync(id),
                        "Cancelar",
                      )
                    }
                    title={
                      podeCancelar === 0
                        ? "Nenhum job em andamento na seleção"
                        : `${podeCancelar} em andamento`
                    }
                  >
                    Cancelar selecionados ({podeCancelar})
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={ocupado || podeExcluir === 0}
                    onClick={() =>
                      executarEmLote(
                        marcadosJobs.filter((j) => !EM_ANDAMENTO.has(j.status)),
                        async (id) => {
                          await deletar.mutateAsync(id);
                          if (selecionado?.idJob === id) setSelecionado(null);
                        },
                        "Excluir",
                      )
                    }
                    title={
                      podeExcluir === 0
                        ? "Nenhum job finalizado na seleção"
                        : `${podeExcluir} finalizado(s)`
                    }
                  >
                    Excluir selecionados ({podeExcluir})
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => setMarcados(new Set())}>
                    Limpar seleção
                  </Button>
                </>
              ) : null}
              <Button
                size="sm"
                variant="outline"
                disabled={limpar.isPending}
                onClick={async () => {
                  if (
                    !confirm(
                      "Excluir todos os jobs finalizados (done/failed/cancelled)? Os jobs em execução não são afetados.",
                    )
                  ) {
                    return;
                  }
                  try {
                    const r = await limpar.mutateAsync(undefined);
                    toast.success(`${r.deletados} jobs excluídos.`);
                  } catch (err: unknown) {
                    toast.error(_msgErro(err));
                  }
                }}
              >
                {limpar.isPending ? "Limpando..." : "Limpar histórico"}
              </Button>
            </div>
          ) : null}
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border">
            <Table>
              <TableHeader>
                <TableRow>
                  {isAdmin ? (
                    <TableHead className="w-8">
                      <Checkbox
                        aria-label="Selecionar todos da página"
                        checked={cabecalhoEstado}
                        onCheckedChange={(v) => alternarTodos(v === true)}
                        disabled={idsPagina.length === 0}
                      />
                    </TableHead>
                  ) : null}
                  <TableHead>Tipo</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Args</TableHead>
                  <TableHead>Criado</TableHead>
                  <TableHead>Iniciado</TableHead>
                  <TableHead>Fim</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data?.items.length === 0 && !isFetching ? (
                  <TableRow>
                    <TableCell
                      colSpan={isAdmin ? 8 : 7}
                      className="py-8 text-center text-muted-foreground"
                    >
                      Nenhum job ainda.
                    </TableCell>
                  </TableRow>
                ) : (
                  data?.items.map((j) => (
                    <TableRow
                      key={j.idJob}
                      data-state={marcados.has(j.idJob) ? "selected" : undefined}
                    >
                      {isAdmin ? (
                        <TableCell className="w-8">
                          <Checkbox
                            aria-label={`Selecionar job ${j.idJob}`}
                            checked={marcados.has(j.idJob)}
                            onCheckedChange={(v) => alternarMarcado(j.idJob, v === true)}
                          />
                        </TableCell>
                      ) : null}
                      <TableCell className="font-mono text-xs">{j.tipo}</TableCell>
                      <TableCell>
                        <Badge variant={STATUS_VARIANT[j.status]}>{j.status}</Badge>
                      </TableCell>
                      <TableCell className="font-mono text-xs">{j.argumentos ?? "—"}</TableCell>
                      <TableCell className="font-mono text-xs">{_dt(j.dataCriacao)}</TableCell>
                      <TableCell className="font-mono text-xs">{_dt(j.dataInicio)}</TableCell>
                      <TableCell className="font-mono text-xs">{_dt(j.dataFim)}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-1">
                          <Button size="sm" variant="outline" onClick={() => setSelecionado(j)}>
                            Logs
                          </Button>
                          {isAdmin && EM_ANDAMENTO.has(j.status) ? (
                            <Button
                              size="sm"
                              variant="outline"
                              disabled={cancelar.isPending}
                              onClick={async () => {
                                if (!confirm(`Cancelar job #${j.idJob} (${j.tipo})?`)) return;
                                try {
                                  await cancelar.mutateAsync(j.idJob);
                                  toast.success("Cancelado.");
                                } catch (err: unknown) {
                                  toast.error(_msgErro(err));
                                }
                              }}
                            >
                              Cancelar
                            </Button>
                          ) : null}
                          {isAdmin && !EM_ANDAMENTO.has(j.status) ? (
                            <Button
                              size="sm"
                              variant="outline"
                              disabled={deletar.isPending}
                              onClick={async () => {
                                if (!confirm(`Excluir job #${j.idJob} (${j.tipo})?`)) return;
                                try {
                                  await deletar.mutateAsync(j.idJob);
                                  if (selecionado?.idJob === j.idJob) setSelecionado(null);
                                  toast.success("Excluído.");
                                } catch (err: unknown) {
                                  toast.error(_msgErro(err));
                                }
                              }}
                            >
                              Excluir
                            </Button>
                          ) : null}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
          <div className="mt-3 flex items-center justify-end gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page <= 1 || isFetching}
              onClick={() => setPage(Math.max(1, page - 1))}
            >
              Anterior
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= totalPages || isFetching}
              onClick={() => setPage(page + 1)}
            >
              Próxima
            </Button>
          </div>
        </CardContent>
      </Card>

      {selecionado ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              Logs · {selecionado.tipo} #{selecionado.idJob}
            </CardTitle>
            <CardDescription>{selecionado.arqJobId}</CardDescription>
          </CardHeader>
          <CardContent>
            {selecionado.erroMensagem ? (
              <pre className="mb-3 max-h-72 overflow-auto rounded border border-destructive/50 bg-destructive/10 p-3 text-xs">
                {selecionado.erroMensagem}
              </pre>
            ) : null}
            <pre className="max-h-96 overflow-auto rounded border bg-muted p-3 text-xs">
              {selecionado.resultado ?? "(sem saída)"}
            </pre>
            <Button
              className="mt-3"
              variant="outline"
              size="sm"
              onClick={() => setSelecionado(null)}
            >
              Fechar
            </Button>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}

function UploadCard({ upload }: { upload: ReturnType<typeof useUploadExtrato> }) {
  const [conta, setConta] = useState<string>(CONTAS[0]);
  const [periodo, setPeriodo] = useState("");
  const [arquivo, setArquivo] = useState<File | null>(null);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Upload de extrato</CardTitle>
        <CardDescription>
          Envia o <code>.txt</code> para <code>docs/extratos_frap/&lt;conta&gt;/</code>.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <div className="grid grid-cols-2 gap-2">
          <SelectNative value={conta} onChange={(e) => setConta(e.target.value)}>
            {CONTAS.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </SelectNative>
          <Input
            placeholder="Período MMAAAA"
            value={periodo}
            maxLength={6}
            onChange={(e) => setPeriodo(e.target.value)}
          />
        </div>
        <Input
          type="file"
          accept=".txt"
          onChange={(e) => setArquivo(e.target.files?.[0] ?? null)}
        />
        <Button
          disabled={upload.isPending || !arquivo || !/^\d{6}$/.test(periodo)}
          onClick={async () => {
            if (!arquivo) return;
            try {
              const r = await upload.mutateAsync({ conta, periodo, arquivo });
              toast.success(`Salvo em ${r.caminho}`);
              setArquivo(null);
            } catch (err: unknown) {
              toast.error(_msgErro(err));
            }
          }}
        >
          {upload.isPending ? "Enviando..." : "Enviar"}
        </Button>
      </CardContent>
    </Card>
  );
}

function _msgErro(err: unknown): string {
  const status = (err as { response?: { status?: number } })?.response?.status;
  if (status === 503) return "Worker indisponível (REDIS_URL não configurado).";
  if (status === 409) return "Job em estado incompatível com a operação.";
  if (status === 404) return "Job não encontrado.";
  if (status === 403) return "Operação restrita a admin.";
  if (status === 401) return "Sessão expirada.";
  return "Falha ao executar.";
}

function _dt(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return `${formatDate(iso.split("T")[0])} ${d.toTimeString().slice(0, 8)}`;
}
