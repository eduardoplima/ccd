"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCurrentUser } from "@/hooks/use-current-user";
import { useTrocarSenha } from "@/hooks/use-usuarios";
import { trocarSenhaInputSchema, type TrocarSenhaInput } from "@/schemas/usuario";

export default function ContaPage() {
  const { data: user } = useCurrentUser();
  const trocar = useTrocarSenha();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<TrocarSenhaInput>({ resolver: zodResolver(trocarSenhaInputSchema) });

  async function onSubmit(input: TrocarSenhaInput) {
    try {
      await trocar.mutateAsync({ senhaAtual: input.senhaAtual, senhaNova: input.senhaNova });
      toast.success("Senha trocada. Faça login novamente nos próximos acessos.");
      reset();
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      toast.error(status === 401 ? "Senha atual incorreta." : "Falha ao trocar senha.");
    }
  }

  return (
    <div className="flex max-w-xl flex-col gap-6">
      <h1 className="section-heading text-2xl">Conta</h1>
      {user ? (
        <Card>
          <CardHeader>
            <CardTitle>{user.nomeCompleto}</CardTitle>
            <CardDescription>
              <span className="font-mono">{user.login}</span> · {user.email} · papel{" "}
              <span className="font-mono">{user.papel}</span>
            </CardDescription>
          </CardHeader>
        </Card>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Trocar senha</CardTitle>
          <CardDescription>Após trocar, sessões antigas serão invalidadas.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="flex flex-col gap-4" onSubmit={handleSubmit(onSubmit)} noValidate>
            <div className="flex flex-col gap-2">
              <Label htmlFor="s-atual">Senha atual</Label>
              <Input
                id="s-atual"
                type="password"
                autoComplete="current-password"
                {...register("senhaAtual")}
              />
              {errors.senhaAtual ? (
                <p className="text-xs text-destructive">{errors.senhaAtual.message}</p>
              ) : null}
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="s-nova">Senha nova</Label>
              <Input
                id="s-nova"
                type="password"
                autoComplete="new-password"
                {...register("senhaNova")}
              />
              {errors.senhaNova ? (
                <p className="text-xs text-destructive">{errors.senhaNova.message}</p>
              ) : null}
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="s-conf">Confirmação</Label>
              <Input
                id="s-conf"
                type="password"
                autoComplete="new-password"
                {...register("confirmacao")}
              />
              {errors.confirmacao ? (
                <p className="text-xs text-destructive">{errors.confirmacao.message}</p>
              ) : null}
            </div>
            <Button type="submit" disabled={trocar.isPending}>
              {trocar.isPending ? "Trocando..." : "Trocar senha"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
