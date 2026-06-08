"""Queries em BdSIAIPessoal — itens de contracheque marcados como desconto TCE/FRAP.

A rubrica não tem ID fixo: cada órgão/folha cadastra a sua. Identificamos por
descrição (`SiaiDp_Rubrica.Descricao` contendo "TCE", "TRIBUNAL DE CONTAS" ou
"FRAP") combinada com `Tipo='2'` (Desconto). Mes/Ano em SIAIPessoal são CHAR
com padding — sempre normalizar para int antes de comparar.

Caminho de join:
  SiaiDp_ContraChequeItem  ─→ SiaiDp_ContraCheque         (IdContraCheque)
                           ─→ SiaiDp_FolhaPagamento       (IdFolhaPagamento)
                           ─→ SiaiDp_Funcionario          (IdFuncionario)
                           ─→ Comum_Pessoa                (IdPessoa → CPF, Nome)
                           ─→ SiaiDp_Rubrica              (IdRubrica → Descricao)
"""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd
from sqlalchemy import Engine, bindparam, text

_SQL_CONTRACHEQUE_DESCONTOS_TCE = """
SELECT
    CCI.IdContraChequeItem,
    CCI.IdContraCheque,
    CCI.IdRubrica,
    R.Codigo                             AS RubricaCodigo,
    LTRIM(RTRIM(R.Descricao))            AS RubricaDescricao,
    CAST(LTRIM(RTRIM(CCI.MesReferencia)) AS INT)   AS MesReferencia,
    CAST(LTRIM(RTRIM(CCI.AnoReferencia)) AS INT)   AS AnoReferencia,
    CCI.Valor,
    F.IdFolhaPagamento,
    CAST(LTRIM(RTRIM(F.Mes)) AS INT)     AS MesFolha,
    CAST(LTRIM(RTRIM(F.Ano)) AS INT)     AS AnoFolha,
    CC.IdFuncionario,
    P.IdPessoa,
    P.CPF,
    LTRIM(RTRIM(P.Nome))                 AS NomePessoa
FROM dbo.SiaiDp_ContraChequeItem CCI
JOIN dbo.SiaiDp_Rubrica          R   ON R.IdRubrica       = CCI.IdRubrica
JOIN dbo.SiaiDp_ContraCheque     CC  ON CC.IdContraCheque = CCI.IdContraCheque
JOIN dbo.SiaiDp_FolhaPagamento   F   ON F.IdFolhaPagamento = CC.IdFolhaPagamento
LEFT JOIN dbo.SiaiDp_Funcionario FU  ON FU.IdFuncionario  = CC.IdFuncionario
LEFT JOIN dbo.Comum_Pessoa       P   ON P.IdPessoa        = FU.IdPessoa
WHERE
    R.Tipo = '2'
    AND (UPPER(R.Descricao) LIKE '%TCE%'
         OR UPPER(R.Descricao) LIKE '%TRIBUNAL DE CONTAS%'
         OR UPPER(R.Descricao) LIKE '%FRAP%')
    AND CAST(LTRIM(RTRIM(CCI.AnoReferencia)) AS INT) = :ano
    AND CAST(LTRIM(RTRIM(CCI.MesReferencia)) AS INT) = :mes
    AND P.CPF IN :cpfs
"""


def contracheque_descontos_tce(
    engine: Engine,
    cpfs: Iterable[str],
    mes: int,
    ano: int,
) -> pd.DataFrame:
    """Itens de contracheque marcados como desconto TCE/FRAP no mês/ano para a lista de CPFs.

    `cpfs` deve ser iterável de strings só-dígitos (CPF normalizado, 11 dígitos).
    Retorna DataFrame vazio se a lista for vazia.
    """
    docs = tuple({c for c in cpfs if c})
    if not docs:
        return pd.DataFrame()

    stmt = text(_SQL_CONTRACHEQUE_DESCONTOS_TCE).bindparams(bindparam("cpfs", expanding=True))
    with engine.connect() as conn:
        return pd.read_sql(
            stmt,
            conn,
            params={"cpfs": docs, "mes": mes, "ano": ano},
        )


# Órgão pagador da folha onde o desconto TCE foi processado.
# Caminho: SiaiDp_FolhaPagamento.IdRemessa -> Envio_Remessa.IdEnvioRemessa
#                                          -> Envio_Remessa.IdOrgao
#         -> Bdc.dbo.vw_Gen_Orgao (cross-database; requer permissão no Bdc).
_SQL_ORGAO_POR_PESSOA_MES = """
SELECT DISTINCT
    P.CPF,
    CAST(LTRIM(RTRIM(CCI.MesReferencia)) AS INT)   AS MesReferencia,
    CAST(LTRIM(RTRIM(CCI.AnoReferencia)) AS INT)   AS AnoReferencia,
    org.IdOrgao,
    LTRIM(RTRIM(org.NomeOrgao))                    AS NomeOrgao
FROM dbo.SiaiDp_ContraChequeItem CCI
JOIN dbo.SiaiDp_Rubrica          R   ON R.IdRubrica       = CCI.IdRubrica
JOIN dbo.SiaiDp_ContraCheque     CC  ON CC.IdContraCheque = CCI.IdContraCheque
JOIN dbo.SiaiDp_FolhaPagamento   F   ON F.IdFolhaPagamento = CC.IdFolhaPagamento
JOIN dbo.Envio_Remessa           ER  ON ER.IdEnvioRemessa  = F.IdRemessa
JOIN Bdc.dbo.vw_Gen_Orgao        org ON org.IdOrgao        = ER.IdOrgao
LEFT JOIN dbo.SiaiDp_Funcionario FU  ON FU.IdFuncionario  = CC.IdFuncionario
LEFT JOIN dbo.Comum_Pessoa       P   ON P.IdPessoa        = FU.IdPessoa
WHERE
    R.Tipo = '2'
    AND (UPPER(R.Descricao) LIKE '%TCE%'
         OR UPPER(R.Descricao) LIKE '%TRIBUNAL DE CONTAS%'
         OR UPPER(R.Descricao) LIKE '%FRAP%')
    AND CAST(LTRIM(RTRIM(CCI.AnoReferencia)) AS INT) = :ano
    AND CAST(LTRIM(RTRIM(CCI.MesReferencia)) AS INT) = :mes
    AND P.CPF IN :cpfs
"""


# Hierarquia de órgãos via Bdc.dbo.vw_Gen_Orgao (cross-DB).
_SQL_ORGAO_SUPERIOR = """
SELECT IdOrgao, IdOrgaoSuperior
FROM Bdc.dbo.vw_Gen_Orgao
WHERE IdOrgao IN :ids
"""


def orgao_superior_por_id(engine: Engine, ids_orgao: Iterable[int]) -> dict[int, int | None]:
    """Resolve `IdOrgao -> IdOrgaoSuperior` em batch via `Bdc.dbo.vw_Gen_Orgao`.

    Engine deve apontar para um banco que enxerga `Bdc` (BdDIP ou BdSIAIPessoal).
    Retorna dict; `IdOrgao` ausente significa que o órgão não foi achado.
    """
    ids = tuple({int(i) for i in ids_orgao if i is not None})
    if not ids:
        return {}
    stmt = text(_SQL_ORGAO_SUPERIOR).bindparams(bindparam("ids", expanding=True))
    with engine.connect() as conn:
        rows = conn.execute(stmt, {"ids": ids}).fetchall()
    return {int(r[0]): (int(r[1]) if r[1] is not None else None) for r in rows}


def orgao_pagador_por_funcionario(
    engine: Engine,
    cpfs: Iterable[str],
    mes: int,
    ano: int,
) -> pd.DataFrame:
    """Órgão pagador onde o desconto TCE/FRAP da pessoa foi processado no mês/ano.

    Resolve via folha de pagamento → remessa → órgão (cross-database para `Bdc`).
    Retorna DataFrame com colunas: CPF, MesReferencia, AnoReferencia, IdOrgao, NomeOrgao.
    Uma pessoa pode aparecer em mais de um órgão no mesmo mês (acumulação de cargos).
    """
    docs = tuple({c for c in cpfs if c})
    if not docs:
        return pd.DataFrame(
            columns=["CPF", "MesReferencia", "AnoReferencia", "IdOrgao", "NomeOrgao"]
        )

    stmt = text(_SQL_ORGAO_POR_PESSOA_MES).bindparams(bindparam("cpfs", expanding=True))
    with engine.connect() as conn:
        return pd.read_sql(
            stmt,
            conn,
            params={"cpfs": docs, "mes": mes, "ano": ano},
        )


_SQL_DESCONTOS_FRAP_TCE_AGREGADO = """
-- O BdSIAIPessoal pode ter mais de uma `SiaiDp_FolhaPagamento` Normal para a mesma
-- (CPF, mês, ano, órgão, rubrica) quando o órgão reenvia a remessa (correção/
-- retransmissão). Cada reenvio gera novo IdFuncionario e novo item de contracheque
-- com o MESMO valor — somar tudo inflaria o total. A CTE mantém apenas o item
-- da folha mais recente por (CPF, ano, mês, IdOrgao, IdRubrica).
WITH itens AS (
    SELECT
        CCI.Valor,
        CAST(LTRIM(RTRIM(CCI.AnoReferencia)) AS INT) AS AnoReferencia,
        CAST(LTRIM(RTRIM(CCI.MesReferencia)) AS INT) AS MesReferencia,
        org.IdOrgao,
        LTRIM(RTRIM(org.NomeOrgao))                  AS NomeOrgao,
        R.IdRubrica,
        P.CPF,
        ROW_NUMBER() OVER (
            PARTITION BY
                P.CPF,
                CAST(LTRIM(RTRIM(CCI.AnoReferencia)) AS INT),
                CAST(LTRIM(RTRIM(CCI.MesReferencia)) AS INT),
                org.IdOrgao,
                R.IdRubrica
            ORDER BY F.IdFolhaPagamento DESC
        ) AS rn
    FROM dbo.SiaiDp_ContraChequeItem CCI
    JOIN dbo.SiaiDp_Rubrica          R   ON R.IdRubrica       = CCI.IdRubrica
    JOIN dbo.SiaiDp_ContraCheque     CC  ON CC.IdContraCheque = CCI.IdContraCheque
    JOIN dbo.SiaiDp_FolhaPagamento   F   ON F.IdFolhaPagamento = CC.IdFolhaPagamento
    JOIN dbo.Envio_Remessa           ER  ON ER.IdEnvioRemessa  = F.IdRemessa
    JOIN Bdc.dbo.vw_Gen_Orgao        org ON org.IdOrgao        = ER.IdOrgao
    LEFT JOIN dbo.SiaiDp_Funcionario FU  ON FU.IdFuncionario  = CC.IdFuncionario
    LEFT JOIN dbo.Comum_Pessoa       P   ON P.IdPessoa        = FU.IdPessoa
    WHERE
        R.Tipo = '2'
        AND (UPPER(R.Descricao) LIKE '%TCE%'
             OR UPPER(R.Descricao) LIKE '%TRIBUNAL DE CONTAS%'
             OR UPPER(R.Descricao) LIKE '%FRAP%')
        AND CAST(LTRIM(RTRIM(CCI.AnoReferencia)) AS INT) IN :anos
)
SELECT
    AnoReferencia,
    MesReferencia,
    IdOrgao,
    NomeOrgao,
    COUNT(*)              AS NumeroItens,
    COUNT(DISTINCT CPF)   AS NumeroPessoas,
    SUM(Valor)            AS TotalDescontos
FROM itens
WHERE rn = 1
GROUP BY AnoReferencia, MesReferencia, IdOrgao, NomeOrgao
ORDER BY AnoReferencia, MesReferencia, NomeOrgao
"""


def descontos_frap_tce_agregado_por_orgao_mes(
    engine: Engine, anos: Iterable[int]
) -> pd.DataFrame:
    """Soma os descontos FRAP/TCE por (ano, mês, órgão pagador) para os anos pedidos.

    Sem filtro de CPF — varre toda a folha. Engine deve enxergar `Bdc` cross-DB
    (BdSIAIPessoal em prod).
    """
    ano_list = tuple({int(a) for a in anos})
    if not ano_list:
        return pd.DataFrame(
            columns=["AnoReferencia", "MesReferencia", "IdOrgao", "NomeOrgao",
                     "NumeroItens", "NumeroPessoas", "TotalDescontos"]
        )
    stmt = text(_SQL_DESCONTOS_FRAP_TCE_AGREGADO).bindparams(
        bindparam("anos", expanding=True)
    )
    with engine.connect() as conn:
        return pd.read_sql(stmt, conn, params={"anos": ano_list})
