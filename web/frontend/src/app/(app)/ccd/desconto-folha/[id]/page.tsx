"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { LancamentoDetailSheet } from "@/components/app/lancamento-detail-sheet";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
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
  useMapaRetencoes,
  useMatchAutomatico,
  useRemoverCadastro,
  useRemoverValor,
  useVincular,
} from "@/hooks/use-desconto-folha";
import { messageForError } from "@/lib/error-messages";
import { formatCpf, formatCurrencyBRL } from "@/lib/format";
import type { Lancamento, Valor } from "@/schemas/desconto-folha";
import { podeEditar } from "@/lib/permissoes";

import { RetencoesTabela } from "../_retencoes-tabela";
import { STATUS_EXTRACAO, TIPO_NOTIFICACAO, TIPO_RECEBIMENTO, formatData } from "../_shared";

const JOB_LABEL: Record<string, string> = {
  pending: "Na fila...",
  running: "Lendo os PDFs e consultando a LLM...",
  done: "Extração concluída",
  failed: "Extração falhou",
  cancelled: "Cancelada",
};

function EventoLink({ evento, url }: { evento?: number | null; url?: string | null }) {
  if (evento == null) return null;
  const texto = `Ev. ${evento}`;
  return url ? (
    <a
      href={url}
      target="_blank"
      rel="noreferrer"
      className="ml-1 text-primary underline-offset-2 hover:underline"
    >
      {texto}
    </a>
  ) : (
    <span className="ml-1">{texto}</span>
  );
}

export default function DescontoFolhaDetalhePage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const id = Number(params.id);
  const { data: me } = useCurrentUser();
  const canEdit = podeEditar(me, "ccd.desconto-folha");

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
            {c.cpfCnpj ? ` (${formatCpf(c.cpfCnpj)})` : ""}
            {c.idDebito != null ? ` · débito #${c.idDebito}` : " · sem débito vinculado"}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" onClick={() => router.push("/ccd/desconto-folha")}>
            Voltar
          </Button>
          {c.cpfCnpj && c.cpfCnpj.replace(/\D/g, "").length === 11 && (
            <Link
              href={`/ccd/siai-pessoal/contracheque?${new URLSearchParams({
                cpf: c.cpfCnpj.replace(/\D/g, ""),
                processo: c.processo,
                cadastro: String(c.id),
              }).toString()}`}
              className={buttonVariants({ variant: "outline" })}
            >
              SIAI Pessoal
            </Link>
          )}
          {canEdit && (
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
          {canEdit && (
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
          {canEdit && (
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
          {c.notificacao.numero ?? (c.notificacao.data ? "sem número" : "não localizada")}
          <EventoLink evento={c.notificacao.evento} url={c.notificacao.url} />
          <div className="text-xs text-muted-foreground">
            {formatData(c.notificacao.data)}
            {c.notificacao.tipo ? ` · ${TIPO_NOTIFICACAO[c.notificacao.tipo]}` : ""}
          </div>
        </Info>
        <Info titulo="Recebimento">
          {c.ar.tipo ? TIPO_RECEBIMENTO[c.ar.tipo] : (c.ar.numeroPostagem ?? "não localizado")}
          <EventoLink evento={c.ar.evento} url={c.ar.url} />
          <div className="text-xs text-muted-foreground">
            {formatData(c.ar.data)}
            {c.ar.tipo && c.ar.numeroPostagem ? ` · ${c.ar.numeroPostagem}` : ""}
          </div>
        </Info>
        <Info titulo="Resposta do órgão">
          {c.resposta.processo ? (
            <>
              {c.resposta.url ? (
                <a
                  href={c.resposta.url}
                  target="_blank"
                  rel="noreferrer"
                  className="font-mono text-primary underline-offset-2 hover:underline"
                >
                  {c.resposta.processo}
                </a>
              ) : (
                <span className="font-mono">{c.resposta.processo}</span>
              )}
              {c.resposta.evento != null && ` · Ev. ${c.resposta.evento}`}
            </>
          ) : (
            c.eventosResposta.length === 0 &&
            "nenhuma resposta localizada (apensado ou evento com resumo de resposta)"
          )}
          {!c.resposta.processo && c.eventosResposta.length > 0 && (
            <ul className="mt-2 space-y-0.5 text-xs">
              {c.eventosResposta.map((e) => (
                <li key={e.idEvento}>
                  <a
                    href={e.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-primary underline-offset-2 hover:underline"
                  >
                    {e.processo ? `${e.processo} · ` : ""}Ev. {e.evento} · {e.nome ?? "informação"}{" "}
                    · {formatData(e.data)}
                  </a>
                </li>
              ))}
            </ul>
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
            <CardTitle className="text-base">Valores e conciliação com o FRAP</CardTitle>
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
                  onError: (err) => toast.error(messageForError(err, "Erro na conciliação.")),
                })
              }
            >
              Conciliar automaticamente
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <ValoresTable
            id={c.id}
            valores={c.valores}
            canEdit={canEdit}
            cpf={c.cpfCnpj ?? null}
            processo={c.processo}
          />
          {canEdit && <NovoValorForm id={c.id} />}
        </CardContent>
      </Card>

      {c.cpfCnpj && c.cpfCnpj.replace(/\D/g, "").length === 11 && (
        <RetencoesCard
          cpf={c.cpfCnpj.replace(/\D/g, "")}
          processo={c.processo}
          id={c.id}
          debitoOriginal={c.debitoValorOriginal ?? null}
          debitoAtualizado={c.debitoValorAtualizado ?? null}
        />
      )}
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

function linkContracheque(id: number, cpf: string, v: Valor, processo: string): string {
  const qs = new URLSearchParams({
    cpf,
    ano: String(v.ano),
    mes: String(v.mes),
    processo,
    cadastro: String(id),
  });
  return `/ccd/siai-pessoal/contracheque?${qs.toString()}`;
}

function ValoresTable({
  id,
  valores,
  canEdit,
  cpf,
  processo,
}: {
  id: number;
  valores: Valor[];
  canEdit: boolean;
  cpf: string | null;
  processo: string;
}) {
  const vincular = useVincular(id);
  const desvincular = useDesvincular(id);
  const removerValor = useRemoverValor(id);
  const [lancamentoAberto, setLancamentoAberto] = useState<number | null>(null);

  return (
    <>
      <LancamentoDetailSheet
        idLancamento={lancamentoAberto}
        onOpenChange={(open) => !open && setLancamentoAberto(null)}
      />
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Parcela</TableHead>
            <TableHead>Competência</TableHead>
            <TableHead>Valor resposta</TableHead>
            <TableHead>Valor SIAI Pessoal</TableHead>
            <TableHead>Origem</TableHead>
            <TableHead>Conciliação FRAP</TableHead>
            <TableHead className="w-0" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {valores.length === 0 ? (
            <TableRow>
              <TableCell colSpan={7} className="py-8 text-center text-sm text-muted-foreground">
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
                  <div className="flex items-center gap-2">
                    <span
                      className={
                        v.valorSiai != null && Math.abs(v.valorSiai - v.valor) >= 0.01
                          ? "text-amber-700"
                          : undefined
                      }
                    >
                      {v.valorSiai == null ? "—" : formatCurrencyBRL(v.valorSiai)}
                    </span>
                    {cpf && v.ano != null && v.mes != null && (
                      <Link
                        href={linkContracheque(id, cpf, v, processo)}
                        className={buttonVariants({ variant: "ghost", size: "sm" })}
                      >
                        Contracheque
                      </Link>
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  <Badge variant="outline">{v.origem === "L" ? "LLM" : "Manual"}</Badge>
                </TableCell>
                <TableCell className="text-sm">
                  {v.match ? (
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge variant="success">
                        {v.match.automatico ? "Automático" : "Manual"}
                      </Badge>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setLancamentoAberto(v.match!.lancamento.idLancamento)}
                      >
                        Crédito FRAP
                      </Button>
                      {canEdit && (
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
                  {canEdit && (
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
    </>
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
        <Input id="v-mes" className="w-16" value={mes} onChange={(e) => setMes(e.target.value)} />
      </div>
      <div className="flex flex-col gap-1">
        <Label htmlFor="v-ano" className="text-xs">
          Ano
        </Label>
        <Input id="v-ano" className="w-20" value={ano} onChange={(e) => setAno(e.target.value)} />
      </div>
      <div className="flex flex-col gap-1">
        <Label htmlFor="v-valor" className="text-xs">
          Valor (R$)
        </Label>
        <Input
          id="v-valor"
          className="w-32"
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

function RetencoesCard({
  cpf,
  processo,
  id,
  debitoOriginal,
  debitoAtualizado,
}: {
  cpf: string;
  processo: string;
  id: number;
  debitoOriginal: number | null;
  debitoAtualizado: number | null;
}) {
  const { data, isPending, isError, error } = useMapaRetencoes(cpf);
  const moeda = (v: number | null | undefined) => (v == null ? "—" : formatCurrencyBRL(v));
  return (
    <Card>
      <CardHeader className="gap-3">
        <CardTitle className="text-base">Retenções TCE/FRAP no SIAI Pessoal</CardTitle>
        <div className="flex flex-wrap gap-x-8 gap-y-2 rounded-lg border px-4 py-3">
          <div>
            <div className="text-xs text-muted-foreground">Total retido</div>
            <div className="text-lg font-semibold">{moeda(data?.totalRetido)}</div>
            <div className="text-xs text-muted-foreground">
              {data ? `${data.meses.length} mês(es)` : ""}
            </div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">Débito do processo</div>
            <div className="text-lg font-semibold">{moeda(debitoAtualizado)}</div>
            <div className="text-xs text-muted-foreground">
              atualizado · original {moeda(debitoOriginal)}
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isPending ? (
          <p className="text-sm text-muted-foreground">Consultando o SIAI Pessoal...</p>
        ) : isError ? (
          <p className="text-sm text-destructive">
            {messageForError(error, "Erro ao consultar as retenções.")}
          </p>
        ) : data.meses.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            Nenhuma retenção TCE/FRAP no SIAI Pessoal para este CPF.
          </p>
        ) : (
          <RetencoesTabela cpf={cpf} meses={data.meses} processo={processo} cadastro={id} />
        )}
      </CardContent>
    </Card>
  );
}
