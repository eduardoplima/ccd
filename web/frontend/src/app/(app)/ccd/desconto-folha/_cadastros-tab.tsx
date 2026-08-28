"use client";

import { parseAsInteger, parseAsString, useQueryState } from "nuqs";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
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
import {
  useAtualizarCadastro,
  useCadastro,
  useCadastros,
  useCriarCadastro,
  useCriarParcela,
  useDeletarCadastro,
  useDeletarParcela,
  useOrgaosDisponiveis,
} from "@/hooks/use-desconto-folha";
import { formatBRL, formatDate } from "@/lib/format";
import type { ParcelaCadastroItem } from "@/schemas/desconto-folha";

import { Paginacao } from "./_paginacao";

const SIZE = 50;

export function CadastrosTab() {
  const { data: me } = useCurrentUser();
  const isAdmin = me?.papel === "admin";

  const [q, setQ] = useQueryState("cq", parseAsString.withDefault(""));
  const [page, setPage] = useQueryState("cpage", parseAsInteger.withDefault(1));
  const [criarOpen, setCriarOpen] = useState(false);
  const [editandoId, setEditandoId] = useState<number | null>(null);

  const { data, isFetching } = useCadastros(q, page, SIZE);
  const deletar = useDeletarCadastro();

  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / SIZE));

  async function handleDelete(id: number, nome: string | null | undefined) {
    if (!confirm(`Excluir o cadastro de ${nome ?? "sem nome"} e todas as parcelas?`)) return;
    try {
      await deletar.mutateAsync(id);
      toast.success("Cadastro excluído.");
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      toast.error(
        status === 409
          ? "Cadastro tem parcelas conciliadas — desfaça os matches antes."
          : "Falha ao excluir.",
      );
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-end gap-3">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="c-q">Busca (nome ou CPF)</Label>
          <Input
            id="c-q"
            value={q}
            onChange={(e) => {
              void setQ(e.target.value);
              void setPage(1);
            }}
            className="w-72"
          />
        </div>
        {isAdmin ? (
          <Button className="ml-auto" onClick={() => setCriarOpen(true)}>
            Novo cadastro
          </Button>
        ) : null}
      </div>

      <p className="text-xs text-muted-foreground">
        {total.toLocaleString("pt-BR")} cadastros manuais · página {page} de {totalPages}
      </p>

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Responsável</TableHead>
              <TableHead>CPF/CNPJ</TableHead>
              <TableHead>Órgão notificado</TableHead>
              <TableHead className="text-right">Parcelas</TableHead>
              <TableHead className="text-right">Valor total</TableHead>
              <TableHead>Incluído em</TableHead>
              <TableHead className="text-right">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.items.length === 0 && !isFetching ? (
              <TableRow>
                <TableCell colSpan={7} className="py-8 text-center text-muted-foreground">
                  Nenhum cadastro manual.
                </TableCell>
              </TableRow>
            ) : (
              data?.items.map((c) => (
                <TableRow key={c.idDescontoFolha} className="hover:bg-muted/40">
                  <TableCell>{c.nomePessoa ?? "—"}</TableCell>
                  <TableCell className="font-mono text-xs">{c.cpfCnpj ?? "—"}</TableCell>
                  <TableCell className="max-w-52 truncate text-xs">
                    {c.nomeOrgaoNotificado ?? "—"}
                  </TableCell>
                  <TableCell className="text-right">{c.qtdParcelas}</TableCell>
                  <TableCell className="text-right">{formatBRL(c.valorTotal)}</TableCell>
                  <TableCell className="font-mono text-xs">
                    {formatDate(c.dataInclusao?.split("T")[0])}
                  </TableCell>
                  <TableCell className="text-right">
                    {isAdmin ? (
                      <div className="flex justify-end gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setEditandoId(c.idDescontoFolha)}
                        >
                          Editar
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => void handleDelete(c.idDescontoFolha, c.nomePessoa)}
                        >
                          Excluir
                        </Button>
                      </div>
                    ) : null}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <Paginacao
        page={page}
        totalPages={totalPages}
        setPage={(p) => void setPage(p)}
        disabled={isFetching}
      />

      <CriarCadastroDialog open={criarOpen} onOpenChange={setCriarOpen} />
      <EditarCadastroDialog
        idDescontoFolha={editandoId}
        onOpenChange={(open) => {
          if (!open) setEditandoId(null);
        }}
      />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Seletor de órgão (busca em vw_Gen_Orgao via /orgaos-disponiveis)
// ---------------------------------------------------------------------------

function OrgaoPicker({
  value,
  onChange,
}: {
  value: { idOrgao: number; nomeOrgao: string } | null;
  onChange: (v: { idOrgao: number; nomeOrgao: string } | null) => void;
}) {
  const [busca, setBusca] = useState("");
  const { data: orgaos } = useOrgaosDisponiveis(busca);

  return (
    <div className="flex flex-col gap-1.5">
      <Label>Órgão notificado</Label>
      {value ? (
        <div className="flex items-center gap-2 text-sm">
          <span className="flex-1 truncate">{value.nomeOrgao}</span>
          <Button size="sm" variant="outline" onClick={() => onChange(null)}>
            Trocar
          </Button>
        </div>
      ) : (
        <>
          <Input
            placeholder="Digite ao menos 2 letras para buscar..."
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
          />
          {orgaos && orgaos.length > 0 ? (
            <SelectNative
              value=""
              onChange={(e) => {
                const id = Number(e.target.value);
                const org = orgaos.find((o) => o.idOrgao === id);
                if (org) onChange(org);
              }}
            >
              <option value="">Selecione o órgão…</option>
              {orgaos.map((o) => (
                <option key={o.idOrgao} value={o.idOrgao}>
                  {o.nomeOrgao}
                </option>
              ))}
            </SelectNative>
          ) : null}
        </>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Criar cadastro (com lista dinâmica de parcelas)
// ---------------------------------------------------------------------------

type ParcelaForm = { mes: string; ano: string; valor: string; vencimento: string };

const PARCELA_VAZIA: ParcelaForm = { mes: "", ano: "", valor: "", vencimento: "" };

function parcelaValida(p: ParcelaForm): boolean {
  return (
    Number(p.mes) >= 1 &&
    Number(p.mes) <= 12 &&
    Number(p.ano) >= 2000 &&
    Number(p.valor.replace(",", ".")) > 0
  );
}

function CriarCadastroDialog({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
}) {
  const criar = useCriarCadastro();
  const [nome, setNome] = useState("");
  const [cpf, setCpf] = useState("");
  const [orgao, setOrgao] = useState<{ idOrgao: number; nomeOrgao: string } | null>(null);
  const [parcelas, setParcelas] = useState<ParcelaForm[]>([{ ...PARCELA_VAZIA }]);

  useEffect(() => {
    if (open) {
      setNome("");
      setCpf("");
      setOrgao(null);
      setParcelas([{ ...PARCELA_VAZIA }]);
    }
  }, [open]);

  function setParcela(idx: number, patch: Partial<ParcelaForm>) {
    setParcelas((prev) => prev.map((p, i) => (i === idx ? { ...p, ...patch } : p)));
  }

  async function onSubmit() {
    const cpfDigits = cpf.replace(/\D/g, "");
    const validas = parcelas.filter(parcelaValida);
    if (!nome.trim() || !(cpfDigits.length === 11 || cpfDigits.length === 14) || !orgao) {
      toast.error("Preencha nome, CPF/CNPJ (11 ou 14 dígitos) e órgão.");
      return;
    }
    if (validas.length === 0) {
      toast.error("Informe ao menos uma parcela válida (mês, ano e valor).");
      return;
    }
    try {
      await criar.mutateAsync({
        cpfCnpj: cpfDigits,
        nomePessoa: nome.trim(),
        idOrgaoNotificado: orgao.idOrgao,
        nomeOrgaoNotificado: orgao.nomeOrgao,
        parcelas: validas.map((p, idx) => ({
          numeroParcela: idx + 1,
          mesReferencia: Number(p.mes),
          anoReferencia: Number(p.ano),
          valorEsperado: Number(p.valor.replace(",", ".")),
          dataVencimento: p.vencimento || null,
        })),
      });
      toast.success("Cadastro criado.");
      onOpenChange(false);
    } catch {
      toast.error("Falha ao criar o cadastro.");
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[85vh] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Novo cadastro de desconto</DialogTitle>
          <DialogDescription>
            Plano manual de parcelas (equivale à aba de valores da planilha).
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-4">
          <div className="grid gap-3 md:grid-cols-2">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="nc-nome">Responsável</Label>
              <Input id="nc-nome" value={nome} onChange={(e) => setNome(e.target.value)} />
            </div>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="nc-cpf">CPF/CNPJ</Label>
              <Input id="nc-cpf" value={cpf} onChange={(e) => setCpf(e.target.value)} />
            </div>
          </div>
          <OrgaoPicker value={orgao} onChange={setOrgao} />

          <div className="flex flex-col gap-2">
            <Label>Parcelas</Label>
            {parcelas.map((p, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <Input
                  placeholder="Mês"
                  className="w-16"
                  value={p.mes}
                  onChange={(e) => setParcela(idx, { mes: e.target.value })}
                />
                <Input
                  placeholder="Ano"
                  className="w-20"
                  value={p.ano}
                  onChange={(e) => setParcela(idx, { ano: e.target.value })}
                />
                <Input
                  placeholder="Valor (R$)"
                  className="w-28"
                  inputMode="decimal"
                  value={p.valor}
                  onChange={(e) => setParcela(idx, { valor: e.target.value })}
                />
                <Input
                  type="date"
                  className="w-40"
                  value={p.vencimento}
                  onChange={(e) => setParcela(idx, { vencimento: e.target.value })}
                />
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setParcelas((prev) => prev.filter((_, i) => i !== idx))}
                  disabled={parcelas.length === 1}
                >
                  Remover
                </Button>
              </div>
            ))}
            <Button
              size="sm"
              variant="outline"
              className="self-start"
              onClick={() => setParcelas((prev) => [...prev, { ...PARCELA_VAZIA }])}
            >
              Adicionar parcela
            </Button>
          </div>
        </div>

        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button type="button" disabled={criar.isPending} onClick={() => void onSubmit()}>
            {criar.isPending ? "Criando..." : "Criar"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// ---------------------------------------------------------------------------
// Editar cadastro (dados do pai + CRUD de parcelas individuais)
// ---------------------------------------------------------------------------

function EditarCadastroDialog({
  idDescontoFolha,
  onOpenChange,
}: {
  idDescontoFolha: number | null;
  onOpenChange: (o: boolean) => void;
}) {
  const { data: detail } = useCadastro(idDescontoFolha);
  const atualizar = useAtualizarCadastro();
  const criarParcela = useCriarParcela();
  const deletarParcela = useDeletarParcela();

  const [nome, setNome] = useState("");
  const [orgao, setOrgao] = useState<{ idOrgao: number; nomeOrgao: string } | null>(null);
  const [nova, setNova] = useState<ParcelaForm>({ ...PARCELA_VAZIA });

  useEffect(() => {
    if (detail) {
      setNome(detail.nomePessoa ?? "");
      setOrgao(
        detail.idOrgaoNotificado != null && detail.nomeOrgaoNotificado
          ? { idOrgao: detail.idOrgaoNotificado, nomeOrgao: detail.nomeOrgaoNotificado }
          : null,
      );
      setNova({ ...PARCELA_VAZIA });
    }
  }, [detail]);

  async function salvarPai() {
    if (!idDescontoFolha) return;
    try {
      await atualizar.mutateAsync({
        id: idDescontoFolha,
        input: {
          nomePessoa: nome.trim() || undefined,
          idOrgaoNotificado: orgao?.idOrgao,
          nomeOrgaoNotificado: orgao?.nomeOrgao,
        },
      });
      toast.success("Cadastro atualizado.");
      onOpenChange(false);
    } catch {
      toast.error("Falha ao atualizar.");
    }
  }

  async function adicionarParcela() {
    if (!idDescontoFolha || !detail) return;
    if (!parcelaValida(nova)) {
      toast.error("Parcela inválida (mês, ano e valor são obrigatórios).");
      return;
    }
    const proximo = Math.max(0, ...detail.parcelas.map((p) => p.numeroParcela ?? 0)) + 1;
    try {
      await criarParcela.mutateAsync({
        id: idDescontoFolha,
        input: {
          numeroParcela: proximo,
          mesReferencia: Number(nova.mes),
          anoReferencia: Number(nova.ano),
          valorEsperado: Number(nova.valor.replace(",", ".")),
          dataVencimento: nova.vencimento || null,
        },
      });
      toast.success("Parcela adicionada.");
      setNova({ ...PARCELA_VAZIA });
    } catch {
      toast.error("Falha ao adicionar a parcela.");
    }
  }

  async function excluirParcela(p: ParcelaCadastroItem) {
    if (!idDescontoFolha) return;
    if (!confirm(`Excluir a parcela ${p.mesReferencia}/${p.anoReferencia}?`)) return;
    try {
      await deletarParcela.mutateAsync({ id: idDescontoFolha, idParcela: p.idFrapParcela });
      toast.success("Parcela excluída.");
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      toast.error(
        status === 409 ? "Parcela conciliada — desfaça o match antes." : "Falha ao excluir.",
      );
    }
  }

  return (
    <Dialog open={idDescontoFolha !== null} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[85vh] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Editar cadastro</DialogTitle>
          <DialogDescription>
            {detail?.cpfCnpj ? <span className="font-mono">{detail.cpfCnpj}</span> : "…"} — o CPF
            não é editável (exclua e recrie se estiver errado).
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="ec-nome">Responsável</Label>
            <Input id="ec-nome" value={nome} onChange={(e) => setNome(e.target.value)} />
          </div>
          <OrgaoPicker value={orgao} onChange={setOrgao} />

          <div className="flex flex-col gap-2">
            <Label>Parcelas</Label>
            <div className="rounded-lg border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nº</TableHead>
                    <TableHead>Competência</TableHead>
                    <TableHead className="text-right">Valor</TableHead>
                    <TableHead>Vencimento</TableHead>
                    <TableHead />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {detail?.parcelas.map((p) => (
                    <TableRow key={p.idFrapParcela}>
                      <TableCell>{p.numeroParcela ?? "—"}</TableCell>
                      <TableCell className="font-mono text-xs">
                        {String(p.mesReferencia ?? "?").padStart(2, "0")}/{p.anoReferencia ?? "?"}
                      </TableCell>
                      <TableCell className="text-right">{formatBRL(p.valorEsperado)}</TableCell>
                      <TableCell className="font-mono text-xs">
                        {formatDate(p.dataVencimento)}
                      </TableCell>
                      <TableCell className="text-right">
                        {p.temMatch ? (
                          <Badge variant="success">Conciliada</Badge>
                        ) : (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => void excluirParcela(p)}
                          >
                            Excluir
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
            <div className="flex items-center gap-2">
              <Input
                placeholder="Mês"
                className="w-16"
                value={nova.mes}
                onChange={(e) => setNova({ ...nova, mes: e.target.value })}
              />
              <Input
                placeholder="Ano"
                className="w-20"
                value={nova.ano}
                onChange={(e) => setNova({ ...nova, ano: e.target.value })}
              />
              <Input
                placeholder="Valor (R$)"
                className="w-28"
                inputMode="decimal"
                value={nova.valor}
                onChange={(e) => setNova({ ...nova, valor: e.target.value })}
              />
              <Input
                type="date"
                className="w-40"
                value={nova.vencimento}
                onChange={(e) => setNova({ ...nova, vencimento: e.target.value })}
              />
              <Button
                size="sm"
                variant="outline"
                disabled={criarParcela.isPending}
                onClick={() => void adicionarParcela()}
              >
                Adicionar
              </Button>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
            Fechar
          </Button>
          <Button type="button" disabled={atualizar.isPending} onClick={() => void salvarPai()}>
            {atualizar.isPending ? "Salvando..." : "Salvar dados"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
