"use client";

import { useMemo } from "react";
import {
  Bar,
  BarChart,
  Brush,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { useBeneficiosSerie } from "@/hooks/use-beneficios";

const COLOR_PRIMARY = "#347d6b";

function primeiroDia(ano: number, mes: number): string {
  return `${ano}-${String(mes).padStart(2, "0")}-01`;
}

function ultimoDia(ano: number, mes: number): string {
  const dia = new Date(Date.UTC(ano, mes, 0)).getUTCDate();
  return `${ano}-${String(mes).padStart(2, "0")}-${String(dia).padStart(2, "0")}`;
}

export function SerieTemporal({
  de,
  ate,
  onChange,
}: {
  de: string;
  ate: string;
  onChange: (de: string | null, ate: string | null) => void;
}) {
  const { data, isLoading } = useBeneficiosSerie();

  const meses = useMemo(
    () =>
      (data ?? []).map((m) => ({
        ...m,
        label: `${String(m.mes).padStart(2, "0")}/${m.ano}`,
        ini: primeiroDia(m.ano, m.mes),
        fim: ultimoDia(m.ano, m.mes),
      })),
    [data],
  );

  if (isLoading || meses.length === 0) {
    return (
      <div className="text-muted-foreground flex h-40 items-center justify-center rounded-lg border text-sm">
        {isLoading ? "Carregando..." : "Nenhum item."}
      </div>
    );
  }

  const dentro = (m: { ini: string; fim: string }) =>
    (!de || m.fim >= de) && (!ate || m.ini <= ate);
  let startIndex = meses.findIndex(dentro);
  let endIndex = meses.findLastIndex(dentro);
  if (startIndex < 0 || endIndex < 0) {
    startIndex = 0;
    endIndex = meses.length - 1;
  }

  return (
    <div className="h-40 rounded-lg border p-2">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          key={`${startIndex}-${endIndex}`}
          data={meses}
          margin={{ top: 4, right: 8, left: 0, bottom: 0 }}
        >
          <CartesianGrid vertical={false} strokeDasharray="3 3" />
          <XAxis dataKey="label" tick={{ fontSize: 11 }} interval="preserveStartEnd" />
          <YAxis allowDecimals={false} width={36} tick={{ fontSize: 11 }} />
          <Tooltip formatter={(v) => [`${v as number} benefícios`, ""]} separator="" />
          <Bar dataKey="qtd" name="Benefícios" fill={COLOR_PRIMARY}>
            {meses.map((m, i) => (
              <Cell key={m.label} fillOpacity={i >= startIndex && i <= endIndex ? 1 : 0.3} />
            ))}
          </Bar>
          <Brush
            dataKey="label"
            height={22}
            travellerWidth={8}
            stroke={COLOR_PRIMARY}
            startIndex={startIndex}
            endIndex={endIndex}
            onDragEnd={({ startIndex: s, endIndex: e }) => {
              if (s === undefined || e === undefined) return;
              if (s === 0 && e === meses.length - 1) onChange(null, null);
              else onChange(meses[s].ini, meses[e].fim);
            }}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
