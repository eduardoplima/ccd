"use client";

import { useMemo, useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
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
import {
  useCandidatosAntecedentes,
  useGerarAntecedentes,
} from "@/hooks/use-ccd-antecedentes";
import { downloadCcdArtefato } from "@/lib/api/ccd-jobs";

const PROCESSO_RE = /^\d{1,6}\/\d{4}$/;

function parseProcessosTexto(texto: string): string[] {
  return texto
    .split(/[\s,;]+/)
    .map((p) => p.trim())
    .filter((p) => p.length > 0);
}

export default function AntecedentesPage() {
  const [todos, setTodos] = useState(false);
  const [marcados, setMarcados] = useState<Set<string>>(new Set());
  const [texto, setTexto] = useState("");
  const [idJob, setIdJob] = useState<number | null>(null);
  const [baixado, setBaixado] = useState(false);

  const { data, isFetching, isError, error } = useCandidatosAntecedentes(todos);
  const gerar = useGerarAntecedentes();
  const { data: job } = useCcdJob(idJob);

  const candidatos = useMemo(() => data?.items ?? [], [data]);
  const idsPagina = useMemo(() => candidatos.map((c) => c.processo), [candidatos]);
  const marcadosPagina = useMemo(
    () => idsPagina.filter((id) => marcados.has(id)),
    [idsPagina, marcados],
  );
  const cabecalhoEstado: boolean | "indeterminate" =
    idsPagina.length > 0 && marcadosPagina.length === idsPagina.length
      ? true
      : marcadosPagina.length > 0
        ? "indeterminate"
        : false;

  const processosFinais = useMemo(() => {
    const set = new Set<string>(marcados);
    for (const p of parseProcessosTexto(texto)) set.add(p);
    return Array.from(set);
  }, [marcados, texto]);

  const invalidos = useMemo(
    () => processosFinais.filter((p) => !PROCESSO_RE.test(p)),
    [processosFinais],
  );

  function alternarMarcado(id: string, alvo: boolean) {
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

  async function onGerar() {
    if (processosFinais.length === 0) {
      toast.error("Selecione ou informe ao menos um processo.");
      return;
    }
    if (invalidos.length > 0) {
      toast.error(`Processo(s) em formato inválido: ${invalidos.join(", ")}`);
      return;
    }
    try {
      const novoJob = await gerar.mutateAsync(processosFinais);
      setIdJob(novoJob.idJob);
      setBaixado(false);
      toast.success("Geração enfileirada. Acompanhe o andamento abaixo.");
    } catch (err: unknown) {
      toast.error(msgErro(err));
    }
  }

  async function onBaixar() {
    if (idJob == null) return;
    try {
      await downloadCcdArtefato(idJob);
      setBaixado(true);
    } catch {
      toast.error("Falha ao baixar o documento.");
    }
  }

  const status = job?.status;
  const emAndamento = status === "pending" || status === "running";

  return (
    <div className="flex flex-col gap-6">
      <h1 className="section-heading text-2xl">Antecedentes</h1>
      <p className="text-sm text-muted-foreground">
        Gera o despacho de antecedentes de cada processo selecionado. O servidor lê o último
        despacho no share de PDFs e usa um LLM para identificar os responsáveis — pode demorar
        alguns minutos. A geração roda no worker ARQ e o resultado é um PDF (1 processo) ou um
        ZIP (vários).
      </p>

      <div className="flex items-center gap-2">
        <Checkbox
          id="todos"
          checked={todos}
          onCheckedChange={(v) => {
            setTodos(v === true);
            setMarcados(new Set());
          }}
        />
        <Label htmlFor="todos">Ampliar para todos os processos da CCD</Label>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Processos candidatos</CardTitle>
          <CardDescription>
            {isFetching
              ? "Carregando..."
              : `${(data?.total ?? 0).toLocaleString("pt-BR")} processo(s)`}
            {marcadosPagina.length > 0 ? ` · ${marcadosPagina.length} selecionado(s)` : null}
          </CardDescription>
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
                      disabled={idsPagina.length === 0}
                    />
                  </TableHead>
                  <TableHead>Processo</TableHead>
                  <TableHead>Interessado</TableHead>
                  <TableHead>Assunto</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {candidatos.length === 0 && !isFetching ? (
                  <TableRow>
                    <TableCell colSpan={4} className="py-8 text-center text-muted-foreground">
                      Nenhum processo encontrado.
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
                      <TableCell className="max-w-[260px] truncate" title={c.interessado ?? ""}>
                        {c.interessado ?? "—"}
                      </TableCell>
                      <TableCell className="max-w-[320px] truncate" title={c.assunto ?? ""}>
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

      <div className="flex flex-col gap-1.5">
        <Label htmlFor="texto-processos">Processos avulsos (numero/ano)</Label>
        <Textarea
          id="texto-processos"
          placeholder="Ex.: 000519/2021, 002667/2025"
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          rows={3}
        />
        <p className="text-xs text-muted-foreground">
          Separe por vírgula, espaço ou quebra de linha. São combinados (sem duplicar) com os
          processos marcados na tabela.
        </p>
      </div>

      <div className="flex items-center gap-3">
        <Button onClick={onGerar} disabled={gerar.isPending || processosFinais.length === 0}>
          {gerar.isPending
            ? "Enfileirando..."
            : `Gerar (${processosFinais.length} processo(s))`}
        </Button>
        {invalidos.length > 0 ? (
          <span className="text-xs text-destructive">
            Formato inválido: {invalidos.join(", ")}
          </span>
        ) : null}
      </div>

      {idJob != null ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Andamento da geração · #{idJob}</CardTitle>
            <CardDescription>
              {status ? (
                <Badge
                  variant={
                    status === "done"
                      ? "success"
                      : status === "failed"
                        ? "destructive"
                        : status === "cancelled"
                          ? "outline"
                          : "warning"
                  }
                >
                  {status}
                </Badge>
              ) : (
                "carregando status..."
              )}
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            {emAndamento ? (
              <p className="text-sm text-muted-foreground">
                Gerando documentos... a página atualiza automaticamente.
              </p>
            ) : null}
            {status === "done" ? (
              <div className="flex items-center gap-3">
                <Button onClick={onBaixar}>{baixado ? "Baixar novamente" : "Baixar"}</Button>
                {job?.resultado ? (
                  <span className="text-sm text-muted-foreground">{job.resultado}</span>
                ) : null}
              </div>
            ) : null}
            {status === "failed" ? (
              <pre className="max-h-72 overflow-auto rounded border border-destructive/50 bg-destructive/10 p-3 text-xs">
                {job?.erroMensagem ?? "Falha na geração."}
              </pre>
            ) : null}
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}

function msgErro(err: unknown): string {
  const status = (err as { response?: { status?: number } })?.response?.status;
  if (status === 503) return "Worker indisponível (Redis não configurado).";
  if (status === 422) return "Há processos em formato inválido.";
  if (status === 401) return "Sessão expirada.";
  return "Falha ao enfileirar a geração.";
}
