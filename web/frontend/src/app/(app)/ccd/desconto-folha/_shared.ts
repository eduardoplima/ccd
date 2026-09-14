import type { StatusExtracao } from "@/schemas/desconto-folha";

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
