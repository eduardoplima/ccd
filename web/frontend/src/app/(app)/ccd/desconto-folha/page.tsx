"use client";

import Link from "next/link";
import { useState } from "react";
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { SelectNative } from "@/components/ui/select-native";
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
  useCadastros,
  useCriarCadastro,
  useLocalizarNotificacoes,
  useRetencoes,
  useSugestoes,
  useLookupProcesso,
} from "@/hooks/use-desconto-folha";
import { messageForError } from "@/lib/error-messages";
import { formatCpf, formatCurrencyBRL } from "@/lib/format";
import { cn } from "@/lib/utils";
import {
  JOB_LABEL,
  STATUS_EXTRACAO,
  TIPO_NOTIFICACAO,
  TIPO_RECEBIMENTO,
  formatData,
} from "./_shared";

const SIZE = 50;

const FILTROS_PRESENCA = [
  ["comNotificacao", "Com notificação"],
  ["comRecebimento", "Com recebimento"],
  ["comResposta", "Com resposta"],
  ["comValores", "Com valores"],
  ["comConciliacao", "Com conciliação"],
] as const;

type Selecao = { tipo: "pessoa" | "orgao"; valor: string; rotulo: string };

const TOTAIS = [
  ["processos", "Processos", false],
  ["pessoas", "Pessoas", false],
  ["valorAReceber", "A receber", true],
  ["valorRecebido", "Recebido em conciliação", true],
] as const;

export default function DescontoFolhaPage() {
  const { data: me } = useCurrentUser();
  const isAdmin = me?.papel === "admin";
  const [qInput, setQInput] = useState("");
  const [q, setQ] = useState("");
  const [page, setPage] = useState(1);
  const [novoOpen, setNovoOpen] = useState(false);
  const [filtros, setFiltros] = useState({
    comNotificacao: false,
    comRecebimento: false,
    comResposta: false,
    comValores: false,
    comConciliacao: false,
  });

  const [selecao, setSelecao] = useState<Selecao | null>(null);
  const [sugestoesAbertas, setSugestoesAbertas] = useState(false);
  const { data: sugestoes } = useSugestoes(qInput);

  const { data, isLoading, refetch } = useCadastros({
    q,
    page,
    size: SIZE,
    ...filtros,
    cpf: selecao?.tipo === "pessoa" ? selecao.valor : undefined,
    orgao: selecao?.tipo === "orgao" ? selecao.valor : undefined,
  });
  const totais = data?.totais;
  const cpfSelecionado = selecao?.tipo === "pessoa" ? selecao.valor : null;
  const { data: retencoes } = useRetencoes(cpfSelecionado);

  const escolher = (s: Selecao) => {
    setSelecao(s);
    setQInput("");
    setQ("");
    setPage(1);
    setSugestoesAbertas(false);
  };
  const limparTudo = () => {
    setSelecao(null);
    setQInput("");
    setQ("");
    setPage(1);
  };
  const temSugestoes =
    sugestoesAbertas &&
    qInput.trim().length >= 2 &&
    !!sugestoes &&
    (sugestoes.pessoas.length > 0 || sugestoes.orgaos.length > 0);
  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / SIZE));

  const localizar = useLocalizarNotificacoes();
  const [idJob, setIdJob] = useState<number | null>(null);
  const { data: job } = useCcdJob(idJob);
  const jobAtivo = job != null && (job.status === "pending" || job.status === "running");
  const [jobVisto, setJobVisto] = useState<number | null>(null);
  if (job && !jobAtivo && idJob != null && jobVisto !== idJob) {
    setJobVisto(idJob);
    void refetch();
    if (job.status === "done") toast.success(job.resultado ?? "Notificações localizadas.");
    if (job.status === "failed") toast.error(job.erroMensagem ?? "A localização falhou.");
  }

  return (
    <main className="mx-auto flex w-full max-w-screen-2xl flex-col gap-4 p-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Desconto em Folha</h1>
          <p className="text-sm text-muted-foreground">
            Processos notificados para desconto em folha, a resposta do órgão no apensado e o
            crédito correspondente no FRAP.
          </p>
        </div>
        {isAdmin && (
          <div className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              disabled={localizar.isPending || jobAtivo}
              onClick={() =>
                localizar.mutate(undefined, {
                  onSuccess: (j) => setIdJob(j.idJob),
                  onError: (err) =>
                    toast.error(messageForError(err, "Erro ao enfileirar a localização.")),
                })
              }
            >
              {jobAtivo ? JOB_LABEL[job!.status] : "Localizar notificações"}
            </Button>
            <Button onClick={() => setNovoOpen(true)}>Novo cadastro</Button>
          </div>
        )}
      </div>

      <div className="flex flex-wrap items-end gap-x-8 gap-y-2 rounded-lg border px-4 py-3">
        <span className="text-sm font-medium">
          {selecao ? `Totais de ${selecao.rotulo}` : "Totais"}
        </span>
        {TOTAIS.map(([chave, rotulo, moeda]) => (
          <div key={chave}>
            <div className="text-xs text-muted-foreground">{rotulo}</div>
            <div className="text-lg font-semibold">
              {totais == null
                ? "—"
                : moeda
                  ? formatCurrencyBRL(totais[chave])
                  : totais[chave].toLocaleString("pt-BR")}
            </div>
          </div>
        ))}
        {cpfSelecionado && (
          <>
            <div>
              <div className="text-xs text-muted-foreground">Total de retenções</div>
              <div className="text-lg font-semibold">
                {retencoes == null ? "—" : formatCurrencyBRL(retencoes.total)}
              </div>
            </div>
            <div>
              <div className="text-xs text-muted-foreground">SIAI Pessoal</div>
              <div className="flex gap-1">
                <Link
                  href={`/ccd/siai-pessoal/contracheque?cpf=${cpfSelecionado}`}
                  className={cn(buttonVariants({ variant: "outline", size: "sm" }), "h-6 text-xs")}
                >
                  Contracheques
                </Link>
                <Link
                  href={`/ccd/desconto-folha/retencoes?cpf=${cpfSelecionado}`}
                  className={cn(buttonVariants({ variant: "outline", size: "sm" }), "h-6 text-xs")}
                >
                  Retenções
                </Link>
              </div>
            </div>
          </>
        )}
      </div>

      <form
        className="flex flex-wrap items-center gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          setQ(qInput.trim());
          setPage(1);
          setSugestoesAbertas(false);
        }}
      >
        <div className="relative w-full max-w-sm">
          <Input
            value={qInput}
            onChange={(e) => {
              setQInput(e.target.value);
              setSugestoesAbertas(true);
            }}
            onFocus={() => setSugestoesAbertas(true)}
            onBlur={() => setSugestoesAbertas(false)}
            onKeyDown={(e) => e.key === "Escape" && setSugestoesAbertas(false)}
            placeholder="Processo (ex.: 100/2023), responsável, CPF ou órgão"
          />
          {temSugestoes && sugestoes && (
            <div className="absolute z-10 mt-1 w-full rounded-md border bg-popover p-1 text-sm shadow-md">
              {sugestoes.pessoas.length > 0 && (
                <div className="px-2 pt-1 text-xs font-medium text-muted-foreground">Pessoas</div>
              )}
              {sugestoes.pessoas.map((p) => (
                <button
                  key={p.cpf}
                  type="button"
                  className="flex w-full items-center justify-between gap-2 rounded px-2 py-1 text-left hover:bg-muted"
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() =>
                    escolher({
                      tipo: "pessoa",
                      valor: p.cpf,
                      rotulo: `${p.nome ?? "sem nome"} (${formatCpf(p.cpf)})`,
                    })
                  }
                >
                  <span className="truncate">
                    {p.nome ?? "sem nome"}{" "}
                    <span className="font-mono text-xs text-muted-foreground">
                      {formatCpf(p.cpf)}
                    </span>
                  </span>
                  <span className="shrink-0 text-xs text-muted-foreground">
                    {p.qtd} cadastro{p.qtd === 1 ? "" : "s"}
                  </span>
                </button>
              ))}
              {sugestoes.orgaos.length > 0 && (
                <div className="px-2 pt-1 text-xs font-medium text-muted-foreground">Órgãos</div>
              )}
              {sugestoes.orgaos.map((o) => (
                <button
                  key={o.nome}
                  type="button"
                  className="flex w-full items-center justify-between gap-2 rounded px-2 py-1 text-left hover:bg-muted"
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => escolher({ tipo: "orgao", valor: o.nome, rotulo: o.nome })}
                >
                  <span className="truncate">{o.nome}</span>
                  <span className="shrink-0 text-xs text-muted-foreground">
                    {o.qtd} cadastro{o.qtd === 1 ? "" : "s"}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
        <Button type="submit" variant="outline">
          Buscar
        </Button>
        {selecao && (
          <>
            <Badge variant="secondary" className="max-w-md truncate">
              {selecao.tipo === "pessoa" ? "Pessoa: " : "Órgão: "}
              {selecao.rotulo}
            </Badge>
            <Button type="button" variant="ghost" onClick={limparTudo}>
              Limpar
            </Button>
          </>
        )}
        {q && !selecao && (
          <Button
            type="button"
            variant="ghost"
            onClick={() => {
              setQInput("");
              setQ("");
              setPage(1);
            }}
          >
            Limpar
          </Button>
        )}
      </form>

      <div className="flex flex-wrap gap-x-6 gap-y-2">
        {FILTROS_PRESENCA.map(([chave, rotulo]) => (
          <div key={chave} className="flex items-center gap-2">
            <Checkbox
              id={`f-${chave}`}
              checked={filtros[chave]}
              onCheckedChange={(c) => {
                setFiltros((f) => ({ ...f, [chave]: c === true }));
                setPage(1);
              }}
            />
            <Label htmlFor={`f-${chave}`} className="cursor-pointer font-normal">
              {rotulo}
            </Label>
          </div>
        ))}
      </div>

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Processo</TableHead>
              <TableHead>Órgão</TableHead>
              <TableHead>Responsável</TableHead>
              <TableHead>Notificação</TableHead>
              <TableHead>Recebimento</TableHead>
              <TableHead>Resposta</TableHead>
              <TableHead>Valor</TableHead>
              <TableHead className="w-0" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={8} className="py-10 text-center text-sm text-muted-foreground">
                  Carregando...
                </TableCell>
              </TableRow>
            ) : (data?.items.length ?? 0) === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="py-10 text-center text-sm text-muted-foreground">
                  Nenhum cadastro.
                </TableCell>
              </TableRow>
            ) : (
              data!.items.map((c) => {
                const st = STATUS_EXTRACAO[c.statusExtracao];
                return (
                  <TableRow key={c.id}>
                    <TableCell className="whitespace-nowrap font-mono text-xs font-medium">
                      {c.processo}
                    </TableCell>
                    <TableCell className="max-w-[260px] truncate" title={c.orgao ?? ""}>
                      {c.orgao ?? "—"}
                    </TableCell>
                    <TableCell className="max-w-[260px] truncate" title={c.responsavel ?? ""}>
                      {c.responsavel ?? "—"}
                      {c.idDebito == null && (
                        <span className="ml-2 text-xs text-amber-700">sem débito</span>
                      )}
                    </TableCell>
                    <TableCell className="whitespace-nowrap text-sm">
                      {c.notificacao.numero ?? (c.notificacao.data ? "s/ nº" : "—")}
                      <div className="text-xs text-muted-foreground">
                        {formatData(c.notificacao.data)}
                        {c.notificacao.tipo ? ` · ${TIPO_NOTIFICACAO[c.notificacao.tipo]}` : ""}
                      </div>
                    </TableCell>
                    <TableCell className="whitespace-nowrap text-sm">
                      {c.ar.tipo ? TIPO_RECEBIMENTO[c.ar.tipo] : (c.ar.numeroPostagem ?? "—")}
                      <div className="text-xs text-muted-foreground">
                        {formatData(c.ar.data)}
                        {c.ar.tipo && c.ar.numeroPostagem ? ` · ${c.ar.numeroPostagem}` : ""}
                      </div>
                    </TableCell>
                    <TableCell className="whitespace-nowrap text-sm">
                      {c.resposta.processo ? (
                        <>
                          <span className="font-mono text-xs">{c.resposta.processo}</span>
                          {c.resposta.evento != null && (
                            <span className="ml-1 text-xs text-muted-foreground">
                              Ev. {c.resposta.evento}
                            </span>
                          )}
                          <div className="text-xs text-muted-foreground">
                            {formatData(c.resposta.data)}
                          </div>
                        </>
                      ) : (
                        "—"
                      )}
                    </TableCell>
                    <TableCell className="whitespace-nowrap text-sm">
                      <div>{c.valorTotal != null ? formatCurrencyBRL(c.valorTotal) : "—"}</div>
                      <div className="flex items-center gap-1 text-xs text-muted-foreground">
                        <Badge variant={st.variant}>{st.label}</Badge>
                        {c.qtdValores > 0 && (
                          <span>
                            {c.qtdMatches}/{c.qtdValores} conciliados
                          </span>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Link
                        href={`/ccd/desconto-folha/${c.id}`}
                        className={buttonVariants({ size: "sm", variant: "outline" })}
                      >
                        Detalhes
                      </Link>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>
          Página {page} de {totalPages} · {total} cadastro(s)
        </span>
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            disabled={page <= 1}
            onClick={() => setPage(page - 1)}
          >
            Anterior
          </Button>
          <Button
            size="sm"
            variant="outline"
            disabled={page >= totalPages}
            onClick={() => setPage(page + 1)}
          >
            Próxima
          </Button>
        </div>
      </div>

      <NovoCadastroDialog open={novoOpen} onOpenChange={setNovoOpen} />
    </main>
  );
}

function NovoCadastroDialog({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (v: boolean) => void;
}) {
  const [processoInput, setProcessoInput] = useState("");
  const [processo, setProcesso] = useState("");
  const [idDebito, setIdDebito] = useState("");
  const [nomeOrgao, setNomeOrgao] = useState("");
  const lookup = useLookupProcesso(processo);
  const criar = useCriarCadastro();

  const debitos = lookup.data?.debitos ?? [];
  const orgaoSugerido = lookup.data?.orgao ?? "";

  function fechar() {
    onOpenChange(false);
    setProcessoInput("");
    setProcesso("");
    setIdDebito("");
    setNomeOrgao("");
  }

  return (
    <Dialog open={open} onOpenChange={(v) => (v ? onOpenChange(v) : fechar())}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Novo cadastro</DialogTitle>
          <DialogDescription>
            Informe o processo de execução. O débito e o responsável vêm do banco processo; a
            notificação, o recebimento e o apensado são localizados ao salvar.
          </DialogDescription>
        </DialogHeader>
        <form
          className="flex flex-col gap-4"
          onSubmit={(e) => {
            e.preventDefault();
            if (!lookup.data) return;
            criar.mutate(
              {
                idProcesso: lookup.data.idProcesso,
                idDebito: idDebito ? Number(idDebito) : null,
                nomeOrgao: nomeOrgao.trim() || orgaoSugerido || null,
              },
              {
                onSuccess: () => {
                  toast.success("Cadastro criado.");
                  fechar();
                },
                onError: (err) => toast.error(messageForError(err, "Erro ao criar o cadastro.")),
              },
            );
          }}
        >
          <div className="flex flex-col gap-2">
            <Label htmlFor="n-processo">Processo</Label>
            <div className="flex gap-2">
              <Input
                id="n-processo"
                value={processoInput}
                onChange={(e) => setProcessoInput(e.target.value)}
                placeholder="100/2023"
                inputMode="numeric"
              />
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setProcesso(processoInput.trim());
                  setIdDebito("");
                }}
              >
                Localizar
              </Button>
            </div>
            {lookup.isFetching && (
              <p className="text-xs text-muted-foreground">Consultando o banco processo...</p>
            )}
            {lookup.isError && (
              <p className="text-xs text-destructive">
                {messageForError(lookup.error, "Processo não encontrado.")}
              </p>
            )}
            {lookup.data && (
              <p className="text-xs text-muted-foreground">
                {lookup.data.processo} · {debitos.length} débito(s)
              </p>
            )}
          </div>

          <div className="flex flex-col gap-2">
            <Label htmlFor="n-debito">Débito e responsável</Label>
            <SelectNative
              id="n-debito"
              value={idDebito}
              onChange={(e) => setIdDebito(e.target.value)}
              disabled={!lookup.data}
            >
              <option value="">Sem débito (completar depois)</option>
              {debitos.map((d) => (
                <option key={d.idDebito} value={d.idDebito}>
                  #{d.idDebito} · {d.tipo ?? "débito"} · {formatCurrencyBRL(d.valorOriginal)} ·{" "}
                  {d.nomePessoa ?? "sem responsável"}
                  {d.cancelado ? " (cancelado)" : d.desdobrado ? " (original, desdobrado)" : ""}
                </option>
              ))}
            </SelectNative>
          </div>

          <div className="flex flex-col gap-2">
            <Label htmlFor="n-orgao">Órgão notificado</Label>
            <Input
              id="n-orgao"
              value={nomeOrgao}
              onChange={(e) => setNomeOrgao(e.target.value)}
              placeholder={orgaoSugerido || "Nome do órgão"}
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={fechar}>
              Cancelar
            </Button>
            <Button type="submit" disabled={!lookup.data || criar.isPending}>
              {criar.isPending ? "Salvando..." : "Salvar"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
