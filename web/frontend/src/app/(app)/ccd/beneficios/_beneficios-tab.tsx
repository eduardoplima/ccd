"use client";

import { parseAsInteger, parseAsString, parseAsStringEnum, useQueryState } from "nuqs";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
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
import {
  useBeneficios,
  useBeneficiosDominios,
  useDeletarBeneficio,
  useTransicionarBeneficio,
} from "@/hooks/use-beneficios";
import { formatBRL, formatDate } from "@/lib/format";
import {
  ORIGENS_BENEFICIO,
  STATUS_BENEFICIO,
  type BeneficioItem,
  type OrigemBeneficio,
  type StatusBeneficio,
} from "@/schemas/beneficios";

import { Paginacao } from "./_paginacao";

const SIZE = 50;

const ORIGEM_LABEL: Record<OrigemBeneficio, string> = {
  MANUAL: "Manual",
  DEBITO: "Débito (potencial)",
  BOLETO: "Boleto pago",
  PGE: "Repasse PGE",
  FOLHA: "Desconto em folha",
  DIVIDA_ATIVA: "Dívida ativa",
  FRAP: "FRAP",
  PROPOSTA: "Proposta UTCE",
};

const STATUS_LABEL: Record<StatusBeneficio, string> = {
  RASCUNHO: "Rascunho",
  VALIDADO: "Validado",
  ENVIADO: "Enviado",
  DESCARTADO: "Descartado",
};

// Origens da carteira com detecção ativa na v1 (FOLHA/DIVIDA_ATIVA/FRAP desligadas).
const ORIGENS_ATIVAS = [
  "MANUAL",
  "DEBITO",
  "BOLETO",
  "PGE",
] as const satisfies readonly OrigemBeneficio[];

// Ações por status: [rótulo, status destino]
const ACOES: Record<StatusBeneficio, Array<[string, StatusBeneficio]>> = {
  RASCUNHO: [
    ["Validar", "VALIDADO"],
    ["Descartar", "DESCARTADO"],
  ],
  VALIDADO: [
    ["Devolver", "RASCUNHO"],
    ["Descartar", "DESCARTADO"],
  ],
  ENVIADO: [["Desfazer envio", "VALIDADO"]],
  DESCARTADO: [["Restaurar", "RASCUNHO"]],
};

export function BeneficiosTab({
  status,
  fonte,
  selecao,
  onSelecao,
  onEditar,
}: {
  status?: StatusBeneficio;
  fonte?: "propostas" | "carteira";
  selecao?: Set<number>;
  onSelecao?: (ids: Set<number>) => void;
  onEditar: (item: BeneficioItem) => void;
}) {
  const prefixo = status ? status.toLowerCase().slice(0, 1) : "pp";
  const [q, setQ] = useQueryState(`${prefixo}q`, parseAsString.withDefault(""));
  const [page, setPage] = useQueryState(`${prefixo}page`, parseAsInteger.withDefault(1));
  const [origem, setOrigem] = useQueryState(
    `${prefixo}origem`,
    parseAsStringEnum<OrigemBeneficio>([...ORIGENS_BENEFICIO]),
  );
  const [efetivacao, setEfetivacao] = useQueryState(`${prefixo}efet`, parseAsInteger);
  // Aba sem status fixo (Propostas): filtro de status próprio.
  const [statusFiltro, setStatusFiltro] = useQueryState(
    `${prefixo}st`,
    parseAsStringEnum<StatusBeneficio>([...STATUS_BENEFICIO]),
  );

  const { data, isFetching } = useBeneficios({
    q: q || undefined,
    status: status ?? statusFiltro ?? undefined,
    origem: origem ?? undefined,
    fonte,
    situacaoEfetivacao: efetivacao ?? undefined,
    page,
    size: SIZE,
    sortBy: "dataInclusao",
    sortDir: "desc",
  });
  const { data: dominios } = useBeneficiosDominios();
  const transicionar = useTransicionarBeneficio();
  const deletar = useDeletarBeneficio();

  const items = data?.items ?? [];
  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / SIZE));
  const tipoDesc = new Map((dominios?.tipos ?? []).map((d) => [d.id, d.descricao]));

  const comSelecao = !!selecao && !!onSelecao;
  const colunas = 8 + (comSelecao ? 1 : 0) + (status ? 0 : 1) + (status === "ENVIADO" ? 1 : 0);

  async function agir(item: BeneficioItem, destino: StatusBeneficio, rotulo: string) {
    try {
      await transicionar.mutateAsync({ id: item.idBeneficio, status: destino });
      toast.success(`${rotulo}: ok.`);
    } catch (err) {
      const resp = (err as { response?: { status?: number; data?: { detail?: string } } }).response;
      toast.error(resp?.data?.detail ?? `Falha ao ${rotulo.toLowerCase()}.`);
    }
  }

  async function remover(item: BeneficioItem) {
    if (!confirm("Excluir este benefício criado manualmente?")) return;
    try {
      await deletar.mutateAsync(item.idBeneficio);
      toast.success("Benefício excluído.");
    } catch {
      toast.error("Falha ao excluir (candidatos detectados devem ser descartados).");
    }
  }

  function toggleSelecao(id: number) {
    if (!selecao || !onSelecao) return;
    const nova = new Set(selecao);
    if (nova.has(id)) nova.delete(id);
    else nova.add(id);
    onSelecao(nova);
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center gap-2">
        <Input
          value={q}
          onChange={(e) => {
            void setQ(e.target.value);
            void setPage(1);
          }}
          placeholder="Buscar processo, pessoa, CPF ou descrição..."
          className="max-w-md"
        />
        {fonte === "propostas" ? (
          <SelectNative
            value={statusFiltro ?? ""}
            onChange={(e) => {
              void setStatusFiltro((e.target.value || null) as StatusBeneficio | null);
              void setPage(1);
            }}
            className="w-40"
          >
            <option value="">Todos os status</option>
            {STATUS_BENEFICIO.map((s) => (
              <option key={s} value={s}>
                {STATUS_LABEL[s]}
              </option>
            ))}
          </SelectNative>
        ) : (
          <SelectNative
            value={origem ?? ""}
            onChange={(e) => {
              void setOrigem((e.target.value || null) as OrigemBeneficio | null);
              void setPage(1);
            }}
            className="w-44"
          >
            <option value="">Todas as origens</option>
            {ORIGENS_ATIVAS.map((o) => (
              <option key={o} value={o}>
                {ORIGEM_LABEL[o]}
              </option>
            ))}
          </SelectNative>
        )}
        <SelectNative
          value={efetivacao?.toString() ?? ""}
          onChange={(e) => {
            void setEfetivacao(e.target.value ? Number(e.target.value) : null);
            void setPage(1);
          }}
          className="w-40"
        >
          <option value="">Todos os estágios</option>
          <option value="2">Potencial</option>
          <option value="1">Efetivo</option>
        </SelectNative>
        <span className="text-muted-foreground ml-auto text-sm">{total} registro(s)</span>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            {comSelecao ? <TableHead className="w-8" /> : null}
            <TableHead>Processo</TableHead>
            <TableHead>Pessoa</TableHead>
            <TableHead>Estágio</TableHead>
            <TableHead>Tipo</TableHead>
            <TableHead>Origem</TableHead>
            {status ? null : <TableHead>Status</TableHead>}
            <TableHead className="text-right">Valor</TableHead>
            <TableHead>Ocorrência</TableHead>
            {status === "ENVIADO" ? <TableHead>Lote</TableHead> : null}
            <TableHead>Ações</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {items.length === 0 && !isFetching ? (
            <TableRow>
              <TableCell colSpan={colunas} className="text-muted-foreground text-center">
                Nenhum registro.
              </TableCell>
            </TableRow>
          ) : (
            items.map((b) => (
              <TableRow key={b.idBeneficio}>
                {comSelecao ? (
                  <TableCell>
                    {b.status === "VALIDADO" ? (
                      <Checkbox
                        checked={selecao.has(b.idBeneficio)}
                        onCheckedChange={() => toggleSelecao(b.idBeneficio)}
                      />
                    ) : null}
                  </TableCell>
                ) : null}
                <TableCell>
                  {b.numeroProcessoDecisao
                    ? `${b.numeroProcessoDecisao}/${b.anoProcessoDecisao ?? "?"}`
                    : "—"}
                </TableCell>
                <TableCell className="max-w-56 truncate" title={b.nomePessoa ?? undefined}>
                  {b.nomePessoa ?? "—"}
                </TableCell>
                <TableCell>
                  {b.idSituacaoEfetivacao === 2 ? (
                    <Badge variant="outline">Potencial</Badge>
                  ) : b.idSituacaoEfetivacao === 1 ? (
                    <Badge variant="success">Efetivo</Badge>
                  ) : (
                    "—"
                  )}
                </TableCell>
                <TableCell
                  className="max-w-48 truncate"
                  title={b.idTipo ? tipoDesc.get(b.idTipo) : undefined}
                >
                  {b.idTipo ? (tipoDesc.get(b.idTipo) ?? b.idTipo) : "—"}
                </TableCell>
                <TableCell>{ORIGEM_LABEL[b.origem] ?? b.origem}</TableCell>
                {status ? null : (
                  <TableCell>
                    <Badge variant={b.status === "ENVIADO" ? "success" : "outline"}>
                      {STATUS_LABEL[b.status]}
                    </Badge>
                  </TableCell>
                )}
                <TableCell className="text-right">
                  {b.valorQuantidade ? formatBRL(Number(b.valorQuantidade)) : "—"}
                </TableCell>
                <TableCell>{b.dataOcorrencia ? formatDate(b.dataOcorrencia) : "—"}</TableCell>
                {status === "ENVIADO" ? <TableCell>{b.loteEnvio ?? "—"}</TableCell> : null}
                <TableCell>
                  <div className="flex flex-wrap gap-1">
                    {b.status !== "ENVIADO" ? (
                      <Button size="sm" variant="outline" onClick={() => onEditar(b)}>
                        Editar
                      </Button>
                    ) : null}
                    {ACOES[b.status].map(([rotulo, destino]) => (
                      <Button
                        key={rotulo}
                        size="sm"
                        variant={rotulo === "Validar" ? "default" : "outline"}
                        disabled={transicionar.isPending}
                        onClick={() => void agir(b, destino, rotulo)}
                      >
                        {rotulo}
                      </Button>
                    ))}
                    {b.status === "RASCUNHO" && b.origem === "MANUAL" ? (
                      <Button size="sm" variant="outline" onClick={() => void remover(b)}>
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

      <Paginacao page={page} totalPages={totalPages} setPage={(p) => void setPage(p)} />
    </div>
  );
}
