"use client";

import Link from "next/link";
import { parseAsInteger, parseAsString, parseAsStringEnum, useQueryState } from "nuqs";
import { useEffect, useId, useState } from "react";
import { toast } from "sonner";

import { OrgaoField, PessoaField } from "@/components/review/entity-panel";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
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
import { Textarea } from "@/components/ui/textarea";
import {
  useAtualizarMonitoramento,
  useCriarMonitoramento,
  useDeletarMonitoramento,
  useMonitoramento,
  useMonitoramentoResumo,
  usePessoasProcesso,
} from "@/hooks/use-desconto-folha";
import { useOrgaos } from "@/hooks/use-reviews";
import { formatBRL, formatDate } from "@/lib/format";
import {
  GRUPOS_MONITORAMENTO,
  type GrupoMonitoramento,
  type MonitoramentoItem,
  type MonitoramentoPayload,
} from "@/schemas/desconto-folha";

import { Paginacao } from "./_paginacao";

const SIZE = 50;

const GRUPO_LABEL: Record<string, string> = {
  GERAL: "Geral",
  ANTIGO: "Antigo",
  NEREU: "Nereu",
};

export function MonitoramentoTab() {
  const [q, setQ] = useQueryState("mq", parseAsString.withDefault(""));
  const [grupo, setGrupo] = useQueryState(
    "mgrupo",
    parseAsStringEnum<GrupoMonitoramento>([...GRUPOS_MONITORAMENTO]),
  );
  const [page, setPage] = useQueryState("mpage", parseAsInteger.withDefault(1));
  const [criarOpen, setCriarOpen] = useState(false);
  const [editando, setEditando] = useState<MonitoramentoItem | null>(null);

  const { data, isFetching } = useMonitoramento({
    q: q || undefined,
    grupo: grupo ?? undefined,
    page,
    size: SIZE,
  });
  const { data: resumo } = useMonitoramentoResumo(grupo ?? undefined);
  const deletar = useDeletarMonitoramento();

  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / SIZE));

  async function handleDelete(m: MonitoramentoItem) {
    if (!confirm(`Remover ${m.numeroProcesso} (${m.nomePessoa ?? "sem nome"}) do monitoramento?`))
      return;
    try {
      await deletar.mutateAsync(m.idMonitoramento);
      toast.success("Registro removido.");
    } catch {
      toast.error("Falha ao remover.");
    }
  }

  return (
    <div className="flex flex-col gap-4">
      {resumo ? (
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4 xl:grid-cols-8">
          <StatCard label="Processos" value={resumo.total} />
          <StatCard label="Notificados" value={resumo.qtdNotificados} />
          <StatCard label="AR recebido" value={resumo.qtdComAr} />
          <StatCard label="Respondidos" value={resumo.qtdRespondidos} />
          <StatCard label="2ª notificação" value={resumo.qtdSegundaNotificacao} />
          <StatCard label="Desconto implantado" value={resumo.qtdDescontoImplementado} />
          <StatCard label="Transf. FRAP" value={resumo.qtdTransfFrap} />
          <StatCard label="Pago no site" value={resumo.qtdPagoSite} />
        </div>
      ) : null}

      <div className="flex flex-wrap items-end gap-3">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="m-q">Busca (processo, nome ou CPF)</Label>
          <Input
            id="m-q"
            value={q}
            onChange={(e) => {
              void setQ(e.target.value);
              void setPage(1);
            }}
            className="w-72"
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="m-grupo">Grupo</Label>
          <SelectNative
            id="m-grupo"
            value={grupo ?? ""}
            onChange={(e) => {
              void setGrupo(e.target.value ? (e.target.value as GrupoMonitoramento) : null);
              void setPage(1);
            }}
          >
            <option value="">Todos</option>
            {GRUPOS_MONITORAMENTO.map((g) => (
              <option key={g} value={g}>
                {GRUPO_LABEL[g]}
              </option>
            ))}
          </SelectNative>
        </div>
        <Button className="ml-auto" onClick={() => setCriarOpen(true)}>
          Novo processo
        </Button>
      </div>

      <p className="text-xs text-muted-foreground">
        {total.toLocaleString("pt-BR")} registros · página {page} de {totalPages}
      </p>

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Processo</TableHead>
              <TableHead>Grupo</TableHead>
              <TableHead>Responsável</TableHead>
              <TableHead>Órgão</TableHead>
              <TableHead>Notificação</TableHead>
              <TableHead>AR</TableHead>
              <TableHead>Resposta</TableHead>
              <TableHead>Desc. folha</TableHead>
              <TableHead className="text-right">Valor original</TableHead>
              <TableHead className="text-right">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.items.length === 0 && !isFetching ? (
              <TableRow>
                <TableCell colSpan={10} className="py-8 text-center text-muted-foreground">
                  Nenhum registro.
                </TableCell>
              </TableRow>
            ) : (
              data?.items.map((m) => (
                <TableRow key={m.idMonitoramento} className="hover:bg-muted/40">
                  <TableCell className="font-mono text-xs">{m.numeroProcesso}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{GRUPO_LABEL[m.grupo] ?? m.grupo}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-col">
                      <span>{m.nomePessoa ?? "—"}</span>
                      {m.cpfCnpj ? (
                        <span className="font-mono text-xs text-muted-foreground">{m.cpfCnpj}</span>
                      ) : null}
                    </div>
                  </TableCell>
                  <TableCell className="max-w-52 truncate text-xs" title={m.nomeOrgao ?? undefined}>
                    {m.nomeOrgao ?? "—"}
                  </TableCell>
                  <TableCell className="font-mono text-xs">
                    {formatDate(m.dataNotificacao)}
                  </TableCell>
                  <TableCell className="font-mono text-xs">
                    {formatDate(m.dataRecebimentoAr)}
                  </TableCell>
                  <TableCell className="font-mono text-xs">{formatDate(m.dataResposta)}</TableCell>
                  <TableCell>{descontoBadge(m)}</TableCell>
                  <TableCell className="text-right">
                    {m.valorOriginal != null ? formatBRL(m.valorOriginal) : "—"}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      {m.cpfCnpj && m.idFrapDescontoFolha ? (
                        <Link
                          href={`/ccd/desconto-folha/${encodeURIComponent(m.cpfCnpj)}`}
                          className="text-xs underline underline-offset-2"
                        >
                          Parcelas
                        </Link>
                      ) : null}
                      <Button size="sm" variant="outline" onClick={() => setEditando(m)}>
                        Editar
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => void handleDelete(m)}>
                        Excluir
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <Paginacao
        page={page}
        totalPages={totalPages}
        setPage={(p) => void setPage(p)}
        disabled={isFetching}
      />

      <MonitoramentoFormDialog open={criarOpen} item={null} onOpenChange={setCriarOpen} />
      <MonitoramentoFormDialog
        open={editando !== null}
        item={editando}
        onOpenChange={(open) => {
          if (!open) setEditando(null);
        }}
      />
    </div>
  );
}

function descontoBadge(m: MonitoramentoItem) {
  const implantado = (m.descFolhaTexto ?? "").trim().toUpperCase().startsWith("S");
  if (implantado) return <Badge variant="success">Sim</Badge>;
  if (m.descFolhaTexto) return <Badge variant="outline">{m.descFolhaTexto}</Badge>;
  return <span className="text-muted-foreground">—</span>;
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-xl font-semibold">{value.toLocaleString("pt-BR")}</p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Form (criar/editar) — campos espelham a planilha aposentada
// ---------------------------------------------------------------------------

type FieldDef = {
  key: keyof MonitoramentoPayload & string;
  label: string;
  tipo: "text" | "date" | "number";
};

const CAMPOS_FLUXO: FieldDef[] = [
  { key: "dataDespacho", label: "Despacho", tipo: "date" },
  { key: "dataNotificacao", label: "Notificação", tipo: "date" },
  { key: "dataRecebimentoAr", label: "Recebimento AR", tipo: "date" },
  { key: "dataResposta", label: "Resposta", tipo: "date" },
  { key: "dataSegundaNotificacao", label: "2ª notificação", tipo: "date" },
  { key: "dataRecebimentoAr2", label: "AR da 2ª notificação", tipo: "date" },
];

const CAMPOS_PAGAMENTO: FieldDef[] = [
  { key: "descFolhaTexto", label: "Desc. folha", tipo: "text" },
  { key: "transfFrap", label: "Transf. FRAP", tipo: "text" },
  { key: "pagoSiteTce", label: "Pago site TCE", tipo: "text" },
  { key: "tipoPagamento", label: "Tipo de pagamento", tipo: "text" },
  { key: "remanescente", label: "Remanescente", tipo: "text" },
  { key: "apr", label: "APR", tipo: "text" },
  { key: "valorOriginal", label: "Valor original (R$)", tipo: "number" },
];

const CAMPOS_NEREU: FieldDef[] = [
  { key: "relator", label: "Relator", tipo: "text" },
  { key: "valorImplementado", label: "Valor implementado (R$)", tipo: "number" },
  { key: "dataImplementacao", label: "Data de implementação", tipo: "date" },
  { key: "verificadoSiaidp", label: "Verificado no SIAI DP", tipo: "text" },
  { key: "verificadoFrap", label: "Verificado no FRAP", tipo: "text" },
];

const CAMPOS_FORM: FieldDef[] = [
  { key: "numeroProcesso", label: "", tipo: "text" },
  { key: "nomePessoa", label: "", tipo: "text" },
  { key: "cpfCnpj", label: "", tipo: "text" },
  { key: "processoSei", label: "", tipo: "text" },
  { key: "nomeOrgao", label: "", tipo: "text" },
  { key: "observacoes", label: "", tipo: "text" },
  ...CAMPOS_FLUXO,
  ...CAMPOS_PAGAMENTO,
  ...CAMPOS_NEREU,
];

type FormState = Record<string, string>;

function itemToForm(item: MonitoramentoItem | null): FormState {
  const f: FormState = {};
  for (const c of CAMPOS_FORM) {
    const v = item?.[c.key as keyof MonitoramentoItem];
    f[c.key] = v == null ? "" : String(v);
  }
  f.grupo = item?.grupo ?? "GERAL";
  f.esferaOrgao = item?.esferaOrgao ?? "";
  f.cadastradoDescontoFolha =
    item?.cadastradoDescontoFolha == null ? "" : item.cadastradoDescontoFolha ? "S" : "N";
  return f;
}

function formToPayload(f: FormState): MonitoramentoPayload {
  const payload: MonitoramentoPayload = {
    grupo: f.grupo as GrupoMonitoramento,
    esferaOrgao: f.esferaOrgao || null,
    cadastradoDescontoFolha:
      f.cadastradoDescontoFolha === "" ? null : f.cadastradoDescontoFolha === "S",
  };
  for (const c of CAMPOS_FORM) {
    const raw = (f[c.key] ?? "").trim();
    if (c.tipo === "number") {
      const n = raw === "" ? null : Number(raw.replace(",", "."));
      (payload as Record<string, unknown>)[c.key] = n != null && Number.isNaN(n) ? null : n;
    } else {
      (payload as Record<string, unknown>)[c.key] = raw === "" ? null : raw;
    }
  }
  return payload;
}

function MonitoramentoFormDialog({
  open,
  item,
  onOpenChange,
}: {
  open: boolean;
  item: MonitoramentoItem | null;
  onOpenChange: (o: boolean) => void;
}) {
  const criar = useCriarMonitoramento();
  const atualizar = useAtualizarMonitoramento();
  const [f, setF] = useState<FormState>(() => itemToForm(null));
  const pending = criar.isPending || atualizar.isPending;
  const { data: pessoas } = usePessoasProcesso(open ? (f.numeroProcesso ?? "") : "");
  const { data: orgaos } = useOrgaos();
  const pessoasDatalistId = useId();
  const orgaosDatalistId = useId();

  useEffect(() => {
    if (open) setF(itemToForm(item));
  }, [open, item]);

  function set(key: string, value: string) {
    setF((prev) => ({ ...prev, [key]: value }));
  }

  async function onSubmit() {
    const payload = formToPayload(f);
    if (!payload.numeroProcesso) {
      toast.error("Informe o número do processo (NNNNNN/AAAA).");
      return;
    }
    try {
      if (item) {
        await atualizar.mutateAsync({ id: item.idMonitoramento, payload });
        toast.success("Registro atualizado.");
      } else {
        await criar.mutateAsync(payload);
        toast.success("Processo adicionado ao monitoramento.");
      }
      onOpenChange(false);
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      toast.error(
        status === 409
          ? "Este processo/responsável já está monitorado neste grupo."
          : "Falha ao salvar.",
      );
    }
  }

  function campo(key: string, label: string, tipo: "text" | "date" | "number" = "text") {
    return (
      <div className="flex flex-col gap-1.5">
        <Label htmlFor={`mf-${key}`}>{label}</Label>
        <Input
          id={`mf-${key}`}
          type={tipo === "date" ? "date" : "text"}
          inputMode={tipo === "number" ? "decimal" : undefined}
          value={f[key] ?? ""}
          onChange={(e) => set(key, e.target.value)}
        />
      </div>
    );
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[85vh] max-w-3xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{item ? `Editar ${item.numeroProcesso}` : "Novo processo"}</DialogTitle>
          <DialogDescription>
            Registro de monitoramento de desconto em folha (substitui a planilha).
          </DialogDescription>
        </DialogHeader>

        {(pessoas ?? []).length > 0 && (
          <datalist id={pessoasDatalistId}>
            {(pessoas ?? []).map((p) => (
              <option key={`${p.nome}-${p.documento ?? ""}`} value={p.nome} />
            ))}
          </datalist>
        )}
        {(orgaos ?? []).length > 0 && (
          <datalist id={orgaosDatalistId}>
            {(orgaos ?? []).map((o) => (
              <option key={o.id} value={o.nome} />
            ))}
          </datalist>
        )}

        <div className="flex flex-col gap-5">
          <div className="grid gap-3 md:grid-cols-3">
            {campo("numeroProcesso", "Processo (NNNNNN/AAAA)")}
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="mf-grupo">Grupo</Label>
              <SelectNative
                id="mf-grupo"
                value={f.grupo}
                onChange={(e) => set("grupo", e.target.value)}
              >
                {GRUPOS_MONITORAMENTO.map((g) => (
                  <option key={g} value={g}>
                    {GRUPO_LABEL[g]}
                  </option>
                ))}
              </SelectNative>
            </div>
            {campo("processoSei", "Processo SEI")}
            <PessoaField
              label="Responsável"
              value={f.nomePessoa}
              pessoas={pessoas ?? []}
              disabled={pending}
              datalistId={pessoasDatalistId}
              onPick={(nome, documento) =>
                setF((prev) => ({
                  ...prev,
                  nomePessoa: nome ?? "",
                  ...(documento !== undefined ? { cpfCnpj: documento ?? "" } : {}),
                }))
              }
            />
            {campo("cpfCnpj", "CPF/CNPJ")}
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="mf-esfera">Esfera</Label>
              <SelectNative
                id="mf-esfera"
                value={f.esferaOrgao}
                onChange={(e) => set("esferaOrgao", e.target.value)}
              >
                <option value="">—</option>
                <option value="ESTADUAL">Estadual</option>
                <option value="MUNICIPAL">Municipal</option>
              </SelectNative>
            </div>
            <OrgaoField
              label="Órgão"
              value={f.nomeOrgao}
              orgaos={orgaos ?? []}
              disabled={pending}
              datalistId={orgaosDatalistId}
              onPick={(nome) => set("nomeOrgao", nome ?? "")}
            />
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="mf-cadastrado">Cadastrado DF</Label>
              <SelectNative
                id="mf-cadastrado"
                value={f.cadastradoDescontoFolha}
                onChange={(e) => set("cadastradoDescontoFolha", e.target.value)}
              >
                <option value="">—</option>
                <option value="S">Sim</option>
                <option value="N">Não</option>
              </SelectNative>
            </div>
          </div>

          <fieldset className="flex flex-col gap-2">
            <legend className="text-sm font-medium">Fluxo de notificação</legend>
            <div className="grid gap-3 md:grid-cols-3">
              {CAMPOS_FLUXO.map((c) => campo(c.key, c.label, c.tipo))}
            </div>
          </fieldset>

          <fieldset className="flex flex-col gap-2">
            <legend className="text-sm font-medium">Desconto e pagamento</legend>
            <div className="grid gap-3 md:grid-cols-3">
              {CAMPOS_PAGAMENTO.map((c) => campo(c.key, c.label, c.tipo))}
            </div>
          </fieldset>

          {f.grupo === "NEREU" ? (
            <fieldset className="flex flex-col gap-2">
              <legend className="text-sm font-medium">Acompanhamento Nereu</legend>
              <div className="grid gap-3 md:grid-cols-3">
                {CAMPOS_NEREU.map((c) => campo(c.key, c.label, c.tipo))}
              </div>
            </fieldset>
          ) : null}

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="mf-observacoes">Observações</Label>
            <Textarea
              id="mf-observacoes"
              rows={3}
              value={f.observacoes ?? ""}
              onChange={(e) => set("observacoes", e.target.value)}
            />
          </div>
        </div>

        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button type="button" disabled={pending} onClick={() => void onSubmit()}>
            {pending ? "Salvando..." : "Salvar"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
