"use client";

import { useEffect, useMemo, useState } from "react";
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
import { toast } from "sonner";

import { KpiCard } from "@/components/dashboards/kpi-card";
import { PeriodPicker } from "@/components/dashboards/period-picker";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useDashboardSummary } from "@/hooks/use-dashboards";
import { messageForError } from "@/lib/error-messages";
import { formatCurrencyBRL, formatPercent } from "@/lib/format";
import { OrgaoBucket, PessoaBucket } from "@/schemas/dashboards";

const TOP_N = 10;

function isoToday(): string {
  return new Date().toISOString().slice(0, 10);
}

function isoMinusDays(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() - days);
  return d.toISOString().slice(0, 10);
}

export default function DashboardsPage() {
  const [range, setRange] = useState<{ startDate: string; endDate: string }>(() => ({
    startDate: isoMinusDays(90),
    endDate: isoToday(),
  }));

  const { data, isLoading, isError, error } = useDashboardSummary({
    startDate: range.startDate,
    endDate: range.endDate,
    topN: TOP_N,
  });

  useEffect(() => {
    if (isError) {
      toast.error(messageForError(error, "Erro ao carregar o dashboard."));
    }
  }, [isError, error]);

  const orgaos = useMemo(() => data?.top_orgaos ?? [], [data]);
  const pessoas = useMemo(() => data?.top_pessoas ?? [], [data]);

  return (
    <main className="mx-auto flex w-full max-w-screen-2xl flex-col gap-6 p-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Dashboards</h1>
          <p className="text-sm text-muted-foreground">
            Visão consolidada de obrigações e recomendações já cadastradas.
          </p>
        </div>
        <PeriodPicker startDate={range.startDate} endDate={range.endDate} onChange={setRange} />
      </div>

      <section className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <KpiCard
          label="Pendentes — Obrigação"
          value={String(data?.kpis.pendentes_obrigacao ?? "—")}
          hint="Aguardando revisão"
        />
        <KpiCard
          label="Pendentes — Recomendação"
          value={String(data?.kpis.pendentes_recomendacao ?? "—")}
          hint="Aguardando revisão"
        />
        <KpiCard
          label="Revisadas no período"
          value={String(data?.kpis.revisadas_periodo ?? "—")}
          hint={`Aprovadas: ${data?.kpis.aprovadas_periodo ?? "—"}`}
        />
        <KpiCard
          label="% Aprovação"
          value={formatPercent(data?.kpis.percent_aprovacao)}
          hint="Aprovadas ÷ revisadas no período"
        />
        <KpiCard
          label="Obrigações com multa"
          value={String(data?.kpis.obrigacoes_com_multa ?? "—")}
          hint="Com multa cominatória"
        />
        <KpiCard
          label="Ticket médio multa"
          value={formatCurrencyBRL(data?.kpis.ticket_medio_multa)}
          hint="Média do valor das multas aprovadas"
        />
      </section>

      <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <ChartCard title="Top órgãos responsáveis">
          <OrgaoBarChart data={orgaos} isLoading={isLoading} />
        </ChartCard>
        <ChartCard title="Top pessoas responsáveis">
          <PessoaBarChart data={pessoas} isLoading={isLoading} />
        </ChartCard>
      </section>
    </main>
  );
}

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="section-heading text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-80">{children}</div>
      </CardContent>
    </Card>
  );
}

const COLOR_PRIMARY = "#347d6b";
const COLOR_ACCENT = "#d4a017";

function EmptyOrLoading({ isLoading, isEmpty }: { isLoading: boolean; isEmpty: boolean }) {
  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
        Carregando...
      </div>
    );
  }
  if (isEmpty) {
    return (
      <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
        Nenhum item no período.
      </div>
    );
  }
  return null;
}

function truncate(value: string, max = 40): string {
  return value.length > max ? `${value.slice(0, max - 1)}…` : value;
}

function OrgaoBarChart({ data, isLoading }: { data: OrgaoBucket[]; isLoading: boolean }) {
  if (isLoading || data.length === 0) {
    return <EmptyOrLoading isLoading={isLoading} isEmpty={data.length === 0} />;
  }
  const chartData = data.map((b) => ({ ...b, label: truncate(b.nome) }));
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart
        data={chartData}
        layout="vertical"
        margin={{ top: 5, right: 16, left: 8, bottom: 5 }}
      >
        <CartesianGrid horizontal={false} strokeDasharray="3 3" />
        <XAxis type="number" allowDecimals={false} />
        <YAxis type="category" dataKey="label" width={180} />
        <Tooltip
          formatter={(value, name) => [value as number, name as string]}
          labelFormatter={(_, payload) => payload?.[0]?.payload?.nome ?? ""}
        />
        <Legend />
        <Bar dataKey="obrigacoes" name="Obrigações" stackId="a" fill={COLOR_PRIMARY} />
        <Bar dataKey="recomendacoes" name="Recomendações" stackId="a" fill={COLOR_ACCENT} />
      </BarChart>
    </ResponsiveContainer>
  );
}

function PessoaBarChart({ data, isLoading }: { data: PessoaBucket[]; isLoading: boolean }) {
  if (isLoading || data.length === 0) {
    return <EmptyOrLoading isLoading={isLoading} isEmpty={data.length === 0} />;
  }
  const chartData = data.map((b) => ({ ...b, label: truncate(b.nome) }));
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart
        data={chartData}
        layout="vertical"
        margin={{ top: 5, right: 16, left: 8, bottom: 5 }}
      >
        <CartesianGrid horizontal={false} strokeDasharray="3 3" />
        <XAxis type="number" allowDecimals={false} />
        <YAxis type="category" dataKey="label" width={180} />
        <Tooltip
          formatter={(value, name) => [value as number, name as string]}
          labelFormatter={(_, payload) => {
            const item = payload?.[0]?.payload as PessoaBucket | undefined;
            if (!item) return "";
            return item.documento ? `${item.nome} (${item.documento})` : item.nome;
          }}
        />
        <Legend />
        <Bar dataKey="obrigacoes" name="Obrigações" stackId="a" fill={COLOR_PRIMARY} />
        <Bar dataKey="recomendacoes" name="Recomendações" stackId="a" fill={COLOR_ACCENT} />
      </BarChart>
    </ResponsiveContainer>
  );
}
