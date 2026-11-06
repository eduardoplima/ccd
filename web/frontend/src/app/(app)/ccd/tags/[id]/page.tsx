"use client";

import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
import { Textarea } from "@/components/ui/textarea";
import { useCurrentUser } from "@/hooks/use-current-user";
import { useAtualizarTag, useRemoverTag, useSalvarObrigacoes, useTag } from "@/hooks/use-tags";
import { messageForError } from "@/lib/error-messages";
import { podeEditar } from "@/lib/permissoes";
import type {
  ObrigacaoInput,
  SituacaoObrigacao,
  SituacaoTag,
  TagDetalhe,
  TagPatch,
} from "@/schemas/tags";

import { SITUACAO_TAG } from "../_shared";

const SITUACOES_TAG: SituacaoTag[] = ["VIGENTE", "CUMPRIDO", "PRORROGADO", "RESCINDIDO"];
const SITUACOES_OBRIGACAO: SituacaoObrigacao[] = [
  "PENDENTE",
  "CUMPRIDA",
  "DESCUMPRIDA",
  "PRORROGADA",
];

type Cabecalho = {
  numero: string;
  orgao: string;
  responsavel: string;
  cargoResponsavel: string;
  cpfResponsavel: string;
  compromissario: string;
  dataCelebracao: string;
  prazo: string;
  homologacao: string;
  valorMultaDescumprimento: string;
  situacao: SituacaoTag;
  observacoes: string;
};

function cabecalhoDe(t: TagDetalhe): Cabecalho {
  return {
    numero: t.numero,
    orgao: t.orgao,
    responsavel: t.responsavel,
    cargoResponsavel: t.cargoResponsavel ?? "",
    cpfResponsavel: t.cpfResponsavel ?? "",
    compromissario: t.compromissario ?? "",
    dataCelebracao: t.dataCelebracao ?? "",
    prazo: t.prazo ?? "",
    homologacao: t.homologacao ?? "",
    valorMultaDescumprimento:
      t.valorMultaDescumprimento != null ? String(t.valorMultaDescumprimento) : "",
    situacao: t.situacao,
    observacoes: t.observacoes ?? "",
  };
}

function patchDe(c: Cabecalho): TagPatch {
  const ouNulo = (s: string) => s.trim() || null;
  return {
    numero: c.numero.trim(),
    orgao: c.orgao.trim(),
    responsavel: c.responsavel.trim(),
    cargoResponsavel: ouNulo(c.cargoResponsavel),
    cpfResponsavel: ouNulo(c.cpfResponsavel),
    compromissario: ouNulo(c.compromissario),
    dataCelebracao: ouNulo(c.dataCelebracao),
    prazo: ouNulo(c.prazo),
    homologacao: ouNulo(c.homologacao),
    valorMultaDescumprimento: c.valorMultaDescumprimento.trim()
      ? Number(c.valorMultaDescumprimento.replace(",", "."))
      : null,
    situacao: c.situacao,
    observacoes: ouNulo(c.observacoes),
  };
}

function obrigacoesDe(t: TagDetalhe): ObrigacaoInput[] {
  return t.obrigacoes.map((o) => ({
    clausula: o.clausula,
    descricao: o.descricao,
    prazoTexto: o.prazoTexto ?? null,
    dataLimite: o.dataLimite ?? null,
    situacao: o.situacao,
    dataCumprimento: o.dataCumprimento ?? null,
    eventoComprovacao: o.eventoComprovacao ?? null,
    observacoes: o.observacoes ?? null,
  }));
}

const NOVA: ObrigacaoInput = {
  clausula: "",
  descricao: "",
  prazoTexto: null,
  dataLimite: null,
  situacao: "PENDENTE",
  dataCumprimento: null,
  eventoComprovacao: null,
  observacoes: null,
};

export default function TagDetalhePage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const id = Number(params.id);
  const { data: me } = useCurrentUser();
  const canEdit = podeEditar(me, "ccd.tags");
  const { data: t, isLoading, isError, error } = useTag(Number.isFinite(id) ? id : null);

  if (isError) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 p-10">
        <p className="text-sm">{messageForError(error, "Não foi possível carregar o TAG.")}</p>
        <Button variant="outline" onClick={() => router.push("/ccd/tags")}>
          Voltar
        </Button>
      </div>
    );
  }
  if (isLoading || !t) {
    return (
      <div className="flex flex-1 items-center justify-center p-10 text-sm text-muted-foreground">
        Carregando...
      </div>
    );
  }
  return <Editor key={`${t.id}-${t.dataInclusao}`} t={t} canEdit={canEdit} />;
}

function Editor({ t, canEdit }: { t: TagDetalhe; canEdit: boolean }) {
  const router = useRouter();
  const [cab, setCab] = useState<Cabecalho>(() => cabecalhoDe(t));
  const [obs, setObs] = useState<ObrigacaoInput[]>(() => obrigacoesDe(t));
  const [mostrarOcr, setMostrarOcr] = useState(false);
  const atualizar = useAtualizarTag(t.id);
  const salvarObs = useSalvarObrigacoes(t.id);
  const remover = useRemoverTag();
  const salvando = atualizar.isPending || salvarObs.isPending;
  const st = SITUACAO_TAG[t.situacao];

  function set<K extends keyof Cabecalho>(k: K, v: Cabecalho[K]) {
    setCab((c) => ({ ...c, [k]: v }));
  }
  function setObr(i: number, patch: Partial<ObrigacaoInput>) {
    setObs((xs) => xs.map((o, j) => (j === i ? { ...o, ...patch } : o)));
  }

  async function salvar(revisado?: boolean) {
    const invalida = obs.find((o) => !o.clausula.trim() || !o.descricao.trim());
    if (invalida) {
      toast.error("Toda obrigação precisa de cláusula e descrição.");
      return;
    }
    try {
      await salvarObs.mutateAsync(obs);
      await atualizar.mutateAsync({ ...patchDe(cab), ...(revisado == null ? {} : { revisado }) });
      toast.success(revisado ? "TAG revisado." : "TAG salvo.");
    } catch (err) {
      toast.error(messageForError(err, "Erro ao salvar."));
    }
  }

  return (
    <main className="flex flex-col gap-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Button variant="link" className="px-0" onClick={() => router.push("/ccd/tags")}>
            ← TAGs
          </Button>
          <h1 className="section-heading text-2xl">
            TAG {t.numero}
            <Badge variant={st.variant} className="ml-3 align-middle">
              {st.label}
            </Badge>
            {!t.revisado && (
              <Badge variant="warning" className="ml-2 align-middle">
                rascunho da extração
              </Badge>
            )}
          </h1>
          <p className="text-sm text-muted-foreground">
            Processo{" "}
            <a
              href={`https://processos.tce.rn.gov.br/#/dashboard/processos/${t.idProcesso}`}
              target="_blank"
              rel="noreferrer"
              className="text-primary underline-offset-2 hover:underline"
            >
              {t.processo}
            </a>
            {" · "}
            {t.urlEvento ? (
              <a
                href={t.urlEvento}
                target="_blank"
                rel="noreferrer"
                className="text-primary underline-offset-2 hover:underline"
              >
                Ev. {t.evento}
              </a>
            ) : (
              `Ev. ${t.evento}`
            )}
          </p>
        </div>
        {canEdit && (
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" disabled={salvando} onClick={() => void salvar()}>
              Salvar
            </Button>
            {!t.revisado && (
              <Button disabled={salvando} onClick={() => void salvar(true)}>
                Salvar e marcar como revisado
              </Button>
            )}
            <Button
              variant="ghost"
              className="text-destructive"
              disabled={remover.isPending}
              onClick={() => {
                if (!window.confirm("Remover este TAG do cadastro?")) return;
                remover.mutate(t.id, {
                  onSuccess: () => router.push("/ccd/tags"),
                  onError: (err) => toast.error(messageForError(err, "Erro ao remover.")),
                });
              }}
            >
              Remover
            </Button>
          </div>
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Termo</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <Campo label="Número do termo">
            <Input
              value={cab.numero}
              onChange={(e) => set("numero", e.target.value)}
              disabled={!canEdit}
            />
          </Campo>
          <Campo label="Órgão compromitente">
            <Input
              value={cab.orgao}
              onChange={(e) => set("orgao", e.target.value)}
              disabled={!canEdit}
            />
          </Campo>
          <Campo label="Compromissário (MPC)">
            <Input
              value={cab.compromissario}
              onChange={(e) => set("compromissario", e.target.value)}
              disabled={!canEdit}
            />
          </Campo>
          <Campo label="Responsável">
            <Input
              value={cab.responsavel}
              onChange={(e) => set("responsavel", e.target.value)}
              disabled={!canEdit}
            />
          </Campo>
          <Campo label="Cargo">
            <Input
              value={cab.cargoResponsavel}
              onChange={(e) => set("cargoResponsavel", e.target.value)}
              disabled={!canEdit}
            />
          </Campo>
          <Campo label="CPF do responsável">
            <Input
              value={cab.cpfResponsavel}
              onChange={(e) => set("cpfResponsavel", e.target.value)}
              inputMode="numeric"
              disabled={!canEdit}
            />
          </Campo>
          <Campo label="Celebração">
            <Input
              type="date"
              value={cab.dataCelebracao}
              onChange={(e) => set("dataCelebracao", e.target.value)}
              disabled={!canEdit}
            />
          </Campo>
          <Campo label="Prazo final">
            <Input
              type="date"
              value={cab.prazo}
              onChange={(e) => set("prazo", e.target.value)}
              disabled={!canEdit}
            />
          </Campo>
          <Campo label="Multa por obrigação descumprida (R$)">
            <Input
              value={cab.valorMultaDescumprimento}
              onChange={(e) => set("valorMultaDescumprimento", e.target.value)}
              inputMode="decimal"
              disabled={!canEdit}
            />
          </Campo>
          <Campo label="Homologação">
            <Input
              value={cab.homologacao}
              onChange={(e) => set("homologacao", e.target.value)}
              placeholder="Acórdão nº/ano (câmara, data)"
              disabled={!canEdit}
            />
          </Campo>
          <Campo label="Situação">
            <SelectNative
              value={cab.situacao}
              onChange={(e) => set("situacao", e.target.value as SituacaoTag)}
              disabled={!canEdit}
            >
              {SITUACOES_TAG.map((s) => (
                <option key={s} value={s}>
                  {SITUACAO_TAG[s].label}
                </option>
              ))}
            </SelectNative>
          </Campo>
          <Campo label="Observações" className="md:col-span-3">
            <Textarea
              value={cab.observacoes}
              onChange={(e) => set("observacoes", e.target.value)}
              disabled={!canEdit}
            />
          </Campo>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Obrigações</CardTitle>
          {canEdit && (
            <Button size="sm" variant="outline" onClick={() => setObs((xs) => [...xs, NOVA])}>
              Adicionar
            </Button>
          )}
        </CardHeader>
        <CardContent className="overflow-x-auto p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-8">#</TableHead>
                <TableHead className="min-w-40">Cláusula</TableHead>
                <TableHead className="min-w-80">Obrigação</TableHead>
                <TableHead className="min-w-40">Prazo (texto)</TableHead>
                <TableHead>Data-limite</TableHead>
                <TableHead>Situação</TableHead>
                <TableHead>Cumprida em</TableHead>
                <TableHead className="w-20">Ev.</TableHead>
                <TableHead className="min-w-40">Obs.</TableHead>
                {canEdit && <TableHead />}
              </TableRow>
            </TableHeader>
            <TableBody>
              {obs.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={10} className="text-center text-muted-foreground">
                    Nenhuma obrigação.
                  </TableCell>
                </TableRow>
              ) : (
                obs.map((o, i) => (
                  <TableRow key={i} className="align-top">
                    <TableCell className="pt-4 text-muted-foreground">{i + 1}</TableCell>
                    <TableCell>
                      <Input
                        value={o.clausula}
                        onChange={(e) => setObr(i, { clausula: e.target.value })}
                        disabled={!canEdit}
                      />
                    </TableCell>
                    <TableCell>
                      <Textarea
                        value={o.descricao}
                        onChange={(e) => setObr(i, { descricao: e.target.value })}
                        disabled={!canEdit}
                        className="min-h-10"
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        value={o.prazoTexto ?? ""}
                        onChange={(e) => setObr(i, { prazoTexto: e.target.value || null })}
                        disabled={!canEdit}
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        type="date"
                        value={o.dataLimite ?? ""}
                        onChange={(e) => setObr(i, { dataLimite: e.target.value || null })}
                        disabled={!canEdit}
                      />
                    </TableCell>
                    <TableCell>
                      <SelectNative
                        value={o.situacao}
                        onChange={(e) =>
                          setObr(i, { situacao: e.target.value as SituacaoObrigacao })
                        }
                        disabled={!canEdit}
                      >
                        {SITUACOES_OBRIGACAO.map((s) => (
                          <option key={s} value={s}>
                            {s.charAt(0) + s.slice(1).toLowerCase()}
                          </option>
                        ))}
                      </SelectNative>
                    </TableCell>
                    <TableCell>
                      <Input
                        type="date"
                        value={o.dataCumprimento ?? ""}
                        onChange={(e) => setObr(i, { dataCumprimento: e.target.value || null })}
                        disabled={!canEdit}
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        value={o.eventoComprovacao ?? ""}
                        inputMode="numeric"
                        onChange={(e) =>
                          setObr(i, {
                            eventoComprovacao: e.target.value ? Number(e.target.value) : null,
                          })
                        }
                        disabled={!canEdit}
                      />
                    </TableCell>
                    <TableCell>
                      <Textarea
                        value={o.observacoes ?? ""}
                        onChange={(e) => setObr(i, { observacoes: e.target.value || null })}
                        disabled={!canEdit}
                        className="min-h-10"
                      />
                    </TableCell>
                    {canEdit && (
                      <TableCell>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="text-destructive"
                          onClick={() => setObs((xs) => xs.filter((_, j) => j !== i))}
                        >
                          ×
                        </Button>
                      </TableCell>
                    )}
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Texto lido do PDF</CardTitle>
          <Button size="sm" variant="outline" onClick={() => setMostrarOcr((v) => !v)}>
            {mostrarOcr ? "Ocultar" : "Mostrar"}
          </Button>
        </CardHeader>
        {mostrarOcr && (
          <CardContent>
            <pre className="max-h-[32rem] overflow-auto whitespace-pre-wrap rounded-md bg-muted p-3 text-xs">
              {t.textoOcr || "Sem texto."}
            </pre>
          </CardContent>
        )}
      </Card>
    </main>
  );
}

function Campo({
  label,
  children,
  className,
}: {
  label: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`flex flex-col gap-1.5 ${className ?? ""}`}>
      <Label>{label}</Label>
      {children}
    </div>
  );
}
