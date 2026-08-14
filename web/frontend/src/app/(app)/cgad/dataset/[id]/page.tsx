"use client";

import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { AnnotationCanvas } from "@/components/dataset/annotation-canvas";
import { Button } from "@/components/ui/button";
import { useDocumento, useSalvarAnotacao } from "@/hooks/use-dataset";
import { messageForError } from "@/lib/error-messages";
import { Span } from "@/schemas/dataset";

export default function AnotarPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const searchParams = useSearchParams();
  const id = Number(params.id);

  // A aba de origem viaja na URL: sem isso o Concluir devolve o anotador para a
  // fila inteira, mesmo tendo entrado pela triagem.
  const comEntidades = searchParams.get("com_entidades");
  const filtro = {
    comEntidades: comEntidades === null ? undefined : comEntidades === "true",
    semAtosPessoal: searchParams.get("sem_atos_pessoal") === "true" || undefined,
  };
  const query = searchParams.toString() ? `?${searchParams}` : "";

  const documento = useDocumento(id, filtro);
  const salvar = useSalvarAnotacao(id, filtro);

  const [spans, setSpans] = useState<Span[] | null>(null);

  // Só semeia o estado local uma vez por documento; depois o usuário manda.
  useEffect(() => {
    setSpans(null);
  }, [id]);
  useEffect(() => {
    if (spans === null && documento.data) setSpans(documento.data.spans);
  }, [documento.data, spans]);

  useEffect(() => {
    if (!documento.isError) return;
    toast.error(messageForError(documento.error, "Erro ao carregar o documento."));
  }, [documento.isError, documento.error]);

  if (documento.isLoading || spans === null) {
    return <main className="p-6 text-muted-foreground">Carregando…</main>;
  }
  if (!documento.data) {
    return <main className="p-6 text-muted-foreground">Documento indisponível.</main>;
  }

  const doc = documento.data;

  function concluir() {
    salvar.mutate(
      { spans: spans ?? [], status: "done" },
      {
        onSuccess: (atualizado) => {
          toast.success("Anotação registrada.");
          if (atualizado.proximo_pendente) {
            router.push(`/cgad/dataset/${atualizado.proximo_pendente}${query}`);
          } else {
            router.push("/cgad/dataset");
          }
        },
        onError: (e) => toast.error(messageForError(e, "Erro ao salvar a anotação.")),
      },
    );
  }

  function salvarRascunho() {
    salvar.mutate(
      { spans: spans ?? [], status: "pending" },
      {
        onSuccess: () => toast.success("Rascunho salvo."),
        onError: (e) => toast.error(messageForError(e, "Erro ao salvar o rascunho.")),
      },
    );
  }

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-col gap-4 p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">
            {doc.processo ? `Processo ${doc.processo}` : `Documento ${doc.id}`}
          </h1>
          <p className="text-sm text-muted-foreground">
            {doc.codigo_tipo_processo ?? "—"}
            {doc.data_sessao
              ? ` · sessão de ${new Date(doc.data_sessao).toLocaleDateString("pt-BR")}`
              : ""}
            {doc.status === "done" ? " · já concluído" : ""}
          </p>
        </div>
        <Link
          href="/cgad/dataset"
          className="text-sm text-muted-foreground hover:text-foreground hover:underline"
        >
          Voltar à fila
        </Link>
      </div>

      <p className="text-sm text-muted-foreground">
        Selecione o trecho com o mouse e escolha o rótulo. Clique num trecho já marcado para
        removê-lo. Nenhum span pode se sobrepor a outro.
      </p>

      <AnnotationCanvas text={doc.texto} spans={spans} onChange={setSpans} />

      <div className="flex items-center gap-3">
        <Button onClick={concluir} disabled={salvar.isPending}>
          {doc.status === "done" ? "Salvar alterações" : "Concluir e ir para o próximo"}
        </Button>
        <Button variant="outline" onClick={salvarRascunho} disabled={salvar.isPending}>
          Salvar rascunho
        </Button>
        <span className="text-sm text-muted-foreground">
          {spans.length} {spans.length === 1 ? "entidade marcada" : "entidades marcadas"}
        </span>
      </div>
    </main>
  );
}
