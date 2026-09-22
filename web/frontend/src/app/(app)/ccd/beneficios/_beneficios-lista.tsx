"use client";

import { parseAsInteger, useQueryState } from "nuqs";
import { useEffect } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
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
import { useBeneficios, useBeneficiosDominios } from "@/hooks/use-beneficios";
import { formatBRL, formatDate } from "@/lib/format";
import { ORIGENS_BENEFICIO, type BeneficioItem, type OrigemBeneficio } from "@/schemas/beneficios";

import { Paginacao } from "./_paginacao";

const SIZE = 50;

export const ORIGEM_LABEL: Record<OrigemBeneficio, string> = {
  MANUAL: "Manual",
  DEBITO: "Débito (potencial)",
  BOLETO: "Boleto pago",
  PGE: "Repasse PGE",
  FOLHA: "Desconto em folha",
  DIVIDA_ATIVA: "Dívida ativa",
  FRAP: "FRAP",
  PROPOSTA: "Proposta UTCE",
};

export function BeneficiosLista({
  q,
  origem,
  dataDe,
  dataAte,
  onQ,
  onOrigem,
  onVer,
}: {
  q: string;
  origem: OrigemBeneficio | null;
  dataDe?: string;
  dataAte?: string;
  onQ: (q: string) => void;
  onOrigem: (origem: OrigemBeneficio | null) => void;
  onVer: (item: BeneficioItem) => void;
}) {
  const [page, setPage] = useQueryState("page", parseAsInteger.withDefault(1));

  const { data, isFetching } = useBeneficios({
    q: q || undefined,
    origem: origem ?? undefined,
    dataDe,
    dataAte,
    page,
    size: SIZE,
    sortBy: "dataInclusao",
    sortDir: "desc",
  });
  const { data: dominios } = useBeneficiosDominios();

  const items = data?.items ?? [];
  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / SIZE));
  // Os filtros vêm da página e mudam o total sem passar por aqui: página fora
  // do alcance volta para a 1.
  useEffect(() => {
    if (data && !isFetching && page > totalPages) void setPage(1);
  }, [data, isFetching, page, totalPages, setPage]);

  const tipoDesc = new Map((dominios?.tipos ?? []).map((d) => [d.id, d.descricao]));

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center gap-2">
        <Input
          value={q}
          onChange={(e) => {
            onQ(e.target.value);
            void setPage(1);
          }}
          placeholder="Buscar processo, pessoa, CPF ou descrição..."
          className="max-w-md"
        />
        <SelectNative
          value={origem ?? ""}
          onChange={(e) => {
            onOrigem((e.target.value || null) as OrigemBeneficio | null);
            void setPage(1);
          }}
          className="w-44"
        >
          <option value="">Todas as origens</option>
          {ORIGENS_BENEFICIO.map((o) => (
            <option key={o} value={o}>
              {ORIGEM_LABEL[o]}
            </option>
          ))}
        </SelectNative>
        <span className="text-muted-foreground ml-auto text-sm">{total} registro(s)</span>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Processo</TableHead>
            <TableHead>Pessoa</TableHead>
            <TableHead>Estágio</TableHead>
            <TableHead>Tipo</TableHead>
            <TableHead>Origem</TableHead>
            <TableHead className="text-right">Valor</TableHead>
            <TableHead>Ocorrência</TableHead>
            <TableHead className="w-16" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {items.length === 0 && !isFetching ? (
            <TableRow>
              <TableCell colSpan={8} className="text-muted-foreground text-center">
                Nenhum registro.
              </TableCell>
            </TableRow>
          ) : (
            items.map((b) => (
              <TableRow key={b.idBeneficio} className="cursor-pointer" onClick={() => onVer(b)}>
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
                <TableCell className="text-right">
                  {b.valorQuantidade ? formatBRL(Number(b.valorQuantidade)) : "—"}
                </TableCell>
                <TableCell>{b.dataOcorrencia ? formatDate(b.dataOcorrencia) : "—"}</TableCell>
                <TableCell>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={(e) => {
                      e.stopPropagation();
                      onVer(b);
                    }}
                  >
                    Ver
                  </Button>
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
