"use client";

import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
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
import { useCurrentUser } from "@/hooks/use-current-user";
import { useCadastros, useCriarCadastro, useLookupProcesso } from "@/hooks/use-desconto-folha";
import { messageForError } from "@/lib/error-messages";
import { formatCurrencyBRL } from "@/lib/format";
import { STATUS_EXTRACAO, formatData } from "./_shared";

const SIZE = 50;

export default function DescontoFolhaPage() {
  const { data: me } = useCurrentUser();
  const isAdmin = me?.papel === "admin";
  const [qInput, setQInput] = useState("");
  const [q, setQ] = useState("");
  const [page, setPage] = useState(1);
  const [novoOpen, setNovoOpen] = useState(false);

  const { data, isLoading } = useCadastros({ q, page, size: SIZE });
  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / SIZE));

  return (
    <main className="mx-auto flex w-full max-w-screen-2xl flex-col gap-4 p-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Desconto em Folha</h1>
          <p className="text-sm text-muted-foreground">
            Processos notificados para desconto em folha, a resposta do órgão no apensado e o
            crédito correspondente no FRAP.
          </p>
        </div>
        {isAdmin && <Button onClick={() => setNovoOpen(true)}>Novo cadastro</Button>}
      </div>

      <form
        className="flex gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          setQ(qInput.trim());
          setPage(1);
        }}
      >
        <Input
          value={qInput}
          onChange={(e) => setQInput(e.target.value)}
          placeholder="Processo (ex.: 100/2023), responsável ou órgão"
          className="max-w-sm"
        />
        <Button type="submit" variant="outline">
          Buscar
        </Button>
        {q && (
          <Button
            type="button"
            variant="ghost"
            onClick={() => {
              setQInput("");
              setQ("");
              setPage(1);
            }}
          >
            Limpar
          </Button>
        )}
      </form>

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Processo</TableHead>
              <TableHead>Órgão</TableHead>
              <TableHead>Responsável</TableHead>
              <TableHead>Notificação</TableHead>
              <TableHead>AR</TableHead>
              <TableHead>Resposta</TableHead>
              <TableHead>Valor</TableHead>
              <TableHead className="w-0" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={8} className="py-10 text-center text-sm text-muted-foreground">
                  Carregando...
                </TableCell>
              </TableRow>
            ) : (data?.items.length ?? 0) === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="py-10 text-center text-sm text-muted-foreground">
                  Nenhum cadastro.
                </TableCell>
              </TableRow>
            ) : (
              data!.items.map((c) => {
                const st = STATUS_EXTRACAO[c.statusExtracao];
                return (
                  <TableRow key={c.id}>
                    <TableCell className="whitespace-nowrap font-mono text-xs font-medium">
                      {c.processo}
                    </TableCell>
                    <TableCell className="max-w-[260px] truncate" title={c.orgao ?? ""}>
                      {c.orgao ?? "—"}
                    </TableCell>
                    <TableCell className="max-w-[260px] truncate" title={c.responsavel ?? ""}>
                      {c.responsavel ?? "—"}
                      {c.idDebito == null && (
                        <span className="ml-2 text-xs text-amber-700">sem débito</span>
                      )}
                    </TableCell>
                    <TableCell className="whitespace-nowrap text-sm">
                      {c.notificacao.numero ?? "—"}
                      <div className="text-xs text-muted-foreground">
                        {formatData(c.notificacao.data)}
                      </div>
                    </TableCell>
                    <TableCell className="whitespace-nowrap text-sm">
                      {c.ar.numeroPostagem ?? "—"}
                      <div className="text-xs text-muted-foreground">{formatData(c.ar.data)}</div>
                    </TableCell>
                    <TableCell className="whitespace-nowrap text-sm">
                      {c.resposta.processo ? (
                        <>
                          <span className="font-mono text-xs">{c.resposta.processo}</span>
                          {c.resposta.evento != null && (
                            <span className="ml-1 text-xs text-muted-foreground">
                              Ev. {c.resposta.evento}
                            </span>
                          )}
                          <div className="text-xs text-muted-foreground">
                            {formatData(c.resposta.data)}
                          </div>
                        </>
                      ) : (
                        "—"
                      )}
                    </TableCell>
                    <TableCell className="whitespace-nowrap text-sm">
                      <div>{c.valorTotal != null ? formatCurrencyBRL(c.valorTotal) : "—"}</div>
                      <div className="flex items-center gap-1 text-xs text-muted-foreground">
                        <Badge variant={st.variant}>{st.label}</Badge>
                        {c.qtdValores > 0 && (
                          <span>
                            {c.qtdMatches}/{c.qtdValores} FRAP
                          </span>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Link
                        href={`/ccd/desconto-folha/${c.id}`}
                        className={buttonVariants({ size: "sm", variant: "outline" })}
                      >
                        Detalhes
                      </Link>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>
          Página {page} de {totalPages} · {total} cadastro(s)
        </span>
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            disabled={page <= 1}
            onClick={() => setPage(page - 1)}
          >
            Anterior
          </Button>
          <Button
            size="sm"
            variant="outline"
            disabled={page >= totalPages}
            onClick={() => setPage(page + 1)}
          >
            Próxima
          </Button>
        </div>
      </div>

      <NovoCadastroDialog open={novoOpen} onOpenChange={setNovoOpen} />
    </main>
  );
}

function NovoCadastroDialog({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (v: boolean) => void;
}) {
  const [processoInput, setProcessoInput] = useState("");
  const [processo, setProcesso] = useState("");
  const [idDebito, setIdDebito] = useState("");
  const [nomeOrgao, setNomeOrgao] = useState("");
  const lookup = useLookupProcesso(processo);
  const criar = useCriarCadastro();

  const debitos = lookup.data?.debitos ?? [];
  const orgaoSugerido = lookup.data?.orgao ?? "";

  function fechar() {
    onOpenChange(false);
    setProcessoInput("");
    setProcesso("");
    setIdDebito("");
    setNomeOrgao("");
  }

  return (
    <Dialog open={open} onOpenChange={(v) => (v ? onOpenChange(v) : fechar())}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Novo cadastro</DialogTitle>
          <DialogDescription>
            Informe o processo de execução. O débito e o responsável vêm do banco processo; a
            notificação, o AR e o apensado são localizados ao salvar.
          </DialogDescription>
        </DialogHeader>
        <form
          className="flex flex-col gap-4"
          onSubmit={(e) => {
            e.preventDefault();
            if (!lookup.data) return;
            criar.mutate(
              {
                idProcesso: lookup.data.idProcesso,
                idDebito: idDebito ? Number(idDebito) : null,
                nomeOrgao: nomeOrgao.trim() || orgaoSugerido || null,
              },
              {
                onSuccess: () => {
                  toast.success("Cadastro criado.");
                  fechar();
                },
                onError: (err) => toast.error(messageForError(err, "Erro ao criar o cadastro.")),
              },
            );
          }}
        >
          <div className="flex flex-col gap-2">
            <Label htmlFor="n-processo">Processo</Label>
            <div className="flex gap-2">
              <Input
                id="n-processo"
                value={processoInput}
                onChange={(e) => setProcessoInput(e.target.value)}
                placeholder="100/2023"
                inputMode="numeric"
              />
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setProcesso(processoInput.trim());
                  setIdDebito("");
                }}
              >
                Localizar
              </Button>
            </div>
            {lookup.isFetching && (
              <p className="text-xs text-muted-foreground">Consultando o banco processo...</p>
            )}
            {lookup.isError && (
              <p className="text-xs text-destructive">
                {messageForError(lookup.error, "Processo não encontrado.")}
              </p>
            )}
            {lookup.data && (
              <p className="text-xs text-muted-foreground">
                {lookup.data.processo} · {debitos.length} débito(s)
              </p>
            )}
          </div>

          <div className="flex flex-col gap-2">
            <Label htmlFor="n-debito">Débito e responsável</Label>
            <SelectNative
              id="n-debito"
              value={idDebito}
              onChange={(e) => setIdDebito(e.target.value)}
              disabled={!lookup.data}
            >
              <option value="">Sem débito (completar depois)</option>
              {debitos.map((d) => (
                <option key={d.idDebito} value={d.idDebito}>
                  #{d.idDebito} · {d.tipo ?? "débito"} · {formatCurrencyBRL(d.valorOriginal)} ·{" "}
                  {d.nomePessoa ?? "sem responsável"}
                  {d.cancelado ? " (cancelado)" : ""}
                </option>
              ))}
            </SelectNative>
          </div>

          <div className="flex flex-col gap-2">
            <Label htmlFor="n-orgao">Órgão notificado</Label>
            <Input
              id="n-orgao"
              value={nomeOrgao}
              onChange={(e) => setNomeOrgao(e.target.value)}
              placeholder={orgaoSugerido || "Nome do órgão"}
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={fechar}>
              Cancelar
            </Button>
            <Button type="submit" disabled={!lookup.data || criar.isPending}>
              {criar.isPending ? "Salvando..." : "Salvar"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
