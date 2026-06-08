"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { TopBar } from "@/components/app/top-bar";
import { useCurrentUser } from "@/hooks/use-current-user";
import { hasSession } from "@/lib/auth";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
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

  if (isLoading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-sm text-muted-foreground">Carregando...</p>
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
