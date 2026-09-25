"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { ThemeToggle } from "@/components/app/theme-toggle";
import { Button } from "@/components/ui/button";
import { logout } from "@/lib/auth-api";
import { type Modulo, podeEditar, podeVer } from "@/lib/permissoes";
import { cn } from "@/lib/utils";
import type { UserOut } from "@/schemas/auth";

type NavItem = { href: string; label: string; modulo: Modulo; editar?: boolean };

const MODULES = [
  { key: "ccd", label: "CCD" },
  { key: "cgad", label: "CGAD" },
  { key: "frap", label: "FRAP" },
  { key: "wiki", label: "WIKI" },
] as const;

const SUBNAV: Record<string, NavItem[]> = {
  ccd: [
    { href: "/ccd", label: "Início", modulo: "ccd.inicio" },
    { href: "/ccd/desconto-folha", label: "Desconto em Folha", modulo: "ccd.desconto-folha" },
    { href: "/ccd/beneficios", label: "Benefícios", modulo: "ccd.beneficios" },
    { href: "/ccd/automacao", label: "Automação", modulo: "ccd.automacao" },
    { href: "/ccd/alertas", label: "Alertas", modulo: "ccd.alertas" },
  ],
  cgad: [
    { href: "/cgad/reviews", label: "Revisões", modulo: "cgad.reviews" },
    { href: "/cgad/etl", label: "Extrações", modulo: "cgad.etl", editar: true },
    { href: "/cgad/dashboards", label: "Painéis", modulo: "cgad.dashboards" },
    { href: "/cgad/dataset", label: "Conjunto de Dados", modulo: "cgad.dataset" },
    {
      href: "/cgad/multas-nao-cominadas",
      label: "Multas não cominadas",
      modulo: "cgad.multas-nao-cominadas",
    },
  ],
  frap: [
    { href: "/frap/extratos", label: "Extratos", modulo: "frap.extratos" },
    { href: "/frap/jobs", label: "Extrações", modulo: "frap.jobs" },
  ],
  wiki: [
    { href: "/wiki", label: "Início", modulo: "wiki" },
    { href: "/wiki/procedimentos", label: "POPs", modulo: "wiki" },
  ],
};

function activeModule(pathname: string | null): string {
  if (pathname?.startsWith("/cgad")) return "cgad";
  if (pathname?.startsWith("/frap")) return "frap";
  if (pathname?.startsWith("/wiki")) return "wiki";
  return "ccd";
}

export function TopBar({ user }: { user: UserOut }) {
  const pathname = usePathname();
  const router = useRouter();
  const isAdmin = user.papel === "admin";
  const current = activeModule(pathname);
  const visiveis = (key: string) =>
    (SUBNAV[key] ?? []).filter((l) =>
      l.editar ? podeEditar(user, l.modulo) : podeVer(user, l.modulo),
    );
  const subnav = visiveis(current);
  // link ativo = correspondência de prefixo mais longa (evita o root "/ccd"
  // ficar aceso junto com "/ccd/desconto-folha" etc.)
  const activeHref = [...subnav]
    .sort((a, b) => b.href.length - a.href.length)
    .find((l) => pathname === l.href || pathname?.startsWith(l.href + "/"))?.href;

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
              const href = visiveis(m.key)[0]?.href;
              if (!href) return null;
              const active = current === m.key;
              return (
                <Link
                  key={m.key}
                  href={href}
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
          <ThemeToggle />
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
          const active = link.href === activeHref;
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
