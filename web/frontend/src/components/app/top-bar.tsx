"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { logout } from "@/lib/auth-api";
import { cn } from "@/lib/utils";
import type { UserOut } from "@/schemas/auth";

type NavItem = { href: string; label: string; admin?: boolean };

const MODULES = [
  { key: "ccd", label: "CCD", href: "/ccd" },
  { key: "cgad", label: "CGAD", href: "/cgad/reviews" },
  { key: "frap", label: "FRAP", href: "/frap/extratos" },
] as const;

const SUBNAV: Record<string, NavItem[]> = {
  ccd: [{ href: "/ccd", label: "Início" }],
  cgad: [
    { href: "/cgad/reviews", label: "Revisões" },
    { href: "/cgad/etl", label: "Extrações", admin: true },
    { href: "/cgad/dashboards", label: "Painéis" },
  ],
  frap: [
    { href: "/frap/extratos", label: "Extratos" },
    { href: "/frap/conciliacoes", label: "Conciliações" },
    { href: "/frap/desconto-folha", label: "Desconto em Folha" },
    { href: "/frap/jobs", label: "Extrações", admin: true },
  ],
};

function activeModule(pathname: string | null): string {
  if (pathname?.startsWith("/cgad")) return "cgad";
  if (pathname?.startsWith("/frap")) return "frap";
  return "ccd";
}

export function TopBar({ user }: { user: UserOut }) {
  const pathname = usePathname();
  const router = useRouter();
  const isAdmin = user.papel === "admin";
  const current = activeModule(pathname);
  const subnav = (SUBNAV[current] ?? []).filter((l) => !l.admin || isAdmin);

  async function handleLogout() {
    await logout();
    router.replace("/login");
  }

  return (
    <header>
      {/* faixa de módulos */}
      <div className="flex h-16 items-center justify-between bg-[var(--brand-dark)] px-6 text-white">
        <div className="flex items-center gap-8">
          <Link href="/ccd" className="text-lg font-bold tracking-tight whitespace-nowrap">
            Coordenadoria de Controle de Decisões
          </Link>
          <nav className="flex items-center gap-2 text-sm font-medium">
            {MODULES.map((m) => {
              const active = current === m.key;
              return (
                <Link
                  key={m.key}
                  href={m.href}
                  className={cn(
                    "rounded-md px-3 py-1.5 transition-colors",
                    active
                      ? "bg-white/15 text-white"
                      : "text-yellow-300 hover:bg-white/10 hover:text-white",
                  )}
                >
                  {m.label}
                </Link>
              );
            })}
          </nav>
        </div>
        <div className="flex items-center gap-4">
          {isAdmin && (
            <Link
              href="/admin/usuarios"
              className={cn(
                "text-sm",
                pathname?.startsWith("/admin")
                  ? "text-white underline underline-offset-4"
                  : "text-yellow-300 hover:text-white",
              )}
            >
              Usuários
            </Link>
          )}
          <Link
            href="/conta"
            className="text-sm text-yellow-300 hover:text-white"
            title="Conta / trocar senha"
          >
            {user.nomeCompleto}
          </Link>
          <Button
            variant="outline"
            size="sm"
            className="border-white/40 bg-transparent text-white hover:bg-white/10"
            onClick={handleLogout}
          >
            Sair
          </Button>
        </div>
      </div>

      {/* sub-navegação do módulo ativo */}
      <div className="flex h-11 items-center gap-6 bg-[var(--brand-dark)]/95 px-6 text-sm text-white/90">
        {subnav.map((link) => {
          const active = pathname === link.href || pathname?.startsWith(link.href + "/");
          return (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                "transition-colors",
                active
                  ? "text-white underline decoration-2 underline-offset-[6px]"
                  : "text-yellow-300 hover:text-white",
              )}
            >
              {link.label}
            </Link>
          );
        })}
      </div>

      <div className="h-1 bg-[var(--brand-accent)]" />
    </header>
  );
}
