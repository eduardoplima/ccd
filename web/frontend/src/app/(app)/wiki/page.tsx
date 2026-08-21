"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { WikiMarkdown } from "@/components/wiki/markdown";
import { useWikiPage, useWikiPages, useWikiSearch } from "@/hooks/use-wiki";

export default function WikiHomePage() {
  const router = useRouter();
  const [q, setQ] = useState("");
  const [novoSlug, setNovoSlug] = useState("");
  const { data: index, isPending } = useWikiPage("index");
  const { data: pages } = useWikiPages();
  const busca = useWikiSearch(q);
  const buscando = q.trim().length >= 2;

  function criarPagina() {
    const slug = novoSlug
      .trim()
      .toLowerCase()
      .replace(/\.md$/, "")
      .replace(/\s+/g, "-")
      .replace(/[^\w/-]/g, "");
    if (slug) router.push(`/wiki/${slug}`);
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-6">
      <div className="flex items-center gap-3">
        <Input
          placeholder="Buscar na wiki…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="max-w-sm"
        />
        <div className="ml-auto flex items-center gap-2">
          <Input
            placeholder="nova-pagina ou procedimentos/nova"
            value={novoSlug}
            onChange={(e) => setNovoSlug(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && criarPagina()}
            className="w-64"
          />
          <Button variant="outline" size="sm" onClick={criarPagina} disabled={!novoSlug.trim()}>
            Nova página
          </Button>
        </div>
      </div>

      {buscando ? (
        <div className="space-y-3">
          {busca.isFetching && <p className="text-sm text-muted-foreground">Buscando…</p>}
          {busca.data?.length === 0 && (
            <p className="text-sm text-muted-foreground">Nenhum resultado para “{q}”.</p>
          )}
          {busca.data?.map((hit) => (
            <Link
              key={hit.slug}
              href={hit.slug === "index" ? "/wiki" : `/wiki/${hit.slug}`}
              className="block rounded-md border p-3 hover:bg-muted/50"
            >
              <span className="font-medium">{hit.title}</span>
              <p className="mt-1 text-sm text-muted-foreground">…{hit.snippet}…</p>
            </Link>
          ))}
        </div>
      ) : (
        <>
          {isPending && <p className="text-sm text-muted-foreground">Carregando…</p>}
          {index && <WikiMarkdown content={index.content} baseSlug="index" />}

          <div className="border-t pt-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-muted-foreground">Todas as páginas</h2>
              <Link href="/wiki/index" className={buttonVariants({ variant: "ghost", size: "sm" })}>
                Editar página inicial
              </Link>
            </div>
            <ul className="mt-2 grid gap-1 text-sm sm:grid-cols-2">
              {pages
                ?.filter((p) => p.slug !== "index")
                .map((p) => (
                  <li key={p.slug}>
                    <Link href={`/wiki/${p.slug}`} className="text-primary hover:underline">
                      {p.title}
                    </Link>{" "}
                    {p.editado && <Badge variant="outline">editado na UI</Badge>}
                  </li>
                ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );
}
