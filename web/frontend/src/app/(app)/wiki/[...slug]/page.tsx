"use client";

import { isAxiosError } from "axios";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { WikiMarkdown } from "@/components/wiki/markdown";
import { useDeleteWikiOverride, useSaveWikiPage, useWikiPage } from "@/hooks/use-wiki";

export default function WikiPageView() {
  const params = useParams<{ slug: string[] }>();
  const slug = (params.slug ?? []).join("/");
  const { data: page, isPending, error } = useWikiPage(slug);
  const salvar = useSaveWikiPage();
  const reverter = useDeleteWikiOverride();
  const [draft, setDraft] = useState<string | null>(null);
  const [preview, setPreview] = useState(false);

  const notFound = isAxiosError(error) && error.response?.status === 404;
  const editing = draft !== null;

  function onSalvar() {
    if (draft === null) return;
    salvar.mutate(
      { slug, content: draft },
      {
        onSuccess: () => {
          setDraft(null);
          setPreview(false);
          toast.success("Página salva.");
        },
        onError: () => toast.error("Erro ao salvar a página."),
      },
    );
  }

  if (isPending) {
    return <p className="p-6 text-sm text-muted-foreground">Carregando…</p>;
  }

  if (notFound && !editing) {
    return (
      <div className="mx-auto max-w-4xl space-y-4 p-6">
        <p className="text-sm text-muted-foreground">
          A página <code>{slug}</code> ainda não existe.
        </p>
        <div className="flex gap-2">
          <Button onClick={() => setDraft(`# ${slug.split("/").pop()}\n\n`)}>
            Criar esta página
          </Button>
          <Link
            href={slug.startsWith("procedimentos/") ? "/wiki/procedimentos" : "/wiki"}
            className={buttonVariants({ variant: "outline" })}
          >
            Voltar
          </Link>
        </div>
      </div>
    );
  }

  if (!notFound && !page) {
    return <p className="p-6 text-sm text-destructive">Erro ao carregar a página.</p>;
  }

  return (
    <div className="mx-auto max-w-4xl space-y-4 p-6">
      <div className="flex items-center gap-2">
        <Link
          href={slug.startsWith("procedimentos/") ? "/wiki/procedimentos" : "/wiki"}
          className={buttonVariants({ variant: "ghost", size: "sm" })}
        >
          {slug.startsWith("procedimentos/") ? "← POPs" : "← Wiki"}
        </Link>
        {page?.editado && <Badge variant="outline">editado na UI</Badge>}
        <div className="ml-auto flex gap-2">
          {editing ? (
            <>
              <Button variant="outline" size="sm" onClick={() => setPreview((v) => !v)}>
                {preview ? "Editar texto" : "Pré-visualizar"}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setDraft(null);
                  setPreview(false);
                }}
              >
                Cancelar
              </Button>
              <Button size="sm" onClick={onSalvar} disabled={salvar.isPending}>
                {salvar.isPending ? "Salvando…" : "Salvar"}
              </Button>
            </>
          ) : (
            <>
              {page?.editado && (
                <Button
                  variant="outline"
                  size="sm"
                  disabled={reverter.isPending}
                  onClick={() =>
                    reverter.mutate(slug, {
                      onSuccess: () => toast.success("Edição descartada — versão do repo."),
                      onError: () => toast.error("Erro ao reverter."),
                    })
                  }
                >
                  Reverter edição
                </Button>
              )}
              <Button variant="outline" size="sm" onClick={() => setDraft(page?.content ?? "")}>
                Editar
              </Button>
            </>
          )}
        </div>
      </div>

      {editing ? (
        preview ? (
          <WikiMarkdown content={draft} baseSlug={slug} />
        ) : (
          <Textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            rows={28}
            className="font-mono text-sm"
          />
        )
      ) : (
        page && <WikiMarkdown content={page.content} baseSlug={slug} />
      )}
    </div>
  );
}
