"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { login } from "@/lib/auth-api";
import { loginSchema, type LoginInput } from "@/schemas/auth";

export default function LoginPage() {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginInput>({ resolver: zodResolver(loginSchema) });

  async function onSubmit(values: LoginInput) {
    setPending(true);
    try {
      await login(values);
      router.replace("/frap/extratos");
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      const msg =
        status === 401
          ? "Login ou senha incorretos."
          : status === 403
            ? "Usuário inativo. Procure o administrador."
            : "Não foi possível entrar. Tente novamente.";
      toast.error(msg);
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted px-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Coordenadoria de Controle de Decisões</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="flex flex-col gap-4" onSubmit={handleSubmit(onSubmit)} noValidate>
            <div className="flex flex-col gap-2">
              <Label htmlFor="login">Login</Label>
              <Input
                id="login"
                type="text"
                autoComplete="username"
                autoCapitalize="none"
                spellCheck={false}
                {...register("login")}
              />
              {errors.login ? (
                <p className="text-xs text-destructive">{errors.login.message}</p>
              ) : null}
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="senha">Senha</Label>
              <Input
                id="senha"
                type="password"
                autoComplete="current-password"
                {...register("senha")}
              />
              {errors.senha ? (
                <p className="text-xs text-destructive">{errors.senha.message}</p>
              ) : null}
            </div>
            <Button type="submit" className="w-full" disabled={pending}>
              {pending ? "Entrando..." : "Entrar"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
