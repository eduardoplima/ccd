"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { useCurrentUser } from "@/hooks/use-current-user";
import { podeEditar } from "@/lib/permissoes";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { data: user, isLoading } = useCurrentUser();

  useEffect(() => {
    if (!isLoading && user && !podeEditar(user, "cgad.dataset")) {
      router.replace("/cgad/reviews");
    }
  }, [isLoading, user, router]);

  if (isLoading || !user) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center text-sm text-muted-foreground">
        Carregando...
      </div>
    );
  }
  if (!podeEditar(user, "cgad.dataset")) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center text-sm text-muted-foreground">
        Acesso restrito a administradores.
      </div>
    );
  }
  return <>{children}</>;
}
