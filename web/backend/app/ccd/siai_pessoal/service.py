"""Leitura do SIAI Pessoal (BDSiaiPessoal, por nome de três partes a partir da sessão do BdDIP).

Tabelas-base, não a view vwSiaiPessoalFolhaCompletaTodas (UNION DISTINCT de dezenas de
joins: 15–35 s por CPF). Competência da FOLHA (F.Ano/F.Mes), nunca do item — a ALRN congela
a do item. Ano/mês são CHAR com padding.

Dedupe: a mesma folha é reenviada em remessas retificadoras (situação 4 = processado,
7 = processado retificado) e pode ter contracheque duplicado dentro da última remessa. Vale
uma folha por (ano, mês, órgão, tipo de folha): a da última remessa, último contracheque.
"""

from __future__ import annotations

import re
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ccd.siai_pessoal import schemas

# Um contracheque por (ano, mês, órgão, tipo de folha), com rn = 1 na última remessa.
_CTE_CONTRACHEQUES = """
WITH cc AS (
    SELECT CC.IdContraCheque, F.IdTipoFolhaPagamento, ER.IdOrgao,
           TRY_CAST(LTRIM(RTRIM(F.Ano)) AS INT) AS ano,
           TRY_CAST(LTRIM(RTRIM(F.Mes)) AS INT) AS mes,
           FU.Matricula, FU.NomeCargo, FU.Lotacao, P.Nome,
           CC.TotalVantagens, CC.TotalDescontos,
           ROW_NUMBER() OVER (
               PARTITION BY TRY_CAST(LTRIM(RTRIM(F.Ano)) AS INT),
                            TRY_CAST(LTRIM(RTRIM(F.Mes)) AS INT),
                            ER.IdOrgao, F.IdTipoFolhaPagamento
               ORDER BY ER.IdEnvioRemessa DESC, CC.IdContraCheque DESC) AS rn,
           COUNT(*) OVER (
               PARTITION BY TRY_CAST(LTRIM(RTRIM(F.Ano)) AS INT),
                            TRY_CAST(LTRIM(RTRIM(F.Mes)) AS INT),
                            ER.IdOrgao, F.IdTipoFolhaPagamento) AS remessas
    FROM BDSiaiPessoal.dbo.Comum_Pessoa P
    JOIN BDSiaiPessoal.dbo.SiaiDp_Funcionario FU ON FU.IdPessoa = P.IdPessoa
    JOIN BDSiaiPessoal.dbo.SiaiDp_ContraCheque CC ON CC.IdFuncionario = FU.IdFuncionario
    JOIN BDSiaiPessoal.dbo.SiaiDp_FolhaPagamento F ON F.IdFolhaPagamento = CC.IdFolhaPagamento
    JOIN BDSiaiPessoal.dbo.SiaiDp_RemessaFolhaPagamento RFP
      ON RFP.IdRemessaFolhaPagamento = F.IdRemessaFolhaPagamento
    JOIN BDSiaiPessoal.dbo.Envio_Remessa ER ON ER.IdEnvioRemessa = RFP.IdEnvioRemessa
    WHERE P.CPF = :cpf
      AND ER.IdTipoEnvioRemessa = 1
      AND ER.IdSituacaoRemessa IN (4, 7)
      AND ER.IdEnvioRemessaVinculada IS NOT NULL
      AND TRY_CAST(LTRIM(RTRIM(F.Ano)) AS INT) >= :ano_min
)
"""
# O período no CTE é só a faixa de ano: igualdade em ano/mês dentro do CTE leva o
# otimizador a um plano de ~11 s; filtrando o mês fora, 2,4 s.

# A rubrica é filtrada em Python: o LIKE no SQL leva o otimizador a um plano de ~10 s;
# agrupado por rubrica são poucas linhas por CPF (0,2–1,4 s).
_SQL_TCE_POR_COMPETENCIA = (
    _CTE_CONTRACHEQUES
    + """
SELECT cc.ano, cc.mes, R.Tipo AS tipo, UPPER(LTRIM(RTRIM(R.Descricao))) AS rubrica,
       SUM(CAST(CCI.Valor AS DECIMAL(18, 2))) AS valor
FROM cc
JOIN BDSiaiPessoal.dbo.SiaiDp_ContraChequeItem CCI ON CCI.IdContraCheque = cc.IdContraCheque
JOIN BDSiaiPessoal.dbo.SiaiDp_Rubrica R ON R.IdRubrica = CCI.IdRubrica
WHERE cc.rn = 1
GROUP BY cc.ano, cc.mes, R.Tipo, UPPER(LTRIM(RTRIM(R.Descricao)))
"""
)

_SQL_CONTRACHEQUE = (
    _CTE_CONTRACHEQUES
    + """
SELECT cc.IdContraCheque, cc.IdOrgao, O.NomeOrgao, TF.NomeTipoFolhaPagamento AS tipo_folha,
       cc.Matricula, cc.NomeCargo, cc.Lotacao, cc.Nome, cc.TotalVantagens, cc.TotalDescontos,
       cc.remessas, R.Codigo AS codigo, R.Descricao AS descricao, R.Tipo AS tipo,
       CCI.Valor AS valor
FROM cc
JOIN BDSiaiPessoal.dbo.SiaiDp_TipoFolhaPagamento TF
  ON TF.IdTipoFolhaPagamento = cc.IdTipoFolhaPagamento
LEFT JOIN Bdc.dbo.vw_Gen_Orgao O ON O.IdOrgao = cc.IdOrgao
JOIN BDSiaiPessoal.dbo.SiaiDp_ContraChequeItem CCI ON CCI.IdContraCheque = cc.IdContraCheque
JOIN BDSiaiPessoal.dbo.SiaiDp_Rubrica R ON R.IdRubrica = CCI.IdRubrica
WHERE cc.rn = 1 AND cc.ano = :ano AND cc.mes = :mes
ORDER BY cc.IdOrgao, cc.IdTipoFolhaPagamento, R.Tipo, R.Codigo
"""
)


def normalizar_cpf(cpf: str) -> str:
    return cpf.strip()[-11:].zfill(11)


def _mssql(session: Session) -> bool:
    dialect = session.bind.dialect.name if session.bind is not None else "mssql"
    return dialect != "sqlite"  # testes: o BDSiaiPessoal não existe


def _texto(v: Any) -> str | None:
    return (str(v).strip() or None) if v is not None else None


def _variantes_processo(processo: str | None) -> tuple[str, ...]:
    """'000627/2026' -> ('000627/2026', '627/2026'): o órgão grava o número como quiser."""
    if not processo or "/" not in processo:
        return ()
    numero, ano = processo.split("/", 1)
    numero, ano = numero.strip(), ano.strip()
    return tuple({f"{numero}/{ano}", f"{numero.lstrip('0') or '0'}/{ano}"})


def rubrica_tce(tipo: Any, nome: Any, processo: str | None = None) -> bool:
    """Desconto (Tipo 2) TCE/FRAP: nome com TCE/FRAP/Tribunal de Contas (predicado de
    tools/frap, descontos_extras.FILTRO_RUBRICA_TCE, sem a variante 'VANT'), a sigla TC
    isolada ("DESC. PROCESSO Nº 000627/2026-TC") ou o número do processo, quando dado."""
    n = str(nome or "").upper()
    if str(tipo or "").strip() != "2" or "VANT" in n:
        return False
    return (
        any(k in n for k in ("TCE", "FRAP", "TRIBUNAL DE CONTAS"))
        or re.search(r"\bTC\b", n) is not None
        or any(v in n for v in _variantes_processo(processo))
    )


def valores_tce_por_competencia(
    session: Session, cpf: str, ano_min: int, processo: str | None = None
) -> dict[tuple[int, int], float]:
    """Desconto TCE/FRAP por (ano, mês) da folha, para o CPF.

    ponytail: soma todos os órgãos do CPF na competência; quebrar por órgão se um CPF
    aparecer descontado em dois órgãos no mesmo mês.
    """
    if not _mssql(session):
        return {}
    rows = session.execute(
        text(_SQL_TCE_POR_COMPETENCIA), {"cpf": normalizar_cpf(cpf), "ano_min": ano_min}
    ).all()
    out: dict[tuple[int, int], float] = {}
    for r in rows:
        if r.ano is None or r.mes is None or r.valor is None:
            continue
        if not rubrica_tce(r.tipo, r.rubrica, processo):
            continue
        chave = (int(r.ano), int(r.mes))
        out[chave] = out.get(chave, 0.0) + float(r.valor)
    return out


_SQL_RETENCOES = (
    _CTE_CONTRACHEQUES
    + """
SELECT cc.ano, cc.mes, cc.IdOrgao AS id_orgao, O.NomeOrgao AS orgao,
       R.Codigo AS codigo, R.Descricao AS descricao, R.Tipo AS tipo,
       SUM(CAST(CCI.Valor AS DECIMAL(18, 2))) AS valor
FROM cc
LEFT JOIN Bdc.dbo.vw_Gen_Orgao O ON O.IdOrgao = cc.IdOrgao
JOIN BDSiaiPessoal.dbo.SiaiDp_ContraChequeItem CCI ON CCI.IdContraCheque = cc.IdContraCheque
JOIN BDSiaiPessoal.dbo.SiaiDp_Rubrica R ON R.IdRubrica = CCI.IdRubrica
WHERE cc.rn = 1 AND R.Tipo = '2'
GROUP BY cc.ano, cc.mes, cc.IdOrgao, O.NomeOrgao, R.Codigo, R.Descricao, R.Tipo
"""
)


def retencoes_detalhadas(
    session: Session, cpf: str, processos: list[str] | None = None
) -> list[dict[str, Any]]:
    """Rubricas TCE/FRAP retidas por (ano, mês, órgão, rubrica), todas as competências.

    `processos` = números dos processos da pessoa: a rubrica pode citar o número
    ("DESC. PROCESSO Nº 000627/2026-TC") em vez de TCE/FRAP.
    """
    if not _mssql(session):
        return []
    rows = session.execute(
        text(_SQL_RETENCOES), {"cpf": normalizar_cpf(cpf), "ano_min": 2000}
    ).mappings()
    out = []
    for r in rows:
        if r["ano"] is None or r["mes"] is None or r["valor"] is None:
            continue
        if not any(rubrica_tce(r["tipo"], r["descricao"], p) for p in (processos or [None])):
            continue
        out.append(
            {
                "ano": int(r["ano"]),
                "mes": int(r["mes"]),
                "id_orgao": r["id_orgao"],
                "orgao": _texto(r["orgao"]),
                "codigo": _texto(r["codigo"]),
                "rubrica": _texto(r["descricao"]) or "",
                "valor": float(r["valor"]),
            }
        )
    out.sort(key=lambda x: (-x["ano"], -x["mes"], x["orgao"] or "", x["codigo"] or ""))
    return out


def contracheque(
    session: Session, cpf: str, ano: int, mes: int, processo: str | None = None
) -> schemas.ContrachequeMes:
    """Folhas do CPF na competência: uma por (órgão, tipo de folha), com todos os itens.

    ponytail: só um mês por chamada; lista de meses disponíveis quando alguém pedir.
    """
    cpf = normalizar_cpf(cpf)
    out = schemas.ContrachequeMes(cpf=cpf, ano=ano, mes=mes)
    if not _mssql(session):
        return out
    rows = (
        session.execute(
            text(_SQL_CONTRACHEQUE), {"cpf": cpf, "ano_min": ano, "ano": ano, "mes": mes}
        )
        .mappings()
        .all()
    )
    folhas: dict[int, schemas.FolhaContrachequeOut] = {}
    for r in rows:
        out.nome = out.nome or _texto(r["Nome"])
        f = folhas.get(int(r["IdContraCheque"]))
        if f is None:
            f = schemas.FolhaContrachequeOut(
                id_contracheque=int(r["IdContraCheque"]),
                tipo_folha=_texto(r["tipo_folha"]) or "",
                id_orgao=r["IdOrgao"],
                orgao=_texto(r["NomeOrgao"]),
                matricula=_texto(r["Matricula"]),
                cargo=_texto(r["NomeCargo"]),
                lotacao=_texto(r["Lotacao"]),
                total_vantagens=(
                    float(r["TotalVantagens"]) if r["TotalVantagens"] is not None else None
                ),
                total_descontos=(
                    float(r["TotalDescontos"]) if r["TotalDescontos"] is not None else None
                ),
                remessas=int(r["remessas"]),
            )
            folhas[f.id_contracheque] = f
        tipo = str(r["tipo"] or "").strip()
        f.itens.append(
            schemas.ItemContrachequeOut(
                codigo=_texto(r["codigo"]),
                descricao=_texto(r["descricao"]) or "",
                tipo="D" if tipo == "2" else "V",
                valor=float(r["valor"] or 0),
                tce=rubrica_tce(tipo, r["descricao"], processo),
            )
        )
    out.folhas = list(folhas.values())
    return out
