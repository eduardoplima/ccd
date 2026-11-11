"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
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
import { Textarea } from "@/components/ui/textarea";
import { useRemocoes, useRemover } from "@/hooks/use-remocoes";
import { messageForError } from "@/lib/error-messages";
import { cn } from "@/lib/utils";
import { Acordao, ItemCurado } from "@/schemas/remocoes";

const STATUS_LABEL: Record<ItemCurado["status"], string> = {
  approved: "Aprovado",
  dispatched: "Enviado",
  removed: "Removido",
};

const chave = (i: Pick<ItemCurado, "tipo" | "id">) => `${i.tipo}:${i.id}`;

function rotuloAcordao(a: Acordao | undefined, id?: number | null): string {
  if (!a) return id ? `#${id}` : "—";
  const tipo = a.tipo === "D" ? "Decisão" : "Acórdão";
  const num = a.numero ? `${Number(a.numero)}/${a.ano ?? ""}` : `#${a.id_composicao_pauta}`;
  const data = a.data_sessao ? ` (${new Date(a.data_sessao).toLocaleDateString("pt-BR")})` : "";
  return `${tipo} ${num}${data}`;
}

export default function RemocoesPage() {
  const [entrada, setEntrada] = useState("");
  const [processo, setProcesso] = useState<string | null>(null);
  const [selecionados, setSelecionados] = useState<Set<string>>(new Set());
  const [acordao, setAcordao] = useState("");
  const [justificativa, setJustificativa] = useState("");
  const [confirmando, setConfirmando] = useState(false);

  const { data, isFetching, isError, error } = useRemocoes(processo);
  const remover = useRemover(processo);

  useEffect(() => {
    if (isError) toast.error(messageForError(error, "Erro ao consultar o processo."));
  }, [isError, error]);

  useEffect(() => {
    setSelecionados(new Set());
    setAcordao("");
    setJustificativa("");
    setConfirmando(false);
  }, [processo]);

  const acordaos = useMemo(
    () => new Map((data?.acordaos ?? []).map((a) => [a.id_composicao_pauta, a])),
    [data],
  );
  const podeRemover = selecionados.size > 0 && !!acordao && justificativa.trim().length > 0;

  function consultar(e: FormEvent) {
    e.preventDefault();
    const v = entrada.trim();
    if (!/^\d{1,6}\/\d{4}$/.test(v)) {
      toast.error("Informe o processo no formato NNNNNN/AAAA.");
      return;
    }
    const [n, a] = v.split("/");
    setProcesso(`${n.padStart(6, "0")}/${a}`);
  }

  function alternar(item: ItemCurado, marcado: boolean) {
    setConfirmando(false);
    setSelecionados((prev) => {
      const next = new Set(prev);
      if (marcado) next.add(chave(item));
      else next.delete(chave(item));
      return next;
    });
  }

  function enviar() {
    if (!data || !podeRemover) return;
    if (!confirmando) {
      setConfirmando(true);
      return;
    }
    const itens = data.itens
      .filter((i) => selecionados.has(chave(i)))
      .map((i) => ({ tipo: i.tipo, id: i.id }));
    remover.mutate(
      {
        id_processo: data.id_processo,
        id_composicao_pauta_remocao: Number(acordao),
        justificativa: justificativa.trim(),
        itens,
      },
      {
        onSuccess: (r) => {
          toast.success(`${r.removidos} item(ns) removido(s) do acervo.`);
          setSelecionados(new Set());
          setJustificativa("");
          setConfirmando(false);
        },
        onError: (err) => {
          setConfirmando(false);
          toast.error(messageForError(err, "Erro ao remover."));
        },
      },
    );
  }

  return (
    <main className="mx-auto flex w-full max-w-screen-2xl flex-col gap-6 p-6">
      <div>
        <h1 className="text-2xl font-semibold">Remoção de obrigações e recomendações</h1>
        <p className="text-sm text-muted-foreground">
          Retira do acervo curado as obrigações e recomendações que um acórdão posterior
          desconstituiu ou excluiu. O registro é mantido, com o acórdão, a justificativa, o
          responsável e a data da remoção.
        </p>
      </div>

      <Card>
        <CardContent className="pt-6">
          <form onSubmit={consultar} className="flex flex-wrap items-end gap-3">
            <div className="flex flex-col gap-1">
              <Label htmlFor="processo">Processo</Label>
              <Input
                id="processo"
                placeholder="200163/2021"
                value={entrada}
                onChange={(e) => setEntrada(e.target.value)}
                className="w-48"
              />
            </div>
            <Button type="submit" disabled={isFetching}>
              {isFetching ? "Consultando…" : "Consultar"}
            </Button>
          </form>
        </CardContent>
      </Card>

      {data && (
        <Card>
          <CardHeader>
            <CardTitle className="section-heading text-base">
              Itens curados do processo {data.processo}
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-6">
            {data.itens.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                Nenhuma obrigação ou recomendação aprovada para este processo. Cadastre-a pela
                revisão da decisão antes de removê-la.
              </p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-10" />
                    <TableHead>Tipo</TableHead>
                    <TableHead>Decisão de origem</TableHead>
                    <TableHead>Descrição</TableHead>
                    <TableHead>Órgão</TableHead>
                    <TableHead>Situação</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.itens.map((item) => {
                    const removido = item.status === "removed";
                    return (
                      <TableRow key={chave(item)} className={cn(removido && "opacity-60")}>
                        <TableCell>
                          {!removido && (
                            <Checkbox
                              aria-label="Selecionar"
                              checked={selecionados.has(chave(item))}
                              onCheckedChange={(v) => alternar(item, v === true)}
                            />
                          )}
                        </TableCell>
                        <TableCell>
                          {item.tipo === "obrigacao" ? "Obrigação" : "Recomendação"}
                        </TableCell>
                        <TableCell className="whitespace-nowrap">
                          {rotuloAcordao(acordaos.get(item.id_composicao_pauta))}
                        </TableCell>
                        <TableCell className="max-w-xl whitespace-pre-wrap text-sm">
                          {item.descricao}
                          {removido && (
                            <p className="mt-2 text-xs text-muted-foreground">
                              Removido por{" "}
                              {rotuloAcordao(
                                acordaos.get(item.id_composicao_pauta_remocao ?? -1),
                                item.id_composicao_pauta_remocao,
                              )}
                              {item.data_remocao &&
                                ` em ${new Date(item.data_remocao).toLocaleDateString("pt-BR")}`}
                              {item.removido_por && ` (${item.removido_por})`}:{" "}
                              {item.justificativa_remocao}
                            </p>
                          )}
                        </TableCell>
                        <TableCell>{item.orgao ?? "—"}</TableCell>
                        <TableCell>
                          <Badge variant={removido ? "outline" : "secondary"}>
                            {STATUS_LABEL[item.status]}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            )}

            {data.itens.some((i) => i.status !== "removed") && (
              <div className="grid gap-4 md:grid-cols-2">
                <div className="flex flex-col gap-1">
                  <Label htmlFor="acordao">Acórdão que determinou a remoção</Label>
                  <SelectNative
                    id="acordao"
                    value={acordao}
                    onChange={(e) => {
                      setAcordao(e.target.value);
                      setConfirmando(false);
                    }}
                  >
                    <option value="">Selecione…</option>
                    {data.acordaos.map((a) => (
                      <option key={a.id_composicao_pauta} value={a.id_composicao_pauta}>
                        {rotuloAcordao(a)}
                      </option>
                    ))}
                  </SelectNative>
                </div>
                <div className="flex flex-col gap-1 md:col-span-2">
                  <Label htmlFor="justificativa">Justificativa</Label>
                  <Textarea
                    id="justificativa"
                    rows={4}
                    value={justificativa}
                    onChange={(e) => {
                      setJustificativa(e.target.value);
                      setConfirmando(false);
                    }}
                  />
                </div>
                <div className="flex items-center gap-3 md:col-span-2">
                  <Button
                    variant="destructive"
                    disabled={!podeRemover || remover.isPending}
                    onClick={enviar}
                  >
                    {remover.isPending
                      ? "Removendo…"
                      : confirmando
                        ? `Confirmar remoção de ${selecionados.size} item(ns)`
                        : "Remover selecionados"}
                  </Button>
                  {confirmando && (
                    <Button variant="ghost" onClick={() => setConfirmando(false)}>
                      Cancelar
                    </Button>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </main>
  );
}
