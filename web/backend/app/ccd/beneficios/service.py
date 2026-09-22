"""Leitura do staging CCDBeneficio (migração 0020).

Somente leitura: a tabela é populada pelo job de detecção (tasks.py) e a tela
lista/exporta. As colunas Status/DataEnvio/LoteEnvio do antigo ciclo de
validação continuam no banco (default 'RASCUNHO'), mas não são mais lidas.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.ccd.beneficios.schemas import (
    BeneficioItem,
    BeneficioListResponse,
    BeneficioResumo,
    MesSerie,
)

# campo Pydantic (snake_case) -> coluna SQL. Fonte única do SELECT.
CAMPOS: dict[str, str] = {
    "descricao": "DescricaoPropostaBeneficio",
    "memoria_calculo": "MemoriaCalculoPropostaBeneficio",
    "valor_quantidade": "ValorQuantidade",
    "justificativa": "JustificativaPropostaBeneficio",
    "id_situacao_efetivacao": "IdBeneficioSituacaoEfetivacao",
    "id_area_tematica": "IdAreaTematica",
    "id_caracterizacao": "IdCaracterizacaoBeneficio",
    "id_unidade_medida": "IdUnidadeDeMedida",
    "id_situacao": "IdBeneficioSituacao",
    "id_tipo": "IdTipoBeneficio",
    "id_subtipo": "IdSubTipoBeneficio",
    "numero_processo_decisao": "NumeroProcessoDecisao",
    "ano_processo_decisao": "AnoProcessoDecisao",
    "id_processo_decisao": "IdProcessoDecisao",
    "descricao_motivo": "DescricaoMotivo",
    "id_beneficio_potencial": "IdCCDBeneficioPotencial",
    "cpfcnpj": "CpfCnpj",
    "nome_pessoa": "NomePessoa",
    "data_ocorrencia": "DataOcorrencia",
}

_META_COLS = "IdCCDBeneficio, Origem, ChaveOrigem, IdDebitoExecucao, DataInclusao, DataAtualizacao"
_SELECT_COLS = _META_COLS + ", " + ", ".join(CAMPOS.values())

_SORT_COLS = {
    "processo": "NumeroProcessoDecisao",
    "nome": "NomePessoa",
    "valor": "ValorQuantidade",
    "dataOcorrencia": "DataOcorrencia",
    "origem": "Origem",
    "dataInclusao": "DataInclusao",
}


def _to_item(r: Any) -> BeneficioItem:
    dados = {campo: r[coluna] for campo, coluna in CAMPOS.items()}
    return BeneficioItem(
        id_beneficio=int(r["IdCCDBeneficio"]),
        origem=r["Origem"],
        chave_origem=r["ChaveOrigem"],
        id_debito_execucao=r["IdDebitoExecucao"],
        data_inclusao=r["DataInclusao"],
        data_atualizacao=r["DataAtualizacao"],
        **dados,
    )


def filtro_periodo(
    where: list[str],
    params: dict[str, Any],
    data_de: date | None,
    data_ate: date | None,
    alias: str = "b.",
) -> None:
    """Acrescenta a `where`/`params` o recorte por data do fato gerador.
    PROPOSTA não tem DataOcorrencia — cai na data de inclusão no staging."""
    # ponytail: COALESCE não é sargável; ok p/ ~21k linhas. Coluna computada + índice se crescer.
    ref = f"COALESCE({alias}DataOcorrencia, CAST({alias}DataInclusao AS DATE))"
    if data_de:
        where.append(f"{ref} >= :data_de")
        params["data_de"] = data_de
    if data_ate:
        where.append(f"{ref} <= :data_ate")
        params["data_ate"] = data_ate


def _where_lista(
    q: str | None,
    origem: str | None,
    data_de: date | None,
    data_ate: date | None,
    alias: str = "b.",
) -> tuple[str, dict[str, Any]]:
    """WHERE comum a lista, resumo e export — o mesmo recorte em todos."""
    where = [f"{alias}Ativo = 1"]
    params: dict[str, Any] = {}
    if q:
        where.append(
            f"(CONCAT({alias}NumeroProcessoDecisao, '/', {alias}AnoProcessoDecisao) LIKE :q "
            f"OR {alias}NomePessoa LIKE :q OR {alias}CpfCnpj LIKE :q "
            f"OR {alias}DescricaoPropostaBeneficio LIKE :q)"
        )
        params["q"] = f"%{q}%"
    if origem:
        where.append(f"{alias}Origem = :origem")
        params["origem"] = origem
    filtro_periodo(where, params, data_de, data_ate, alias=alias)
    return "WHERE " + " AND ".join(where), params


def listar(
    session: Session,
    *,
    q: str | None = None,
    origem: str | None = None,
    data_de: date | None = None,
    data_ate: date | None = None,
    page: int = 1,
    size: int = 50,
    sort_by: str | None = None,
    sort_dir: str = "asc",
) -> BeneficioListResponse:
    where_sql, params = _where_lista(q, origem, data_de, data_ate)

    total = int(
        session.execute(
            text(f"SELECT COUNT(*) FROM dbo.CCDBeneficio b {where_sql}"), params
        ).scalar_one()
    )
    order_col = _SORT_COLS.get(sort_by or "", "DataInclusao")
    order_dir = "ASC" if sort_dir == "asc" else "DESC"
    sql = text(
        f"""
        SELECT {_SELECT_COLS}
        FROM dbo.CCDBeneficio b
        {where_sql}
        ORDER BY b.{order_col} {order_dir}, b.IdCCDBeneficio
        OFFSET :offset ROWS FETCH NEXT :size ROWS ONLY
        """
    ).bindparams(bindparam("offset"), bindparam("size"))
    rows = (
        session.execute(sql, {**params, "offset": (page - 1) * size, "size": size}).mappings().all()
    )
    return BeneficioListResponse(
        items=[_to_item(r) for r in rows], total=total, page=page, size=size
    )


def resumo(
    session: Session,
    *,
    q: str | None = None,
    origem: str | None = None,
    data_de: date | None = None,
    data_ate: date | None = None,
) -> BeneficioResumo:
    where_sql, params = _where_lista(q, origem, data_de, data_ate, alias="")
    row = (
        session.execute(
            text(
                f"""
            SELECT
                COUNT(*) AS Total,
                SUM(CASE WHEN IdBeneficioSituacaoEfetivacao = 2 THEN 1 ELSE 0 END) AS Potencial,
                SUM(CASE WHEN IdBeneficioSituacaoEfetivacao = 1 THEN 1 ELSE 0 END) AS Efetivo,
                SUM(CASE WHEN IdBeneficioSituacaoEfetivacao = 2
                    THEN COALESCE(ValorQuantidade, 0) ELSE 0 END) AS ValorPotencial,
                SUM(CASE WHEN IdBeneficioSituacaoEfetivacao = 1
                    THEN COALESCE(ValorQuantidade, 0) ELSE 0 END) AS ValorEfetivo
            FROM dbo.CCDBeneficio
            {where_sql}
            """
            ),
            params,
        )
        .mappings()
        .one()
    )
    return BeneficioResumo(
        total=int(row["Total"] or 0),
        qtd_potencial=int(row["Potencial"] or 0),
        qtd_efetivo=int(row["Efetivo"] or 0),
        valor_potencial=row["ValorPotencial"] or Decimal(0),
        valor_efetivo=row["ValorEfetivo"] or Decimal(0),
    )


def _preencher_meses(rows: list[tuple[int, int, int]]) -> list[MesSerie]:
    """(ano, mes, qtd) ordenado -> série mensal contígua, meses sem linha com qtd=0."""
    if not rows:
        return []
    qtd = {(a, m): q for a, m, q in rows}
    (ano, mes), (fim_ano, fim_mes) = min(qtd), max(qtd)
    serie: list[MesSerie] = []
    while (ano, mes) <= (fim_ano, fim_mes):
        serie.append(MesSerie(ano=ano, mes=mes, qtd=qtd.get((ano, mes), 0)))
        ano, mes = (ano + 1, 1) if mes == 12 else (ano, mes + 1)
    return serie


def serie_mensal(session: Session) -> list[MesSerie]:
    """Quantidade de benefícios ativos por mês da data de referência (histograma do período)."""
    ref = "COALESCE(DataOcorrencia, CAST(DataInclusao AS DATE))"
    rows = session.execute(
        text(
            f"""
            SELECT YEAR({ref}) AS Ano, MONTH({ref}) AS Mes, COUNT(*) AS Qtd
            FROM dbo.CCDBeneficio
            WHERE Ativo = 1
            GROUP BY YEAR({ref}), MONTH({ref})
            ORDER BY 1, 2
            """
        )
    ).all()
    return _preencher_meses([(int(a), int(m), int(q)) for a, m, q in rows])


def obter(session: Session, id_beneficio: int) -> BeneficioItem | None:
    row = (
        session.execute(
            text(
                f"SELECT {_SELECT_COLS} FROM dbo.CCDBeneficio b "
                "WHERE b.IdCCDBeneficio = :id AND b.Ativo = 1"
            ),
            {"id": id_beneficio},
        )
        .mappings()
        .first()
    )
    return _to_item(row) if row else None
