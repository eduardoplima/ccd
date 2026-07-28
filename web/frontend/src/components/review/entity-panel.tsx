"use client";

import { Plus, Trash2 } from "lucide-react";
import { useId } from "react";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { Pessoa, ReviewStatus, SolidarioMulta, TIPO_LABEL, TipoEntidade } from "@/schemas/review";
import { TIPO_SPAN_CLASS } from "@/components/review/decision-canvas";

export type EntityDraft = {
  key: string;
  tipo: TipoEntidade;
  idNer: number | null;
  serverStatus: ReviewStatus;
  reviewer?: string | null;
  serverObservacoes?: string | null;
  descricao: string;
  spanMissing: boolean;
  rejected: boolean;
  motivo: string;
  campos: Record<string, unknown>;
};

type EntityPanelProps = {
  drafts: EntityDraft[];
  pessoas: Pessoa[];
  selectedKey: string | null;
  onSelect: (key: string) => void;
  onUpdate: (key: string, patch: Partial<EntityDraft>) => void;
  onUpdateCampos: (key: string, patch: Record<string, unknown>) => void;
  onRemove: (key: string) => void;
  disabled?: boolean;
};

export function EntityPanel({
  drafts,
  pessoas,
  selectedKey,
  onSelect,
  onUpdate,
  onUpdateCampos,
  onRemove,
  disabled,
}: EntityPanelProps) {
  const datalistId = useId();

  if (drafts.length === 0) {
    return (
      <p className="rounded-md border bg-muted/30 p-4 text-sm text-muted-foreground">
        Nenhuma entidade extraída. Selecione um trecho do acórdão para adicionar.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {pessoas.length > 0 && (
        <datalist id={datalistId}>
          {pessoas.map((p) => (
            <option key={`${p.nome}-${p.documento ?? ""}`} value={p.nome} />
          ))}
        </datalist>
      )}
      {drafts.map((draft) => (
        <EntityCard
          key={draft.key}
          draft={draft}
          datalistId={datalistId}
          selected={draft.key === selectedKey}
          onSelect={() => onSelect(draft.key)}
          onUpdate={(patch) => onUpdate(draft.key, patch)}
          onUpdateCampos={(patch) => onUpdateCampos(draft.key, patch)}
          onRemove={() => onRemove(draft.key)}
          disabled={disabled}
        />
      ))}
    </div>
  );
}

function EntityCard({
  draft,
  datalistId,
  selected,
  onSelect,
  onUpdate,
  onUpdateCampos,
  onRemove,
  disabled,
}: {
  draft: EntityDraft;
  datalistId: string;
  selected: boolean;
  onSelect: () => void;
  onUpdate: (patch: Partial<EntityDraft>) => void;
  onUpdateCampos: (patch: Record<string, unknown>) => void;
  onRemove: () => void;
  disabled?: boolean;
}) {
  const readOnly = draft.serverStatus !== "pending";
  const fieldsDisabled = disabled || readOnly || draft.rejected;

  return (
    <div
      id={`entity-card-${draft.key}`}
      className={cn(
        "space-y-3 rounded-md border p-4",
        selected && "border-primary ring-1 ring-primary",
        readOnly && "opacity-70",
      )}
      onClick={onSelect}
    >
      <div className="flex flex-wrap items-center gap-2">
        <span
          className={cn("rounded px-1.5 py-0.5 text-xs font-medium", TIPO_SPAN_CLASS[draft.tipo])}
        >
          {TIPO_LABEL[draft.tipo]}
        </span>
        {draft.idNer === null && (
          <span className="rounded bg-blue-100 px-1.5 py-0.5 text-xs font-medium text-blue-950">
            Adicionada pelo revisor
          </span>
        )}
        {draft.spanMissing && draft.idNer !== null && (
          <span
            className="rounded bg-red-100 px-1.5 py-0.5 text-xs font-medium text-red-950"
            title="O trecho extraído não foi localizado no texto do acórdão."
          >
            Trecho não localizado
          </span>
        )}
        {readOnly && (
          <span className="text-xs text-muted-foreground">
            {draft.serverStatus === "approved" ? "Aprovada" : "Rejeitada"}
            {draft.reviewer ? ` por ${draft.reviewer}` : ""} (fluxo anterior)
          </span>
        )}
        <div className="ml-auto flex items-center gap-2">
          {!readOnly && draft.idNer === null && (
            <Button
              type="button"
              variant="ghost"
              size="icon"
              aria-label="Remover entidade"
              disabled={disabled}
              onClick={(e) => {
                e.stopPropagation();
                onRemove();
              }}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          )}
          {!readOnly && draft.idNer !== null && (
            <label className="flex items-center gap-2 text-xs">
              <Checkbox
                checked={draft.rejected}
                disabled={disabled}
                onCheckedChange={(checked) => onUpdate({ rejected: !!checked })}
              />
              Marcar como incorreta
            </label>
          )}
        </div>
      </div>

      {readOnly ? (
        <div className="space-y-1 text-sm">
          <p className="whitespace-pre-wrap">{draft.descricao}</p>
          {draft.serverObservacoes && (
            <p className="text-xs text-muted-foreground">Motivo: {draft.serverObservacoes}</p>
          )}
        </div>
      ) : draft.rejected ? (
        <div className="space-y-2">
          <p className="whitespace-pre-wrap text-sm text-muted-foreground line-through">
            {draft.descricao}
          </p>
          <Textarea
            rows={2}
            placeholder="Motivo da rejeição (mínimo 10 caracteres)"
            value={draft.motivo}
            disabled={disabled}
            onChange={(e) => onUpdate({ motivo: e.target.value })}
          />
        </div>
      ) : (
        <EntityFields
          tipo={draft.tipo}
          campos={draft.campos}
          onChange={onUpdateCampos}
          disabled={fieldsDisabled}
          datalistId={datalistId}
        />
      )}
    </div>
  );
}

// ----- generic controlled fields ---------------------------------------------

type FieldProps = {
  label: string;
  value: unknown;
  onChange: (value: unknown) => void;
  disabled?: boolean;
  list?: string;
};

function TextField({ label, value, onChange, disabled, list }: FieldProps) {
  return (
    <div className="space-y-1">
      <label className="text-xs font-medium text-muted-foreground">{label}</label>
      <Input
        list={list}
        disabled={disabled}
        value={(value as string | null | undefined) ?? ""}
        onChange={(e) => onChange(e.target.value === "" ? null : e.target.value)}
      />
    </div>
  );
}

function TextAreaField({ label, value, onChange, disabled }: FieldProps) {
  return (
    <div className="space-y-1">
      <label className="text-xs font-medium text-muted-foreground">{label}</label>
      <Textarea
        rows={3}
        disabled={disabled}
        value={(value as string | null | undefined) ?? ""}
        onChange={(e) => onChange(e.target.value === "" ? null : e.target.value)}
      />
    </div>
  );
}

function NumberField({ label, value, onChange, disabled }: FieldProps) {
  return (
    <div className="space-y-1">
      <label className="text-xs font-medium text-muted-foreground">{label}</label>
      <Input
        type="number"
        step="0.01"
        disabled={disabled}
        value={(value as number | null | undefined) ?? ""}
        onChange={(e) => onChange(e.target.value === "" ? null : Number(e.target.value))}
      />
    </div>
  );
}

function DateField({ label, value, onChange, disabled }: FieldProps) {
  return (
    <div className="space-y-1">
      <label className="text-xs font-medium text-muted-foreground">{label}</label>
      <Input
        type="date"
        disabled={disabled}
        value={(value as string | null | undefined) ?? ""}
        onChange={(e) => onChange(e.target.value === "" ? null : e.target.value)}
      />
    </div>
  );
}

function CheckField({ label, value, onChange, disabled }: FieldProps) {
  return (
    <label className="flex items-center gap-2 text-sm">
      <Checkbox checked={!!value} disabled={disabled} onCheckedChange={(c) => onChange(!!c)} />
      {label}
    </label>
  );
}

function SolidariosEditor({
  value,
  onChange,
  disabled,
  datalistId,
}: {
  value: unknown;
  onChange: (value: SolidarioMulta[] | null) => void;
  disabled?: boolean;
  datalistId: string;
}) {
  const rows: SolidarioMulta[] = Array.isArray(value) ? (value as SolidarioMulta[]) : [];

  function update(index: number, patch: Partial<SolidarioMulta>) {
    onChange(rows.map((row, i) => (i === index ? { ...row, ...patch } : row)));
  }

  return (
    <div className="space-y-2 rounded-md border bg-muted/20 p-3">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-medium">Solidários</h4>
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={disabled}
          onClick={() => onChange([...rows, { nome: "", documento: null }])}
        >
          <Plus className="mr-1 h-3.5 w-3.5" />
          Adicionar
        </Button>
      </div>
      {rows.length === 0 ? (
        <p className="text-xs text-muted-foreground">Nenhum solidário.</p>
      ) : (
        rows.map((row, index) => (
          <div key={index} className="flex items-end gap-2">
            <div className="flex-1 space-y-1">
              <label className="text-xs text-muted-foreground">Nome</label>
              <Input
                list={datalistId}
                disabled={disabled}
                value={row.nome}
                onChange={(e) => update(index, { nome: e.target.value })}
              />
            </div>
            <div className="flex-1 space-y-1">
              <label className="text-xs text-muted-foreground">Documento</label>
              <Input
                disabled={disabled}
                value={row.documento ?? ""}
                onChange={(e) =>
                  update(index, { documento: e.target.value === "" ? null : e.target.value })
                }
              />
            </div>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              aria-label="Remover solidário"
              disabled={disabled}
              onClick={() => onChange(rows.filter((_, i) => i !== index))}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        ))
      )}
    </div>
  );
}

// ----- per-tipo fields ---------------------------------------------------------

function EntityFields({
  tipo,
  campos,
  onChange,
  disabled,
  datalistId,
}: {
  tipo: TipoEntidade;
  campos: Record<string, unknown>;
  onChange: (patch: Record<string, unknown>) => void;
  disabled?: boolean;
  datalistId: string;
}) {
  const set = (key: string) => (value: unknown) => onChange({ [key]: value });

  if (tipo === "multa") {
    return (
      <div className="space-y-3">
        <TextAreaField
          label="Descrição da multa"
          value={campos.descricao_multa}
          onChange={set("descricao_multa")}
          disabled={disabled}
        />
        <div className="grid grid-cols-3 gap-3">
          <NumberField
            label="Valor fixo"
            value={campos.valor_fixo}
            onChange={set("valor_fixo")}
            disabled={disabled}
          />
          <NumberField
            label="Percentual"
            value={campos.percentual}
            onChange={set("percentual")}
            disabled={disabled}
          />
          <NumberField
            label="Base de cálculo"
            value={campos.base_calculo}
            onChange={set("base_calculo")}
            disabled={disabled}
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <TextField
            label="Responsável"
            value={campos.nome_responsavel}
            onChange={set("nome_responsavel")}
            disabled={disabled}
            list={datalistId}
          />
          <TextField
            label="Documento do responsável"
            value={campos.documento_responsavel}
            onChange={set("documento_responsavel")}
            disabled={disabled}
          />
        </div>
        <CheckField
          label="Multa solidária"
          value={campos.e_multa_solidaria}
          onChange={(checked) =>
            onChange({
              e_multa_solidaria: checked,
              solidarios: checked ? (campos.solidarios ?? [{ nome: "", documento: null }]) : null,
            })
          }
          disabled={disabled}
        />
        {!!campos.e_multa_solidaria && (
          <SolidariosEditor
            value={campos.solidarios}
            onChange={set("solidarios")}
            disabled={disabled}
            datalistId={datalistId}
          />
        )}
      </div>
    );
  }

  if (tipo === "obrigacao") {
    return (
      <div className="space-y-3">
        <TextAreaField
          label="Descrição da obrigação"
          value={campos.descricao_obrigacao}
          onChange={set("descricao_obrigacao")}
          disabled={disabled}
        />
        <div className="grid grid-cols-2 gap-3">
          <CheckField
            label="Obrigação de fazer"
            value={campos.de_fazer}
            onChange={set("de_fazer")}
            disabled={disabled}
          />
          <CheckField
            label="Multa cominatória"
            value={campos.tem_multa_cominatoria}
            onChange={set("tem_multa_cominatoria")}
            disabled={disabled}
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <TextField
            label="Prazo"
            value={campos.prazo}
            onChange={set("prazo")}
            disabled={disabled}
          />
          <DateField
            label="Data de cumprimento"
            value={campos.data_cumprimento}
            onChange={set("data_cumprimento")}
            disabled={disabled}
          />
        </div>
        <TextField
          label="Órgão responsável"
          value={campos.orgao_responsavel}
          onChange={set("orgao_responsavel")}
          disabled={disabled}
        />
        {!!campos.tem_multa_cominatoria && (
          <>
            <div className="grid grid-cols-2 gap-3">
              <TextField
                label="Responsável pela multa"
                value={campos.nome_responsavel_multa_cominatoria}
                onChange={set("nome_responsavel_multa_cominatoria")}
                disabled={disabled}
                list={datalistId}
              />
              <TextField
                label="Documento do responsável"
                value={campos.documento_responsavel_multa_cominatoria}
                onChange={set("documento_responsavel_multa_cominatoria")}
                disabled={disabled}
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <NumberField
                label="Valor da multa"
                value={campos.valor_multa_cominatoria}
                onChange={set("valor_multa_cominatoria")}
                disabled={disabled}
              />
              <TextField
                label="Período da multa"
                value={campos.periodo_multa_cominatoria}
                onChange={set("periodo_multa_cominatoria")}
                disabled={disabled}
              />
            </div>
            <CheckField
              label="Multa solidária"
              value={campos.e_multa_cominatoria_solidaria}
              onChange={(checked) =>
                onChange({
                  e_multa_cominatoria_solidaria: checked,
                  solidarios_multa_cominatoria: checked
                    ? (campos.solidarios_multa_cominatoria ?? [{ nome: "", documento: null }])
                    : null,
                })
              }
              disabled={disabled}
            />
            {!!campos.e_multa_cominatoria_solidaria && (
              <SolidariosEditor
                value={campos.solidarios_multa_cominatoria}
                onChange={set("solidarios_multa_cominatoria")}
                disabled={disabled}
                datalistId={datalistId}
              />
            )}
          </>
        )}
      </div>
    );
  }

  if (tipo === "recomendacao") {
    return (
      <div className="space-y-3">
        <TextAreaField
          label="Descrição da recomendação"
          value={campos.descricao_recomendacao}
          onChange={set("descricao_recomendacao")}
          disabled={disabled}
        />
        <div className="grid grid-cols-2 gap-3">
          <TextField
            label="Prazo"
            value={campos.prazo_cumprimento_recomendacao}
            onChange={set("prazo_cumprimento_recomendacao")}
            disabled={disabled}
          />
          <DateField
            label="Data de cumprimento"
            value={campos.data_cumprimento_recomendacao}
            onChange={set("data_cumprimento_recomendacao")}
            disabled={disabled}
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <TextField
            label="Responsável"
            value={campos.nome_responsavel}
            onChange={set("nome_responsavel")}
            disabled={disabled}
            list={datalistId}
          />
          <TextField
            label="Órgão responsável"
            value={campos.orgao_responsavel}
            onChange={set("orgao_responsavel")}
            disabled={disabled}
          />
        </div>
        <CheckField
          label="Cancelado"
          value={campos.cancelado}
          onChange={set("cancelado")}
          disabled={disabled}
        />
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <TextAreaField
        label="Descrição do ressarcimento"
        value={campos.descricao_ressarcimento}
        onChange={set("descricao_ressarcimento")}
        disabled={disabled}
      />
      <div className="grid grid-cols-3 gap-3">
        <NumberField
          label="Valor do dano"
          value={campos.valor_dano}
          onChange={set("valor_dano")}
          disabled={disabled}
        />
        <NumberField
          label="Percentual imputado"
          value={campos.percentual_imputado}
          onChange={set("percentual_imputado")}
          disabled={disabled}
        />
        <NumberField
          label="Valor imputado"
          value={campos.valor_imputado}
          onChange={set("valor_imputado")}
          disabled={disabled}
        />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <TextField
          label="Responsável"
          value={campos.nome_responsavel}
          onChange={set("nome_responsavel")}
          disabled={disabled}
          list={datalistId}
        />
        <TextField
          label="Documento do responsável"
          value={campos.documento_responsavel}
          onChange={set("documento_responsavel")}
          disabled={disabled}
        />
      </div>
    </div>
  );
}
