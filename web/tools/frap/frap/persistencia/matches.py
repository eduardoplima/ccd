"""Persistência dos resultados dos 3 matchers em FRAPMatchOB / FRAPMatchPessoa / FRAPMatchGuia.

Estratégia: para cada (IdConta, Periodo), DELETE + INSERT. IdLancamento é resolvido
para linhas que vieram do extrato; linhas órfãs (SO_SIGEF, SO_PROCESSO) ficam com NULL.
"""
from __future__ import annotations

import pandas as pd
from sqlalchemy import Engine, text

from frap.persistencia.lookups import get_id_conta, get_id_status_match

_SQL_MAPA_LANC = """
SELECT IdLancamento, OrdemNoArquivo
FROM dbo.FRAPLancamento
WHERE IdConta = :id_conta AND Periodo = :periodo;
"""


def _mapa_lancamento(engine: Engine, id_conta: int, periodo: str) -> dict[int, int]:
    with engine.connect() as conn:
        df = pd.read_sql(
            text(_SQL_MAPA_LANC),
            conn,
            params={"id_conta": id_conta, "periodo": periodo},
        )
    return dict(zip(df["OrdemNoArquivo"].astype(int), df["IdLancamento"].astype(int)))


# --- OB ---------------------------------------------------------------------

_SQL_DELETE_OB = "DELETE FROM dbo.FRAPMatchOB WHERE IdConta = :id_conta AND Periodo = :periodo;"

_SQL_INSERT_OB = """
INSERT INTO dbo.FRAPMatchOB
    (IdLancamento, IdConta, Periodo, AnoSigef, CdUnidadeGestora, CdGestao,
     NuOrdemBancaria, DataPagamento, ValorOB, CdCredor, NmCredor,
     NuPreparacaoPagamento, NuNotaEmpenho, IdStatusMatch)
VALUES
    (:id_lancamento, :id_conta, :periodo, :ano_sigef, :cd_unidade_gestora, :cd_gestao,
     :nu_ordem_bancaria, :data_pagamento, :valor_ob, :cd_credor, :nm_credor,
     :nu_preparacao_pagamento, :nu_nota_empenho, :id_status_match);
"""


def publica_match_ob(
    engine: Engine,
    df: pd.DataFrame,
    conta: str,
    periodo: str,
    ano_sigef: int,
) -> int:
    """Substitui os match-OB de (`conta`, `periodo`) pelos do `df` (filtrado pela conta)."""
    id_conta = get_id_conta(engine, conta)
    mapa = _mapa_lancamento(engine, id_conta, periodo)
    df = _filtra_por_conta(df, conta)

    with engine.begin() as conn:
        conn.execute(text(_SQL_DELETE_OB), {"id_conta": id_conta, "periodo": periodo})
        if df.empty:
            return 0
        params = [_to_ob_param(row, id_conta, periodo, ano_sigef, mapa, engine) for _, row in df.iterrows()]
        conn.execute(text(_SQL_INSERT_OB), params)
        return len(params)


def _to_ob_param(
    row: pd.Series,
    id_conta: int,
    periodo: str,
    ano_sigef: int,
    mapa: dict[int, int],
    engine: Engine,
) -> dict:
    ordem = row.get("ordem_no_arquivo")
    id_lanc = mapa.get(int(ordem)) if pd.notna(ordem) else None
    return {
        "id_lancamento": id_lanc,
        "id_conta": id_conta,
        "periodo": periodo,
        "ano_sigef": int(ano_sigef),
        "cd_unidade_gestora": _int_or_none(row.get("CDUNIDADEGESTORA")),
        "cd_gestao": _int_or_none(row.get("CDGESTAO")),
        "nu_ordem_bancaria": _str_or_none(row.get("OB_Sigef")),
        "data_pagamento": _date(row.get("DataPagamento")),
        "valor_ob": _float_or_none(row.get("ValorOB")),
        "cd_credor": _str_or_none(row.get("CDCREDOR")),
        "nm_credor": _str_or_none(row.get("Credor")),
        "nu_preparacao_pagamento": _str_or_none(row.get("PP")),
        "nu_nota_empenho": _str_or_none(row.get("Empenho")),
        "id_status_match": get_id_status_match(engine, "OB", str(row["status_match"])),
    }


# --- Pessoa -----------------------------------------------------------------

_SQL_DELETE_PESSOA = (
    "DELETE FROM dbo.FRAPMatchPessoa WHERE IdConta = :id_conta AND Periodo = :periodo;"
)

_SQL_INSERT_PESSOA = """
INSERT INTO dbo.FRAPMatchPessoa
    (IdLancamento, IdConta, Periodo, IdDebito, IdProcessoExecucao, CpfCnpj, NomePessoa,
     ValorPago, ValorAPagar, ValorOriginalDebito, ValorCasadoEm, IdStatusMatch)
VALUES
    (:id_lancamento, :id_conta, :periodo, :id_debito, :id_processo_execucao, :cpf_cnpj, :nome_pessoa,
     :valor_pago, :valor_a_pagar, :valor_original_debito, :valor_casado_em, :id_status_match);
"""


def publica_match_pessoa(
    engine: Engine,
    df: pd.DataFrame,
    conta: str,
    periodo: str,
) -> int:
    id_conta = get_id_conta(engine, conta)
    mapa = _mapa_lancamento(engine, id_conta, periodo)
    df = _filtra_por_conta(df, conta)

    with engine.begin() as conn:
        conn.execute(text(_SQL_DELETE_PESSOA), {"id_conta": id_conta, "periodo": periodo})
        if df.empty:
            return 0
        params = [_to_pessoa_param(row, id_conta, periodo, mapa, engine) for _, row in df.iterrows()]
        conn.execute(text(_SQL_INSERT_PESSOA), params)
        return len(params)


def _to_pessoa_param(
    row: pd.Series,
    id_conta: int,
    periodo: str,
    mapa: dict[int, int],
    engine: Engine,
) -> dict:
    ordem = row.get("ordem_no_arquivo")
    id_lanc = mapa.get(int(ordem)) if pd.notna(ordem) else None
    cpf = _str_or_none(row.get("cpfcnpj_depositante")) or _str_or_none(row.get("Documento"))
    casado = row.get("valor_casado_em")
    casado_csv = ",".join(casado) if isinstance(casado, list) and casado else None
    return {
        "id_lancamento": id_lanc,
        "id_conta": id_conta,
        "periodo": periodo,
        "id_debito": _int_or_none(row.get("IdDebito")),
        "id_processo_execucao": _int_or_none(row.get("IdProcessoExecucao")),
        "cpf_cnpj": cpf or "",
        "nome_pessoa": _str_or_none(row.get("Nome")),
        "valor_pago": _float_or_none(row.get("ValorPago")),
        "valor_a_pagar": _float_or_none(row.get("ValorAPagar")),
        "valor_original_debito": _float_or_none(row.get("valorOriginalDebito")),
        "valor_casado_em": casado_csv,
        "id_status_match": get_id_status_match(engine, "PESSOA", str(row["status_match"])),
    }


# --- Guia -------------------------------------------------------------------

_SQL_DELETE_GUIA = "DELETE FROM dbo.FRAPMatchGuia WHERE IdConta = :id_conta AND Periodo = :periodo;"

_SQL_INSERT_GUIA = """
INSERT INTO dbo.FRAPMatchGuia
    (IdLancamento, IdConta, Periodo, IdBoleto, IdDebito, IdProcessoExecucao,
     CodigoBarras, DataPagamento, ValorPago, NomePessoa, CpfCnpj, IdStatusMatch)
VALUES
    (:id_lancamento, :id_conta, :periodo, :id_boleto, :id_debito, :id_processo_execucao,
     :codigo_barras, :data_pagamento, :valor_pago, :nome_pessoa, :cpf_cnpj, :id_status_match);
"""


def publica_match_guia(
    engine: Engine,
    df: pd.DataFrame,
    conta: str,
    periodo: str,
) -> int:
    id_conta = get_id_conta(engine, conta)
    mapa = _mapa_lancamento(engine, id_conta, periodo)
    df = _filtra_por_conta(df, conta)

    with engine.begin() as conn:
        conn.execute(text(_SQL_DELETE_GUIA), {"id_conta": id_conta, "periodo": periodo})
        if df.empty:
            return 0
        params = [_to_guia_param(row, id_conta, periodo, mapa, engine) for _, row in df.iterrows()]
        conn.execute(text(_SQL_INSERT_GUIA), params)
        return len(params)


def _to_guia_param(
    row: pd.Series,
    id_conta: int,
    periodo: str,
    mapa: dict[int, int],
    engine: Engine,
) -> dict:
    ordem = row.get("ordem_no_arquivo")
    id_lanc = mapa.get(int(ordem)) if pd.notna(ordem) else None
    return {
        "id_lancamento": id_lanc,
        "id_conta": id_conta,
        "periodo": periodo,
        "id_boleto": _int_or_none(row.get("IdBoleto")),
        "id_debito": _int_or_none(row.get("IdDebito")),
        "id_processo_execucao": _int_or_none(row.get("IdProcessoExecucao")),
        "codigo_barras": _str_or_none(row.get("CodigoBarras")),
        "data_pagamento": _date(row.get("DataPagamento")),
        "valor_pago": _float_or_none(row.get("ValorPago")),
        "nome_pessoa": _str_or_none(row.get("Nome")),
        "cpf_cnpj": _str_or_none(row.get("Documento")),
        "id_status_match": get_id_status_match(engine, "GUIA", str(row["status_match"])),
    }


# --- helpers ----------------------------------------------------------------


def _filtra_por_conta(df: pd.DataFrame, conta: str) -> pd.DataFrame:
    """Mantém apenas linhas cuja `conta` casa. Linhas com `conta` ausente
    (órfãs SO_SIGEF/SO_PROCESSO) são descartadas — `IdConta` não pode ser
    inferido para elas e o schema FRAPMatch* exige `IdConta NOT NULL`."""
    if df.empty or "conta" not in df.columns:
        return df.iloc[0:0] if not df.empty else df
    return df[df["conta"].astype(str) == conta]


def _date(v):
    if v is None or pd.isna(v):
        return None
    if isinstance(v, pd.Timestamp):
        return v.date()
    return v


def _int_or_none(v):
    if v is None or pd.isna(v):
        return None
    return int(v)


def _float_or_none(v):
    if v is None or pd.isna(v):
        return None
    return float(v)


def _str_or_none(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = str(v).strip()
    return s if s else None
