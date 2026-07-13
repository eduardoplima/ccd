"""Processos com débito de Nereu cujo ato aposentador foi publicado antes de 15/07/2014.

A data de publicação do ato de concessão (aposentadoria/pensão) vem de
processo.dbo.Registro_AtoPessoal.DataDoeEstado, registrada no processo de ORIGEM
(a apreciação da concessão), não no de execução. Validado contra os casos conferidos
manualmente: 004599/2016 -> 11/12/2014 (exec 003677/2022); 003603/2016 -> 03/12/2014
(exec 000131/2022).

Recorte: débitos ATIVOS (não cancelados) de NEREU BATISTA LINHARES (CPF 13006444434),
head do débito (IdDebitoAnterior IS NULL). Saída: uma linha por processo de execução.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ccd.db import run_query_df

CPF_NEREU = "13006444434"
CORTE = "2014-07-15"  # estritamente antes

# MIN(DataDoeEstado) por processo de origem: se a origem tem mais de um ato, pega o mais
# antigo (coerente com "publicado antes de"). O ato mora sempre na origem (apreciação).
SQL = """
SELECT
    e.IdDebito AS id_debito,
    CONCAT(RTRIM(po.numero_processo), CHAR(47), RTRIM(po.ano_processo)) AS processo_origem,
    CONCAT(RTRIM(px.numero_processo), CHAR(47), RTRIM(px.ano_processo)) AS processo_execucao,
    ra.dt          AS data_publicacao_ato,
    RTRIM(po.interessado) AS interessado,
    ra.matricula   AS matricula,
    etd.Descricao  AS tipo_debito,
    esd.DescricaoStatusDivida AS situacao_divida,
    processo.dbo.fn_Exe_RetornaValorAtualizado(e.IdDebito) AS valor_atualizado
FROM processo.dbo.Exe_Debito e
INNER JOIN processo.dbo.Exe_DebitoPessoa edp ON edp.IDDebito = e.IdDebito
INNER JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = edp.IDPessoa
INNER JOIN (
    SELECT IdProcesso,
           MIN(DataDoeEstado)          AS dt,
           MIN(RTRIM(Matricula))       AS matricula
    FROM processo.dbo.Registro_AtoPessoal
    WHERE DataDoeEstado IS NOT NULL
    GROUP BY IdProcesso
) ra ON ra.IdProcesso = e.IdProcessoOrigem
LEFT JOIN processo.dbo.Processos po ON po.IdProcesso = e.IdProcessoOrigem
LEFT JOIN processo.dbo.Processos px ON px.IdProcesso = e.IdProcessoExecucao
LEFT JOIN processo.dbo.Exe_TipoDebito etd ON etd.CodigoTipoDebito = e.CodigoTipoDebito
LEFT JOIN processo.dbo.Exe_StatusDivida esd ON esd.CodigoStatusDivida = e.CodigoStatusDivida
WHERE gp.Documento = :cpf
  AND e.IdDebitoAnterior IS NULL
  AND esd.StatusCancelamento IS NULL
  AND ra.dt < :corte
"""

# Cobertura: débitos ativos SEM ato mapeado (origem ausente ou sem Registro_AtoPessoal),
# só para reportar no stdout quantos ficaram de fora da checagem.
SQL_SEM_ATO = """
SELECT COUNT(*) AS n
FROM processo.dbo.Exe_Debito e
INNER JOIN processo.dbo.Exe_DebitoPessoa edp ON edp.IDDebito = e.IdDebito
INNER JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = edp.IDPessoa
LEFT JOIN processo.dbo.Exe_StatusDivida esd ON esd.CodigoStatusDivida = e.CodigoStatusDivida
LEFT JOIN (
    SELECT IdProcesso, MIN(DataDoeEstado) AS dt
    FROM processo.dbo.Registro_AtoPessoal WHERE DataDoeEstado IS NOT NULL
    GROUP BY IdProcesso
) ra ON ra.IdProcesso = e.IdProcessoOrigem
WHERE gp.Documento = :cpf
  AND e.IdDebitoAnterior IS NULL
  AND esd.StatusCancelamento IS NULL
  AND ra.dt IS NULL
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpf", default=CPF_NEREU)
    parser.add_argument("--corte", default=CORTE, help="Data de corte (ato publicado ANTES de)")
    parser.add_argument("--outdir", default="scripts/analise/docs")
    args = parser.parse_args()

    df = run_query_df(SQL, cpf=args.cpf, corte=args.corte)
    df["data_publicacao_ato"] = pd.to_datetime(df["data_publicacao_ato"])

    # Unidade = processo de ORIGEM (a apreciação onde mora o ato). Um ato = uma origem;
    # dela podem sair vários débitos/execuções. Agrupar por execução seria errado porque
    # débitos sem processo de execução ficariam todos com a mesma chave vazia.
    def _juntar(s: pd.Series) -> str:
        return ", ".join(sorted({v for v in s.dropna() if str(v).strip("/ ")}))

    por_proc = (
        df.groupby("processo_origem", as_index=False)
        .agg(
            processos_execucao=("processo_execucao", _juntar),
            interessado=("interessado", "first"),
            matricula=("matricula", "first"),
            data_publicacao_ato=("data_publicacao_ato", "min"),
            tipo_debito=("tipo_debito", _juntar),
            situacao_divida=("situacao_divida", _juntar),
            valor_atualizado=("valor_atualizado", "sum"),
            n_debitos=("id_debito", "nunique"),
        )
        .sort_values("data_publicacao_ato")
        .reset_index(drop=True)
    )
    por_proc["processos_execucao"] = por_proc["processos_execucao"].replace("", "(sem execução)")
    por_proc["data_publicacao_ato"] = por_proc["data_publicacao_ato"].dt.strftime("%d/%m/%Y")

    sem_ato = int(run_query_df(SQL_SEM_ATO, cpf=args.cpf).iloc[0]["n"])

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    xlsx = outdir / "atos_nereu_pre_20140715.xlsx"
    por_proc.to_excel(xlsx, index=False)

    print(f"Débitos ativos de Nereu (CPF {args.cpf}) com ato publicado antes de "
          f"{pd.to_datetime(args.corte).strftime('%d/%m/%Y')}:")
    print(f"  processos de origem (atos): {len(por_proc)}  (débitos: {int(por_proc['n_debitos'].sum())})")
    print(f"  valor atualizado total: R$ {por_proc['valor_atualizado'].sum():,.2f}")
    print(f"  [cobertura] débitos ativos sem ato mapeado (fora da checagem): {sem_ato}")
    print(f"\nPlanilha: {xlsx.resolve()}\n")
    with pd.option_context("display.width", 240, "display.max_rows", 200):
        print(por_proc[["processo_origem", "processos_execucao", "data_publicacao_ato",
                        "interessado", "situacao_divida", "valor_atualizado"]].to_string(index=False))


if __name__ == "__main__":
    main()
