"use client";

import type { ReactNode } from "react";

import { Badge } from "@/components/ui/badge";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { useBeneficiosDominios } from "@/hooks/use-beneficios";
import { formatBRL, formatCpf, formatDate } from "@/lib/format";
import type { BeneficioItem, DominioItem } from "@/schemas/beneficios";

import { ORIGEM_LABEL } from "./_beneficios-lista";

const ECONTAS = "https://processos.tce.rn.gov.br/#/dashboard/processos";

function desc(itens: DominioItem[] | undefined, id: number | null | undefined): string {
  if (id == null) return "—";
  return itens?.find((d) => d.id === id)?.descricao ?? String(id);
}

function dataHora(iso: string | null | undefined): string {
  if (!iso) return "—";
  const [data, hora] = iso.split("T");
  return hora ? `${formatDate(data)} ${hora.slice(0, 5)}` : formatDate(data);
}

function Campo({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex flex-col gap-0.5">
      <dt className="text-muted-foreground text-xs">{label}</dt>
      <dd className="text-sm">{children ?? "—"}</dd>
    </div>
  );
}

function Texto({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <Campo label={label}>
      {value ? <span className="whitespace-pre-wrap">{value}</span> : "—"}
    </Campo>
  );
}

export function BeneficioDetalhe({
  item,
  onClose,
}: {
  item: BeneficioItem | null;
  onClose: () => void;
}) {
  const { data: dom } = useBeneficiosDominios();
  const b = item;

  return (
    <Sheet open={b !== null} onOpenChange={(open) => (open ? null : onClose())}>
      <SheetContent>
        {b ? (
          <div className="flex flex-col gap-5">
            <SheetHeader>
              <SheetTitle>Benefício #{b.idBeneficio}</SheetTitle>
              <SheetDescription>{b.descricao}</SheetDescription>
              <div className="flex flex-wrap gap-2">
                {b.idSituacaoEfetivacao === 2 ? (
                  <Badge variant="outline">Potencial</Badge>
                ) : b.idSituacaoEfetivacao === 1 ? (
                  <Badge variant="success">Efetivo</Badge>
                ) : null}
                <Badge variant="outline">{ORIGEM_LABEL[b.origem] ?? b.origem}</Badge>
              </div>
            </SheetHeader>

            <dl className="grid grid-cols-2 gap-3">
              <Campo label="Processo">
                {b.numeroProcessoDecisao ? (
                  b.idProcessoDecisao ? (
                    <a
                      className="text-primary underline"
                      href={`${ECONTAS}/${b.idProcessoDecisao}`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {b.numeroProcessoDecisao}/{b.anoProcessoDecisao ?? "?"}
                    </a>
                  ) : (
                    `${b.numeroProcessoDecisao}/${b.anoProcessoDecisao ?? "?"}`
                  )
                ) : (
                  "—"
                )}
              </Campo>
              <Campo label="Valor / quantidade">
                {b.valorQuantidade ? formatBRL(Number(b.valorQuantidade)) : "—"}
              </Campo>
              <Campo label="Pessoa">{b.nomePessoa ?? "—"}</Campo>
              <Campo label="CPF/CNPJ">{formatCpf(b.cpfCnpj)}</Campo>
              <Campo label="Data da ocorrência">{formatDate(b.dataOcorrencia)}</Campo>
              <Campo label="Unidade de medida">
                {desc(dom?.unidadesMedida, b.idUnidadeMedida)}
              </Campo>
              <Campo label="Tipo">{desc(dom?.tipos, b.idTipo)}</Campo>
              <Campo label="Subtipo">{desc(dom?.subtipos, b.idSubtipo)}</Campo>
              <Campo label="Área temática">{desc(dom?.areasTematicas, b.idAreaTematica)}</Campo>
              <Campo label="Característica">{desc(dom?.caracterizacoes, b.idCaracterizacao)}</Campo>
              <Campo label="Situação">{desc(dom?.situacoes, b.idSituacao)}</Campo>
              <Campo label="Estágio">
                {desc(dom?.situacoesEfetivacao, b.idSituacaoEfetivacao)}
              </Campo>
            </dl>

            <dl className="flex flex-col gap-3">
              <Texto label="Memória de cálculo" value={b.memoriaCalculo} />
              <Texto label="Justificativa" value={b.justificativa} />
              <Texto label="Motivo / observações" value={b.descricaoMotivo} />
            </dl>

            <dl className="text-muted-foreground grid grid-cols-2 gap-3 border-t pt-3">
              <Campo label="Chave de origem">{b.chaveOrigem ?? "—"}</Campo>
              <Campo label="Débito (Exe_Debito)">{b.idDebitoExecucao ?? "—"}</Campo>
              <Campo label="Potencial vinculado">
                {b.idBeneficioPotencial ? `#${b.idBeneficioPotencial}` : "—"}
              </Campo>
              <Campo label="Id do processo">{b.idProcessoDecisao ?? "—"}</Campo>
              <Campo label="Incluído em">{dataHora(b.dataInclusao)}</Campo>
              <Campo label="Atualizado em">{dataHora(b.dataAtualizacao)}</Campo>
            </dl>
          </div>
        ) : null}
      </SheetContent>
    </Sheet>
  );
}
