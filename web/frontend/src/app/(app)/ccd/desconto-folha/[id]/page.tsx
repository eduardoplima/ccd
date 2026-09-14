"use client";

import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useCcdJob } from "@/hooks/use-ccd-job";
import { useCurrentUser } from "@/hooks/use-current-user";
import {
  useAtualizarProcesso,
  useCadastro,
  useCriarValor,
  useDesvincular,
  useExtrairResposta,
  useMatchAutomatico,
  useRemoverCadastro,
  useRemoverValor,
  useVincular,
} from "@/hooks/use-desconto-folha";
import { messageForError } from "@/lib/error-messages";
import { formatCurrencyBRL } from "@/lib/format";
import type { Lancamento, Valor } from "@/schemas/desconto-folha";

import { STATUS_EXTRACAO, formatData } from "../_shared";

const JOB_LABEL: Record<string, string> = {
  pending: "Na fila...",
  running: "Lendo os PDFs e consultando a LLM...",
  done: "Extração concluída",
  failed: "Extração falhou",
  cancelled: "Cancelada",
};

export default function DescontoFolhaDetalhePage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const id = Number(params.id);
  const { data: me } = useCurrentUser();
  const isAdmin = me?.papel === "admin";

  const {
    data: c,
    isLoading,
    isError,
    error,
    refetch,
  } = useCadastro(Number.isFinite(id) ? id : null);
  const extrair = useExtrairResposta();
  const atualizarProcesso = useAtualizarProcesso();
  const remover = useRemoverCadastro();
  const matchAuto = useMatchAutomatico(id);
  const [idJob, setIdJob] = useState<number | null>(null);
  const { data: job } = useCcdJob(idJob);

  const jobAtivo = job != null && (job.status === "pending" || job.status === "running");
  // Quando o job termina, recarrega o cadastro uma vez.
  const [jobVisto, setJobVisto] = useState<number | null>(null);
  if (job && !jobAtivo && idJob != null && jobVisto !== idJob) {
    setJobVisto(idJob);
    void refetch();
    if (job.status === "done") toast.success(job.resultado ?? "Extração concluída.");
    if (job.status === "failed") toast.error(job.erroMensagem ?? "Extração falhou.");
  }

  if (isError) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 p-10">
        <p className="text-sm">{messageForError(error, "Não foi possível carregar o cadastro.")}</p>
        <Button variant="outline" onClick={() => router.push("/ccd/desconto-folha")}>
          Voltar
        </Button>
      </div>
    );
  }
  if (isLoading || !c) {
    return (
      <div className="flex flex-1 items-center justify-center p-10 text-sm text-muted-foreground">
        Carregando...
      </div>
    );
  }

  const st = STATUS_EXTRACAO[c.statusExtracao];

  return (
    <main className="mx-auto flex w-full max-w-screen-2xl flex-col gap-4 p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">
            Processo <span className="font-mono">{c.processo}</span>
          </h1>
          <p className="text-sm text-muted-foreground">
            {c.orgao ?? "Órgão não informado"} · {c.responsavel ?? "responsável não informado"}
            {c.idDebito != null ? ` · débito #${c.idDebito}` : " · sem débito vinculado"}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" onClick={() => router.push("/ccd/desconto-folha")}>
            Voltar
          </Button>
          {isAdmin && (
            <Button
              variant="outline"
              disabled={atualizarProcesso.isPending}
              onClick={() =>
                atualizarProcesso.mutate(c.id, {
                  onSuccess: () => toast.success("Dados do processo atualizados."),
                  onError: (err) => toast.error(messageForError(err, "Erro ao atualizar.")),
                })
              }
            >
              Reconsultar processo
            </Button>
          )}
          {isAdmin && (
            <Button
              disabled={extrair.isPending || jobAtivo}
              onClick={() =>
                extrair.mutate(c.id, {
                  onSuccess: (j) => setIdJob(j.idJob),
                  onError: (err) =>
                    toast.error(messageForError(err, "Erro ao enfileirar a extração.")),
                })
              }
            >
              {jobAtivo ? JOB_LABEL[job!.status] : "Extrair resposta"}
            </Button>
          )}
          {isAdmin && (
            <Button
              variant="ghost"
              className="text-destructive"
              disabled={remover.isPending}
              onClick={() => {
                if (!window.confirm("Remover este cadastro?")) return;
                remover.mutate(c.id, {
                  onSuccess: () => router.push("/ccd/desconto-folha"),
                  onError: (err) => toast.error(messageForError(err, "Erro ao remover.")),
                });
              }}
            >
              Remover
            </Button>
          )}
        </div>
      </div>

      <section className="grid grid-cols-1 gap-3 md:grid-cols-3">
        <Info titulo="Notificação">
          {c.notificacao.numero ?? "—"}
          <div className="text-xs text-muted-foreground">{formatData(c.notificacao.data)}</div>
        </Info>
        <Info titulo="AR">
          {c.ar.numeroPostagem ?? "não rastreável no banco"}
          <div className="text-xs text-muted-foreground">{formatData(c.ar.data)}</div>
        </Info>
        <Info titulo="Resposta (apensado)">
          {c.resposta.processo ? (
            <>
              <span className="font-mono">{c.resposta.processo}</span>
              {c.resposta.evento != null && ` · Ev. ${c.resposta.evento}`}
              <div className="text-xs text-muted-foreground">
                {formatData(c.resposta.data)}
                {c.arquivoResposta ? ` · ${c.arquivoResposta}` : ""}
              </div>
            </>
          ) : (
            "nenhum apensado"
          )}
        </Info>
      </section>

      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-center gap-2">
            <CardTitle className="text-base">Resposta do órgão</CardTitle>
            <Badge variant={st.variant}>{st.label}</Badge>
            {c.dataExtracao && (
              <span className="text-xs text-muted-foreground">
                extraída em {formatData(c.dataExtracao)}
              </span>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          {c.trechoResposta ? (
            <blockquote className="whitespace-pre-wrap rounded-md border-l-4 border-primary bg-muted/40 p-3">
              {c.trechoResposta}
            </blockquote>
          ) : (
            <p className="text-muted-foreground">
              Nenhum trecho extraído ainda. Use &ldquo;Extrair resposta&rdquo; ou informe os valores
              manualmente.
            </p>
          )}
          {c.valorTotal != null && (
            <p>
              Valor total: <strong>{formatCurrencyBRL(c.valorTotal)}</strong>
              {c.parcelado ? " (parcelado)" : " (único)"}
            </p>
          )}
          {c.observacoes && <p className="text-xs text-muted-foreground">{c.observacoes}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-center justify-between gap-2">
            <CardTitle className="text-base">Valores e matches com o FRAP</CardTitle>
            <Button
              size="sm"
              variant="outline"
              disabled={matchAuto.isPending || c.valores.length === 0}
              onClick={() =>
                matchAuto.mutate(undefined, {
                  onSuccess: (n) =>
                    toast.success(
                      n === 1 ? "1 valor vinculado." : `${n} valores vinculados automaticamente.`,
                    ),
                  onError: (err) => toast.error(messageForError(err, "Erro no match.")),
                })
              }
            >
              Buscar matches
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <ValoresTable id={c.id} valores={c.valores} isAdmin={isAdmin} />
          {isAdmin && <NovoValorForm id={c.id} />}
        </CardContent>
      </Card>
    </main>
  );
}

function Info({ titulo, children }: { titulo: string; children: React.ReactNode }) {
  return (
    <div className="rounded-md border p-3 text-sm">
      <div className="text-xs font-medium uppercase text-muted-foreground">{titulo}</div>
      <div className="mt-1">{children}</div>
    </div>
  );
}

function competencia(v: Valor): string {
  return v.mes && v.ano ? `${String(v.mes).padStart(2, "0")}/${v.ano}` : "—";
}

function LancamentoResumo({ l }: { l: Lancamento }) {
  return (
    <span>
      {formatData(l.dtMovimento)} · {formatCurrencyBRL(l.valor)}
      <span className="ml-1 text-xs text-muted-foreground">
        {l.historico ?? ""} {l.documento ? `· doc. ${l.documento}` : ""}
      </span>
    </span>
  );
}

function ValoresTable({
  id,
  valores,
  isAdmin,
}: {
  id: number;
  valores: Valor[];
  isAdmin: boolean;
}) {
  const vincular = useVincular(id);
  const desvincular = useDesvincular(id);
  const removerValor = useRemoverValor(id);

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Parcela</TableHead>
          <TableHead>Competência</TableHead>
          <TableHead>Valor</TableHead>
          <TableHead>Origem</TableHead>
          <TableHead>Match FRAP</TableHead>
          <TableHead className="w-0" />
        </TableRow>
      </TableHeader>
      <TableBody>
        {valores.length === 0 ? (
          <TableRow>
            <TableCell colSpan={6} className="py-8 text-center text-sm text-muted-foreground">
              Nenhum valor. Extraia a resposta ou informe um valor manualmente.
            </TableCell>
          </TableRow>
        ) : (
          valores.map((v) => (
            <TableRow key={v.idValor}>
              <TableCell>{v.numeroParcela}</TableCell>
              <TableCell>{competencia(v)}</TableCell>
              <TableCell className="font-medium">{formatCurrencyBRL(v.valor)}</TableCell>
              <TableCell>
                <Badge variant="outline">{v.origem === "L" ? "LLM" : "Manual"}</Badge>
              </TableCell>
              <TableCell className="text-sm">
                {v.match ? (
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant="success">{v.match.automatico ? "Automático" : "Manual"}</Badge>
                    <LancamentoResumo l={v.match.lancamento} />
                    {isAdmin && (
                      <Button
                        size="sm"
                        variant="ghost"
                        disabled={desvincular.isPending}
                        onClick={() =>
                          desvincular.mutate(v.idValor, {
                            onError: (err) =>
                              toast.error(messageForError(err, "Erro ao desvincular.")),
                          })
                        }
                      >
                        Desvincular
                      </Button>
                    )}
                  </div>
                ) : v.candidatos.length === 0 ? (
                  <span className="text-muted-foreground">
                    Nenhum crédito com esse valor no FRAP.
                  </span>
                ) : (
                  <ul className="space-y-1">
                    {v.candidatos.map((l) => (
                      <li key={l.idLancamento} className="flex flex-wrap items-center gap-2">
                        <LancamentoResumo l={l} />
                        <Button
                          size="sm"
                          variant="outline"
                          disabled={vincular.isPending}
                          onClick={() =>
                            vincular.mutate(
                              { idValor: v.idValor, idLancamento: l.idLancamento },
                              {
                                onError: (err) =>
                                  toast.error(messageForError(err, "Erro ao vincular.")),
                              },
                            )
                          }
                        >
                          Vincular
                        </Button>
                      </li>
                    ))}
                  </ul>
                )}
              </TableCell>
              <TableCell>
                {isAdmin && (
                  <Button
                    size="sm"
                    variant="ghost"
                    className="text-destructive"
                    disabled={removerValor.isPending}
                    onClick={() =>
                      removerValor.mutate(v.idValor, {
                        onError: (err) => toast.error(messageForError(err, "Erro ao remover.")),
                      })
                    }
                  >
                    Remover
                  </Button>
                )}
              </TableCell>
            </TableRow>
          ))
        )}
      </TableBody>
    </Table>
  );
}

function NovoValorForm({ id }: { id: number }) {
  const criar = useCriarValor(id);
  const [parcela, setParcela] = useState("1");
  const [mes, setMes] = useState("");
  const [ano, setAno] = useState("");
  const [valor, setValor] = useState("");

  return (
    <form
      className="flex flex-wrap items-end gap-2 border-t pt-3"
      onSubmit={(e) => {
        e.preventDefault();
        const v = Number(valor.replace(/\./g, "").replace(",", "."));
        if (!Number.isFinite(v) || v <= 0) {
          toast.error("Informe um valor válido.");
          return;
        }
        criar.mutate(
          {
            numeroParcela: Number(parcela) || 1,
            mes: mes ? Number(mes) : null,
            ano: ano ? Number(ano) : null,
            valor: v,
          },
          {
            onSuccess: () => {
              setValor("");
              toast.success("Valor incluído.");
            },
            onError: (err) => toast.error(messageForError(err, "Erro ao incluir o valor.")),
          },
        );
      }}
    >
      <div className="flex flex-col gap-1">
        <Label htmlFor="v-parcela" className="text-xs">
          Parcela
        </Label>
        <Input
          id="v-parcela"
          className="w-20"
          value={parcela}
          onChange={(e) => setParcela(e.target.value)}
        />
      </div>
      <div className="flex flex-col gap-1">
        <Label htmlFor="v-mes" className="text-xs">
          Mês
        </Label>
        <Input
          id="v-mes"
          className="w-16"
          placeholder="05"
          value={mes}
          onChange={(e) => setMes(e.target.value)}
        />
      </div>
      <div className="flex flex-col gap-1">
        <Label htmlFor="v-ano" className="text-xs">
          Ano
        </Label>
        <Input
          id="v-ano"
          className="w-20"
          placeholder="2025"
          value={ano}
          onChange={(e) => setAno(e.target.value)}
        />
      </div>
      <div className="flex flex-col gap-1">
        <Label htmlFor="v-valor" className="text-xs">
          Valor (R$)
        </Label>
        <Input
          id="v-valor"
          className="w-32"
          placeholder="2.477,35"
          value={valor}
          onChange={(e) => setValor(e.target.value)}
        />
      </div>
      <Button type="submit" size="sm" variant="outline" disabled={criar.isPending}>
        Adicionar valor manual
      </Button>
    </form>
  );
}
