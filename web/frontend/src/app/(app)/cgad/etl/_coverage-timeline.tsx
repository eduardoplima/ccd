"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useExtracoes } from "@/hooks/use-etl";
import { ExtracaoOut, RunStatus } from "@/schemas/etl";

const BAR_COLOR: Record<RunStatus, string> = {
  queued: "bg-muted-foreground/40",
  running: "bg-blue-500",
  done: "bg-emerald-500",
  error: "bg-red-500",
};

const STATUS_LABEL: Record<RunStatus, string> = {
  queued: "na fila",
  running: "em andamento",
  done: "concluída",
  error: "erro",
};

// Quem "ganha" quando várias extrações cobrem o mesmo período: uma extração
// concluída torna o período coberto, mesmo que outra tentativa ali tenha falhado.
const PRIORITY: Record<RunStatus, number> = { done: 3, running: 2, queued: 1, error: 0 };

const DAY = 86_400_000;

function day(iso: string): number {
  return Date.parse(`${iso}T00:00:00`);
}

function br(iso: string): string {
  const [y, m, d] = iso.split("-");
  return `${d}/${m}/${y}`;
}

function brFromMs(ms: number): string {
  return new Date(ms).toLocaleDateString("pt-BR");
}

type Segment = { from: number; to: number; status: RunStatus };

/** Achata as extrações numa única faixa: fatia nos limites e mantém o status
 * de maior prioridade em cada fatia, unindo fatias vizinhas iguais. */
function coverage(items: ExtracaoOut[]): Segment[] {
  const spans = items.map((i) => ({
    from: day(i.data_inicio),
    to: day(i.data_fim) + DAY,
    status: i.status,
  }));
  const points = [...new Set(spans.flatMap((s) => [s.from, s.to]))].sort((a, b) => a - b);
  const out: Segment[] = [];
  for (let k = 0; k < points.length - 1; k++) {
    const [from, to] = [points[k], points[k + 1]];
    const covering = spans.filter((s) => s.from <= from && s.to >= to);
    if (covering.length === 0) continue;
    const status = covering.reduce(
      (a, s) => (PRIORITY[s.status] > PRIORITY[a] ? s.status : a),
      covering[0].status,
    );
    const prev = out[out.length - 1];
    if (prev && prev.to === from && prev.status === status) prev.to = to;
    else out.push({ from, to, status });
  }
  return out;
}

/** Marcas anuais, trimestrais ou mensais conforme a extensão do período. */
function ticks(t0: number, t1: number): { at: number; label: string }[] {
  const start = new Date(t0);
  const end = new Date(t1);
  const months = (end.getFullYear() - start.getFullYear()) * 12 + end.getMonth() - start.getMonth();
  const step = months > 30 ? 12 : months > 12 ? 3 : 1;
  const out: { at: number; label: string }[] = [];
  const cursor = new Date(start.getFullYear(), step === 12 ? 0 : start.getMonth(), 1);
  while (cursor.getTime() <= t1) {
    if (cursor.getTime() >= t0) {
      out.push({
        at: cursor.getTime(),
        label:
          step === 12
            ? String(cursor.getFullYear())
            : cursor.toLocaleDateString("pt-BR", { month: "short", year: "2-digit" }),
      });
    }
    cursor.setMonth(cursor.getMonth() + step);
  }
  return out;
}

export function CoverageTimeline() {
  // Uma página sem filtro basta para desenhar a cobertura (o backend limita page_size a 100).
  const { data } = useExtracoes({ page: 1, pageSize: 100 });
  const items = data?.items ?? [];
  if (items.length === 0) return null;

  const t0 = Math.min(...items.map((i) => day(i.data_inicio)));
  const t1 = Math.max(...items.map((i) => day(i.data_fim))) + DAY;
  const span = Math.max(t1 - t0, 1);
  const pct = (t: number) => ((t - t0) / span) * 100;
  const segments = coverage(items);
  const usedStatuses = (Object.keys(STATUS_LABEL) as RunStatus[]).filter((s) =>
    segments.some((seg) => seg.status === s),
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>Período coberto</CardTitle>
        <CardDescription>
          Cobertura consolidada das extrações por data de sessão. Trechos vazios são períodos ainda
          não extraídos.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <div>
          <div className="relative h-4 rounded-[4px] bg-muted">
            {ticks(t0, t1).map((tick) => (
              <div
                key={tick.at}
                className="absolute top-0 bottom-0 w-px bg-border"
                style={{ left: `${pct(tick.at)}%` }}
              />
            ))}
            {segments.map((seg) => (
              <div
                key={seg.from}
                title={`${brFromMs(seg.from)} a ${brFromMs(seg.to - DAY)} — ${STATUS_LABEL[seg.status]}`}
                className={`absolute top-0 h-4 rounded-[4px] ${BAR_COLOR[seg.status]}`}
                style={{
                  left: `${pct(seg.from)}%`,
                  width: `max(3px, ${pct(seg.to) - pct(seg.from)}%)`,
                }}
              />
            ))}
          </div>
          <div className="relative mt-2 h-4 border-t">
            {ticks(t0, t1).map((tick) => (
              <span
                key={tick.at}
                className="absolute top-1 -translate-x-1/2 text-[11px] text-muted-foreground"
                style={{ left: `${pct(tick.at)}%` }}
              >
                {tick.label}
              </span>
            ))}
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
          {usedStatuses.map((s) => (
            <span key={s} className="flex items-center gap-1.5">
              <span className={`h-2.5 w-2.5 rounded-[2px] ${BAR_COLOR[s]}`} />
              {STATUS_LABEL[s]}
            </span>
          ))}
          <span className="ml-auto">
            {br(
              items.reduce((a, i) => (i.data_inicio < a ? i.data_inicio : a), items[0].data_inicio),
            )}{" "}
            a {br(items.reduce((a, i) => (i.data_fim > a ? i.data_fim : a), items[0].data_fim))}
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
