"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { parseAsInteger, parseAsString, useQueryState } from "nuqs";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
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
  useCreateUsuario,
  useResetSenha,
  useUpdateUsuario,
  useUsuarios,
} from "@/hooks/use-usuarios";
import { formatDate } from "@/lib/format";
import { usuarioCreateInputSchema, type Usuario, type UsuarioCreateInput } from "@/schemas/usuario";

const SIZE = 50;

export default function AdminUsuariosPage() {
  const { data: me } = useCurrentUser();
  const [q, setQ] = useQueryState("q", parseAsString.withDefault(""));
  const [papel, setPapel] = useQueryState("papel", parseAsString.withDefault(""));
  const [page, setPage] = useQueryState("page", parseAsInteger.withDefault(1));
  const [criarOpen, setCriarOpen] = useState(false);
  const [editando, setEditando] = useState<Usuario | null>(null);
  const [senhaGerada, setSenhaGerada] = useState<string | null>(null);

  const { data, isFetching } = useUsuarios({
    q: q || undefined,
    papel: papel === "user" || papel === "admin" ? papel : undefined,
    page,
    size: SIZE,
  });

  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / SIZE));

  if (me && me.papel !== "admin") {
    return <p className="text-sm text-destructive">Acesso restrito a administradores.</p>;
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="section-heading text-2xl">Usuários</h1>
        <Button onClick={() => setCriarOpen(true)}>Criar usuário</Button>
      </div>

      <div className="grid gap-3 md:grid-cols-3">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="f-q">Busca (nome, login ou e-mail)</Label>
          <Input
            id="f-q"
            value={q}
            onChange={(e) => {
              void setQ(e.target.value);
              void setPage(1);
            }}
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="f-papel">Papel</Label>
          <SelectNative
            id="f-papel"
            value={papel}
            onChange={(e) => {
              void setPapel(e.target.value);
              void setPage(1);
            }}
          >
            <option value="">Todos</option>
            <option value="user">user</option>
            <option value="admin">admin</option>
          </SelectNative>
        </div>
      </div>

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nome</TableHead>
              <TableHead>Login</TableHead>
              <TableHead>E-mail</TableHead>
              <TableHead>Papel</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Criado</TableHead>
              <TableHead className="text-right">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.items.length === 0 && !isFetching ? (
              <TableRow>
                <TableCell colSpan={7} className="py-8 text-center text-muted-foreground">
                  Nenhum usuário.
                </TableCell>
              </TableRow>
            ) : (
              data?.items.map((u) => (
                <TableRow key={u.idUsuario}>
                  <TableCell>{u.nomeCompleto}</TableCell>
                  <TableCell className="font-mono text-xs">{u.login}</TableCell>
                  <TableCell className="font-mono text-xs">{u.email}</TableCell>
                  <TableCell>
                    <Badge variant={u.papel === "admin" ? "default" : "outline"}>{u.papel}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={u.ativo ? "success" : "destructive"}>
                      {u.ativo ? "Ativo" : "Inativo"}
                    </Badge>
                  </TableCell>
                  <TableCell className="font-mono text-xs">
                    {formatDate(u.dataCriacao.split("T")[0])}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button size="sm" variant="outline" onClick={() => setEditando(u)}>
                        Editar
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {total.toLocaleString("pt-BR")} usuários · página {page} de {totalPages}
        </p>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1 || isFetching}
            onClick={() => setPage(Math.max(1, page - 1))}
          >
            Anterior
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= totalPages || isFetching}
            onClick={() => setPage(page + 1)}
          >
            Próxima
          </Button>
        </div>
      </div>

      <CriarDialog
        open={criarOpen}
        onOpenChange={setCriarOpen}
        onCreated={(senha) => {
          setSenhaGerada(senha);
          setCriarOpen(false);
        }}
      />

      <EditarDialog
        usuario={editando}
        onOpenChange={(open) => {
          if (!open) setEditando(null);
        }}
        onResetSenha={(senha) => {
          setSenhaGerada(senha);
          setEditando(null);
        }}
      />

      <SenhaGeradaDialog
        senha={senhaGerada}
        onOpenChange={(open) => {
          if (!open) setSenhaGerada(null);
        }}
      />
    </div>
  );
}

function CriarDialog({
  open,
  onOpenChange,
  onCreated,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  onCreated: (senha: string) => void;
}) {
  const create = useCreateUsuario();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<UsuarioCreateInput>({
    resolver: zodResolver(usuarioCreateInputSchema),
    defaultValues: { login: "", email: "", nomeCompleto: "", papel: "user" },
  });

  async function onSubmit(input: UsuarioCreateInput) {
    try {
      const res = await create.mutateAsync(input);
      reset();
      onCreated(res.senhaTemporaria);
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      toast.error(
        status === 409 ? "Login ou e-mail já cadastrado." : "Não foi possível criar o usuário.",
      );
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Criar usuário</DialogTitle>
          <DialogDescription>
            Uma senha temporária será gerada e exibida uma única vez.
          </DialogDescription>
        </DialogHeader>
        <form className="flex flex-col gap-4" onSubmit={handleSubmit(onSubmit)} noValidate>
          <div className="flex flex-col gap-2">
            <Label htmlFor="c-login">Login</Label>
            <Input
              id="c-login"
              type="text"
              autoCapitalize="none"
              spellCheck={false}
              {...register("login")}
            />
            {errors.login ? (
              <p className="text-xs text-destructive">{errors.login.message}</p>
            ) : null}
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="c-email">E-mail</Label>
            <Input id="c-email" type="email" {...register("email")} />
            {errors.email ? (
              <p className="text-xs text-destructive">{errors.email.message}</p>
            ) : null}
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="c-nome">Nome completo</Label>
            <Input id="c-nome" {...register("nomeCompleto")} />
            {errors.nomeCompleto ? (
              <p className="text-xs text-destructive">{errors.nomeCompleto.message}</p>
            ) : null}
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="c-papel">Papel</Label>
            <SelectNative id="c-papel" {...register("papel")}>
              <option value="user">user</option>
              <option value="admin">admin</option>
            </SelectNative>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={create.isPending}>
              {create.isPending ? "Criando..." : "Criar"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function EditarDialog({
  usuario,
  onOpenChange,
  onResetSenha,
}: {
  usuario: Usuario | null;
  onOpenChange: (o: boolean) => void;
  onResetSenha: (senha: string) => void;
}) {
  const update = useUpdateUsuario();
  const reset = useResetSenha();

  const [nome, setNome] = useState("");
  const [papel, setPapel] = useState<"user" | "admin">("user");
  const [ativo, setAtivo] = useState(true);

  const editingId = usuario?.idUsuario ?? null;
  const open = usuario !== null;

  useEffect(() => {
    if (usuario) {
      setNome(usuario.nomeCompleto);
      setPapel(usuario.papel);
      setAtivo(usuario.ativo);
    }
  }, [usuario]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Editar {usuario?.nomeCompleto}</DialogTitle>
          <DialogDescription>
            {usuario?.login ? (
              <>
                <span className="font-mono">{usuario.login}</span> · {usuario.email}
              </>
            ) : (
              usuario?.email
            )}
          </DialogDescription>
        </DialogHeader>
        <div className="flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <Label htmlFor="e-nome">Nome</Label>
            <Input id="e-nome" value={nome} onChange={(e) => setNome(e.target.value)} />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="e-papel">Papel</Label>
            <SelectNative
              id="e-papel"
              value={papel}
              onChange={(e) => setPapel(e.target.value as "user" | "admin")}
            >
              <option value="user">user</option>
              <option value="admin">admin</option>
            </SelectNative>
          </div>
          <div className="flex items-center gap-2">
            <input
              id="e-ativo"
              type="checkbox"
              checked={ativo}
              onChange={(e) => setAtivo(e.target.checked)}
            />
            <Label htmlFor="e-ativo">Ativo</Label>
          </div>
        </div>
        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={async () => {
              if (!editingId) return;
              if (!confirm("Resetar a senha deste usuário?")) return;
              try {
                const res = await reset.mutateAsync(editingId);
                onResetSenha(res.senhaTemporaria);
              } catch {
                toast.error("Falha ao resetar senha.");
              }
            }}
          >
            Resetar senha
          </Button>
          <Button
            type="button"
            disabled={update.isPending || !editingId}
            onClick={async () => {
              if (!editingId || !usuario) return;
              try {
                await update.mutateAsync({
                  id: editingId,
                  input: { nomeCompleto: nome, papel, ativo },
                });
                toast.success("Usuário atualizado.");
                onOpenChange(false);
              } catch {
                toast.error("Falha ao atualizar.");
              }
            }}
          >
            {update.isPending ? "Salvando..." : "Salvar"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function SenhaGeradaDialog({
  senha,
  onOpenChange,
}: {
  senha: string | null;
  onOpenChange: (o: boolean) => void;
}) {
  return (
    <Dialog open={senha !== null} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Senha temporária</DialogTitle>
          <DialogDescription>
            Copie agora — esta senha não será exibida novamente. Compartilhe com o usuário por canal
            seguro; ele deve trocar no primeiro acesso.
          </DialogDescription>
        </DialogHeader>
        <div className="flex items-center gap-2 rounded-md border bg-muted p-3 font-mono text-sm">
          <code className="flex-1 break-all">{senha ?? ""}</code>
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={async () => {
              if (senha) {
                await navigator.clipboard.writeText(senha);
                toast.success("Senha copiada.");
              }
            }}
          >
            Copiar
          </Button>
        </div>
        <DialogFooter>
          <Button type="button" onClick={() => onOpenChange(false)}>
            Fechar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
