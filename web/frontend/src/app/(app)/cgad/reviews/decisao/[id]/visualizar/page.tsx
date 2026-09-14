"use client";

import { useParams, useRouter, useSearchParams } from "next/navigation";

import { formatData } from "@/components/review/entity-panel";
import { Button } from "@/components/ui/button";
import { useDecisao, useDecisaoTexto } from "@/hooks/use-reviews";
import { messageForError } from "@/lib/error-messages";
import { formatAcordao, formatBRL, formatDate, formatProcesso } from "@/lib/format";
import { cn } from "@/lib/utils";
import { EntidadeOut, TIPO_LABEL, TipoEntidade } from "@/schemas/review";

const TABS_VALIDAS = new Set([
  "pendentes",
  "reserva",
  "minha-reserva",
  "realizadas",
  "awaiting-dispatch",
]);

const CARD_CLASS: Record<TipoEntidade, string> = {
  multa: "border-amber-300",
  obrigacao: "border-sky-300",
  ressarcimento: "border-emerald-300",
  recomendacao: "border-violet-300",
};

// Campos exibidos por tipo, na ordem; rótulos iguais aos do formulário de revisão.
const CAMPOS: Record<TipoEntidade, [string, string][]> = {
  obrigacao: [
    ["descricao_obrigacao", "Descrição"],
    ["de_fazer", "Obrigação de fazer"],
    ["prazo", "Prazo"],
    ["data_cumprimento", "Data de cumprimento"],
    ["orgao_responsavel", "Órgão responsável"],
    ["tem_multa_cominatoria", "Multa cominatória"],
    ["nome_responsavel_multa_cominatoria", "Responsável pela multa"],
    ["documento_responsavel_multa_cominatoria", "Documento do responsável"],
    ["valor_multa_cominatoria", "Valor da multa"],
    ["periodo_multa_cominatoria", "Período da multa"],
    ["e_multa_cominatoria_solidaria", "Multa solidária"],
    ["solidarios_multa_cominatoria", "Solidários"],
  ],
  recomendacao: [
    ["descricao_recomendacao", "Descrição"],
    ["prazo_cumprimento_recomendacao", "Prazo"],
    ["data_cumprimento_recomendacao", "Data de cumprimento"],
    ["nome_responsavel", "Responsável"],
    ["orgao_responsavel", "Órgão responsável"],
    ["cancelado", "Cancelado"],
  ],
  multa: [
    ["descricao_multa", "Descrição"],
    ["valor_fixo", "Valor fixo"],
    ["percentual", "Percentual"],
    ["base_calculo", "Base de cálculo"],
    ["nome_responsavel", "Responsável"],
    ["documento_responsavel", "Documento do responsável"],
    ["e_multa_solidaria", "Multa solidária"],
    ["solidarios", "Solidários"],
  ],
  ressarcimento: [
    ["descricao_ressarcimento", "Descrição"],
    ["valor_dano", "Valor do dano"],
    ["percentual_imputado", "Percentual imputado"],
    ["valor_imputado", "Valor imputado"],
    ["nome_responsavel", "Responsável"],
    ["documento_responsavel", "Documento do responsável"],
  ],
};

const STATUS_LABEL: Record<string, string> = {
  pending: "Pendente",
  approved: "Aprovada",
  rejected: "Rejeitada",
  sent: "Enviada",
};

function formatDataHora(iso: string): string {
  return new Date(iso).toLocaleDateString("pt-BR");
}

function formatValor(chave: string, valor: unknown): string | null {
  if (valor === null || valor === undefined || valor === "") return null;
  if (typeof valor === "boolean") return valor ? "Sim" : "Não";
  if (Array.isArray(valor)) {
    const nomes = valor
      .map((s) =>
        s && typeof s === "object" && "nome" in s
          ? [s.nome, "documento" in s && s.documento ? `(${s.documento})` : ""]
              .filter(Boolean)
              .join(" ")
          : String(s),
      )
      .filter(Boolean);
    return nomes.length > 0 ? nomes.join("; ") : null;
  }
  if (typeof valor === "number") {
    if (chave.startsWith("percentual")) return `${valor}%`;
    if (chave.startsWith("valor") || chave === "base_calculo") return formatBRL(valor);
    return String(valor);
  }
  if (typeof valor === "string" && chave.startsWith("data_")) return formatDate(valor);
  return String(valor);
}

export default function DecisaoVisualizarPage() {
  const params = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const router = useRouter();
  const id = Number(params.id);
  const tabParam = searchParams.get("tab") ?? "";
  const tab = TABS_VALIDAS.has(tabParam) ? tabParam : "awaiting-dispatch";
  const voltarParam = searchParams.get("voltar") ?? "";
  const destino = voltarParam.startsWith("/cgad/") ? voltarParam : `/cgad/reviews?tab=${tab}`;
  const voltar = () => router.push(destino);

  const query = useDecisao(id);
  const textoQuery = useDecisaoTexto(id);
  const detail = query.data;
  const texto = textoQuery.data ?? null;

  if (query.isError) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 p-10">
        <p className="text-sm">
          {messageForError(query.error, "Não foi possível carregar a decisão.")}
        </p>
        <Button variant="outline" onClick={voltar}>
          Voltar
        </Button>
      </div>
    );
  }
  if (!detail) {
    return (
      <div className="flex flex-1 items-center justify-center p-10 text-sm text-muted-foreground">
        Carregando decisão...
      </div>
    );
  }

  const ordem: TipoEntidade[] = ["obrigacao", "recomendacao", "multa", "ressarcimento"];
  const entidades = [...detail.entidades].sort(
    (a, b) => ordem.indexOf(a.tipo) - ordem.indexOf(b.tipo),
  );

  return (
    <main className="mx-auto flex w-full max-w-screen-2xl flex-col gap-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">
            {texto?.numero_acordao
              ? formatAcordao(texto.numero_acordao, texto.ano_acordao, texto.tipo_acordao)
              : "Decisão"}{" "}
            · Processo{" "}
            {formatProcesso(texto?.numero_processo, texto?.ano_processo, detail.id_processo)}
          </h1>
          <p className="text-xs text-muted-foreground">
            {texto?.data_sessao ? `Sessão de ${formatData(texto.data_sessao)} · ` : ""}
            Decisão #{detail.id} · Pauta {detail.id_composicao_pauta}/{detail.id_voto_pauta}
            {detail.revisado_por ? ` · Revisada por ${detail.revisado_por}` : ""}
            {detail.data_revisao ? ` em ${formatDataHora(detail.data_revisao)}` : ""}
          </p>
        </div>
        <Button variant="outline" onClick={voltar}>
          Voltar
        </Button>
      </div>

      <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-2">
        <div className="lg:sticky lg:top-4">
          <h2 className="mb-2 text-sm font-medium">Texto do acórdão</h2>
          <div className="max-h-[70vh] overflow-y-auto whitespace-pre-wrap rounded-md border bg-muted/30 p-4 text-sm">
            {textoQuery.isLoading && !texto
              ? "Carregando texto do acórdão..."
              : texto?.texto_acordao || "Texto do acórdão indisponível."}
          </div>
        </div>

        <div className="space-y-3">
          <h2 className="text-sm font-medium">Entidades</h2>
          {entidades.length === 0 && (
            <p className="text-sm text-muted-foreground">Nenhuma entidade nesta decisão.</p>
          )}
          {entidades.map((e) => (
            <EntidadeCard key={`${e.tipo}-${e.id_ner}`} entidade={e} />
          ))}
        </div>
      </div>
    </main>
  );
}

function EntidadeCard({ entidade }: { entidade: EntidadeOut }) {
  const linhas = CAMPOS[entidade.tipo]
    .map(([chave, rotulo]) => [rotulo, formatValor(chave, entidade.campos[chave])] as const)
    .filter((par): par is readonly [string, string] => par[1] !== null);

  return (
    <div
      className={cn(
        "rounded-md border-l-4 border bg-background p-3 text-sm",
        CARD_CLASS[entidade.tipo],
      )}
    >
      <div className="mb-2 flex flex-wrap items-center gap-2">
        <span className="font-medium">{TIPO_LABEL[entidade.tipo]}</span>
        <span className="rounded bg-muted px-1.5 py-0.5 text-xs">
          {STATUS_LABEL[entidade.status] ?? entidade.status}
        </span>
        {entidade.reviewer && (
          <span className="text-xs text-muted-foreground">
            por {entidade.reviewer}
            {entidade.reviewed_at ? ` em ${formatDataHora(entidade.reviewed_at)}` : ""}
          </span>
        )}
      </div>
      <dl className="grid grid-cols-[max-content_1fr] gap-x-4 gap-y-1">
        {linhas.map(([rotulo, valor]) => (
          <div key={rotulo} className="contents">
            <dt className="text-muted-foreground">{rotulo}</dt>
            <dd className="whitespace-pre-wrap">{valor}</dd>
          </div>
        ))}
      </dl>
      {entidade.observacoes && (
        <p className="mt-2 text-xs text-muted-foreground">Observações: {entidade.observacoes}</p>
      )}
    </div>
  );
}
