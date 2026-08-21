"use client";

import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { useWikiPages } from "@/hooks/use-wiki";

export default function WikiPopsPage() {
  const { data: pages, isPending } = useWikiPages();
  const pops = (pages?.filter((p) => p.slug.startsWith("procedimentos/")) ?? []).sort((a, b) =>
    a.title.localeCompare(b.title),
  );

  return (
    <div className="mx-auto max-w-4xl space-y-4 p-6">
      <h1 className="text-xl font-semibold">Procedimentos Operacionais Padrão (POPs)</h1>
      <p className="text-sm text-muted-foreground">
        Estruturados conforme a ISO 10013:2021. Documentos de apoio:{" "}
        <Link href="/wiki/marcadores" className="text-primary hover:underline">
          Marcadores da CCD
        </Link>{" "}
        e{" "}
        <Link href="/wiki/rotinas-mensais" className="text-primary hover:underline">
          Rotinas mensais
        </Link>
        .
      </p>
      {isPending && <p className="text-sm text-muted-foreground">Carregando…</p>}
      <ul className="divide-y rounded-md border">
        {pops.map((p) => (
          <li key={p.slug}>
            <Link
              href={`/wiki/${p.slug}`}
              className="flex items-center gap-2 p-3 hover:bg-muted/50"
            >
              <span>{p.title}</span>
              {p.editado && <Badge variant="outline">editado na UI</Badge>}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
