"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { usePainelIndicadores } from "@/hooks/use-indicadores";
import { formatBRL } from "@/lib/format";
import { cn } from "@/lib/utils";
import type { Indicador } from "@/schemas/indicadores";

const BRL_COMPACTO = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
  notation: "compact",
  maximumFractionDigits: 1,
});
const NUM = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 });

function fmt(v: number | null | undefined, unidade: Indicador["unidade"]): string {
  if (v === null || v === undefined) return "—";
  if (unidade === "brl") return BRL_COMPACTO.format(v);
  if (unidade === "pct") return `${NUM.format(v)}%`;
  if (unidade === "dias") return `${NUM.format(v)} dias`;
  return NUM.format(v);
}

function IndicadorCard({ ind, ano }: { ind: Indicador; ano: number }) {
  const temSerie = Object.keys(ind.valores).length > 0;
  const valor = temSerie ? ind.valores[String(ano)] : ind.atual;
  const anteriores = Object.entries(ind.valores).filter(([a]) => Number(a) < ano);
  const variacao =
    temSerie && valor != null && ind.linha_base ? (valor / ind.linha_base - 1) * 100 : null;
  const melhora = variacao !== null && (ind.sentido === "maior" ? variacao > 0 : variacao < 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-muted-foreground text-xs font-medium tracking-wide uppercase">
          {ind.titulo}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="flex items-baseline gap-2">
          <span className="text-foreground text-3xl font-bold">{fmt(valor, ind.unidade)}</span>
          <span className="text-muted-foreground text-xs">{temSerie ? ano : "hoje"}</span>
        </div>
        {temSerie ? (
          <div className="text-muted-foreground flex flex-wrap gap-x-3 text-xs">
            {anteriores.map(([a, v]) => (
              <span key={a}>
                {a}: {fmt(v, ind.unidade)}
              </span>
            ))}
            <span className="text-foreground font-medium">
              base: {fmt(ind.linha_base, ind.unidade)}
            </span>
            {variacao !== null ? (
              <span className={cn("font-medium", melhora ? "text-emerald-600" : "text-red-600")}>
                {variacao > 0 ? "+" : ""}
                {NUM.format(variacao)}% vs base
              </span>
            ) : null}
          </div>
        ) : null}
        {ind.detalhe ? <div className="text-muted-foreground text-xs">{ind.detalhe}</div> : null}
        <div className="text-muted-foreground/80 border-t pt-2 text-[11px]">DPG: {ind.ref_dpg}</div>
      </CardContent>
    </Card>
  );
}

export default function PainelPage() {
  const { data, isLoading, isError } = usePainelIndicadores();

  const serie = (data?.anos ?? []).map((a) => {
    const v = (chave: string) =>
      data?.indicadores.find((i) => i.chave === chave)?.valores[String(a)] ?? 0;
    return { ano: String(a), beneficios: v("beneficios_efetivos"), frap: v("arrecadacao_frap") };
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="section-heading text-2xl">Início — Indicadores da CCD</h1>
        <p className="text-muted-foreground text-sm">
          Recorte da CCD sobre os indicadores estratégicos 2027-2028 propostos pela DPG. Linha de
          base = média dos dois anos anteriores; o ano corrente é parcial.
        </p>
      </div>

      {isLoading ? (
        <div className="text-muted-foreground text-sm">Calculando indicadores...</div>
      ) : isError || !data ? (
        <div className="text-destructive text-sm">Falha ao carregar os indicadores.</div>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {data.indicadores.map((ind) => (
              <IndicadorCard key={ind.chave} ind={ind} ano={data.ano} />
            ))}
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Benefícios efetivos × arrecadação do FRAP</CardTitle>
            </CardHeader>
            <CardContent className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={serie} margin={{ top: 4, right: 8, left: 8, bottom: 0 }}>
                  <CartesianGrid vertical={false} strokeDasharray="3 3" />
                  <XAxis dataKey="ano" tick={{ fontSize: 12 }} />
                  <YAxis
                    width={72}
                    tick={{ fontSize: 11 }}
                    tickFormatter={(v: number) => BRL_COMPACTO.format(v)}
                  />
                  <Tooltip formatter={(v) => formatBRL(v as number)} />
                  <Legend />
                  <Bar dataKey="beneficios" name="Benefícios efetivos" fill="#347d6b" />
                  <Bar dataKey="frap" name="Arrecadação FRAP" fill="#1a3d28" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
