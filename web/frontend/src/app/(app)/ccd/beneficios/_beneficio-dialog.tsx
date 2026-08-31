"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";

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
import { Textarea } from "@/components/ui/textarea";
import {
  useAtualizarBeneficio,
  useBeneficiosDominios,
  useCriarBeneficio,
} from "@/hooks/use-beneficios";
import type { BeneficioItem, BeneficioPayload, DominioItem } from "@/schemas/beneficios";

type FormState = Record<string, string>;

const CARACTERIZACAO_QUANT_NAO_FINANCEIRO = 4;

function itemToForm(item: BeneficioItem | null): FormState {
  if (!item) return { idSituacaoEfetivacao: "1", idSituacao: "3", idCaracterizacao: "2" };
  return {
    descricao: item.descricao ?? "",
    idSituacaoEfetivacao: item.idSituacaoEfetivacao?.toString() ?? "",
    idTipo: item.idTipo?.toString() ?? "",
    idSubtipo: item.idSubtipo?.toString() ?? "",
    idAreaTematica: item.idAreaTematica?.toString() ?? "",
    idCaracterizacao: item.idCaracterizacao?.toString() ?? "",
    idSituacao: item.idSituacao?.toString() ?? "",
    idUnidadeMedida: item.idUnidadeMedida?.toString() ?? "",
    valorQuantidade: item.valorQuantidade ?? "",
    memoriaCalculo: item.memoriaCalculo ?? "",
    justificativa: item.justificativa ?? "",
    descricaoMotivo: item.descricaoMotivo ?? "",
    numeroProcessoDecisao: item.numeroProcessoDecisao ?? "",
    anoProcessoDecisao: item.anoProcessoDecisao?.toString() ?? "",
    cpfCnpj: item.cpfCnpj ?? "",
    nomePessoa: item.nomePessoa ?? "",
    dataOcorrencia: item.dataOcorrencia ?? "",
    idBeneficioPotencial: item.idBeneficioPotencial?.toString() ?? "",
  };
}

function num(v: string | undefined): number | null {
  return v && v.trim() !== "" ? Number(v) : null;
}

function txt(v: string | undefined): string | null {
  return v && v.trim() !== "" ? v.trim() : null;
}

function formToPayload(f: FormState): BeneficioPayload {
  return {
    descricao: f.descricao?.trim() ?? "",
    idSituacaoEfetivacao: num(f.idSituacaoEfetivacao),
    idTipo: num(f.idTipo),
    idSubtipo: num(f.idSubtipo),
    idAreaTematica: num(f.idAreaTematica),
    idCaracterizacao: num(f.idCaracterizacao),
    idSituacao: num(f.idSituacao),
    idUnidadeMedida: num(f.idUnidadeMedida),
    valorQuantidade: txt(f.valorQuantidade?.replace(",", ".")),
    memoriaCalculo: txt(f.memoriaCalculo),
    justificativa: txt(f.justificativa),
    descricaoMotivo: txt(f.descricaoMotivo),
    numeroProcessoDecisao: txt(f.numeroProcessoDecisao),
    anoProcessoDecisao: num(f.anoProcessoDecisao),
    cpfCnpj: txt(f.cpfCnpj),
    nomePessoa: txt(f.nomePessoa),
    dataOcorrencia: txt(f.dataOcorrencia),
    idBeneficioPotencial: num(f.idBeneficioPotencial),
  };
}

export function BeneficioFormDialog({
  open,
  item,
  onOpenChange,
}: {
  open: boolean;
  item: BeneficioItem | null;
  onOpenChange: (open: boolean) => void;
}) {
  const { data: dominios } = useBeneficiosDominios();
  const criar = useCriarBeneficio();
  const atualizar = useAtualizarBeneficio();
  const [f, setF] = useState<FormState>({});

  useEffect(() => {
    if (open) setF(itemToForm(item));
  }, [open, item]);

  function set(key: string, value: string) {
    setF((prev) => ({ ...prev, [key]: value }));
  }

  const subtiposDoTipo: DominioItem[] = (() => {
    if (!dominios || !f.idTipo) return dominios?.subtipos ?? [];
    const permitidos = dominios.tipoSubtipos[f.idTipo] ?? [];
    return dominios.subtipos.filter((s) => permitidos.includes(s.id));
  })();

  async function salvar() {
    const payload = formToPayload(f);
    if (!payload.descricao) {
      toast.error("Informe a descrição do benefício.");
      return;
    }
    try {
      if (item) {
        await atualizar.mutateAsync({ id: item.idBeneficio, payload });
        toast.success("Benefício atualizado.");
      } else {
        await criar.mutateAsync(payload);
        toast.success("Benefício criado.");
      }
      onOpenChange(false);
    } catch (err) {
      const status = (err as { response?: { status?: number } }).response?.status;
      if (status === 409) toast.error("Benefício já enviado — desfaça o envio para editar.");
      else toast.error("Falha ao salvar o benefício.");
    }
  }

  function selectDominio(key: string, label: string, itens: DominioItem[], vazio = "—") {
    return (
      <div className="flex flex-col gap-1">
        <Label>{label}</Label>
        <SelectNative value={f[key] ?? ""} onChange={(e) => set(key, e.target.value)}>
          <option value="">{vazio}</option>
          {itens.map((d) => (
            <option key={d.id} value={d.id}>
              {d.descricao}
            </option>
          ))}
        </SelectNative>
      </div>
    );
  }

  function campo(key: string, label: string, tipo: "text" | "date" | "number" = "text") {
    return (
      <div className="flex flex-col gap-1">
        <Label>{label}</Label>
        <Input type={tipo} value={f[key] ?? ""} onChange={(e) => set(key, e.target.value)} />
      </div>
    );
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-3xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{item ? "Editar benefício" : "Novo benefício"}</DialogTitle>
          <DialogDescription>
            Caracterização conforme o Manual de Quantificação de Benefícios (domínios do
            SisBenefícios).
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-4">
          <div className="flex flex-col gap-1">
            <Label>Descrição do benefício *</Label>
            <Textarea
              rows={2}
              value={f.descricao ?? ""}
              onChange={(e) => set("descricao", e.target.value)}
            />
          </div>

          <fieldset className="grid grid-cols-2 gap-3 md:grid-cols-3">
            <legend className="text-muted-foreground mb-1 text-sm font-medium">
              Classificação
            </legend>
            {selectDominio(
              "idSituacaoEfetivacao",
              "Estágio",
              (dominios?.situacoesEfetivacao ?? []).filter((d) => d.id === 1 || d.id === 2),
            )}
            {selectDominio("idTipo", "Tipo", dominios?.tipos ?? [])}
            {selectDominio("idSubtipo", "Subtipo", subtiposDoTipo)}
            {selectDominio("idAreaTematica", "Área temática", dominios?.areasTematicas ?? [])}
            {selectDominio("idCaracterizacao", "Característica", dominios?.caracterizacoes ?? [])}
            {selectDominio("idSituacao", "Situação", dominios?.situacoes ?? [])}
            {Number(f.idCaracterizacao) === CARACTERIZACAO_QUANT_NAO_FINANCEIRO &&
              selectDominio("idUnidadeMedida", "Unidade de medida", dominios?.unidadesMedida ?? [])}
          </fieldset>

          <fieldset className="grid grid-cols-2 gap-3 md:grid-cols-3">
            <legend className="text-muted-foreground mb-1 text-sm font-medium">
              Valores e vínculos
            </legend>
            {campo("valorQuantidade", "Valor / quantidade")}
            {campo("numeroProcessoDecisao", "Processo (número)")}
            {campo("anoProcessoDecisao", "Processo (ano)", "number")}
            {campo("cpfCnpj", "CPF/CNPJ")}
            {campo("nomePessoa", "Pessoa")}
            {campo("dataOcorrencia", "Data da ocorrência", "date")}
            {campo("idBeneficioPotencial", "ID do potencial vinculado", "number")}
          </fieldset>

          <div className="flex flex-col gap-1">
            <Label>Memória de cálculo</Label>
            <Textarea
              rows={2}
              value={f.memoriaCalculo ?? ""}
              onChange={(e) => set("memoriaCalculo", e.target.value)}
            />
          </div>
          <div className="flex flex-col gap-1">
            <Label>Justificativa</Label>
            <Textarea
              rows={2}
              value={f.justificativa ?? ""}
              onChange={(e) => set("justificativa", e.target.value)}
            />
          </div>
          <div className="flex flex-col gap-1">
            <Label>Motivo / observações</Label>
            <Textarea
              rows={2}
              value={f.descricaoMotivo ?? ""}
              onChange={(e) => set("descricaoMotivo", e.target.value)}
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button onClick={() => void salvar()} disabled={criar.isPending || atualizar.isPending}>
            Salvar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
