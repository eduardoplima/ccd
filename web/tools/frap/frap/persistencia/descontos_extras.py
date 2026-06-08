"""Popula FRAPDescontoFolha com origens extras (S = SIAI, C = CCD).

- Origem='S': pessoa tem rubrica TCE/FRAP descontada no contracheque
  (vwSiaiPessoalFolhaCompletaTodas). 1 cadastro por (cpf, id_orgao), 1 parcela
  por linha da view. Parcelas marcadas como SituacaoParcela='2' (paga) já que
  o desconto está consumado no contracheque.
- Origem='C': pessoa notificada via CCD (FRAPNotificacaoDescontoFolha) mas
  ainda não necessariamente implementada. 1 cadastro por CPF; sem parcelas.

Idempotência: identificação via (CpfCnpj, IdOrgaoNotificado, Origem). Para
Origem='C' o IdOrgaoNotificado é NULL e a chave passa a ser (CpfCnpj, Origem).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

import pandas as pd
from sqlalchemy import Engine, text


@dataclass
class ResultadoDescontosExtras:
    cadastros_criados: int = 0
    cadastros_atualizados: int = 0
    parcelas_inseridas: int = 0
    erros: list[dict[str, Any]] = field(default_factory=list)

    def resumo(self) -> str:
        return (
            f"cadastros_criados={self.cadastros_criados} "
            f"cadastros_atualizados={self.cadastros_atualizados} "
            f"parcelas_inseridas={self.parcelas_inseridas} "
            f"erros={len(self.erros)}"
        )


# ---------------------------------------------------------------------------
# Origem='S' — rubrica TCE/FRAP em contracheque (SIAI)
# ---------------------------------------------------------------------------

_SQL_SIAI = """
SELECT v.cpf, v.nome, v.id_orgao, v.nome_orgao,
       v.ano, v.mes, v.valor_rubrica,
       v.id_contracheque, v.codigo_rubrica, v.nome_rubrica
FROM BdDIP.dbo.vwSiaiPessoalFolhaCompletaTodas v
WHERE v.vantagem_desconto = 'D'
  AND (v.nome_rubrica LIKE '%tce%' OR v.nome_rubrica LIKE '%frap%')
  AND v.nome_rubrica NOT LIKE '%VANT%'
ORDER BY v.cpf, v.id_orgao, v.ano, v.mes
"""

_SQL_FIND_S = """
SELECT IdFRAPDescontoFolha
FROM dbo.FRAPDescontoFolha
WHERE Origem = 'S'
  AND CpfCnpj = :cpf
  AND IdOrgaoNotificado = :id_orgao
"""

_SQL_INSERT_S = """
INSERT INTO dbo.FRAPDescontoFolha
    (IdDescontoFolha, Origem, CpfCnpj, NomePessoa,
     IdOrgaoNotificado, NomeOrgaoNotificado,
     QtdParcelasPlanejadas, ValorTotalEsperado, Ativo, DataInclusao)
OUTPUT inserted.IdFRAPDescontoFolha
VALUES (NULL, 'S', :cpf, :nome, :id_orgao, :nome_orgao,
        :qtd, :valor_total, 1, SYSUTCDATETIME());
"""

_SQL_UPDATE_S = """
UPDATE dbo.FRAPDescontoFolha
SET NomePessoa = :nome,
    NomeOrgaoNotificado = :nome_orgao,
    QtdParcelasPlanejadas = :qtd,
    ValorTotalEsperado = :valor_total,
    Ativo = 1,
    DataIngestao = SYSUTCDATETIME()
WHERE IdFRAPDescontoFolha = :id_pai;
"""

_SQL_DELETE_PARCELAS_S = (
    "DELETE FROM dbo.FRAPDescontoFolhaParcela WHERE IdFRAPDescontoFolha = :id_pai;"
)

_SQL_INSERT_PARCELA_S = """
INSERT INTO dbo.FRAPDescontoFolhaParcela
    (IdFRAPDescontoFolha, IdParcela, NumeroParcela, MesReferencia, AnoReferencia,
     ValorEsperado, DataVencimento, DataPagamentoParcela, SituacaoParcela, TipoDeBaixa)
VALUES
    (:id_pai, NULL, :numero_parcela, :mes, :ano, :valor, :dt_venc, :dt_pgto, '2', NULL);
"""


def popular_descontos_siai(engine: Engine, *, dry_run: bool = False) -> ResultadoDescontosExtras:
    """Popula FRAPDescontoFolha Origem='S' a partir da view SIAI."""
    res = ResultadoDescontosExtras()
    with engine.connect() as conn:
        df = pd.read_sql(text(_SQL_SIAI), conn)
    if df.empty:
        return res

    df["cpf"] = df["cpf"].astype(str).str.strip()
    df["id_orgao"] = pd.to_numeric(df["id_orgao"], errors="coerce")
    df = df[df["cpf"].str.len() > 0]
    df = df[df["id_orgao"].notna()]
    df["id_orgao"] = df["id_orgao"].astype(int)
    df["ano"] = df["ano"].astype(int)
    df["mes"] = df["mes"].astype(int)

    if dry_run:
        grupos = df.groupby(["cpf", "id_orgao"])
        res.cadastros_criados = len(grupos)
        res.parcelas_inseridas = len(df)
        return res

    with engine.begin() as conn:
        for (cpf, id_orgao), grupo in df.groupby(["cpf", "id_orgao"], sort=True):
            grupo = grupo.sort_values(["ano", "mes"]).reset_index(drop=True)
            cabeca = grupo.iloc[0]
            valor_total = float(grupo["valor_rubrica"].fillna(0).sum())
            qtd_parcelas = int(len(grupo))

            existente = conn.execute(
                text(_SQL_FIND_S), {"cpf": cpf, "id_orgao": int(id_orgao)}
            ).scalar()

            params_cab = {
                "cpf": cpf,
                "nome": _str_or_none(cabeca["nome"]),
                "id_orgao": int(id_orgao),
                "nome_orgao": _str_or_none(cabeca["nome_orgao"]),
                "qtd": qtd_parcelas,
                "valor_total": valor_total,
            }
            if existente is not None:
                id_pai = int(existente)
                conn.execute(text(_SQL_UPDATE_S), {**params_cab, "id_pai": id_pai})
                res.cadastros_atualizados += 1
            else:
                id_pai = int(conn.execute(text(_SQL_INSERT_S), params_cab).scalar_one())
                res.cadastros_criados += 1

            conn.execute(text(_SQL_DELETE_PARCELAS_S), {"id_pai": id_pai})

            parcelas_params = []
            for idx, row in grupo.iterrows():
                ano = int(row["ano"])
                mes = int(row["mes"])
                valor = float(row["valor_rubrica"] or 0)
                parcelas_params.append(
                    {
                        "id_pai": id_pai,
                        "numero_parcela": int(idx) + 1,
                        "mes": mes,
                        "ano": ano,
                        "valor": valor,
                        "dt_venc": date(ano, mes, 1),
                        "dt_pgto": date(ano, mes, 15),
                    }
                )
            if parcelas_params:
                conn.execute(text(_SQL_INSERT_PARCELA_S), parcelas_params)
                res.parcelas_inseridas += len(parcelas_params)

    return res


# ---------------------------------------------------------------------------
# Origem='C' — notificação CCD para desconto em folha
# ---------------------------------------------------------------------------

_SQL_CCD = """
SELECT
    REPLACE(REPLACE(REPLACE(REPLACE(gp.Documento, '.', ''), '-', ''), '/', ''), ' ', '') AS cpfcnpj,
    MIN(gp.IdPessoa)               AS id_pessoa,
    MAX(LTRIM(RTRIM(gp.Nome)))     AS nome,
    MIN(n.IdProcesso)              AS id_processo,
    MIN(n.IdDebito)                AS id_debito,
    COUNT(DISTINCT n.IdProcesso)   AS qtd_processos,
    COUNT(DISTINCT n.IdDebito)     AS qtd_debitos,
    MIN(n.DataPublicacaoCCD)       AS data_primeira_notif
FROM dbo.FRAPNotificacaoDescontoFolha n
JOIN processo.dbo.Exe_DebitoPessoa dp
       ON dp.IDDebito = n.IdDebito
JOIN processo.dbo.GenPessoa gp
       ON gp.IdPessoa = dp.IDPessoa
WHERE n.IdDebito IS NOT NULL AND gp.TipoDocumento = '1'
GROUP BY REPLACE(REPLACE(REPLACE(REPLACE(gp.Documento, '.', ''), '-', ''), '/', ''), ' ', '')
"""

_SQL_FIND_C = """
SELECT IdFRAPDescontoFolha
FROM dbo.FRAPDescontoFolha
WHERE Origem = 'C' AND CpfCnpj = :cpf
"""

_SQL_INSERT_C = """
INSERT INTO dbo.FRAPDescontoFolha
    (IdDescontoFolha, Origem, CpfCnpj, NomePessoa,
     IdPessoa, IdProcesso, IdDebito,
     IdOrgaoNotificado, NomeOrgaoNotificado,
     QtdParcelasPlanejadas, ValorTotalEsperado, Ativo, DataInclusao)
OUTPUT inserted.IdFRAPDescontoFolha
VALUES (NULL, 'C', :cpf, :nome,
        :id_pessoa, :id_processo, :id_debito,
        NULL, NULL, NULL, NULL, 1, :data_inclusao);
"""

_SQL_UPDATE_C = """
UPDATE dbo.FRAPDescontoFolha
SET NomePessoa = :nome,
    IdPessoa = :id_pessoa,
    IdProcesso = :id_processo,
    IdDebito = :id_debito,
    Ativo = 1,
    DataIngestao = SYSUTCDATETIME()
WHERE IdFRAPDescontoFolha = :id_pai;
"""


def popular_descontos_ccd(engine: Engine, *, dry_run: bool = False) -> ResultadoDescontosExtras:
    """Popula FRAPDescontoFolha Origem='C' a partir de FRAPNotificacaoDescontoFolha."""
    res = ResultadoDescontosExtras()
    with engine.connect() as conn:
        df = pd.read_sql(text(_SQL_CCD), conn)
    if df.empty:
        return res

    df["cpfcnpj"] = df["cpfcnpj"].astype(str).str.strip()
    df = df[df["cpfcnpj"].str.len() > 0]

    if dry_run:
        res.cadastros_criados = int(len(df))
        return res

    with engine.begin() as conn:
        for _, row in df.iterrows():
            cpf = row["cpfcnpj"]
            existente = conn.execute(text(_SQL_FIND_C), {"cpf": cpf}).scalar()
            params = {
                "cpf": cpf,
                "nome": _str_or_none(row["nome"]),
                "id_pessoa": _int_or_none(row["id_pessoa"]),
                "id_processo": _int_or_none(row["id_processo"]),
                "id_debito": _int_or_none(row["id_debito"]),
            }
            if existente is not None:
                conn.execute(text(_SQL_UPDATE_C), {**params, "id_pai": int(existente)})
                res.cadastros_atualizados += 1
            else:
                data_inc = row.get("data_primeira_notif")
                if isinstance(data_inc, pd.Timestamp):
                    data_inc = data_inc.to_pydatetime()
                conn.execute(
                    text(_SQL_INSERT_C),
                    {**params, "data_inclusao": data_inc},
                )
                res.cadastros_criados += 1

    return res


# ---------------------------------------------------------------------------


def _int_or_none(v):
    if v is None or pd.isna(v):
        return None
    return int(v)


def _str_or_none(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = str(v).strip()
    return s if s else None
