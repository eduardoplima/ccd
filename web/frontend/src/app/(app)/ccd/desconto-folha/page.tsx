"use client";

import { useMemo, useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { useCcdJob } from "@/hooks/use-ccd-job";
import { useCandidatosDescontoFolha, useGerarDescontoFolha } from "@/hooks/use-ccd-desconto-folha";
import { downloadCcdArtefato } from "@/lib/api/ccd-jobs";
import type { JobStatus } from "@/schemas/job";

const PROCESSO_RE = /^\d{1,6}\/\d{4}$/;

const STATUS_VARIANT: Record<JobStatus, "success" | "warning" | "destructive" | "outline"> = {
  pending: "outline",
  running: "warning",
  done: "success",
  failed: "destructive",
  cancelled: "outline",
};

const STATUS_LABEL: Record<JobStatus, string> = {
  pending: "Na fila...",
  running: "Gerando documentos...",
  done: "Concluído",
  failed: "Falhou",
  cancelled: "Cancelado",
};

function parseTextarea(texto: string): string[] {
  return texto
    .split(/[\n,;]+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

export default function DescontoFolhaPage() {
  const [todos, setTodos] = useState(false);
  const [marcados, setMarcados] = useState<Set<string>>(new Set());
  const [textoLivre, setTextoLivre] = useState("");
  const [idJob, setIdJob] = useState<number | null>(null);
  const [jaBaixou, setJaBaixou] = useState(false);

  const { data, isFetching, isError, error } = useCandidatosDescontoFolha(todos);
  const gerar = useGerarDescontoFolha();
  const { data: job } = useCcdJob(idJob);

  const candidatos = useMemo(() => data?.items ?? [], [data]);
  const processosPagina = useMemo(() => candidatos.map((c) => c.processo), [candidatos]);

  const marcadosNaPagina = useMemo(
    () => processosPagina.filter((p) => marcados.has(p)),
    [processosPagina, marcados],
  );
  const cabecalhoEstado: boolean | "indeterminate" =
    processosPagina.length > 0 && marcadosNaPagina.length === processosPagina.length
      ? true
      : marcadosNaPagina.length > 0
        ? "indeterminate"
        : false;

  const doTexto = useMemo(() => parseTextarea(textoLivre), [textoLivre]);
  const textoInvalidos = useMemo(() => doTexto.filter((p) => !PROCESSO_RE.test(p)), [doTexto]);
  const finais = useMemo(() => {
    const set = new Set<string>(marcados);
    doTexto.forEach((p) => {
      if (PROCESSO_RE.test(p)) set.add(p);
    });
    return Array.from(set);
  }, [marcados, doTexto]);

  function alternarMarcado(processo: string, alvo: boolean) {
    setMarcados((prev) => {
      const next = new Set(prev);
      if (alvo) next.add(processo);
      else next.delete(processo);
      return next;
    });
  }

  function alternarTodos(alvo: boolean) {
    setMarcados((prev) => {
      const next = new Set(prev);
      if (alvo) processosPagina.forEach((p) => next.add(p));
      else processosPagina.forEach((p) => next.delete(p));
      return next;
    });
  }

  async function onGerar() {
    if (finais.length === 0) {
      toast.error("Selecione ou informe ao menos um processo.");
      return;
    }
    if (textoInvalidos.length > 0) {
      toast.error(`Formato inválido (use numero/ano): ${textoInvalidos.join(", ")}`);
      return;
    }
    try {
      const novoJob = await gerar.mutateAsync(finais);
      setIdJob(novoJob.idJob);
      setJaBaixou(false);
      toast.success(`Geração enfileirada para ${finais.length} processo(s).`);
    } catch (err: unknown) {
      toast.error(_msgErro(err));
    }
  }

  async function baixar() {
    if (idJob == null) return;
    try {
      await downloadCcdArtefato(idJob);
      setJaBaixou(true);
    } catch {
      toast.error("Falha ao baixar o artefato.");
    }
  }

  // Dispara o download automaticamente uma vez quando o job conclui.
  if (job?.status === "done" && idJob != null && !jaBaixou) {
    setJaBaixou(true);
    void downloadCcdArtefato(idJob).catch(() => toast.error("Falha ao baixar o artefato."));
  }

  const gerando = gerar.isPending;
  const emAndamento = job != null && (job.status === "pending" || job.status === "running");

  return (
    <div className="flex flex-col gap-6">
      <h1 className="section-heading text-2xl">Desconto em Folha</h1>
      <p className="text-sm text-muted-foreground">
        Selecione os processos e gere um despacho por processo. A geração roda no worker (precisa do
        Redis) e devolve um PDF (1 processo) ou um ZIP de PDFs (vários).
      </p>

      <Card>
        <CardHeader className="flex flex-row items-start justify-between gap-3">
          <div>
            <CardTitle className="text-base">Candidatos</CardTitle>
            <CardDescription>
              {isFetching
                ? "Carregando..."
                : `${candidatos.length.toLocaleString("pt-BR")} processo(s) · ${marcados.size} selecionado(s)`}
            </CardDescription>
          </div>
          <label className="flex items-center gap-2 text-sm">
            <Checkbox
              checked={todos}
              onCheckedChange={(v) => setTodos(v === true)}
              aria-label="Ampliar para todos os processos da CCD"
            />
            Ampliar para todos os processos da CCD
          </label>
        </CardHeader>
        <CardContent>
          {isError ? (
            <p className="mb-3 text-sm text-destructive">
              Erro ao carregar: {(error as Error).message}
            </p>
          ) : null}
          <div className="rounded-lg border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-8">
                    <Checkbox
                      aria-label="Selecionar todos"
                      checked={cabecalhoEstado}
                      onCheckedChange={(v) => alternarTodos(v === true)}
                      disabled={processosPagina.length === 0}
                    />
                  </TableHead>
                  <TableHead>Processo</TableHead>
                  <TableHead>Assunto</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {candidatos.length === 0 && !isFetching ? (
                  <TableRow>
                    <TableCell colSpan={3} className="py-8 text-center text-muted-foreground">
                      Nenhum processo candidato.
                    </TableCell>
                  </TableRow>
                ) : (
                  candidatos.map((c) => (
                    <TableRow
                      key={c.processo}
                      data-state={marcados.has(c.processo) ? "selected" : undefined}
                    >
                      <TableCell className="w-8">
                        <Checkbox
                          aria-label={`Selecionar ${c.processo}`}
                          checked={marcados.has(c.processo)}
                          onCheckedChange={(v) => alternarMarcado(c.processo, v === true)}
                        />
                      </TableCell>
                      <TableCell className="whitespace-nowrap font-mono text-xs font-medium">
                        {c.processo}
                      </TableCell>
                      <TableCell className="max-w-[480px] truncate" title={c.assunto ?? ""}>
                        {c.assunto ?? "—"}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Processos avulsos</CardTitle>
          <CardDescription>
            Opcional. Informe processos no formato <code>numero/ano</code> separados por vírgula ou
            quebra de linha. São combinados (sem duplicar) com os marcados acima.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="texto-processos">Processos</Label>
            <Textarea
              id="texto-processos"
              placeholder="001425/2022, 001424/2022&#10;001423/2022"
              value={textoLivre}
              onChange={(e) => setTextoLivre(e.target.value)}
              rows={3}
            />
          </div>
          {textoInvalidos.length > 0 ? (
            <p className="text-sm text-destructive">
              Formato inválido: {textoInvalidos.join(", ")}
            </p>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Geração</CardTitle>
          <CardDescription>
            {finais.length.toLocaleString("pt-BR")} processo(s) na lista final.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <div className="flex items-center gap-3">
            <Button disabled={gerando || finais.length === 0} onClick={onGerar}>
              {gerando ? "Enfileirando..." : "Gerar"}
            </Button>
            {job ? (
              <Badge variant={STATUS_VARIANT[job.status]}>{STATUS_LABEL[job.status]}</Badge>
            ) : null}
            {emAndamento ? (
              <span className="text-sm text-muted-foreground">Acompanhando o job #{idJob}...</span>
            ) : null}
          </div>

          {job?.status === "done" ? (
            <div className="flex items-center gap-3">
              <Button variant="outline" onClick={baixar}>
                Baixar
              </Button>
              <span className="text-sm text-muted-foreground">{job.resultado ?? ""}</span>
            </div>
          ) : null}

          {job?.status === "failed" ? (
            <pre className="max-h-72 overflow-auto rounded border border-destructive/50 bg-destructive/10 p-3 text-xs">
              {job.erroMensagem ?? "Falha na geração."}
            </pre>
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
}

function _msgErro(err: unknown): string {
  const status = (err as { response?: { status?: number } })?.response?.status;
  if (status === 503) return "Worker indisponível (Redis não configurado).";
  if (status === 422) return "Lista de processos inválida.";
  if (status === 401) return "Sessão expirada.";
  return "Falha ao enfileirar a geração.";
}
