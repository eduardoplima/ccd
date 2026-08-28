"use client";

import { useState } from "react";

import { Badge } from "@/components/ui/badge";
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
import {
  useTipologiaAtrasoSistemico,
  useTipologiaCpfSemSiai,
  useTipologiaParcelaDuplicada,
  useTipologiaRepasseMulti,
} from "@/hooks/use-desconto-folha";
import { formatBRL, formatDate } from "@/lib/format";

type TipologiaKey = "repasse-multi" | "cpf-sem-siai" | "parcela-dup" | "atraso-sistemico";

export function TipologiasTab({ onAbrirPessoa }: { onAbrirPessoa: (cpfCnpj: string) => void }) {
  const [aberta, setAberta] = useState<TipologiaKey | null>(null);

  return (
    <div className="flex flex-col gap-4">
      <p className="text-xs text-muted-foreground">
        Análises orientadas a problemas conhecidos do desconto em folha. Clique em um cartão para
        ver os casos detectados.
      </p>

      <div className="grid gap-3 md:grid-cols-2">
        <CardTipologia
          titulo="Repasse multi-parcela"
          descricao="Lançamentos cuja soma cobre 2+ parcelas em atraso da mesma pessoa (caso Nereu)."
          onClick={() => setAberta("repasse-multi")}
        />
        <CardTipologia
          titulo="CPF sem cadastro SIAIPessoal"
          descricao="Servidores cadastrados em desconto-folha sem CPF correspondente em BdSIAIPessoal."
          onClick={() => setAberta("cpf-sem-siai")}
        />
        <CardTipologia
          titulo="Parcela duplicada"
          descricao="Mesma parcela (nº/mês/ano/valor) registrada 2+ vezes para o mesmo desconto."
          onClick={() => setAberta("parcela-dup")}
        />
        <CardTipologia
          titulo="Atraso sistemático por órgão"
          descricao="Órgãos com ≥3 meses consecutivos com mais de 20% de NAO_DESCONTADA."
          onClick={() => setAberta("atraso-sistemico")}
        />
      </div>

      <RepasseMultiSheet open={aberta === "repasse-multi"} onClose={() => setAberta(null)} />
      <CpfSemSiaiSheet
        open={aberta === "cpf-sem-siai"}
        onClose={() => setAberta(null)}
        onAbrirPessoa={onAbrirPessoa}
      />
      <ParcelaDuplicadaSheet
        open={aberta === "parcela-dup"}
        onClose={() => setAberta(null)}
        onAbrirPessoa={onAbrirPessoa}
      />
      <AtrasoSistemicoSheet open={aberta === "atraso-sistemico"} onClose={() => setAberta(null)} />
    </div>
  );
}

function CardTipologia({
  titulo,
  descricao,
  onClick,
}: {
  titulo: string;
  descricao: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="rounded-lg border p-4 text-left transition hover:bg-muted/40 hover:shadow-sm"
    >
      <div className="font-medium">{titulo}</div>
      <p className="mt-1 text-xs text-muted-foreground">{descricao}</p>
    </button>
  );
}

// ---------------------------------------------------------------------------
// Repasse multi-parcela
// ---------------------------------------------------------------------------

function RepasseMultiSheet({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { data, isFetching } = useTipologiaRepasseMulti({}, open);

  return (
    <Sheet open={open} onOpenChange={(v) => !v && onClose()}>
      <SheetContent className="w-full sm:max-w-3xl overflow-y-auto">
        <SheetHeader>
          <SheetTitle>Repasse multi-parcela</SheetTitle>
          <SheetDescription>
            Lançamentos OB_RECEBIDA cuja soma de 2+ parcelas em atraso bate (tolerância 0,02).
          </SheetDescription>
        </SheetHeader>
        <div className="mt-4">
          {isFetching ? (
            <p className="text-sm text-muted-foreground">Carregando...</p>
          ) : (data?.items.length ?? 0) === 0 ? (
            <p className="text-sm text-muted-foreground">Nenhum caso encontrado.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Data</TableHead>
                  <TableHead>Pessoa</TableHead>
                  <TableHead className="text-right">Valor</TableHead>
                  <TableHead>Combinações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data?.items.map((it) => (
                  <TableRow key={it.idLancamento}>
                    <TableCell className="font-mono text-xs">
                      {formatDate(it.dtMovimento.split("T")[0] ?? null)}
                    </TableCell>
                    <TableCell>
                      <div>{it.nomePessoa ?? "—"}</div>
                      <div className="font-mono text-xs text-muted-foreground">{it.cpfCnpj}</div>
                    </TableCell>
                    <TableCell className="text-right">{formatBRL(it.valor)}</TableCell>
                    <TableCell>
                      <ul className="space-y-1 text-xs">
                        {it.candidatos.map((c, idx) => (
                          <li key={idx}>
                            <span className="font-mono">{c.descricaoCombinacao}</span>{" "}
                            <Badge variant="outline">{formatBRL(c.somaCandidata)}</Badge>
                          </li>
                        ))}
                      </ul>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}

// ---------------------------------------------------------------------------
// CPF sem SIAIPessoal
// ---------------------------------------------------------------------------

function CpfSemSiaiSheet({
  open,
  onClose,
  onAbrirPessoa,
}: {
  open: boolean;
  onClose: () => void;
  onAbrirPessoa: (cpfCnpj: string) => void;
}) {
  const { data, isFetching } = useTipologiaCpfSemSiai(open);

  return (
    <Sheet open={open} onOpenChange={(v) => !v && onClose()}>
      <SheetContent className="w-full sm:max-w-3xl overflow-y-auto">
        <SheetHeader>
          <SheetTitle>CPF sem cadastro SIAIPessoal</SheetTitle>
          <SheetDescription>
            Cadastros de desconto-folha cujo CPF não casa em BdSIAIPessoal.dbo.Comum_Pessoa.
          </SheetDescription>
        </SheetHeader>
        <div className="mt-4">
          {isFetching ? (
            <p className="text-sm text-muted-foreground">Carregando...</p>
          ) : (data?.items.length ?? 0) === 0 ? (
            <p className="text-sm text-muted-foreground">Nenhum caso encontrado.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>CPF</TableHead>
                  <TableHead>Origem</TableHead>
                  <TableHead>Órgão notificado</TableHead>
                  <TableHead className="text-right">Parcelas</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data?.items.map((it) => (
                  <TableRow
                    key={it.idDescontoFolha}
                    className="cursor-pointer hover:bg-muted/40"
                    onClick={() => it.cpfCnpj && onAbrirPessoa(it.cpfCnpj)}
                  >
                    <TableCell>{it.nomePessoa ?? "—"}</TableCell>
                    <TableCell className="font-mono text-xs">{it.cpfCnpj ?? "—"}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{it.origem}</Badge>
                    </TableCell>
                    <TableCell className="text-xs">
                      {it.nomeOrgaoNotificado ?? (
                        <span className="text-muted-foreground italic">—</span>
                      )}
                    </TableCell>
                    <TableCell className="text-right">{it.qtdParcelas}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}

// ---------------------------------------------------------------------------
// Parcela duplicada
// ---------------------------------------------------------------------------

function ParcelaDuplicadaSheet({
  open,
  onClose,
  onAbrirPessoa,
}: {
  open: boolean;
  onClose: () => void;
  onAbrirPessoa: (cpfCnpj: string) => void;
}) {
  const { data, isFetching } = useTipologiaParcelaDuplicada(undefined, undefined, open);

  return (
    <Sheet open={open} onOpenChange={(v) => !v && onClose()}>
      <SheetContent className="w-full sm:max-w-3xl overflow-y-auto">
        <SheetHeader>
          <SheetTitle>Parcela duplicada</SheetTitle>
          <SheetDescription>
            Mesma parcela (nº/mês/ano/valor) cadastrada 2+ vezes para o mesmo desconto.
          </SheetDescription>
        </SheetHeader>
        <div className="mt-4">
          {isFetching ? (
            <p className="text-sm text-muted-foreground">Carregando...</p>
          ) : (data?.items.length ?? 0) === 0 ? (
            <p className="text-sm text-muted-foreground">Nenhum caso encontrado.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Pessoa</TableHead>
                  <TableHead>Mês/Ano</TableHead>
                  <TableHead>Nº</TableHead>
                  <TableHead className="text-right">Valor</TableHead>
                  <TableHead className="text-right">Qtd</TableHead>
                  <TableHead>IDs</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data?.items.map((it) => (
                  <TableRow
                    key={`${it.idDescontoFolha}-${it.numeroParcela}-${it.mesReferencia}-${it.anoReferencia}`}
                    className="cursor-pointer hover:bg-muted/40"
                    onClick={() => it.cpfCnpj && onAbrirPessoa(it.cpfCnpj)}
                  >
                    <TableCell>
                      <div>{it.nomePessoa ?? "—"}</div>
                      <div className="font-mono text-xs text-muted-foreground">{it.cpfCnpj}</div>
                    </TableCell>
                    <TableCell className="font-mono text-xs">
                      {String(it.mesReferencia).padStart(2, "0")}/{it.anoReferencia}
                    </TableCell>
                    <TableCell>{it.numeroParcela}</TableCell>
                    <TableCell className="text-right">{formatBRL(it.valorEsperado)}</TableCell>
                    <TableCell className="text-right">
                      <Badge variant="destructive">{it.qtd}×</Badge>
                    </TableCell>
                    <TableCell className="font-mono text-xs">{it.idsParcela.join(", ")}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}

// ---------------------------------------------------------------------------
// Atraso sistemático por órgão
// ---------------------------------------------------------------------------

function AtrasoSistemicoSheet({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [meses, setMeses] = useState(3);
  const [pct, setPct] = useState(0.2);
  const { data, isFetching } = useTipologiaAtrasoSistemico(undefined, meses, pct, open);

  return (
    <Sheet open={open} onOpenChange={(v) => !v && onClose()}>
      <SheetContent className="w-full sm:max-w-4xl overflow-y-auto">
        <SheetHeader>
          <SheetTitle>Atraso sistemático por órgão</SheetTitle>
          <SheetDescription>
            Órgãos com ≥N meses consecutivos onde a % de NAO_DESCONTADA passa do limite.
          </SheetDescription>
        </SheetHeader>
        <div className="mt-4 flex items-end gap-3">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs text-muted-foreground">Meses consecutivos</label>
            <input
              type="number"
              min={2}
              max={24}
              value={meses}
              onChange={(e) => setMeses(Number(e.target.value) || 3)}
              className="h-8 w-20 rounded border px-2 text-sm"
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-xs text-muted-foreground">% mínima</label>
            <input
              type="number"
              min={0}
              max={1}
              step={0.05}
              value={pct}
              onChange={(e) => setPct(Number(e.target.value) || 0.2)}
              className="h-8 w-20 rounded border px-2 text-sm"
            />
          </div>
        </div>
        <div className="mt-4">
          {isFetching ? (
            <p className="text-sm text-muted-foreground">Carregando...</p>
          ) : (data?.items.length ?? 0) === 0 ? (
            <p className="text-sm text-muted-foreground">Nenhum caso encontrado.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Órgão</TableHead>
                  <TableHead className="text-right">Meses consec.</TableHead>
                  <TableHead className="text-right">% médio</TableHead>
                  <TableHead>Detalhe</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data?.items.map((it) => (
                  <TableRow key={it.idOrgao ?? "null"}>
                    <TableCell>
                      {it.nomeOrgao ?? (
                        <span className="text-muted-foreground italic">Sem órgão notificado</span>
                      )}
                    </TableCell>
                    <TableCell className="text-right">{it.qtdMesesConsecutivos}</TableCell>
                    <TableCell className="text-right">{(it.pctMedio * 100).toFixed(1)}%</TableCell>
                    <TableCell>
                      <ul className="space-y-0.5 text-xs">
                        {it.detalheMeses.map((m, idx) => (
                          <li key={idx} className="font-mono">
                            {String(m.mes).padStart(2, "0")}/{m.ano}:{" "}
                            {(m.pctAtraso * 100).toFixed(0)}%{" "}
                            <span className="text-muted-foreground">
                              ({m.qtdEmAtraso}/{m.qtdParcelas})
                            </span>
                          </li>
                        ))}
                      </ul>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
