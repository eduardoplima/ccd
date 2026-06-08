"use client";

import { Badge } from "@/components/ui/badge";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { useLancamento } from "@/hooks/use-lancamento";
import { formatBRL, formatDate, matchStatusVariant } from "@/lib/format";
import {
  type LancamentoDetail,
  type Match,
  type MatchDescontoFolha,
  type MatchGuia,
  type MatchOB,
  type MatchPessoa,
} from "@/schemas/lancamento";

interface Props {
  idLancamento: number | null;
  onOpenChange: (open: boolean) => void;
}

export function LancamentoDetailSheet({ idLancamento, onOpenChange }: Props) {
  const { data, isLoading, isError } = useLancamento(idLancamento);

  return (
    <Sheet open={idLancamento !== null} onOpenChange={onOpenChange}>
      <SheetContent>
        <SheetHeader>
          <SheetTitle>Lançamento {idLancamento ?? ""}</SheetTitle>
          <SheetDescription>Detalhes e conciliação cruzada.</SheetDescription>
        </SheetHeader>

        {isLoading ? (
          <p className="mt-6 text-sm text-muted-foreground">Carregando...</p>
        ) : isError ? (
          <p className="mt-6 text-sm text-destructive">Erro ao carregar.</p>
        ) : data ? (
          <div className="mt-6 flex flex-col gap-6">
            <LancamentoFields detail={data} />
            <MatchesSection matches={data.matches} />
          </div>
        ) : null}
      </SheetContent>
    </Sheet>
  );
}

function LancamentoFields({ detail }: { detail: LancamentoDetail }) {
  return (
    <section className="rounded-lg border bg-background p-4">
      <h3 className="section-heading text-sm">Lançamento</h3>
      <dl className="mt-3 grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
        <Field label="Data movimento" value={formatDate(detail.dtMovimento)} />
        <Field label="Data balancete" value={formatDate(detail.dtBalancete)} />
        <Field label="Conta" value={detail.conta} mono />
        <Field label="Período" value={detail.periodo} mono />
        <Field label="Histórico" value={detail.historico} colSpan />
        <Field label="Documento" value={detail.documento ?? "—"} mono />
        <Field label="Doc data" value={formatDate(detail.docData)} />
        <Field label="Ag. origem" value={detail.agOrigem ?? "—"} mono />
        <Field label="Lote" value={detail.lote ?? "—"} mono />
        <Field
          label={`Valor (${detail.valorDC})`}
          value={`${detail.valorDC === "D" ? "−" : ""}${formatBRL(detail.valor)}`}
          mono
        />
        <Field label="Categoria" value={detail.categoria} />
        {detail.descricao ? <Field label="Descrição" value={detail.descricao} colSpan /> : null}
        {detail.cpfcnpjDepositante ? (
          <Field
            label={`CPF/CNPJ depositante${detail.cpfcnpjAmbiguo ? " (ambíguo)" : ""}`}
            value={detail.cpfcnpjDepositante}
            mono
            colSpan
          />
        ) : null}
        {detail.nomeArquivo ? (
          <Field label="Arquivo" value={detail.nomeArquivo} mono colSpan />
        ) : null}
      </dl>
    </section>
  );
}

function MatchesSection({ matches }: { matches: Match[] }) {
  if (matches.length === 0) {
    return (
      <section className="rounded-lg border border-dashed bg-muted/40 p-4">
        <p className="text-sm text-muted-foreground">Nenhum match registrado.</p>
      </section>
    );
  }
  return (
    <section className="flex flex-col gap-3">
      <h3 className="section-heading text-sm">Matches ({matches.length})</h3>
      {matches.map((m) => (
        <MatchCard key={`${m.matcher}-${m.idMatch}`} match={m} />
      ))}
    </section>
  );
}

function MatchCard({ match }: { match: Match }) {
  const title = matcherTitle(match.matcher);
  return (
    <article className="rounded-lg border bg-background p-4">
      <header className="mb-3 flex items-center justify-between gap-3">
        <h4 className="text-sm font-medium">{title}</h4>
        <Badge variant={matchStatusVariant(match.status)}>{match.status}</Badge>
      </header>
      {match.statusDescricao ? (
        <p className="mb-3 text-xs text-muted-foreground">{match.statusDescricao}</p>
      ) : null}
      <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
        {match.matcher === "OB" ? <ObFields match={match} /> : null}
        {match.matcher === "PESSOA" ? <PessoaFields match={match} /> : null}
        {match.matcher === "GUIA" ? <GuiaFields match={match} /> : null}
        {match.matcher === "DESCONTO_FOLHA" ? <DescontoFolhaFields match={match} /> : null}
      </dl>
    </article>
  );
}

function matcherTitle(matcher: Match["matcher"]): string {
  switch (matcher) {
    case "OB":
      return "Ordem Bancária (SIGEF)";
    case "PESSOA":
      return "Pessoa (Exe_Debito)";
    case "GUIA":
      return "Guia (Exe_Boleto)";
    case "DESCONTO_FOLHA":
      return "Desconto em Folha";
  }
}

function ObFields({ match }: { match: MatchOB }) {
  return (
    <>
      <Field label="Ano SIGEF" value={match.anoSigef ?? "—"} mono />
      <Field label="NU OB" value={match.nuOrdemBancaria ?? "—"} mono />
      <Field label="UG" value={match.cdUnidadeGestora ?? "—"} mono />
      <Field label="Gestão" value={match.cdGestao ?? "—"} mono />
      <Field label="Data pagamento" value={formatDate(match.dataPagamento)} />
      <Field label="Valor OB" value={match.valorOB != null ? formatBRL(match.valorOB) : "—"} mono />
      <Field label="Credor" value={match.cdCredor ?? "—"} mono />
      <Field label="Nome credor" value={match.nmCredor ?? "—"} colSpan />
      {match.nuPreparacaoPagamento ? (
        <Field label="PP" value={match.nuPreparacaoPagamento} mono />
      ) : null}
      {match.nuNotaEmpenho ? <Field label="NE" value={match.nuNotaEmpenho} mono /> : null}
    </>
  );
}

function PessoaFields({ match }: { match: MatchPessoa }) {
  return (
    <>
      <Field label="CPF/CNPJ" value={match.cpfcnpj ?? "—"} mono />
      <Field label="Nome" value={match.nomePessoa ?? "—"} colSpan />
      <Field label="ID Débito" value={match.idDebito ?? "—"} mono />
      <Field label="ID Processo Exec." value={match.idProcessoExecucao ?? "—"} mono />
      <Field
        label="Valor pago"
        value={match.valorPago != null ? formatBRL(match.valorPago) : "—"}
        mono
      />
      <Field
        label="Valor a pagar"
        value={match.valorAPagar != null ? formatBRL(match.valorAPagar) : "—"}
        mono
      />
      <Field
        label="Valor original"
        value={match.valorOriginalDebito != null ? formatBRL(match.valorOriginalDebito) : "—"}
        mono
      />
      {match.valorCasadoEm ? <Field label="Casou em" value={match.valorCasadoEm} colSpan /> : null}
    </>
  );
}

function GuiaFields({ match }: { match: MatchGuia }) {
  return (
    <>
      <Field label="Código de barras" value={match.codigoBarras ?? "—"} mono colSpan />
      <Field label="ID Boleto" value={match.idBoleto ?? "—"} mono />
      <Field label="ID Débito" value={match.idDebito ?? "—"} mono />
      <Field label="Data pagamento" value={formatDate(match.dataPagamento)} />
      <Field
        label="Valor pago"
        value={match.valorPago != null ? formatBRL(match.valorPago) : "—"}
        mono
      />
      <Field label="CPF/CNPJ" value={match.cpfcnpj ?? "—"} mono />
      <Field label="Nome" value={match.nomePessoa ?? "—"} colSpan />
    </>
  );
}

function DescontoFolhaFields({ match }: { match: MatchDescontoFolha }) {
  return (
    <>
      <Field
        label="Parcela"
        value={
          match.numeroParcela != null
            ? `${match.numeroParcela} (${match.mesReferencia ?? "?"}/${match.anoReferencia ?? "?"})`
            : "—"
        }
      />
      <Field
        label="Valor esperado"
        value={match.valorEsperado != null ? formatBRL(match.valorEsperado) : "—"}
        mono
      />
      <Field label="CPF/CNPJ" value={match.cpfcnpj ?? "—"} mono />
      <Field label="Nome" value={match.nomePessoa ?? "—"} colSpan />
      <Field
        label="Valor contracheque"
        value={match.valorContracheque != null ? formatBRL(match.valorContracheque) : "—"}
        mono
      />
      <Field label="ID item contracheque" value={match.idContrachequeItem ?? "—"} mono />
    </>
  );
}

function Field({
  label,
  value,
  mono,
  colSpan,
}: {
  label: string;
  value: React.ReactNode;
  mono?: boolean;
  colSpan?: boolean;
}) {
  return (
    <div className={colSpan ? "col-span-2" : ""}>
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className={mono ? "font-mono text-sm" : "text-sm"}>{value}</dd>
    </div>
  );
}
