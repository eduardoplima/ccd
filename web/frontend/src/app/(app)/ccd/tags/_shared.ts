import type { SituacaoTag } from "@/schemas/tags";

export const SITUACAO_TAG: Record<
  SituacaoTag,
  { label: string; variant: "outline" | "success" | "warning" | "destructive" }
> = {
  VIGENTE: { label: "Vigente", variant: "outline" },
  CUMPRIDO: { label: "Cumprido", variant: "success" },
  PRORROGADO: { label: "Prorrogado", variant: "warning" },
  RESCINDIDO: { label: "Rescindido", variant: "destructive" },
};
