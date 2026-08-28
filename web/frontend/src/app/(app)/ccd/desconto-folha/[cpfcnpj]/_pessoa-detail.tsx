"use client";

import { useRouter } from "next/navigation";
import { Fragment, useState } from "react";
import { toast } from "sonner";

import { SortableHead, useClientSort } from "@/components/sortable-table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
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
import { useCurrentUser } from "@/hooks/use-current-user";
import {
  useAtribuirOrgaoPessoa,
  useCriarMatchManual,
  useDeletarMatchManual,
  useOrgaosDisponiveis,
  useParcelasPessoa,
} from "@/hooks/use-desconto-folha";
import { useLancamento } from "@/hooks/use-lancamento";
import { useLancamentos } from "@/hooks/use-lancamentos";
import { formatBRL, formatDate, matchStatusVariant } from "@/lib/format";
import type { ParcelaPessoaItem } from "@/schemas/desconto-folha";

import { FasesSummary } from "../_fases-summary";

const STATUS_ATRASO = new Set(["NAO_DESCONTADA", "DESCONTADA_SEM_REPASSE", "BAIXADA_SEM_RASTRO"]);

type ParcelaSortKey = "mesAno" | "numero" | "esperado" | "pago" | "status" | "vencimento";

const PARCELA_GETTERS: Record<
  ParcelaSortKey,
  (p: ParcelaPessoaItem) => string | number | null | undefined
> = {
  mesAno: (p) => (p.anoReferencia ?? 0) * 12 + (p.mesReferencia ?? 0),
  numero: (p) => p.numeroParcela,
  esperado: (p) => p.valorEsperado,
  pago: (p) => p.valorContracheque,
  status: (p) => p.statusCodigo ?? "",
  vencimento: (p) => p.dataVencimento,
};

export function PessoaDetail({ cpfCnpj }: { cpfCnpj: string }) {
  const router = useRouter();
  const { data: me } = useCurrentUser();
  const isAdmin = me?.papel === "admin";
  const { data, isFetching } = useParcelasPessoa(cpfCnpj);
  const [selecionadas, setSelecionadas] = useState<Set<number>>(new Set());

  function toggle(id: number) {
    setSelecionadas((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          ← Voltar
        </Button>
        <div>
          <h1 className="section-heading text-2xl">{data?.nomePessoa ?? cpfCnpj}</h1>
          <p className="font-mono text-xs text-muted-foreground">{cpfCnpj}</p>
        </div>
      </div>

      <div className="flex flex-col gap-4">
        <FasesSummary cpfCnpj={cpfCnpj} />
        {!isFetching && data && !data.nomeOrgaoNotificado ? (
          <SemOrgaoBanner cpfCnpj={cpfCnpj} isAdmin={!!isAdmin} />
        ) : null}
        {isFetching ? (
          <p className="text-sm text-muted-foreground">Carregando...</p>
        ) : (
          <>
            <ParcelasTable
              parcelas={data?.parcelas ?? []}
              isAdmin={!!isAdmin}
              selecionadas={selecionadas}
              onToggle={toggle}
            />
            {isAdmin ? (
              <MatchManualBar
                cpfCnpj={cpfCnpj}
                selecionadas={selecionadas}
                onLimpar={() => setSelecionadas(new Set())}
              />
            ) : null}
          </>
        )}
      </div>
    </div>
  );
}

export function ParcelasTable({
  parcelas,
  isAdmin,
  selecionadas,
  onToggle,
}: {
  parcelas: ParcelaPessoaItem[];
  isAdmin: boolean;
  selecionadas: Set<number>;
  onToggle: (id: number) => void;
}) {
  const { sorted, sort, toggle } = useClientSort<ParcelaPessoaItem, ParcelaSortKey>(
    parcelas,
    PARCELA_GETTERS,
  );
  const [expandedParcelaId, setExpandedParcelaId] = useState<number | null>(null);
  const colCount = isAdmin ? 8 : 6;
  return (
    <Table>
      <TableHeader>
        <TableRow>
          {isAdmin ? <TableHead className="w-8"></TableHead> : null}
          <SortableHead label="Mês/Ano" col="mesAno" sort={sort} onClick={toggle} />
          <SortableHead label="Nº" col="numero" sort={sort} onClick={toggle} />
          <SortableHead
            label="Esperado"
            col="esperado"
            sort={sort}
            onClick={toggle}
            align="right"
          />
          <SortableHead label="Pago" col="pago" sort={sort} onClick={toggle} align="right" />
          <SortableHead label="Status" col="status" sort={sort} onClick={toggle} />
          <SortableHead label="Vencimento" col="vencimento" sort={sort} onClick={toggle} />
          {isAdmin ? <TableHead className="w-20"></TableHead> : null}
        </TableRow>
      </TableHeader>
      <TableBody>
        {sorted.map((p) => {
          const podeSelecionar =
            isAdmin &&
            p.idParcela !== null &&
            p.idParcela !== undefined &&
            !!p.statusCodigo &&
            STATUS_ATRASO.has(p.statusCodigo);
          const checked = p.idParcela != null && selecionadas.has(p.idParcela);
          const idLancMatch = p.idLancamentoFrap ?? null;
          const isExpandable = idLancMatch !== null && p.idParcela != null;
          const isExpanded = isExpandable && expandedParcelaId === p.idParcela;
          return (
            <Fragment key={p.idParcela ?? `p-${p.idDescontoFolha}`}>
              <TableRow
                className={
                  (checked ? "bg-amber-50/40 " : "") +
                  (isExpandable ? "cursor-pointer hover:bg-muted/40 " : "") +
                  (isExpanded ? "bg-muted/30 " : "")
                }
                onClick={() => {
                  if (!isExpandable || p.idParcela == null) return;
                  setExpandedParcelaId(isExpanded ? null : p.idParcela);
                }}
              >
                {isAdmin ? (
                  <TableCell onClick={(e) => e.stopPropagation()}>
                    {podeSelecionar && p.idParcela != null ? (
                      <Checkbox checked={checked} onCheckedChange={() => onToggle(p.idParcela!)} />
                    ) : null}
                  </TableCell>
                ) : null}
                <TableCell className="font-mono text-xs">
                  {`${String(p.mesReferencia ?? 0).padStart(2, "0")}/${p.anoReferencia}`}
                </TableCell>
                <TableCell>{p.numeroParcela}</TableCell>
                <TableCell className="text-right">{formatBRL(p.valorEsperado)}</TableCell>
                <TableCell className="text-right">
                  {p.valorContracheque !== null && p.valorContracheque !== undefined
                    ? formatBRL(p.valorContracheque)
                    : "—"}
                </TableCell>
                <TableCell>
                  {p.statusCodigo ? (
                    <Badge variant={matchStatusVariant(p.statusCodigo)}>
                      {p.statusCodigo}
                      {p.isManual ? " ✓" : ""}
                    </Badge>
                  ) : (
                    <span className="text-xs text-muted-foreground">—</span>
                  )}
                </TableCell>
                <TableCell className="font-mono text-xs">
                  {formatDate(p.dataVencimento ?? null)}
                </TableCell>
                {isAdmin ? (
                  <TableCell onClick={(e) => e.stopPropagation()}>
                    {p.isManual && p.idMatch ? <DesfazerBotao idMatch={p.idMatch} /> : null}
                  </TableCell>
                ) : null}
              </TableRow>
              {isExpanded && idLancMatch !== null ? (
                <TableRow className="bg-muted/20 hover:bg-muted/20">
                  <TableCell colSpan={colCount} className="p-0">
                    <LancamentoInline idLancamento={idLancMatch} />
                  </TableCell>
                </TableRow>
              ) : null}
            </Fragment>
          );
        })}
      </TableBody>
    </Table>
  );
}

function LancamentoInline({ idLancamento }: { idLancamento: number }) {
  const { data, isLoading, isError } = useLancamento(idLancamento);
  return (
    <div className="border-l-4 border-[var(--brand-accent)] bg-background/60 p-4">
      <h4 className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
        Lançamento conciliado #{idLancamento}
      </h4>
      {isLoading ? (
        <p className="text-xs text-muted-foreground">Carregando...</p>
      ) : isError || !data ? (
        <p className="text-xs text-destructive">Erro ao carregar lançamento.</p>
      ) : (
        <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm md:grid-cols-4">
          <InlineField label="Data" value={formatDate(data.dtMovimento)} />
          <InlineField label="Conta" value={data.conta} mono />
          <InlineField
            label={`Valor (${data.valorDC})`}
            value={`${data.valorDC === "D" ? "−" : ""}${formatBRL(data.valor)}`}
            mono
            tone={data.valorDC === "C" ? "credit" : "debit"}
          />
          <InlineField label="Categoria" value={data.categoria} />
          <InlineField label="Histórico" value={data.historico} colSpan />
          <InlineField label="Documento" value={data.documento ?? "—"} mono />
          {data.cpfcnpjDepositante ? (
            <InlineField
              label={`CPF/CNPJ depositante${data.cpfcnpjAmbiguo ? " (ambíguo)" : ""}`}
              value={data.cpfcnpjDepositante}
              mono
            />
          ) : null}
          {data.descricao ? <InlineField label="Descrição" value={data.descricao} colSpan /> : null}
        </dl>
      )}
    </div>
  );
}

function InlineField({
  label,
  value,
  mono,
  colSpan,
  tone,
}: {
  label: string;
  value: React.ReactNode;
  mono?: boolean;
  colSpan?: boolean;
  tone?: "credit" | "debit";
}) {
  const toneCls =
    tone === "credit" ? "text-emerald-700" : tone === "debit" ? "text-destructive" : "";
  return (
    <div className={colSpan ? "col-span-2 md:col-span-4" : ""}>
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className={`${mono ? "font-mono text-sm" : "text-sm"} ${toneCls}`.trim()}>{value}</dd>
    </div>
  );
}

function DesfazerBotao({ idMatch }: { idMatch: number }) {
  const desfazer = useDeletarMatchManual();
  return (
    <Button
      size="sm"
      variant="outline"
      disabled={desfazer.isPending}
      onClick={async () => {
        if (!confirm("Desfazer match manual?")) return;
        try {
          await desfazer.mutateAsync(idMatch);
          toast.success("Match desfeito.");
        } catch {
          toast.error("Falha ao desfazer.");
        }
      }}
    >
      Desfazer
    </Button>
  );
}

function MatchManualBar({
  cpfCnpj,
  selecionadas,
  onLimpar,
}: {
  cpfCnpj: string;
  selecionadas: Set<number>;
  onLimpar: () => void;
}) {
  const [idLanc, setIdLanc] = useState<number | null>(null);
  const [obs, setObs] = useState("");
  const habilitado = selecionadas.size >= 1;
  const { data: lancs, isFetching } = useLancamentos({
    cpfCnpj,
    categoria: "OB_RECEBIDA",
    page: 1,
    size: 50,
  });
  const criar = useCriarMatchManual();

  if (!habilitado) {
    return (
      <p className="rounded border border-dashed p-3 text-xs text-muted-foreground">
        Selecione 1+ parcelas em atraso para conciliar manualmente.
      </p>
    );
  }

  return (
    <div className="rounded-lg border bg-muted/20 p-3">
      <div className="mb-2 flex items-center justify-between">
        <div className="text-sm font-medium">
          Conciliar {selecionadas.size} parcela{selecionadas.size > 1 ? "s" : ""} manualmente
        </div>
        <Button size="sm" variant="ghost" onClick={onLimpar}>
          Limpar seleção
        </Button>
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="lanc">Lançamento (OB recebida)</Label>
          <SelectNative
            id="lanc"
            value={idLanc ?? ""}
            onChange={(e) => setIdLanc(e.target.value ? Number(e.target.value) : null)}
            disabled={isFetching}
          >
            <option value="">{isFetching ? "Carregando..." : "Selecione..."}</option>
            {lancs?.items.map((L) => (
              <option key={L.idLancamento} value={L.idLancamento}>
                {L.dtMovimento} · {formatBRL(Number(L.valor))} · #{L.idLancamento}
              </option>
            ))}
          </SelectNative>
          {lancs && lancs.items.length === 0 ? (
            <p className="text-xs text-muted-foreground">
              Nenhum lançamento OB_RECEBIDA encontrado para este CPF.
            </p>
          ) : null}
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="obs">Observação (opcional)</Label>
          <Input
            id="obs"
            value={obs}
            onChange={(e) => setObs(e.target.value)}
            maxLength={500}
            placeholder="ex: repasse de 3 meses do órgão X"
          />
        </div>
      </div>
      <div className="mt-3 flex justify-end">
        <Button
          size="sm"
          disabled={!idLanc || criar.isPending}
          onClick={async () => {
            if (!idLanc) return;
            try {
              await criar.mutateAsync({
                idLancamentoFrap: idLanc,
                idsParcela: [...selecionadas],
                observacao: obs || null,
              });
              toast.success("Match manual criado.");
              setObs("");
              setIdLanc(null);
              onLimpar();
            } catch {
              toast.error("Falha ao criar match.");
            }
          }}
        >
          Conciliar manualmente
        </Button>
      </div>
    </div>
  );
}

function SemOrgaoBanner({ cpfCnpj, isAdmin }: { cpfCnpj: string; isAdmin: boolean }) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <div className="flex items-center justify-between gap-3 rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm">
        <span>
          Esta pessoa está <strong>sem órgão notificado</strong>. Os matchers que dependem de órgão
          (Nível B&apos;) não são executados.
        </span>
        {isAdmin ? (
          <Button size="sm" variant="outline" onClick={() => setOpen(true)}>
            Atribuir órgão
          </Button>
        ) : null}
      </div>
      {isAdmin ? (
        <AtribuirOrgaoDialog cpfCnpj={cpfCnpj} open={open} onOpenChange={setOpen} />
      ) : null}
    </>
  );
}

function AtribuirOrgaoDialog({
  cpfCnpj,
  open,
  onOpenChange,
}: {
  cpfCnpj: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [busca, setBusca] = useState("");
  const [selecionado, setSelecionado] = useState<number | null>(null);
  const { data: orgaos, isFetching } = useOrgaosDisponiveis(busca);
  const atribuir = useAtribuirOrgaoPessoa();

  function reset() {
    setBusca("");
    setSelecionado(null);
  }

  async function salvar() {
    if (!selecionado) return;
    try {
      const res = await atribuir.mutateAsync({ cpfCnpj, idOrgao: selecionado });
      toast.success(`Órgão atribuído: ${res.nomeOrgao} (${res.qtdAtualizados} registro(s)).`);
      reset();
      onOpenChange(false);
    } catch {
      toast.error("Falha ao atribuir órgão.");
    }
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(o) => {
        onOpenChange(o);
        if (!o) reset();
      }}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Atribuir órgão notificado</DialogTitle>
          <DialogDescription>
            Atribui órgão a todos os registros ativos deste CPF que estão sem órgão.
          </DialogDescription>
        </DialogHeader>
        <div className="flex flex-col gap-3">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="busca-orgao">Buscar órgão</Label>
            <Input
              id="busca-orgao"
              placeholder="Digite parte do nome (mín. 2 caracteres)"
              value={busca}
              onChange={(e) => {
                setBusca(e.target.value);
                setSelecionado(null);
              }}
              autoFocus
            />
          </div>
          <div className="max-h-64 overflow-y-auto rounded-md border">
            {busca.length < 2 ? (
              <p className="p-3 text-xs text-muted-foreground">
                Digite ao menos 2 caracteres para buscar.
              </p>
            ) : isFetching && !orgaos ? (
              <p className="p-3 text-xs text-muted-foreground">Carregando...</p>
            ) : !orgaos || orgaos.length === 0 ? (
              <p className="p-3 text-xs text-muted-foreground">Nenhum órgão encontrado.</p>
            ) : (
              <ul className="divide-y">
                {orgaos.map((o) => (
                  <li key={o.idOrgao}>
                    <button
                      type="button"
                      onClick={() => setSelecionado(o.idOrgao)}
                      className={
                        "w-full px-3 py-2 text-left text-sm hover:bg-muted/40 " +
                        (selecionado === o.idOrgao ? "bg-amber-50" : "")
                      }
                    >
                      {o.nomeOrgao}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button onClick={salvar} disabled={!selecionado || atribuir.isPending}>
            {atribuir.isPending ? "Salvando..." : "Atribuir"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
