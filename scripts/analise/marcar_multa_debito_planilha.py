"""Marca, na planilha da diretora, se cada (responsável, processo) tem multa ou débito.

Entrada:  docs/contas_julgadas_irregularidade_6218.xlsx
Saída:    docs/contas_julgadas_irregularidade_6218_com_multa_debito.xlsx
          (colunas novas: TemMulta, TemDebito, SituacaoDivida)

Só conta débitos vigentes (Exe_StatusDivida.StatusCancelamento IS NULL).
"""

import pandas as pd

from ccd.config import REPO_ROOT
from ccd.db import run_query_df

SRC = REPO_ROOT / "docs" / "contas_julgadas_irregularidade_6218.xlsx"
OUT = SRC.with_name(SRC.stem + "_com_multa_debito.xlsx")

# Exe_TipoDebito: 1 Ressarcimento, 2 Multa, 3 Remanejamento, 4 Multa Percentual, 5 Multa Cominatória
TIPOS_MULTA = {2, 4, 5}

# Liga o débito ao processo pelos DOIS papéis (execução e origem), nunca COALESCE.
# Sem filtro de IdDebitoAnterior: a cadeia não importa para uma pergunta de existência,
# e o filtro de cancelamento já descarta os débitos substituídos.
SQL = """
SELECT CAST(pr.numero_processo AS int) AS num,
       CAST(pr.ano_processo AS int)    AS ano,
       gp.Documento                    AS cpf,
       d.CodigoTipoDebito              AS tipo,
       sd.DescricaoStatusDivida        AS situacao
FROM   processo.dbo.Exe_Debito d
JOIN   processo.dbo.Exe_DebitoPessoa dp ON dp.IDDebito = d.IdDebito
JOIN   processo.dbo.GenPessoa gp        ON gp.IdPessoa = dp.IDPessoa
JOIN   processo.dbo.Exe_StatusDivida sd ON sd.CodigoStatusDivida = d.CodigoStatusDivida
JOIN   processo.dbo.Processos pr        ON pr.IdProcesso IN (d.IdProcessoExecucao, d.IdProcessoOrigem)
WHERE  sd.StatusCancelamento IS NULL
"""


def _cpf(serie: pd.Series) -> pd.Series:
    """CPF só com dígitos e 11 posições (o Excel come os zeros à esquerda)."""
    return serie.astype(str).str.replace(r"\D", "", regex=True).str.zfill(11)


def main() -> None:
    df = pd.read_excel(SRC)
    df["_cpf"] = _cpf(df["CPF"])
    partes = df["NumeroProcesso"].astype(str).str.split("/", expand=True)
    df["_num"] = partes[0].astype(int)
    df["_ano"] = partes[1].astype(int)

    deb = run_query_df(SQL)
    deb["_cpf"] = _cpf(deb["cpf"])

    agg = (
        deb.groupby(["num", "ano", "_cpf"])
        .agg(
            TemMulta=("tipo", lambda s: "Sim" if set(s) & TIPOS_MULTA else "Não"),
            TemDebito=("tipo", lambda s: "Sim" if set(s) - TIPOS_MULTA else "Não"),
            SituacaoDivida=("situacao", lambda s: ", ".join(sorted(set(s)))),
        )
        .reset_index()
    )

    out = df.merge(
        agg, left_on=["_num", "_ano", "_cpf"], right_on=["num", "ano", "_cpf"], how="left"
    )
    out["TemMulta"] = out["TemMulta"].fillna("Não")
    out["TemDebito"] = out["TemDebito"].fillna("Não")
    out["SituacaoDivida"] = out["SituacaoDivida"].fillna("")
    out = out[list(df.columns[:-3]) + ["TemMulta", "TemDebito", "SituacaoDivida"]]

    out.to_excel(OUT, index=False)

    com = ((out.TemMulta == "Sim") | (out.TemDebito == "Sim")).sum()
    print(f"{OUT}: {len(out)} linhas, {com} com multa/débito vigente")
    print(out.groupby(["TemMulta", "TemDebito"]).size().to_string())
    assert len(out) == len(df), "merge duplicou linhas"
    assert not out.SituacaoDivida.str.contains("Cancelad").any(), "cancelado vazou"


if __name__ == "__main__":
    main()
