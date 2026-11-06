"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useCcdJob } from "@/hooks/use-ccd-job";
import { useCurrentUser } from "@/hooks/use-current-user";
import { useExtrairTag, useTags } from "@/hooks/use-tags";
import { messageForError } from "@/lib/error-messages";
import { formatDate } from "@/lib/format";
import { podeEditar } from "@/lib/permissoes";
import { SITUACAO_TAG } from "./_shared";

const JOB_LABEL: Record<string, string> = {
  pending: "Na fila...",
  running: "Lendo o PDF (OCR) e consultando a LLM...",
  done: "Concluído",
  failed: "Falhou",
  cancelled: "Cancelado",
};

export default function TagsPage() {
  const [q, setQ] = useState("");
  const [busca, setBusca] = useState("");
  const [extrairOpen, setExtrairOpen] = useState(false);
  const { data, isLoading, isError, error } = useTags(busca);
  const { data: me } = useCurrentUser();
  const canEdit = podeEditar(me, "ccd.tags");
  const hoje = new Date().toISOString().slice(0, 10);

  return (
    <main className="flex flex-col gap-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="section-heading text-2xl">Termos de Ajustamento de Gestão</h1>
          <p className="text-sm text-muted-foreground">
            Cadastro Geral de TAGs (RI, art. 431, IV, “d”): termo, órgão, responsável, prazos e
            obrigações da cláusula de compromisso, extraídos do PDF do evento e conferidos aqui.
          </p>
        </div>
        {canEdit && <Button onClick={() => setExtrairOpen(true)}>Extrair de evento</Button>}
      </div>

      <form
        className="flex gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          setBusca(q.trim());
        }}
      >
        <Input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Processo, nº do TAG, órgão ou responsável"
          className="max-w-md"
        />
        <Button type="submit" variant="outline">
          Buscar
        </Button>
      </form>

      {isError && (
        <p className="text-sm text-destructive">
          {messageForError(error, "Erro ao carregar os TAGs.")}
        </p>
      )}

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Processo</TableHead>
              <TableHead>TAG</TableHead>
              <TableHead>Órgão</TableHead>
              <TableHead>Responsável</TableHead>
              <TableHead>Prazo final</TableHead>
              <TableHead>Próximo vencimento</TableHead>
              <TableHead className="text-right">Obrigações</TableHead>
              <TableHead>Situação</TableHead>
              <TableHead />
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={9} className="text-center text-muted-foreground">
                  Carregando...
                </TableCell>
              </TableRow>
            ) : !data?.items.length ? (
              <TableRow>
                <TableCell colSpan={9} className="text-center text-muted-foreground">
                  Nenhum TAG cadastrado.
                </TableCell>
              </TableRow>
            ) : (
              data.items.map((t) => {
                const st = SITUACAO_TAG[t.situacao];
                const vencido =
                  t.situacao === "VIGENTE" && t.proximaDataLimite && t.proximaDataLimite < hoje;
                return (
                  <TableRow key={t.id}>
                    <TableCell className="whitespace-nowrap">
                      <a
                        href={`https://processos.tce.rn.gov.br/#/dashboard/processos/${t.idProcesso}`}
                        target="_blank"
                        rel="noreferrer"
                        className="text-primary underline-offset-2 hover:underline"
                      >
                        {t.processo}
                      </a>
                      <div className="text-xs text-muted-foreground">
                        {t.urlEvento ? (
                          <a href={t.urlEvento} target="_blank" rel="noreferrer">
                            Ev. {t.evento}
                          </a>
                        ) : (
                          `Ev. ${t.evento}`
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="whitespace-nowrap">
                      {t.numero}
                      {!t.revisado && (
                        <Badge variant="warning" className="ml-2">
                          rascunho
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell className="max-w-xs">{t.orgao}</TableCell>
                    <TableCell className="max-w-xs">{t.responsavel}</TableCell>
                    <TableCell className="whitespace-nowrap">{formatDate(t.prazo)}</TableCell>
                    <TableCell className="whitespace-nowrap">
                      {formatDate(t.proximaDataLimite)}
                      {vencido && (
                        <Badge variant="destructive" className="ml-2">
                          vencido
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-right">{t.qtdObrigacoes}</TableCell>
                    <TableCell>
                      <Badge variant={st.variant}>{st.label}</Badge>
                    </TableCell>
                    <TableCell>
                      <Link
                        href={`/ccd/tags/${t.id}`}
                        className={buttonVariants({ size: "sm", variant: "outline" })}
                      >
                        Detalhes
                      </Link>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>

      <ExtrairDialog open={extrairOpen} onOpenChange={setExtrairOpen} />
    </main>
  );
}

function ExtrairDialog({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (v: boolean) => void;
}) {
  const router = useRouter();
  const [processo, setProcesso] = useState("");
  const [evento, setEvento] = useState("");
  const [idJob, setIdJob] = useState<number | null>(null);
  const extrair = useExtrairTag();
  const { data: job } = useCcdJob(idJob);
  const jobAtivo = job != null && (job.status === "pending" || job.status === "running");
  const [jobVisto, setJobVisto] = useState<number | null>(null);

  if (job && !jobAtivo && idJob != null && jobVisto !== idJob) {
    setJobVisto(idJob);
    if (job.status === "done") {
      toast.success(job.resultado ?? "Extração concluída.");
      const m = /\(id (\d+)\)/.exec(job.resultado ?? "");
      onOpenChange(false);
      router.push(m ? `/ccd/tags/${m[1]}` : "/ccd/tags");
    }
    if (job.status === "failed") toast.error(job.erroMensagem ?? "Extração falhou.");
  }

  function fechar() {
    onOpenChange(false);
    setProcesso("");
    setEvento("");
    setIdJob(null);
    setJobVisto(null);
  }

  return (
    <Dialog open={open} onOpenChange={(v) => (v ? onOpenChange(v) : fechar())}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Extrair TAG de um evento</DialogTitle>
          <DialogDescription>
            O PDF do evento é lido do compartilhamento (com OCR se for digitalizado) e a LLM do
            SERPRO monta um rascunho com termo, partes, prazos e obrigações. Confira tudo antes de
            marcar como revisado.
          </DialogDescription>
        </DialogHeader>
        <form
          className="flex flex-col gap-4"
          onSubmit={(e) => {
            e.preventDefault();
            extrair.mutate(
              { processo: processo.trim(), evento: Number(evento) },
              {
                onSuccess: (j) => setIdJob(j.idJob),
                onError: (err) =>
                  toast.error(messageForError(err, "Erro ao enfileirar a extração.")),
              },
            );
          }}
        >
          <div className="flex flex-col gap-2">
            <Label htmlFor="t-processo">Processo</Label>
            <Input
              id="t-processo"
              value={processo}
              onChange={(e) => setProcesso(e.target.value)}
              placeholder="14254/2015"
              pattern="\d{1,6}/\d{4}"
              required
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="t-evento">Evento do termo</Label>
            <Input
              id="t-evento"
              value={evento}
              onChange={(e) => setEvento(e.target.value)}
              placeholder="298"
              inputMode="numeric"
              pattern="\d+"
              required
            />
          </div>
          {job && (
            <p className="text-sm text-muted-foreground">
              {JOB_LABEL[job.status] ?? job.status}
              {job.status === "failed" && job.erroMensagem ? ` — ${job.erroMensagem}` : ""}
            </p>
          )}
          <DialogFooter>
            <Button type="button" variant="outline" onClick={fechar}>
              Fechar
            </Button>
            <Button type="submit" disabled={extrair.isPending || jobAtivo}>
              {jobAtivo ? "Extraindo..." : "Extrair"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
