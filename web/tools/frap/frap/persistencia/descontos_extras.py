"""Popula FRAPDescontoFolha com origens extras (S = SIAI, C = CCD).

- Origem='S': pessoa tem rubrica TCE/FRAP descontada no contracheque
  (vwSiaiPessoalFolhaCompletaTodas). 1 cadastro por (cpf, id_orgao), 1 parcela
  por (competência, valor) distinto. Parcelas marcadas como SituacaoParcela='2'
  (paga) já que o desconto está consumado no contracheque.
- Origem='C': pessoa notificada via CCD (FRAPNotificacaoDescontoFolha) mas
  ainda não necessariamente implementada. 1 cadastro por CPF; sem parcelas.

Idempotência: identificação via (CpfCnpj, IdOrgaoNotificado, Origem). Para
Origem='C' o IdOrgaoNotificado é NULL e a chave passa a ser (CpfCnpj, Origem).

Três regras do Origem='S' que parecem detalhe e não são:

1. **Nada de DELETE.** A versão anterior apagava as parcelas do cadastro antes
   de reinserir. A FK FK_FRAPMatchDescontoFolha_Parcela é NO_ACTION, então isso
   passou a estourar assim que houve match (2.209 deles, 8 manuais). A inserção
   virou incremental por `NOT EXISTS` — o trabalho humano fica intocado por
   construção, não por cuidado.
2. **O grão é (cpf, órgão, ano, mês, valor), não a linha da view.** É o mesmo
   grão com que o matcher casa e deduplica o contracheque
   (`frap.matching.descontofolha`, merge em CPF+mês+ano+valor_cent). Agregar com
   SUM por competência geraria uma parcela que não bate com item nenhum, ou
   seja, NAO_DESCONTADA falso; e não deduplicar deixaria remessa retransmitida
   virar parcela que nunca casa.
3. **Valor diferente numa competência já gravada vira parcela nova, não
   UPDATE.** Folha complementar e 13º são um segundo evento de desconto, não
   correção do primeiro — e reescrever ValorEsperado invalidaria em silêncio um
   match já conciliado. Retificação real de valor (rara) cai na tipologia
   `parcela-duplicada`, que existe para isso.

`NumeroParcela` é NOT NULL e, para Origem='S', significa ordem de chegada, não
posição num plano de parcelamento: continua de MAX(NumeroParcela)+1 do cadastro
e nunca reescreve linha existente.
"""

from __future__ import annotations

from dataclasses import dataclass, field
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

# Predicado único de "rubrica é do TCE/FRAP". Alias obrigatório: `v`.
# Importado também por app/jobs/tasks.py (FRAPVerificacaoSiaiFolha) — as duas
# pontas têm que concordar sobre o que é uma rubrica nossa. O que NÃO se
# compartilha é o grão: lá a linha é agregada com SUM (uso analítico), aqui não
# pode ser (o matcher casa por valor exato).
FILTRO_RUBRICA_TCE = """
    v.vantagem_desconto = 'D'
    AND (v.nome_rubrica LIKE '%tce%' OR v.nome_rubrica LIKE '%frap%'
         OR v.nome_rubrica LIKE '%tribunal de contas%')
    AND v.nome_rubrica NOT LIKE '%VANT%'
"""

# CPF vem da view sem padding garantido; o matcher já faz zfill(11) dos dois
# lados (frap/matching/descontofolha.py). Padronizar aqui evita que um CPF sem
# zero à esquerda crie um cadastro paralelo.
_CPF11 = "RIGHT('00000000000' + LTRIM(RTRIM({col})), 11)"

# ano/mes na view são CHAR com padding -> TRY_CAST obrigatório; lixo vira NULL e
# cai fora. valor <= 0 é estorno: parcela negativa não existe no domínio.
_CTE_SIAI = f"""
WITH valida AS (
    SELECT {_CPF11.format(col="v.cpf")}              AS cpf,
           v.id_orgao                                AS id_orgao,
           TRY_CAST(LTRIM(RTRIM(v.ano)) AS INT)      AS ano,
           TRY_CAST(LTRIM(RTRIM(v.mes)) AS INT)      AS mes,
           CAST(v.valor_rubrica AS DECIMAL(18, 2))   AS valor,
           LTRIM(RTRIM(v.nome))                      AS nome,
           LTRIM(RTRIM(v.nome_orgao))                AS nome_orgao
    FROM BdDIP.dbo.vwSiaiPessoalFolhaCompletaTodas v
    WHERE {FILTRO_RUBRICA_TCE}
      AND v.id_orgao IS NOT NULL
      AND LTRIM(RTRIM(v.cpf)) <> ''
      AND v.valor_rubrica > 0
      AND TRY_CAST(LTRIM(RTRIM(v.ano)) AS INT) IS NOT NULL
      AND TRY_CAST(LTRIM(RTRIM(v.mes)) AS INT) BETWEEN 1 AND 12
),
grao AS (
    SELECT DISTINCT cpf, id_orgao, ano, mes, valor FROM valida
)
"""

# Um cadastro por (cpf, órgão). Sem UPDATE: o antigo só existia para reescrever
# Qtd/ValorTotal, que a etapa 3 refaz de qualquer jeito.
_SQL_INSERT_CADASTROS = f"""
{_CTE_SIAI}
INSERT INTO dbo.FRAPDescontoFolha
    (IdDescontoFolha, Origem, CpfCnpj, NomePessoa,
     IdOrgaoNotificado, NomeOrgaoNotificado,
     QtdParcelasPlanejadas, ValorTotalEsperado, Ativo, DataInclusao)
SELECT NULL, 'S', g.cpf, MAX(g.nome), g.id_orgao, MAX(g.nome_orgao),
       0, 0, 1, SYSUTCDATETIME()
FROM valida g
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.FRAPDescontoFolha df
     WHERE df.Origem = 'S'
       AND {_CPF11.format(col="df.CpfCnpj")} = g.cpf
       AND df.IdOrgaoNotificado = g.id_orgao
)
GROUP BY g.cpf, g.id_orgao;
"""

_SQL_INSERT_PARCELAS = f"""
{_CTE_SIAI},
alvo AS (
    SELECT df.IdFRAPDescontoFolha AS id_pai, g.ano, g.mes, g.valor,
           ROW_NUMBER() OVER (PARTITION BY df.IdFRAPDescontoFolha
                              ORDER BY g.ano, g.mes, g.valor) AS seq
    FROM grao g
    JOIN dbo.FRAPDescontoFolha df
      ON df.Origem = 'S'
     AND df.Ativo = 1
     AND {_CPF11.format(col="df.CpfCnpj")} = g.cpf
     AND df.IdOrgaoNotificado = g.id_orgao
    WHERE NOT EXISTS (
        SELECT 1 FROM dbo.FRAPDescontoFolhaParcela p
         WHERE p.IdFRAPDescontoFolha = df.IdFRAPDescontoFolha
           AND p.AnoReferencia = g.ano
           AND p.MesReferencia = g.mes
           AND p.ValorEsperado = g.valor
    )
),
base AS (
    SELECT a.id_pai,
           ISNULL((SELECT MAX(p.NumeroParcela)
                     FROM dbo.FRAPDescontoFolhaParcela p
                    WHERE p.IdFRAPDescontoFolha = a.id_pai), 0) AS ultimo
    FROM alvo a
    GROUP BY a.id_pai
)
INSERT INTO dbo.FRAPDescontoFolhaParcela
    (IdFRAPDescontoFolha, IdParcela, NumeroParcela, MesReferencia, AnoReferencia,
     ValorEsperado, DataVencimento, DataPagamentoParcela, SituacaoParcela, TipoDeBaixa)
SELECT a.id_pai, NULL, b.ultimo + a.seq, a.mes, a.ano, a.valor,
       DATEFROMPARTS(a.ano, a.mes, 1), DATEFROMPARTS(a.ano, a.mes, 15), '2', NULL
FROM alvo a
JOIN base b ON b.id_pai = a.id_pai;
"""

_SQL_RECALCULAR_CABECALHO = """
UPDATE df
   SET df.QtdParcelasPlanejadas = agg.Qtd,
       df.ValorTotalEsperado    = agg.Total,
       df.DataIngestao          = SYSUTCDATETIME()
FROM dbo.FRAPDescontoFolha df
CROSS APPLY (
    SELECT COUNT(*) AS Qtd, COALESCE(SUM(p.ValorEsperado), 0) AS Total
      FROM dbo.FRAPDescontoFolhaParcela p
     WHERE p.IdFRAPDescontoFolha = df.IdFRAPDescontoFolha
) agg
WHERE df.Origem = 'S';
"""

# Contagens do dry-run. O LEFT JOIN (em vez do JOIN de _SQL_INSERT_PARCELAS) faz
# as parcelas dos cadastros ainda inexistentes entrarem na conta.
_SQL_DRY_CADASTROS = f"""
{_CTE_SIAI}
SELECT COUNT(*) FROM (
    SELECT g.cpf, g.id_orgao
    FROM valida g
    WHERE NOT EXISTS (
        SELECT 1 FROM dbo.FRAPDescontoFolha df
         WHERE df.Origem = 'S'
           AND {_CPF11.format(col="df.CpfCnpj")} = g.cpf
           AND df.IdOrgaoNotificado = g.id_orgao
    )
    GROUP BY g.cpf, g.id_orgao
) x;
"""

_SQL_DRY_PARCELAS = f"""
{_CTE_SIAI}
SELECT COUNT(*)
FROM grao g
LEFT JOIN dbo.FRAPDescontoFolha df
       ON df.Origem = 'S'
      AND df.Ativo = 1
      AND {_CPF11.format(col="df.CpfCnpj")} = g.cpf
      AND df.IdOrgaoNotificado = g.id_orgao
WHERE df.IdFRAPDescontoFolha IS NULL
   OR NOT EXISTS (
        SELECT 1 FROM dbo.FRAPDescontoFolhaParcela p
         WHERE p.IdFRAPDescontoFolha = df.IdFRAPDescontoFolha
           AND p.AnoReferencia = g.ano
           AND p.MesReferencia = g.mes
           AND p.ValorEsperado = g.valor
   );
"""


def popular_descontos_siai(engine: Engine, *, dry_run: bool = False) -> ResultadoDescontosExtras:
    """Materializa FRAPDescontoFolha/Parcela Origem='S' a partir da view SIAI.

    Incremental e idempotente: pode rodar quantas vezes quiser, só insere o que
    falta. Uma segunda execução seguida tem que reportar parcelas_inseridas=0.
    """
    res = ResultadoDescontosExtras()

    if dry_run:
        with engine.connect() as conn:
            res.cadastros_criados = int(conn.execute(text(_SQL_DRY_CADASTROS)).scalar_one())
            res.parcelas_inseridas = int(conn.execute(text(_SQL_DRY_PARCELAS)).scalar_one())
        return res

    with engine.begin() as conn:
        res.cadastros_criados = int(conn.execute(text(_SQL_INSERT_CADASTROS)).rowcount or 0)
        res.parcelas_inseridas = int(conn.execute(text(_SQL_INSERT_PARCELAS)).rowcount or 0)
        res.cadastros_atualizados = int(conn.execute(text(_SQL_RECALCULAR_CABECALHO)).rowcount or 0)

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
