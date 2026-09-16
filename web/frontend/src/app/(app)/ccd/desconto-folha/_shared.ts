import type { StatusExtracao, TipoNotificacao, TipoRecebimento } from "@/schemas/desconto-folha";

export const TIPO_NOTIFICACAO: Record<TipoNotificacao, string> = {
  E: "eletrônica",
  F: "postal",
};

export const TIPO_RECEBIMENTO: Record<TipoRecebimento, string> = {
  E: "comunicação eletrônica",
  T: "recebimento tácito",
  AR: "AR (Correios)",
  DE: "prazo iniciado (certidão da DE)",
};

export const JOB_LABEL: Record<string, string> = {
  pending: "Na fila...",
  running: "Executando...",
  done: "Concluído",
  failed: "Falhou",
  cancelled: "Cancelado",
};

export const STATUS_EXTRACAO: Record<
  StatusExtracao,
  { label: string; variant: "outline" | "success" | "warning" | "destructive" }
> = {
  PENDENTE: { label: "Não extraída", variant: "outline" },
  OK: { label: "Valor extraído", variant: "success" },
  SEM_RESPOSTA: { label: "Sem resposta", variant: "warning" },
  ERRO: { label: "Conferir", variant: "destructive" },
};

export function formatData(iso: string | null | undefined): string {
  return iso ? new Date(iso).toLocaleDateString("pt-BR") : "—";
}
