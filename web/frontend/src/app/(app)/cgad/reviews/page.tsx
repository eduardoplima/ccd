"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { Button, buttonVariants } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { SelectNative } from "@/components/ui/select-native";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useCurrentUser } from "@/hooks/use-current-user";
import {
  useAwaitingDispatch,
  useClaimLote,
  useDecisoes,
  useReleaseFromList,
  useReservas,
  useRevisores,
} from "@/hooks/use-reviews";
import { messageForError } from "@/lib/error-messages";
import { formatAcordao, formatProcesso } from "@/lib/format";
import { cn } from "@/lib/utils";
import {
  AwaitingDispatchGroup,
  DecisaoListItem,
  ReservaFiltro,
  TIPO_LABEL,
  TipoEntidade,
} from "@/schemas/review";
import { podeEditar } from "@/lib/permissoes";

const PAGE_SIZE = 20;

type Tab = "pendentes" | "reserva" | "minha-reserva" | "realizadas" | "awaiting-dispatch";

const TAB_RESERVA: Record<Exclude<Tab, "awaiting-dispatch">, ReservaFiltro> = {
  pendentes: "pendentes",
  reserva: "usuario",
  "minha-reserva": "minhas",
  realizadas: "realizadas",
};

const TAB_TEXT: Record<Tab, { title: string; subtitle: string; empty: string }> = {
  pendentes: {
    title: "Decisões pendentes",
    subtitle:
      "Revise cada decisão: edite, rejeite ou adicione as entidades extraídas do acórdão. " +
      "Multas e ressarcimentos são tratados em outra interface — a fila padrão traz " +
      "apenas decisões com obrigação ou recomendação.",
    empty: "Nenhuma decisão pendente.",
  },
  reserva: {
    title: "Reserva da equipe",
    subtitle: "Decisões reservadas por cada usuário e ainda não revisadas.",
    empty: "Nenhuma decisão pendente na reserva deste usuário.",
  },
  "minha-reserva": {
    title: "Minha reserva",
    subtitle: "Decisões reservadas para você no mutirão. Devolva as que não for revisar.",
    empty: "Nenhuma decisão na sua reserva.",
  },
  realizadas: {
    title: "Revisões realizadas",
    subtitle: "Decisões já revisadas por todos os usuários, da mais recente para a mais antiga.",
    empty: "Nenhuma revisão realizada.",
  },
  "awaiting-dispatch": {
    title: "Aguardando envio",
    subtitle: "Processos com entidades aprovadas. Marque como enviado depois de remeter ao setor.",
    empty: "",
  },
};

const BADGE_CLASS: Record<TipoEntidade, string> = {
  multa: "bg-amber-100 text-amber-950",
  obrigacao: "bg-sky-100 text-sky-950",
  ressarcimento: "bg-emerald-100 text-emerald-950",
  recomendacao: "bg-violet-100 text-violet-950",
};

const TIPO_PLURAL: Record<TipoEntidade, string> = {
  multa: "multas",
  obrigacao: "obrigações",
  recomendacao: "recomendações",
  ressarcimento: "ressarcimentos",
};

const TABS: Tab[] = ["pendentes", "reserva", "minha-reserva", "realizadas", "awaiting-dispatch"];

export default function ReviewsPage() {
  const tabParam = useSearchParams().get("tab");
  const [tab, setTab] = useState<Tab>(
    TABS.includes(tabParam as Tab) ? (tabParam as Tab) : "pendentes",
  );
  const [page, setPage] = useState(1);
  const [processoInput, setProcessoInput] = useState("");
  const [processo, setProcesso] = useState("");
  const [listaCompleta, setListaCompleta] = useState(false);
  const [usuarioReserva, setUsuarioReserva] = useState("");
  const [revisor, setRevisor] = useState("");

  const { data: me } = useCurrentUser();
  const canEdit = podeEditar(me, "cgad.reviews");
  const isAwaiting = tab === "awaiting-dispatch";
  const isMinhaReserva = tab === "minha-reserva";
  const isReserva = tab === "reserva";
  const isRealizadas = tab === "realizadas";

  const reservas = useReservas(canEdit);
  const usuariosComReserva = reservas.data ?? [];
  const usuarioSelecionado =
    usuariosComReserva.find((r) => r.usuario === usuarioReserva)?.usuario ??
    usuariosComReserva[0]?.usuario ??
    "";

  const revisores = useRevisores(isRealizadas);
  const listaRevisores = revisores.data ?? [];
  const totalRealizadas = listaRevisores.reduce((acc, r) => acc + r.total, 0);

  const decisoes = useDecisoes({
    page,
    pageSize: PAGE_SIZE,
    processo,
    listaCompleta: tab === "pendentes" ? listaCompleta : undefined,
    reserva: isAwaiting ? undefined : TAB_RESERVA[tab],
    usuario: isReserva ? usuarioSelecionado : isRealizadas ? revisor || undefined : undefined,
    enabled: !isAwaiting && (!isReserva || !!usuarioSelecionado),
  });
  const devolver = useReleaseFromList();
  const awaiting = useAwaitingDispatch({
    page,
    pageSize: PAGE_SIZE,
    enabled: isAwaiting,
  });

  const isLoading = isAwaiting ? awaiting.isLoading : decisoes.isLoading;
  const isError = isAwaiting ? awaiting.isError : decisoes.isError;
  const error = isAwaiting ? awaiting.error : decisoes.error;

  useEffect(() => {
    if (!isError) return;
    toast.error(
      messageForError(
        error,
        isAwaiting
          ? "Erro ao carregar itens aguardando envio."
          : "Erro ao carregar decisões pendentes.",
      ),
    );
  }, [isError, error, isAwaiting]);

  return (
    <main className="mx-auto flex w-full max-w-screen-2xl flex-col gap-4 p-6">
      <div>
        <h1 className="text-2xl font-semibold">{TAB_TEXT[tab].title}</h1>
        <p className="text-sm text-muted-foreground">{TAB_TEXT[tab].subtitle}</p>
      </div>

      <Tabs
        value={tab}
        onValueChange={(v) => {
          setTab(v as Tab);
          setPage(1);
        }}
      >
        <TabsList>
          <TabsTrigger value="pendentes">Pendentes</TabsTrigger>
          {canEdit && <TabsTrigger value="reserva">Reserva</TabsTrigger>}
          <TabsTrigger value="minha-reserva">Minha reserva</TabsTrigger>
          <TabsTrigger value="realizadas">Realizadas</TabsTrigger>
          <TabsTrigger value="awaiting-dispatch">Aguardando envio</TabsTrigger>
        </TabsList>
      </Tabs>

      {isReserva && (
        <div className="flex items-center gap-2">
          <Label htmlFor="usuario-reserva" className="text-sm font-normal text-muted-foreground">
            Usuário
          </Label>
          {usuariosComReserva.length === 0 ? (
            <span className="text-sm text-muted-foreground">
              {reservas.isLoading ? "Carregando..." : "Ninguém tem reserva."}
            </span>
          ) : (
            <SelectNative
              id="usuario-reserva"
              className="w-auto"
              value={usuarioSelecionado}
              onChange={(e) => {
                setUsuarioReserva(e.target.value);
                setPage(1);
              }}
            >
              {usuariosComReserva.map((r) => (
                <option key={r.usuario} value={r.usuario}>
                  {r.usuario} ({r.total} {r.total === 1 ? "pendente" : "pendentes"})
                </option>
              ))}
            </SelectNative>
          )}
        </div>
      )}

      {!isAwaiting && (
        <form
          className="flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            setProcesso(processoInput.trim());
            setPage(1);
          }}
        >
          <Input
            value={processoInput}
            onChange={(e) => setProcessoInput(e.target.value)}
            placeholder="Buscar por processo (ex.: 123/2026)"
            className="max-w-xs"
            inputMode="numeric"
          />
          <Button type="submit" variant="outline">
            Buscar
          </Button>
          {processo && (
            <Button
              type="button"
              variant="ghost"
              onClick={() => {
                setProcessoInput("");
                setProcesso("");
                setPage(1);
              }}
            >
              Limpar
            </Button>
          )}
          {isRealizadas && (
            <SelectNative
              aria-label="Revisor"
              className="w-auto"
              value={revisor}
              onChange={(e) => {
                setRevisor(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Todos ({totalRealizadas})</option>
              {listaRevisores.map((r) => (
                <option key={r.usuario} value={r.usuario}>
                  {r.usuario} ({r.total})
                </option>
              ))}
            </SelectNative>
          )}
        </form>
      )}

      {tab === "pendentes" && (
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Checkbox
              id="lista-completa"
              checked={listaCompleta}
              onCheckedChange={(v) => {
                setListaCompleta(v === true);
                setPage(1);
              }}
            />
            <Label htmlFor="lista-completa" className="text-sm font-normal text-muted-foreground">
              Lista completa (incluir decisões só com multa ou ressarcimento)
            </Label>
          </div>
          {!listaCompleta && (
            <ReservarLoteDialog
              total={decisoes.data?.total ?? 0}
              onReserved={() => {
                setTab("minha-reserva");
                setPage(1);
              }}
            />
          )}
        </div>
      )}

      {isAwaiting ? (
        <AwaitingDispatchTable
          items={awaiting.data?.items ?? []}
          total={awaiting.data?.total ?? 0}
          page={page}
          pageSize={PAGE_SIZE}
          onPageChange={setPage}
          isLoading={isLoading}
        />
      ) : (
        <DecisoesTable
          items={decisoes.data?.items ?? []}
          total={decisoes.data?.total ?? 0}
          page={page}
          pageSize={PAGE_SIZE}
          onPageChange={setPage}
          isLoading={isLoading}
          emptyMessage={TAB_TEXT[tab].empty}
          showRevisao={tab === "realizadas"}
          onDevolver={
            isMinhaReserva
              ? (id) =>
                  devolver.mutate(id, {
                    onSuccess: () => toast.success("Decisão devolvida à fila."),
                    onError: (err) =>
                      toast.error(messageForError(err, "Erro ao devolver a decisão.")),
                  })
              : undefined
          }
          isDevolvendo={devolver.isPending}
        />
      )}
    </main>
  );
}

function CountBadges({
  item,
}: {
  item: Pick<DecisaoListItem, "multas" | "obrigacoes" | "recomendacoes" | "ressarcimentos">;
}) {
  const counts: [TipoEntidade, number][] = [
    ["multa", item.multas],
    ["obrigacao", item.obrigacoes],
    ["recomendacao", item.recomendacoes],
    ["ressarcimento", item.ressarcimentos],
  ];
  return (
    <div className="flex flex-wrap gap-1">
      {counts
        .filter(([, n]) => n > 0)
        .map(([tipo, n]) => (
          <span
            key={tipo}
            className={cn("rounded px-1.5 py-0.5 text-xs font-medium", BADGE_CLASS[tipo])}
          >
            {n} {n > 1 ? TIPO_PLURAL[tipo] : TIPO_LABEL[tipo].toLowerCase()}
          </span>
        ))}
    </div>
  );
}

function Pagination({
  page,
  totalPages,
  total,
  onPageChange,
  isLoading,
}: {
  page: number;
  totalPages: number;
  total: number;
  onPageChange: (page: number) => void;
  isLoading: boolean;
}) {
  return (
    <div className="flex items-center justify-between text-sm text-muted-foreground">
      <span>
        Página {page} de {totalPages} · {total} itens
      </span>
      <div className="flex gap-2">
        <Button
          size="sm"
          variant="outline"
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1 || isLoading}
        >
          Anterior
        </Button>
        <Button
          size="sm"
          variant="outline"
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages || isLoading}
        >
          Próxima
        </Button>
      </div>
    </div>
  );
}

function ReservarLoteDialog({ total, onReserved }: { total: number; onReserved: () => void }) {
  const [open, setOpen] = useState(false);
  const [quantidade, setQuantidade] = useState("");
  const claimLote = useClaimLote();

  return (
    <>
      <Button variant="outline" disabled={total === 0} onClick={() => setOpen(true)}>
        Reservar lote
      </Button>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const n = Number(quantidade);
              if (!Number.isInteger(n) || n < 1 || n > total) return;
              claimLote.mutate(n, {
                onSuccess: (res) => {
                  toast.success(
                    res.quantidade === n
                      ? `${res.quantidade} ${res.quantidade === 1 ? "decisão reservada" : "decisões reservadas"}.`
                      : `${res.quantidade} de ${n} decisões reservadas — as demais foram reservadas por outro usuário.`,
                  );
                  setOpen(false);
                  setQuantidade("");
                  onReserved();
                },
                onError: (err) => toast.error(messageForError(err, "Erro ao reservar o lote.")),
              });
            }}
            className="space-y-4"
          >
            <DialogHeader>
              <DialogTitle>Reservar lote para o mutirão</DialogTitle>
              <DialogDescription>
                As decisões mais antigas da fila (sem reserva de outro usuário) serão reservadas
                para você e sairão de Pendentes.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-2">
              <Label htmlFor="quantidade-lote">Quantidade (1 a {total})</Label>
              <Input
                id="quantidade-lote"
                type="number"
                min={1}
                max={total}
                value={quantidade}
                onChange={(e) => setQuantidade(e.target.value)}
                autoFocus
                required
              />
            </div>
            <DialogFooter>
              <Button type="submit" disabled={claimLote.isPending}>
                {claimLote.isPending ? "Reservando..." : "Reservar"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </>
  );
}

function DecisoesTable({
  items,
  total,
  page,
  pageSize,
  onPageChange,
  isLoading,
  emptyMessage = "Nenhuma decisão pendente.",
  showRevisao = false,
  onDevolver,
  isDevolvendo = false,
}: {
  items: DecisaoListItem[];
  total: number;
  page: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  isLoading: boolean;
  emptyMessage?: string;
  showRevisao?: boolean;
  onDevolver?: (id: number) => void;
  isDevolvendo?: boolean;
}) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="space-y-3">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Processo</TableHead>
            <TableHead>Acórdão</TableHead>
            <TableHead>Entidades</TableHead>
            <TableHead>{showRevisao ? "Revisado por" : "Reservado por"}</TableHead>
            <TableHead>{showRevisao ? "Revisado em" : "Extraído em"}</TableHead>
            <TableHead className="w-0" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoading ? (
            <TableRow>
              <TableCell colSpan={6} className="py-10 text-center text-sm text-muted-foreground">
                Carregando...
              </TableCell>
            </TableRow>
          ) : items.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} className="py-10 text-center text-sm text-muted-foreground">
                {emptyMessage}
              </TableCell>
            </TableRow>
          ) : (
            items.map((item) => (
              <TableRow key={item.id}>
                <TableCell className="font-mono">
                  {formatProcesso(item.numero_processo, item.ano_processo, item.id_processo)}
                </TableCell>
                <TableCell>
                  {formatAcordao(item.numero_acordao, item.ano_acordao, item.tipo_acordao)}
                </TableCell>
                <TableCell>
                  <CountBadges item={item} />
                </TableCell>
                <TableCell>
                  {(showRevisao ? item.revisado_por : item.claimed_by) ?? (
                    <span className="text-muted-foreground">—</span>
                  )}
                </TableCell>
                <TableCell>
                  {(showRevisao ? item.data_revisao : item.data_extracao) ? (
                    new Date(
                      (showRevisao ? item.data_revisao : item.data_extracao) as string,
                    ).toLocaleDateString("pt-BR")
                  ) : (
                    <span className="text-muted-foreground">—</span>
                  )}
                </TableCell>
                <TableCell>
                  <div className="flex gap-2">
                    <Link
                      href={
                        showRevisao
                          ? `/cgad/reviews/decisao/${item.id}/visualizar?tab=realizadas`
                          : `/cgad/reviews/decisao/${item.id}`
                      }
                      className={buttonVariants({ size: "sm" })}
                    >
                      {showRevisao ? "Ver" : "Revisar"}
                    </Link>
                    {onDevolver && (
                      <Button
                        size="sm"
                        variant="outline"
                        disabled={isDevolvendo}
                        onClick={() => onDevolver(item.id)}
                      >
                        Devolver
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>

      <Pagination
        page={page}
        totalPages={totalPages}
        total={total}
        onPageChange={onPageChange}
        isLoading={isLoading}
      />
    </div>
  );
}

function AwaitingDispatchTable({
  items,
  total,
  page,
  pageSize,
  onPageChange,
  isLoading,
}: {
  items: AwaitingDispatchGroup[];
  total: number;
  page: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  isLoading: boolean;
}) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const router = useRouter();

  return (
    <div className="space-y-3">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Processo</TableHead>
            <TableHead>Entidades</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Revisado por</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoading ? (
            <TableRow>
              <TableCell colSpan={4} className="py-10 text-center text-sm text-muted-foreground">
                Carregando...
              </TableCell>
            </TableRow>
          ) : items.length === 0 ? (
            <TableRow>
              <TableCell colSpan={4} className="py-10 text-center text-sm text-muted-foreground">
                Nenhum item aguardando envio.
              </TableCell>
            </TableRow>
          ) : (
            items.map((item) => (
              // ponytail: processo com mais de uma decisão abre a primeira
              <TableRow
                key={item.id_processo}
                className={cn(item.ids_decisao.length > 0 && "cursor-pointer")}
                onClick={() => {
                  const id = item.ids_decisao[0];
                  if (id !== undefined)
                    router.push(`/cgad/reviews/decisao/${id}/visualizar?tab=awaiting-dispatch`);
                }}
              >
                <TableCell className="font-mono">
                  {formatProcesso(item.numero_processo, item.ano_processo, item.id_processo)}
                  {item.ids_decisao.length > 1 && (
                    <span className="ml-2 font-sans text-xs text-muted-foreground">
                      {item.ids_decisao.length} decisões
                    </span>
                  )}
                </TableCell>
                <TableCell>
                  <CountBadges item={item} />
                </TableCell>
                <TableCell>
                  <span
                    className={cn(
                      "rounded px-1.5 py-0.5 text-xs font-medium",
                      item.status === "dispatched"
                        ? "bg-emerald-100 text-emerald-950"
                        : "bg-amber-100 text-amber-950",
                    )}
                  >
                    {item.status === "dispatched" ? "Enviado" : "Aprovado"}
                  </span>
                </TableCell>
                <TableCell>
                  {item.revisores.length > 0 ? (
                    item.revisores.join(", ")
                  ) : (
                    <span className="text-muted-foreground">—</span>
                  )}
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>

      <Pagination
        page={page}
        totalPages={totalPages}
        total={total}
        onPageChange={onPageChange}
        isLoading={isLoading}
      />
    </div>
  );
}
