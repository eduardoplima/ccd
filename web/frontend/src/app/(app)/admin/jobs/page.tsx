"use client";

import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useAdminJobs, useExecutarJob } from "@/hooks/use-admin-jobs";

export default function JobsPage() {
  const { data, isLoading, isError } = useAdminJobs();
  const executar = useExecutarJob();

  function disparar(nome: string) {
    executar.mutate(nome, {
      onSuccess: (id) => toast.success(`${nome} enfileirado (${id})`),
      onError: (e) => toast.error(`Falha ao enfileirar ${nome}: ${(e as Error).message}`),
    });
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="section-heading text-2xl">Jobs</h1>
        <p className="text-muted-foreground text-sm">
          Tarefas do worker. O cron está em UTC (o container roda em UTC); a coluna ao lado traz o
          horário de Brasília. Os jobs sem cron rodam sob demanda, disparados pelas telas.
        </p>
      </div>

      {isLoading ? (
        <p className="text-muted-foreground text-sm">Carregando...</p>
      ) : isError || !data ? (
        <p className="text-destructive text-sm">Falha ao carregar os jobs.</p>
      ) : (
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Job</TableHead>
                <TableHead>Descrição</TableHead>
                <TableHead>Cron (UTC)</TableHead>
                <TableHead>Horário (Brasília)</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((j) => (
                <TableRow key={j.nome}>
                  <TableCell className="font-mono text-xs">{j.nome}</TableCell>
                  <TableCell className="text-sm">{j.descricao}</TableCell>
                  <TableCell className="font-mono text-xs whitespace-nowrap">
                    {j.cron ?? "—"}
                  </TableCell>
                  <TableCell className="text-sm whitespace-nowrap">
                    {j.horario_brasilia ?? "sob demanda"}
                  </TableCell>
                  <TableCell>
                    {j.cron ? (
                      <Button
                        size="sm"
                        variant="outline"
                        disabled={executar.isPending}
                        onClick={() => disparar(j.nome)}
                      >
                        Executar agora
                      </Button>
                    ) : null}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
