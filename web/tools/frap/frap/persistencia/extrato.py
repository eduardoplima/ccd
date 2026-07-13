"""Persistência do extrato canônico em FRAPExtratoArquivo + FRAPLancamento.

Estratégia: substituição por (conta, periodo). Para cada grupo:
  1. UPSERT em FRAPExtratoArquivo via MERGE (chave UQ_FRAPExtratoArquivo_ContaPeriodo).
  2. DELETE em FRAPLancamento WHERE IdArquivo = ? (limpa lançamentos antigos do arquivo).
  3. INSERT em FRAPLancamento via executemany.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
from sqlalchemy import Engine, text

from frap.persistencia.lookups import get_id_categoria, get_id_conta

_SQL_UPSERT_ARQUIVO = """
MERGE dbo.FRAPExtratoArquivo AS tgt
USING (SELECT :id_conta AS IdConta, :periodo AS Periodo) AS src
ON tgt.IdConta = src.IdConta AND tgt.Periodo = src.Periodo
WHEN MATCHED THEN
    UPDATE SET
        NomeArquivo    = :nome_arquivo,
        HashSha256     = :hash_sha256,
        QtdLancamentos = :qtd_lancamentos,
        DataIngestao   = SYSUTCDATETIME()
WHEN NOT MATCHED THEN
    INSERT (IdConta, Periodo, NomeArquivo, HashSha256, QtdLancamentos)
    VALUES (:id_conta, :periodo, :nome_arquivo, :hash_sha256, :qtd_lancamentos)
OUTPUT inserted.IdArquivo;
"""

_SQL_DELETE_LANC = "DELETE FROM dbo.FRAPLancamento WHERE IdArquivo = :id_arquivo;"

_SQL_INSERT_LANC = """
INSERT INTO dbo.FRAPLancamento
    (IdArquivo, IdConta, Periodo, OrdemNoArquivo, DtMovimento, DtBalancete,
     AgOrigem, Lote, Historico, Documento, DocData, SeqBB, Valor, ValorDC, Descricao,
     IdCategoria, CpfCnpjDepositante, CpfCnpjAmbiguo)
VALUES
    (:id_arquivo, :id_conta, :periodo, :ordem_no_arquivo, :dt_movimento, :dt_balancete,
     :ag_origem, :lote, :historico, :documento, :doc_data, :seq_bb, :valor, :valor_dc, :descricao,
     :id_categoria, :cpfcnpj_depositante, :cpfcnpj_ambiguo);
"""


def publica_extrato(
    engine: Engine,
    df: pd.DataFrame,
    pasta_origem: Path | None = None,
    extensao: str = "txt",
) -> dict[tuple[str, str], int]:
    """Publica todo o DataFrame canônico no BdDIP, agrupando por (conta, periodo).

    Parâmetros
    ----------
    engine : SQLAlchemy Engine apontando para o BdDIP.
    df     : DataFrame canônico (saída de `frap.extratos.ingest.ingest_pasta`).
    pasta_origem : se informada, calcula `HashSha256` lendo `<pasta>/<conta>/<periodo>.txt`;
                   senão grava NULL no hash.

    Retorna mapa `{(conta, periodo): IdArquivo}` para auditoria/log.
    """
    df = df[df["valor"].notna() & df["valor_dc"].isin(["C", "D"])]

    resultado: dict[tuple[str, str], int] = {}

    with engine.begin() as conn:
        for (conta, periodo), grupo in df.groupby(["conta", "periodo"], sort=True):
            id_conta = get_id_conta(engine, str(conta))
            nome_arquivo = f"{periodo}.{extensao}"
            hash_sha = _hash_arquivo(pasta_origem, str(conta), str(periodo)) if pasta_origem else None

            id_arquivo = conn.execute(
                text(_SQL_UPSERT_ARQUIVO),
                {
                    "id_conta": id_conta,
                    "periodo": periodo,
                    "nome_arquivo": nome_arquivo,
                    "hash_sha256": hash_sha,
                    "qtd_lancamentos": int(len(grupo)),
                },
            ).scalar_one()

            conn.execute(text(_SQL_DELETE_LANC), {"id_arquivo": id_arquivo})

            linhas = [_to_lanc_param(row, id_arquivo, id_conta, engine) for _, row in grupo.iterrows()]
            if linhas:
                conn.execute(text(_SQL_INSERT_LANC), linhas)

            resultado[(str(conta), str(periodo))] = int(id_arquivo)

    return resultado


def _to_lanc_param(row: pd.Series, id_arquivo: int, id_conta: int, engine: Engine) -> dict:
    return {
        "id_arquivo": id_arquivo,
        "id_conta": id_conta,
        "periodo": str(row["periodo"]),
        "ordem_no_arquivo": int(row["ordem_no_arquivo"]),
        "dt_movimento": _date(row.get("dt_movimento")),
        "dt_balancete": _date(row.get("dt_balancete")),
        "ag_origem": _str_or_none(row.get("ag_origem")),
        "lote": _str_or_none(row.get("lote")),
        "historico": str(row["historico"]),
        "documento": _str_or_none(row.get("documento")),
        "doc_data": _date(row.get("doc_data")),
        "seq_bb": _str_or_none(row.get("seq_bb")),
        "valor": float(row["valor"]),
        "valor_dc": str(row["valor_dc"]),
        "descricao": _str_or_none(row.get("descricao")),
        "id_categoria": get_id_categoria(engine, str(row["categoria"])),
        "cpfcnpj_depositante": _str_or_none(row.get("cpfcnpj_depositante")),
        "cpfcnpj_ambiguo": bool(row.get("cpfcnpj_ambiguo", False)),
    }


def _date(v):
    if v is None or pd.isna(v):
        return None
    if isinstance(v, pd.Timestamp):
        return v.date()
    return v


def _str_or_none(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = str(v).strip()
    return s if s else None


def _hash_arquivo(pasta: Path, conta: str, periodo: str) -> str | None:
    caminho = pasta / conta / f"{periodo}.txt"
    if not caminho.exists():
        return None
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
