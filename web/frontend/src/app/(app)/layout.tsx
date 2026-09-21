"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

import { TopBar } from "@/components/app/top-bar";
import { useCurrentUser } from "@/hooks/use-current-user";
import { hasSession } from "@/lib/auth";
import { moduloDaRota, podeVer, primeiraRotaVisivel } from "@/lib/permissoes";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { data: user, isLoading, isError } = useCurrentUser();

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (!hasSession()) {
      router.replace("/login");
    }
  }, [router]);

  useEffect(() => {
    if (isError) {
      router.replace("/login");
    }
  }, [isError, router]);

  // Senha provisória: obriga a troca antes de usar o app — só libera /conta.
  const mustChangePassword = !!user?.deveTrocarSenha && pathname !== "/conta";
  useEffect(() => {
    if (mustChangePassword) {
      router.replace("/conta");
    }
  }, [mustChangePassword, router]);

  // Módulo com visualização removida → primeira rota visível.
  const modulo = pathname ? moduloDaRota(pathname) : null;
  const semAcesso = !!user && !mustChangePassword && !!modulo && !podeVer(user, modulo);
  useEffect(() => {
    if (semAcesso && user) {
      router.replace(primeiraRotaVisivel(user));
    }
  }, [semAcesso, user, router]);

  if (isLoading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-sm text-muted-foreground">Carregando...</p>
      </div>
    );
  }

  if (mustChangePassword || semAcesso) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-sm text-muted-foreground">Redirecionando...</p>
      </div>
    );
  }

  return (
    <>
      <TopBar user={user} />
      <main className="container mx-auto px-6 py-8">{children}</main>
    </>
  );
}
