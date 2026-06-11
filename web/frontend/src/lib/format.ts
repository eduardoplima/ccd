const BRL = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
  minimumFractionDigits: 2,
});

export function formatBRL(value: number | string): string {
  const n = typeof value === "string" ? Number(value) : value;
  return BRL.format(n);
}

const BR_DECIMAL = new Intl.NumberFormat("pt-BR", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export function parseBRDecimal(input: string): string | null {
  const cleaned = input.trim();
  if (!cleaned) return null;
  const normalized = cleaned.replace(/\./g, "").replace(",", ".");
  if (!/^\d+(\.\d+)?$/.test(normalized)) return null;
  return normalized;
}

export function formatBRDecimal(input: string): string {
  const n = parseBRDecimal(input);
  if (n === null) return input;
  return BR_DECIMAL.format(Number(n));
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  const [year, month, day] = iso.split("-");
  if (!year || !month || !day) return iso;
  return `${day}/${month}/${year}`;
}

const MATCH_STATUS_OK = new Set([
  "EXATO",
  "EXATO_PESSOA_VALOR",
  "EXATO_BARRAS",
  "EXATO_VD",
  "EXATO_LOTE",
  "OK_TUDO",
  "MATCH_MANUAL",
  "REPASSE_VIA_ORGAO",
]);
const MATCH_STATUS_WARN = new Set(["AMBIGUO", "AMBIGUO_PESSOA", "PARCELA_AGUARDANDO"]);
const MATCH_STATUS_INFO = new Set(["SEM_FONTE_SIGEF"]);

export function matchStatusVariant(
  status: string,
): "success" | "warning" | "destructive" | "outline" {
  if (MATCH_STATUS_OK.has(status)) return "success";
  if (MATCH_STATUS_WARN.has(status)) return "warning";
  if (MATCH_STATUS_INFO.has(status)) return "outline";
  return "destructive";
}

// --- helpers usados pelo módulo CGAD ---

export function formatProcesso(
  numero: number | null | undefined,
  ano: number | null | undefined,
  fallbackId: number | null | undefined,
): string {
  if (numero != null && ano != null) {
    return `${String(numero).padStart(6, "0")}/${String(ano).padStart(4, "0")}`;
  }
  return fallbackId != null ? String(fallbackId) : "—";
}

export function formatPercent(value: number | null | undefined): string {
  if (value == null || Number.isNaN(value)) return "—";
  return `${(value * 100).toFixed(1).replace(".", ",")}%`;
}

export function formatCurrencyBRL(value: number | null | undefined): string {
  if (value == null || Number.isNaN(value)) return "—";
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(value);
}
