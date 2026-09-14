"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  Treemap,
  XAxis,
  YAxis,
} from "recharts";
import { toast } from "sonner";

import { Button, buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useDashboardSummary } from "@/hooks/use-dashboards";
import { messageForError } from "@/lib/error-messages";
import { formatProcesso } from "@/lib/format";
import { cn } from "@/lib/utils";
import {
  EntidadeCadastrada,
  OrgaoBucket,
  PessoaBucket,
  TreemapBucket,
  TreemapSet,
} from "@/schemas/dashboards";

const TOP_N = 10;
const PAGE_SIZE = 25;

type Filtro = { rotulo: string; teste: (e: EntidadeCadastrada) => boolean };
type TipoEntidade = EntidadeCadastrada["tipo"];
type Dimensao = "orgao" | "tipo_processo" | "relator";

const TIPO_TITULO: Record<TipoEntidade, string> = {
  obrigacao: "Obrigações",
  recomendacao: "Recomendações",
};
const DIMENSAO_TITULO: Record<Dimensao, string> = {
  orgao: "por órgão",
  tipo_processo: "por tipo de processo",
  relator: "por relator",
};

export default function DashboardsPage() {
  const { data, isLoading, isError, error } = useDashboardSummary({ topN: TOP_N });
  const [filtro, setFiltro] = useState<Filtro | null>(null);

  function aplicarFiltro(f: Filtro) {
    setFiltro(f);
    setTimeout(() => {
      document.getElementById("entidades")?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 50);
  }

  useEffect(() => {
    if (isError) {
      toast.error(messageForError(error, "Erro ao carregar o dashboard."));
    }
  }, [isError, error]);

  const orgaos = useMemo(() => data?.top_orgaos ?? [], [data]);
  const pessoas = useMemo(() => data?.top_pessoas ?? [], [data]);
  const entidades = useMemo(() => data?.entidades ?? [], [data]);
  const filtradas = useMemo(
    () => (filtro ? entidades.filter(filtro.teste) : entidades),
    [entidades, filtro],
  );

  function filtrarTreemap(tipo: TipoEntidade, campo: Dimensao, nome: string, top: string[]) {
    const rotulo = `${TIPO_TITULO[tipo]} ${DIMENSAO_TITULO[campo]}: ${nome}`;
    const teste =
      nome === "Outros"
        ? (e: EntidadeCadastrada) => e.tipo === tipo && !top.includes(e[campo])
        : (e: EntidadeCadastrada) => e.tipo === tipo && e[campo] === nome;
    aplicarFiltro({ rotulo, teste });
  }

  return (
    <main className="mx-auto flex w-full max-w-screen-2xl flex-col gap-6 p-6">
      <div>
        <h1 className="text-2xl font-semibold">Dashboards</h1>
        <p className="text-sm text-muted-foreground">
          Visão consolidada de obrigações e recomendações já cadastradas e revisadas. Clique numa
          barra ou num quadrado para filtrar a tabela.
        </p>
      </div>

      <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <ChartCard title="Top órgãos responsáveis">
          <RankingBarChart
            data={orgaos}
            isLoading={isLoading}
            onSelect={(b) =>
              aplicarFiltro({ rotulo: `Órgão: ${b.nome}`, teste: (e) => e.orgao === b.nome })
            }
          />
        </ChartCard>
        <ChartCard title="Top pessoas responsáveis">
          <RankingBarChart
            data={pessoas}
            isLoading={isLoading}
            tooltipLabel={(b) => (b.documento ? `${b.nome} (${b.documento})` : b.nome)}
            onSelect={(b) =>
              aplicarFiltro({ rotulo: `Pessoa: ${b.nome}`, teste: (e) => e.pessoa === b.nome })
            }
          />
        </ChartCard>
      </section>

      <TreemapRow
        tipo="obrigacao"
        conjunto={data?.treemap_obrigacao}
        isLoading={isLoading}
        onSelect={filtrarTreemap}
      />
      <TreemapRow
        tipo="recomendacao"
        conjunto={data?.treemap_recomendacao}
        isLoading={isLoading}
        onSelect={filtrarTreemap}
      />

      <EntidadesTable
        items={filtradas}
        total={entidades.length}
        filtro={filtro}
        onLimpar={() => {
          setFiltro(null);
          window.scrollTo({ top: 0, behavior: "smooth" });
        }}
        isLoading={isLoading}
      />
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
        <div className="h-96">{children}</div>
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
        Nenhum item.
      </div>
    );
  }
  return null;
}

function truncate(value: string, max = 32): string {
  return value.length > max ? `${value.slice(0, max - 1)}…` : value;
}

function RankingBarChart<T extends OrgaoBucket | PessoaBucket>({
  data,
  isLoading,
  tooltipLabel,
  onSelect,
}: {
  data: T[];
  isLoading: boolean;
  tooltipLabel?: (b: T) => string;
  onSelect: (b: T) => void;
}) {
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
        <YAxis type="category" dataKey="label" width={210} tick={{ fontSize: 11 }} />
        <Tooltip
          formatter={(value, name) => [value as number, name as string]}
          labelFormatter={(_, payload) => {
            const item = payload?.[0]?.payload as T | undefined;
            if (!item) return "";
            return tooltipLabel ? tooltipLabel(item) : item.nome;
          }}
        />
        <Legend />
        <Bar
          dataKey="obrigacoes"
          name="Obrigações"
          stackId="a"
          fill={COLOR_PRIMARY}
          cursor="pointer"
          onClick={(d) => onSelect(((d as { payload?: T }).payload ?? d) as T)}
        />
        <Bar
          dataKey="recomendacoes"
          name="Recomendações"
          stackId="a"
          fill={COLOR_ACCENT}
          cursor="pointer"
          onClick={(d) => onSelect(((d as { payload?: T }).payload ?? d) as T)}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}

const TREEMAP_COLORS = ["#347d6b", "#1c4433", "#5a9c8a", "#d4a017", "#8fbfb0", "#b8860b"];

function TreemapRow({
  tipo,
  conjunto,
  isLoading,
  onSelect,
}: {
  tipo: TipoEntidade;
  conjunto: TreemapSet | undefined;
  isLoading: boolean;
  onSelect: (tipo: TipoEntidade, campo: Dimensao, nome: string, top: string[]) => void;
}) {
  const dimensoes: [Dimensao, TreemapBucket[]][] = [
    ["orgao", conjunto?.por_orgao ?? []],
    ["tipo_processo", conjunto?.por_tipo ?? []],
    ["relator", conjunto?.por_relator ?? []],
  ];
  return (
    <section className="grid grid-cols-1 gap-4 lg:grid-cols-3">
      {dimensoes.map(([campo, data]) => (
        <ChartCard key={campo} title={`${TIPO_TITULO[tipo]} ${DIMENSAO_TITULO[campo]}`}>
          <TreemapChart
            data={data}
            isLoading={isLoading}
            onSelect={(nome) =>
              onSelect(
                tipo,
                campo,
                nome,
                data.map((b) => b.nome),
              )
            }
          />
        </ChartCard>
      ))}
    </section>
  );
}

type TreemapCell = {
  x: number;
  y: number;
  width: number;
  height: number;
  index: number;
  depth?: number;
  name?: string;
  value?: number;
  onSelect?: (nome: string) => void;
};

function TreemapContent({ x, y, width, height, index, depth, name, value, onSelect }: TreemapCell) {
  // O nó raiz (depth 0) cobre a área toda; só as folhas são desenhadas.
  if (!depth) return null;
  const fill = TREEMAP_COLORS[index % TREEMAP_COLORS.length];
  const showLabel = width > 60 && height > 24;
  const maxChars = Math.max(3, Math.floor(width / 7));
  return (
    <g cursor="pointer" onClick={() => name && onSelect?.(name)}>
      <rect x={x} y={y} width={width} height={height} fill={fill} stroke="#fff" />
      {showLabel && (
        <text x={x + 4} y={y + 14} fill="#fff" fontSize={11} pointerEvents="none">
          {truncate(name ?? "", maxChars)}
          {height > 40 && (
            <tspan x={x + 4} dy={14} fontWeight={500}>
              {value}
            </tspan>
          )}
        </text>
      )}
    </g>
  );
}

function TreemapChart({
  data,
  isLoading,
  onSelect,
}: {
  data: TreemapBucket[];
  isLoading: boolean;
  onSelect: (nome: string) => void;
}) {
  if (isLoading || data.length === 0) {
    return <EmptyOrLoading isLoading={isLoading} isEmpty={data.length === 0} />;
  }
  return (
    <ResponsiveContainer width="100%" height="100%">
      <Treemap
        data={data}
        dataKey="total"
        nameKey="nome"
        isAnimationActive={false}
        content={<TreemapContent x={0} y={0} width={0} height={0} index={0} onSelect={onSelect} />}
      >
        <Tooltip
          content={({ active, payload }) => {
            const first = payload?.[0];
            const item = first?.payload as Partial<TreemapBucket> | undefined;
            if (!active || !first) return null;
            const nome = item?.nome ?? String(first.name ?? "");
            const total = item?.total ?? first.value;
            return (
              <div className="rounded-md border bg-background px-3 py-2 text-sm shadow-sm">
                <div className="font-medium">{nome}</div>
                <div className="text-muted-foreground">Total: {String(total ?? "")}</div>
              </div>
            );
          }}
        />
      </Treemap>
    </ResponsiveContainer>
  );
}

function formatDataHora(iso: string | null | undefined): string {
  return iso ? new Date(iso).toLocaleDateString("pt-BR") : "—";
}

function EntidadesTable({
  items,
  total,
  filtro,
  onLimpar,
  isLoading,
}: {
  items: EntidadeCadastrada[];
  total: number;
  filtro: Filtro | null;
  onLimpar: () => void;
  isLoading: boolean;
}) {
  const [page, setPage] = useState(1);
  useEffect(() => setPage(1), [filtro]);
  const totalPages = Math.max(1, Math.ceil(items.length / PAGE_SIZE));
  const pagina = items.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <Card id="entidades" className="scroll-mt-4">
      <CardHeader>
        <div className="flex flex-wrap items-center gap-3">
          <CardTitle className="section-heading text-base">Entidades cadastradas</CardTitle>
          <span className="text-sm text-muted-foreground">
            {items.length} de {total}
          </span>
          {filtro && (
            <span className="flex items-center gap-2 rounded-full border bg-muted px-3 py-1 text-xs">
              {filtro.rotulo}
              <button type="button" className="font-medium underline" onClick={onLimpar}>
                Limpar
              </button>
            </span>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Data revisão</TableHead>
              <TableHead>Processo</TableHead>
              <TableHead>Entidade</TableHead>
              <TableHead>Revisão</TableHead>
              <TableHead>Data envio</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={6} className="py-10 text-center text-sm text-muted-foreground">
                  Carregando...
                </TableCell>
              </TableRow>
            ) : pagina.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="py-10 text-center text-sm text-muted-foreground">
                  Nenhuma entidade{filtro ? " para o filtro." : "."}
                </TableCell>
              </TableRow>
            ) : (
              pagina.map((e) => (
                <TableRow key={`${e.tipo}-${e.id}`}>
                  <TableCell>{formatDataHora(e.data_revisao)}</TableCell>
                  <TableCell className="font-mono">
                    {formatProcesso(e.numero_processo, e.ano_processo, e.id_processo)}
                  </TableCell>
                  <TableCell className="max-w-md">
                    <span
                      className={cn(
                        "mr-2 rounded px-1.5 py-0.5 text-xs font-medium",
                        e.tipo === "obrigacao"
                          ? "bg-sky-100 text-sky-950"
                          : "bg-violet-100 text-violet-950",
                      )}
                    >
                      {e.tipo === "obrigacao" ? "Obrigação" : "Recomendação"}
                    </span>
                    <span title={e.descricao}>{truncate(e.descricao, 90)}</span>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <span>{e.revisor ?? <span className="text-muted-foreground">—</span>}</span>
                      {e.id_decisao != null && (
                        <Link
                          href={`/cgad/reviews/decisao/${e.id_decisao}/visualizar?voltar=/cgad/dashboards`}
                          className={buttonVariants({ size: "sm", variant: "outline" })}
                        >
                          Ver
                        </Link>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>{formatDataHora(e.data_envio)}</TableCell>
                  <TableCell>
                    <span
                      className={cn(
                        "rounded px-1.5 py-0.5 text-xs font-medium",
                        e.status === "dispatched"
                          ? "bg-emerald-100 text-emerald-950"
                          : "bg-amber-100 text-amber-950",
                      )}
                    >
                      {e.status === "dispatched" ? "Enviado" : "Aprovado"}
                    </span>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>

        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>
            Página {page} de {totalPages}
          </span>
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => setPage(page - 1)}
              disabled={page <= 1}
            >
              Anterior
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => setPage(page + 1)}
              disabled={page >= totalPages}
            >
              Próxima
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
