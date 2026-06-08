"""Recalcula FRAPMetricaPessoa a partir de FRAPDescontoFolha + processo.*.

A UDF `BdDIP.dbo.fn_Exe_RetornaValorAtualizado` é cara (~0,7s por CPF). Rodá-la
em batch via MERGE evita avaliar nas 280 pessoas durante o ORDER BY do
list_pessoas. `only_cpf` permite recalcular um único CPF após cadastro manual
ou após import de monitoramento.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from sqlalchemy import Engine, text


@dataclass
class ResultadoRecalc:
    qtd_pessoas_processadas: int
    tempo_segundos: float

    def resumo(self) -> str:
        return f"pessoas={self.qtd_pessoas_processadas} tempo={self.tempo_segundos:.1f}s"


_SQL_MERGE = """
WITH cpfs AS (
    SELECT DISTINCT CpfCnpj
    FROM dbo.FRAPDescontoFolha
    WHERE Ativo = 1 AND CpfCnpj IS NOT NULL
    {filtro_cpf}
),
m AS (
    SELECT
        c.CpfCnpj,
        ISNULL((
            SELECT SUM(BdDIP.dbo.fn_Exe_RetornaValorAtualizado(ed.IdDebito))
            FROM processo.dbo.Exe_Debito ed
            JOIN processo.dbo.Exe_DebitoPessoa edp ON edp.IDDebito = ed.IdDebito
            JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = edp.IDPessoa
            WHERE REPLACE(REPLACE(REPLACE(REPLACE(gp.Documento,'.',''),'-',''),'/',''),' ','')
                  COLLATE DATABASE_DEFAULT = c.CpfCnpj COLLATE DATABASE_DEFAULT
              AND ed.DataCancelamento IS NULL
              AND ed.CodigoStatusDivida NOT IN (2, 9)
              AND ed.CodigoTipoDebito <> 1
              AND ed.Concluido = 1
        ), 0) AS ValorAtualizadoTotal,
        (SELECT COUNT(DISTINCT n.IdProcesso)
          FROM dbo.FRAPNotificacaoDescontoFolha n
          WHERE EXISTS (
              SELECT 1 FROM processo.dbo.Exe_Debito ed
              JOIN processo.dbo.Exe_DebitoPessoa edp ON edp.IDDebito = ed.IdDebito
              JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = edp.IDPessoa
              WHERE ed.IdProcessoExecucao = n.IdProcesso
                AND REPLACE(REPLACE(REPLACE(REPLACE(gp.Documento,'.',''),'-',''),'/',''),' ','')
                    COLLATE DATABASE_DEFAULT = c.CpfCnpj COLLATE DATABASE_DEFAULT
                AND ed.CodigoTipoDebito <> 1
          )) AS QtdProcessosNotificados,
        (SELECT COUNT(DISTINCT ed.IdDebito)
          FROM processo.dbo.Exe_Debito ed
          JOIN processo.dbo.Exe_DebitoPessoa edp ON edp.IDDebito = ed.IdDebito
          JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = edp.IDPessoa
          WHERE REPLACE(REPLACE(REPLACE(REPLACE(gp.Documento,'.',''),'-',''),'/',''),' ','')
                COLLATE DATABASE_DEFAULT = c.CpfCnpj COLLATE DATABASE_DEFAULT
            AND ed.CodigoTipoDebito <> 1
            AND ed.IdProcessoExecucao IN (
                SELECT DISTINCT n2.IdProcesso FROM dbo.FRAPNotificacaoDescontoFolha n2
            )
          ) AS QtdDebitosNotificados,
        ISNULL((
            SELECT SUM(BdDIP.dbo.fn_Exe_RetornaValorAtualizado(ed.IdDebito))
            FROM processo.dbo.Exe_Debito ed
            JOIN processo.dbo.Exe_DebitoPessoa edp ON edp.IDDebito = ed.IdDebito
            JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = edp.IDPessoa
            WHERE REPLACE(REPLACE(REPLACE(REPLACE(gp.Documento,'.',''),'-',''),'/',''),' ','')
                  COLLATE DATABASE_DEFAULT = c.CpfCnpj COLLATE DATABASE_DEFAULT
              AND ed.DataCancelamento IS NULL
              AND ed.CodigoStatusDivida NOT IN (2, 9)
              AND ed.CodigoTipoDebito <> 1
              AND ed.Concluido = 1
              AND ed.IdProcessoExecucao IN (
                  SELECT DISTINCT n3.IdProcesso FROM dbo.FRAPNotificacaoDescontoFolha n3
              )
        ), 0) AS ValorDebitosNotificadosTotal,
        (SELECT COUNT(DISTINCT ed.IdDebito)
          FROM processo.dbo.Exe_Debito ed
          JOIN processo.dbo.Exe_DebitoPessoa edp ON edp.IDDebito = ed.IdDebito
          JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = edp.IDPessoa
          WHERE REPLACE(REPLACE(REPLACE(REPLACE(gp.Documento,'.',''),'-',''),'/',''),' ','')
                COLLATE DATABASE_DEFAULT = c.CpfCnpj COLLATE DATABASE_DEFAULT
            AND ed.DataCancelamento IS NULL
            AND ed.CodigoStatusDivida NOT IN (2, 9)
            AND ed.CodigoTipoDebito <> 1
            AND ed.Concluido = 1
          ) AS QtdDebitosTotais
    FROM cpfs c
)
MERGE dbo.FRAPMetricaPessoa AS tgt
USING m AS src ON tgt.CpfCnpj = src.CpfCnpj
WHEN MATCHED THEN UPDATE SET
    ValorAtualizadoTotal = src.ValorAtualizadoTotal,
    QtdProcessosNotificados = src.QtdProcessosNotificados,
    QtdDebitosNotificados = src.QtdDebitosNotificados,
    ValorDebitosNotificadosTotal = src.ValorDebitosNotificadosTotal,
    QtdDebitosTotais = src.QtdDebitosTotais,
    DataAtualizacao = SYSUTCDATETIME()
WHEN NOT MATCHED THEN
    INSERT (CpfCnpj, ValorAtualizadoTotal, QtdProcessosNotificados, QtdDebitosNotificados,
            ValorDebitosNotificadosTotal, QtdDebitosTotais)
    VALUES (src.CpfCnpj, src.ValorAtualizadoTotal, src.QtdProcessosNotificados,
            src.QtdDebitosNotificados, src.ValorDebitosNotificadosTotal,
            src.QtdDebitosTotais);
"""

_SQL_COUNT_CPFS = """
SELECT COUNT(DISTINCT CpfCnpj)
FROM dbo.FRAPDescontoFolha
WHERE Ativo = 1 AND CpfCnpj IS NOT NULL
{filtro_cpf}
"""


def recalcular_metricas_pessoa(
    engine: Engine,
    *,
    only_cpf: str | None = None,
    dry_run: bool = False,
) -> ResultadoRecalc:
    """Recalcula FRAPMetricaPessoa via MERGE batch.

    Args:
        engine: engine BdDIP.
        only_cpf: se informado, processa apenas esse CPF.
        dry_run: não executa o MERGE; só conta CPFs candidatos.
    """
    filtro = ""
    params: dict[str, str] = {}
    if only_cpf:
        filtro = "AND CpfCnpj = :cpf"
        params["cpf"] = only_cpf

    inicio = time.perf_counter()
    with engine.connect() as conn:
        qtd = int(
            conn.execute(text(_SQL_COUNT_CPFS.format(filtro_cpf=filtro)), params).scalar_one()
        )

    if dry_run:
        return ResultadoRecalc(
            qtd_pessoas_processadas=qtd,
            tempo_segundos=time.perf_counter() - inicio,
        )

    with engine.begin() as conn:
        conn.execute(text(_SQL_MERGE.format(filtro_cpf=filtro)), params)

    return ResultadoRecalc(
        qtd_pessoas_processadas=qtd,
        tempo_segundos=time.perf_counter() - inicio,
    )
