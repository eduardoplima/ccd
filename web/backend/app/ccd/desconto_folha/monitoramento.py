"""Monitoramento de desconto em folha (substitui a planilha manual).

CRUD sobre dbo.FRAPMonitoramentoDescontoFolha (migração 0018): uma linha por
processo monitorado, grupos GERAL / ANTIGO / NEREU. Soft delete via Ativo=0;
unicidade de (Grupo, NumeroProcesso) garantida por índice único filtrado.
"""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Any

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.ccd.desconto_folha.schemas import (
    MonitoramentoItem,
    MonitoramentoListResponse,
    MonitoramentoResumo,
)

GRUPOS = ("GERAL", "ANTIGO", "NEREU")

# campo Pydantic (snake_case) -> coluna SQL. Fonte única para SELECT/INSERT/UPDATE.
CAMPOS: dict[str, str] = {
    "grupo": "Grupo",
    "numero_processo": "NumeroProcesso",
    "processo_sei": "ProcessoSei",
    "cpfcnpj": "CpfCnpj",
    "nome_pessoa": "NomePessoa",
    "id_orgao_notificado": "IdOrgaoNotificado",
    "nome_orgao": "NomeOrgao",
    "esfera_orgao": "EsferaOrgao",
    "cadastrado_desconto_folha": "CadastradoDescontoFolha",
    "data_despacho": "DataDespacho",
    "data_notificacao": "DataNotificacao",
    "data_recebimento_ar": "DataRecebimentoAr",
    "data_resposta": "DataResposta",
    "data_segunda_notificacao": "DataSegundaNotificacao",
    "data_recebimento_ar2": "DataRecebimentoAr2",
    "desc_folha_texto": "DescFolhaTexto",
    "valor_periodo": "ValorPeriodo",
    "periodo_referencia": "PeriodoReferencia",
    "transf_frap": "TransfFrap",
    "pago_site_tce": "PagoSiteTce",
    "tipo_pagamento": "TipoPagamento",
    "remanescente": "Remanescente",
    "apr": "Apr",
    "valor_original": "ValorOriginal",
    "observacoes": "Observacoes",
    "relator": "Relator",
    "valor_implementado": "ValorImplementado",
    "data_implementacao": "DataImplementacao",
    "verificado_siaidp": "VerificadoSiaidp",
    "verificado_frap": "VerificadoFrap",
    "id_frap_desconto_folha": "IdFRAPDescontoFolha",
}

_SORT_COLS = {
    "processo": "NumeroProcesso",
    "nome": "NomePessoa",
    "grupo": "Grupo",
    "dataNotificacao": "DataNotificacao",
    "valorOriginal": "ValorOriginal",
}

_RE_PROCESSO = re.compile(r"^(\d{1,6})\s*/\s*(\d{4})$")


def normalizar_processo(texto: str) -> str:
    """'4917/2024 ' -> '004917/2024'. Texto fora do padrão volta só com strip."""
    limpo = re.sub(r"\s+", " ", str(texto)).strip()
    m = _RE_PROCESSO.match(limpo)
    if m:
        return f"{int(m.group(1)):06d}/{m.group(2)}"
    return limpo


def _to_item(r: Any) -> MonitoramentoItem:
    dados = {campo: r[coluna] for campo, coluna in CAMPOS.items()}
    if dados["cadastrado_desconto_folha"] is not None:
        dados["cadastrado_desconto_folha"] = bool(dados["cadastrado_desconto_folha"])
    return MonitoramentoItem(
        id_monitoramento=int(r["IdFRAPMonitoramentoDescontoFolha"]),
        data_inclusao=r["DataInclusao"],
        data_atualizacao=r["DataAtualizacao"],
        **dados,
    )


_SELECT_COLS = "IdFRAPMonitoramentoDescontoFolha, DataInclusao, DataAtualizacao, " + ", ".join(
    CAMPOS.values()
)


def listar(
    session: Session,
    *,
    q: str | None = None,
    grupo: str | None = None,
    page: int = 1,
    size: int = 50,
    sort_by: str | None = None,
    sort_dir: str = "asc",
) -> MonitoramentoListResponse:
    where = ["m.Ativo = 1"]
    params: dict[str, Any] = {}
    if q:
        where.append("(m.NumeroProcesso LIKE :q OR m.NomePessoa LIKE :q OR m.CpfCnpj LIKE :q)")
        params["q"] = f"%{q}%"
    if grupo:
        where.append("m.Grupo = :grupo")
        params["grupo"] = grupo
    where_sql = "WHERE " + " AND ".join(where)

    total = int(
        session.execute(
            text(f"SELECT COUNT(*) FROM dbo.FRAPMonitoramentoDescontoFolha m {where_sql}"),
            params,
        ).scalar_one()
    )
    order_col = _SORT_COLS.get(sort_by or "", "NumeroProcesso")
    order_dir = "DESC" if sort_dir == "desc" else "ASC"
    sql = text(
        f"""
        SELECT {_SELECT_COLS}
        FROM dbo.FRAPMonitoramentoDescontoFolha m
        {where_sql}
        ORDER BY m.{order_col} {order_dir}, m.IdFRAPMonitoramentoDescontoFolha
        OFFSET :offset ROWS FETCH NEXT :size ROWS ONLY
        """
    ).bindparams(bindparam("offset"), bindparam("size"))
    rows = (
        session.execute(sql, {**params, "offset": (page - 1) * size, "size": size}).mappings().all()
    )
    return MonitoramentoListResponse(
        items=[_to_item(r) for r in rows], total=total, page=page, size=size
    )


def resumo(session: Session, *, grupo: str | None = None) -> MonitoramentoResumo:
    where = "WHERE Ativo = 1" + (" AND Grupo = :grupo" if grupo else "")
    params = {"grupo": grupo} if grupo else {}
    # Definições (espelham a aba RESUMO da planilha):
    #   notificados        = DataNotificacao preenchida
    #   com AR             = DataRecebimentoAr preenchida
    #   respondidos        = DataResposta preenchida
    #   2ª notificação     = DataSegundaNotificacao preenchida
    #   desconto implantado = "Desc. Folha" começa com S (não usar o vínculo
    #   IdFRAPDescontoFolha: ele liga por CPF a qualquer plano ativo, inclusive
    #   Origem='S' auto-populado, e inflaria a contagem vs a aba RESUMO)
    #   transf. FRAP       = campo TransfFrap preenchido
    #   pagos no site      = campo PagoSiteTce preenchido
    row = (
        session.execute(
            text(
                f"""
            SELECT
                COUNT(*) AS Total,
                SUM(CASE WHEN Grupo = 'GERAL' THEN 1 ELSE 0 END)  AS TotalGeral,
                SUM(CASE WHEN Grupo = 'ANTIGO' THEN 1 ELSE 0 END) AS TotalAntigo,
                SUM(CASE WHEN Grupo = 'NEREU' THEN 1 ELSE 0 END)  AS TotalNereu,
                SUM(CASE WHEN DataNotificacao IS NOT NULL THEN 1 ELSE 0 END) AS Notificados,
                SUM(CASE WHEN DataRecebimentoAr IS NOT NULL THEN 1 ELSE 0 END) AS ComAr,
                SUM(CASE WHEN DataResposta IS NOT NULL THEN 1 ELSE 0 END) AS Respondidos,
                SUM(CASE WHEN DataSegundaNotificacao IS NOT NULL THEN 1 ELSE 0 END)
                    AS SegundaNotificacao,
                SUM(CASE WHEN UPPER(LTRIM(DescFolhaTexto)) LIKE 'S%' THEN 1 ELSE 0 END)
                    AS DescontoImplementado,
                SUM(CASE WHEN NULLIF(LTRIM(RTRIM(TransfFrap)), '') IS NOT NULL
                    THEN 1 ELSE 0 END) AS TransfFrap,
                SUM(CASE WHEN NULLIF(LTRIM(RTRIM(PagoSiteTce)), '') IS NOT NULL
                    THEN 1 ELSE 0 END) AS PagoSite
            FROM dbo.FRAPMonitoramentoDescontoFolha
            {where}
            """
            ),
            params,
        )
        .mappings()
        .one()
    )
    return MonitoramentoResumo(
        total=int(row["Total"] or 0),
        total_geral=int(row["TotalGeral"] or 0),
        total_antigo=int(row["TotalAntigo"] or 0),
        total_nereu=int(row["TotalNereu"] or 0),
        qtd_notificados=int(row["Notificados"] or 0),
        qtd_com_ar=int(row["ComAr"] or 0),
        qtd_respondidos=int(row["Respondidos"] or 0),
        qtd_segunda_notificacao=int(row["SegundaNotificacao"] or 0),
        qtd_desconto_implementado=int(row["DescontoImplementado"] or 0),
        qtd_transf_frap=int(row["TransfFrap"] or 0),
        qtd_pago_site=int(row["PagoSite"] or 0),
    )


def obter(session: Session, id_monitoramento: int) -> MonitoramentoItem | None:
    row = (
        session.execute(
            text(
                f"""
            SELECT {_SELECT_COLS}
            FROM dbo.FRAPMonitoramentoDescontoFolha m
            WHERE m.IdFRAPMonitoramentoDescontoFolha = :id AND m.Ativo = 1
            """
            ),
            {"id": id_monitoramento},
        )
        .mappings()
        .first()
    )
    return _to_item(row) if row else None


def _existe_ativo(
    session: Session,
    grupo: str,
    numero_processo: str,
    cpfcnpj: str | None,
    *,
    exceto_id: int | None = None,
) -> bool:
    # Unicidade espelha UX_FRAPMonitDF_Grupo_Processo: um processo pode ter
    # vários responsáveis (CPFs) monitorados.
    sql = (
        "SELECT COUNT(*) FROM dbo.FRAPMonitoramentoDescontoFolha "
        "WHERE Grupo = :grupo AND NumeroProcesso = :proc AND Ativo = 1 "
        "AND ((:cpf IS NULL AND CpfCnpj IS NULL) OR CpfCnpj = :cpf)"
    )
    params: dict[str, Any] = {"grupo": grupo, "proc": numero_processo, "cpf": cpfcnpj}
    if exceto_id is not None:
        sql += " AND IdFRAPMonitoramentoDescontoFolha <> :id"
        params["id"] = exceto_id
    return int(session.execute(text(sql), params).scalar_one()) > 0


def _preparar(dados: dict[str, Any]) -> dict[str, Any]:
    dados = {k: v for k, v in dados.items() if k in CAMPOS}
    if "numero_processo" in dados and dados["numero_processo"]:
        dados["numero_processo"] = normalizar_processo(dados["numero_processo"])
    for campo in ("valor_periodo", "valor_original", "valor_implementado"):
        if dados.get(campo) is not None:
            dados[campo] = Decimal(str(dados[campo]))
    return dados


def criar(session: Session, *, dados: dict[str, Any], id_usuario: int) -> int | str:
    """Retorna o id criado ou 'duplicado'."""
    dados = _preparar(dados)
    if _existe_ativo(session, dados["grupo"], dados["numero_processo"], dados.get("cpfcnpj")):
        return "duplicado"
    colunas = list(dados)
    sql = text(
        f"""
        INSERT INTO dbo.FRAPMonitoramentoDescontoFolha
            ({", ".join(CAMPOS[c] for c in colunas)}, IdUsuarioAtualizacao)
        OUTPUT inserted.IdFRAPMonitoramentoDescontoFolha
        VALUES ({", ".join(f":{c}" for c in colunas)}, :id_usuario)
        """
    )
    novo_id = int(session.execute(sql, {**dados, "id_usuario": id_usuario}).scalar_one())
    session.commit()
    return novo_id


def atualizar(
    session: Session, id_monitoramento: int, *, dados: dict[str, Any], id_usuario: int
) -> str:
    """Retorna 'ok', 'not_found' ou 'duplicado'."""
    atual = session.execute(
        text(
            "SELECT Grupo, NumeroProcesso, CpfCnpj FROM dbo.FRAPMonitoramentoDescontoFolha "
            "WHERE IdFRAPMonitoramentoDescontoFolha = :id AND Ativo = 1"
        ),
        {"id": id_monitoramento},
    ).first()
    if atual is None:
        return "not_found"
    dados = _preparar(dados)
    if not dados:
        return "ok"
    if "grupo" in dados or "numero_processo" in dados or "cpfcnpj" in dados:
        grupo = dados.get("grupo", atual[0])
        proc = dados.get("numero_processo", atual[1])
        cpf = dados.get("cpfcnpj", atual[2])
        if _existe_ativo(session, grupo, proc, cpf, exceto_id=id_monitoramento):
            return "duplicado"
    sets = ", ".join(f"{CAMPOS[c]} = :{c}" for c in dados)
    session.execute(
        text(
            f"""
            UPDATE dbo.FRAPMonitoramentoDescontoFolha
            SET {sets},
                DataAtualizacao = SYSUTCDATETIME(),
                IdUsuarioAtualizacao = :id_usuario
            WHERE IdFRAPMonitoramentoDescontoFolha = :id
            """
        ),
        {**dados, "id_usuario": id_usuario, "id": id_monitoramento},
    )
    session.commit()
    return "ok"


def deletar(session: Session, id_monitoramento: int, *, id_usuario: int) -> str:
    """Soft delete. Retorna 'ok' ou 'not_found'."""
    res = session.execute(
        text(
            """
            UPDATE dbo.FRAPMonitoramentoDescontoFolha
            SET Ativo = 0,
                DataAtualizacao = SYSUTCDATETIME(),
                IdUsuarioAtualizacao = :id_usuario
            WHERE IdFRAPMonitoramentoDescontoFolha = :id AND Ativo = 1
            """
        ),
        {"id": id_monitoramento, "id_usuario": id_usuario},
    )
    if int(res.rowcount or 0) == 0:
        session.rollback()
        return "not_found"
    session.commit()
    return "ok"
