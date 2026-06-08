"use client";

import { parseAsString, parseAsStringEnum, useQueryState } from "nuqs";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useBuscarDebitosPessoa, useBuscarPessoas, useBuscarProcesso } from "@/hooks/use-busca";
import { formatBRL, formatDate } from "@/lib/format";

type Modo = "pessoa" | "processo";
type TipoProc = "origem" | "execucao";

export default function BuscaPage() {
  const [modo, setModo] = useQueryState(
    "modo",
    parseAsStringEnum<Modo>(["pessoa", "processo"]).withDefault("pessoa"),
  );
  return (
    <div className="flex flex-col gap-6">
      <h1 className="section-heading text-2xl">Busca</h1>
      <p className="text-sm text-muted-foreground -mt-3">
        Investigar débitos por pessoa (nome/CPF) ou por processo (número/ano).
      </p>

      <ModoToggle modo={modo} onChange={(v) => void setModo(v)} />

      {modo === "pessoa" ? <BuscaPessoa /> : <BuscaProcesso />}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Toggle de modo
// ---------------------------------------------------------------------------

function ModoToggle({ modo, onChange }: { modo: Modo; onChange: (v: Modo) => void }) {
  return (
    <div className="flex gap-2">
      <Button
        variant={modo === "pessoa" ? "default" : "outline"}
        size="sm"
        onClick={() => onChange("pessoa")}
      >
        Por pessoa
      </Button>
      <Button
        variant={modo === "processo" ? "default" : "outline"}
        size="sm"
        onClick={() => onChange("processo")}
      >
        Por processo
      </Button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Modo: por pessoa
// ---------------------------------------------------------------------------

function BuscaPessoa() {
  const [q, setQ] = useQueryState("q", parseAsString.withDefault(""));
  const [pessoaSel, setPessoaSel] = useState<{ cpf: string; nome: string } | null>(null);
  const qTrim = q.trim();
  const enabled = qTrim.length >= 3;
  const { data, isFetching } = useBuscarPessoas(qTrim, 1, 50, enabled);

  return (
    <>
      <div className="flex flex-col gap-1.5 max-w-xl">
        <Label htmlFor="f-q">Nome ou CPF/CNPJ</Label>
        <Input
          id="f-q"
          value={q}
          onChange={(e) => void setQ(e.target.value)}
          placeholder="mín. 3 caracteres"
        />
      </div>

      {!enabled ? (
        <p className="text-sm text-muted-foreground">Digite 3+ caracteres pra buscar.</p>
      ) : (
        <div className="flex flex-col gap-3">
          <p className="text-xs text-muted-foreground">
            {isFetching ? "Carregando..." : `${data?.total ?? 0} pessoas`}
          </p>
          <div className="rounded-lg border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>CPF/CNPJ</TableHead>
                  <TableHead className="text-right">Débitos</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data?.items.length === 0 && !isFetching ? (
                  <TableRow>
                    <TableCell colSpan={3} className="py-8 text-center text-muted-foreground">
                      Nenhum resultado.
                    </TableCell>
                  </TableRow>
                ) : (
                  data?.items.map((p) => (
                    <TableRow
                      key={p.idPessoa}
                      className={p.qtdDebitos > 0 ? "cursor-pointer hover:bg-muted/40" : ""}
                      onClick={() => {
                        if (p.qtdDebitos > 0 && p.cpfcnpj) {
                          setPessoaSel({ cpf: p.cpfcnpj, nome: p.nome });
                        }
                      }}
                    >
                      <TableCell>{p.nome}</TableCell>
                      <TableCell className="font-mono text-xs">{p.cpfcnpj ?? "—"}</TableCell>
                      <TableCell className="text-right">{p.qtdDebitos}</TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </div>
      )}

      <DebitosPessoaSheet pessoa={pessoaSel} onClose={() => setPessoaSel(null)} />
    </>
  );
}

// ---------------------------------------------------------------------------
// Modo: por processo
// ---------------------------------------------------------------------------

function BuscaProcesso() {
  const [numero, setNumero] = useQueryState("num", parseAsString.withDefault(""));
  const [ano, setAno] = useQueryState("ano", parseAsString.withDefault(""));
  const [tipo, setTipo] = useQueryState(
    "tipo",
    parseAsStringEnum<TipoProc>(["origem", "execucao"]).withDefault("origem"),
  );
  const [pessoaSel, setPessoaSel] = useState<{ cpf: string; nome: string } | null>(null);

  const valido = /^\d{1,6}$/.test(numero) && /^\d{4}$/.test(ano);
  const { data, isFetching, error } = useBuscarProcesso(numero, ano, tipo, valido);

  return (
    <>
      <div className="grid gap-3 md:grid-cols-3 max-w-2xl">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="f-num">Número</Label>
          <Input
            id="f-num"
            inputMode="numeric"
            maxLength={6}
            value={numero}
            placeholder="ex: 003636"
            onChange={(e) => void setNumero(e.target.value.replace(/\D/g, ""))}
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="f-ano">Ano</Label>
          <Input
            id="f-ano"
            inputMode="numeric"
            maxLength={4}
            value={ano}
            placeholder="ex: 2017"
            onChange={(e) => void setAno(e.target.value.replace(/\D/g, ""))}
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <Label>Tipo</Label>
          <div className="flex items-center gap-2 h-9">
            <Button
              variant={tipo === "origem" ? "default" : "outline"}
              size="sm"
              onClick={() => void setTipo("origem")}
            >
              Origem
            </Button>
            <Button
              variant={tipo === "execucao" ? "default" : "outline"}
              size="sm"
              onClick={() => void setTipo("execucao")}
            >
              Execução
            </Button>
          </div>
        </div>
      </div>

      {!valido ? (
        <p className="text-sm text-muted-foreground">
          Preencha número (até 6 dígitos) e ano (4 dígitos).
        </p>
      ) : isFetching ? (
        <p className="text-sm text-muted-foreground">Carregando...</p>
      ) : error ? (
        <p className="text-sm text-rose-600">Processo não encontrado.</p>
      ) : data ? (
        <ProcessoResultadoView
          data={data}
          onAbrirPessoa={(cpf, nome) => setPessoaSel({ cpf, nome })}
        />
      ) : null}

      <DebitosPessoaSheet
        pessoa={pessoaSel}
        idProcesso={data?.processo.idProcesso}
        onClose={() => setPessoaSel(null)}
      />
    </>
  );
}

function ProcessoResultadoView({
  data,
  onAbrirPessoa,
}: {
  data: NonNullable<ReturnType<typeof useBuscarProcesso>["data"]>;
  onAbrirPessoa: (cpf: string, nome: string) => void;
}) {
  const { processo, pessoas } = data;
  return (
    <div className="flex flex-col gap-4">
      <div className="rounded-lg border p-4 bg-muted/20">
        <p className="text-sm font-medium">
          {processo.numeroProcesso}/{processo.anoProcesso}
        </p>
        {processo.assunto ? (
          <p className="text-xs text-muted-foreground mt-1">{processo.assunto}</p>
        ) : null}
        <div className="mt-2 flex gap-4 text-xs text-muted-foreground">
          {processo.interessado ? <span>Interessado: {processo.interessado}</span> : null}
          {processo.valor != null ? <span>Valor: {formatBRL(processo.valor)}</span> : null}
        </div>
      </div>

      <p className="text-xs text-muted-foreground">
        {pessoas.length} pessoa{pessoas.length === 1 ? "" : "s"} envolvida
        {pessoas.length === 1 ? "" : "s"}
      </p>
      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nome</TableHead>
              <TableHead>CPF/CNPJ</TableHead>
              <TableHead className="text-right">Débitos no processo</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {pessoas.length === 0 ? (
              <TableRow>
                <TableCell colSpan={3} className="py-8 text-center text-muted-foreground">
                  Sem pessoas vinculadas.
                </TableCell>
              </TableRow>
            ) : (
              pessoas.map((p) => (
                <TableRow
                  key={p.idPessoa}
                  className="cursor-pointer hover:bg-muted/40"
                  onClick={() => p.cpfcnpj && onAbrirPessoa(p.cpfcnpj, p.nome)}
                >
                  <TableCell>{p.nome}</TableCell>
                  <TableCell className="font-mono text-xs">{p.cpfcnpj ?? "—"}</TableCell>
                  <TableCell className="text-right">{p.qtdDebitos}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sheet de débitos da pessoa
// ---------------------------------------------------------------------------

function DebitosPessoaSheet({
  pessoa,
  idProcesso,
  onClose,
}: {
  pessoa: { cpf: string; nome: string } | null;
  idProcesso?: number;
  onClose: () => void;
}) {
  const { data, isFetching } = useBuscarDebitosPessoa(
    pessoa?.cpf ?? null,
    idProcesso,
    pessoa !== null,
  );
  return (
    <Sheet open={pessoa !== null} onOpenChange={(v) => !v && onClose()}>
      <SheetContent className="w-full sm:max-w-3xl overflow-y-auto">
        <SheetHeader>
          <SheetTitle>{pessoa?.nome ?? "Débitos"}</SheetTitle>
          <SheetDescription className="font-mono text-xs">
            {pessoa?.cpf} {idProcesso ? `· dentro do processo` : ""}
          </SheetDescription>
        </SheetHeader>
        <div className="mt-4">
          {isFetching ? (
            <p className="text-sm text-muted-foreground">Carregando...</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Id Débito</TableHead>
                  <TableHead>Origem</TableHead>
                  <TableHead>Execução</TableHead>
                  <TableHead className="text-right">Valor original</TableHead>
                  <TableHead className="text-right">Pago</TableHead>
                  <TableHead>Ato</TableHead>
                  <TableHead>Baixa</TableHead>
                  <TableHead>Matches</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data?.items.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="py-8 text-center text-muted-foreground">
                      Sem débitos.
                    </TableCell>
                  </TableRow>
                ) : (
                  data?.items.map((d) => (
                    <TableRow key={d.idDebito}>
                      <TableCell className="font-mono text-xs">{d.idDebito}</TableCell>
                      <TableCell className="font-mono text-xs">
                        {d.idProcessoOrigem ?? "—"}
                      </TableCell>
                      <TableCell className="font-mono text-xs">
                        {d.idProcessoExecucao ?? "—"}
                      </TableCell>
                      <TableCell className="text-right font-mono text-xs">
                        {d.valorOriginalDebito != null ? formatBRL(d.valorOriginalDebito) : "—"}
                      </TableCell>
                      <TableCell className="text-right font-mono text-xs">
                        {d.valorPago != null ? formatBRL(d.valorPago) : "—"}
                      </TableCell>
                      <TableCell className="font-mono text-xs">{formatDate(d.dataAto)}</TableCell>
                      <TableCell className="font-mono text-xs">{formatDate(d.dataBaixa)}</TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          {d.matchesPessoa > 0 ? (
                            <Badge variant="outline" className="text-[10px]">
                              P:{d.matchesPessoa}
                            </Badge>
                          ) : null}
                          {d.matchesGuia > 0 ? (
                            <Badge variant="outline" className="text-[10px]">
                              G:{d.matchesGuia}
                            </Badge>
                          ) : null}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
