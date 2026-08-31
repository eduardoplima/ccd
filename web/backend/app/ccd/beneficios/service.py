"""CRUD e ciclo de vida do staging CCDBeneficio (migração 0020).

RASCUNHO -> VALIDADO -> ENVIADO, com DESCARTADO como saída lateral. DESCARTADO
mantém Ativo=1 de propósito: a ChaveOrigem segue ocupada e o job de detecção
não recria o candidato. Soft delete (Ativo=0) só para registro criado à mão
por engano.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.ccd.beneficios.dominios import obter_dominios
from app.ccd.beneficios.schemas import (
    BeneficioItem,
    BeneficioListResponse,
    BeneficioResumo,
)

# campo Pydantic (snake_case) -> coluna SQL. Fonte única para SELECT/INSERT/UPDATE.
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

_META_COLS = (
    "IdCCDBeneficio, Status, Origem, ChaveOrigem, IdDebitoExecucao, "
    "LoteEnvio, DataEnvio, DataInclusao, DataAtualizacao"
)
_SELECT_COLS = _META_COLS + ", " + ", ".join(CAMPOS.values())

_SORT_COLS = {
    "processo": "NumeroProcessoDecisao",
    "nome": "NomePessoa",
    "valor": "ValorQuantidade",
    "dataOcorrencia": "DataOcorrencia",
    "origem": "Origem",
    "dataInclusao": "DataInclusao",
}

# Transições permitidas do ciclo de vida.
TRANSICOES: dict[str, set[str]] = {
    "RASCUNHO": {"VALIDADO", "DESCARTADO"},
    "VALIDADO": {"ENVIADO", "RASCUNHO", "DESCARTADO"},
    "ENVIADO": {"VALIDADO"},
    "DESCARTADO": {"RASCUNHO"},
}


def _to_item(r: Any) -> BeneficioItem:
    dados = {campo: r[coluna] for campo, coluna in CAMPOS.items()}
    return BeneficioItem(
        id_beneficio=int(r["IdCCDBeneficio"]),
        status=r["Status"],
        origem=r["Origem"],
        chave_origem=r["ChaveOrigem"],
        id_debito_execucao=r["IdDebitoExecucao"],
        lote_envio=r["LoteEnvio"],
        data_envio=r["DataEnvio"],
        data_inclusao=r["DataInclusao"],
        data_atualizacao=r["DataAtualizacao"],
        **dados,
    )


def listar(
    session: Session,
    *,
    q: str | None = None,
    status: str | None = None,
    situacao_efetivacao: int | None = None,
    id_tipo: int | None = None,
    origem: str | None = None,
    fonte: str | None = None,
    page: int = 1,
    size: int = 50,
    sort_by: str | None = None,
    sort_dir: str = "asc",
) -> BeneficioListResponse:
    where = ["b.Ativo = 1"]
    params: dict[str, Any] = {}
    if q:
        where.append(
            "(CONCAT(b.NumeroProcessoDecisao, '/', b.AnoProcessoDecisao) LIKE :q "
            "OR b.NomePessoa LIKE :q OR b.CpfCnpj LIKE :q "
            "OR b.DescricaoPropostaBeneficio LIKE :q)"
        )
        params["q"] = f"%{q}%"
    if status:
        where.append("b.Status = :status")
        params["status"] = status
    if situacao_efetivacao is not None:
        where.append("b.IdBeneficioSituacaoEfetivacao = :sit")
        params["sit"] = situacao_efetivacao
    if id_tipo is not None:
        where.append("b.IdTipoBeneficio = :tipo")
        params["tipo"] = id_tipo
    if origem:
        where.append("b.Origem = :origem")
        params["origem"] = origem
    # fonte separa as propostas das UTCEs (poucas) da carteira detectada (milhares)
    if fonte == "propostas":
        where.append("b.Origem = 'PROPOSTA'")
    elif fonte == "carteira":
        where.append("b.Origem <> 'PROPOSTA'")
    where_sql = "WHERE " + " AND ".join(where)

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


def resumo(session: Session) -> BeneficioResumo:
    row = (
        session.execute(
            text(
                """
            SELECT
                COUNT(*) AS Total,
                SUM(CASE WHEN Status = 'RASCUNHO' THEN 1 ELSE 0 END) AS Rascunho,
                SUM(CASE WHEN Status = 'VALIDADO' THEN 1 ELSE 0 END) AS Validado,
                SUM(CASE WHEN Status = 'ENVIADO' THEN 1 ELSE 0 END) AS Enviado,
                SUM(CASE WHEN Status = 'DESCARTADO' THEN 1 ELSE 0 END) AS Descartado,
                SUM(CASE WHEN IdBeneficioSituacaoEfetivacao = 2 THEN 1 ELSE 0 END) AS Potencial,
                SUM(CASE WHEN IdBeneficioSituacaoEfetivacao = 1 THEN 1 ELSE 0 END) AS Efetivo,
                SUM(CASE WHEN IdBeneficioSituacaoEfetivacao = 2 AND Status <> 'DESCARTADO'
                    THEN COALESCE(ValorQuantidade, 0) ELSE 0 END) AS ValorPotencial,
                SUM(CASE WHEN IdBeneficioSituacaoEfetivacao = 1 AND Status <> 'DESCARTADO'
                    THEN COALESCE(ValorQuantidade, 0) ELSE 0 END) AS ValorEfetivo
            FROM dbo.CCDBeneficio
            WHERE Ativo = 1
            """
            )
        )
        .mappings()
        .one()
    )
    return BeneficioResumo(
        total=int(row["Total"] or 0),
        qtd_rascunho=int(row["Rascunho"] or 0),
        qtd_validado=int(row["Validado"] or 0),
        qtd_enviado=int(row["Enviado"] or 0),
        qtd_descartado=int(row["Descartado"] or 0),
        qtd_potencial=int(row["Potencial"] or 0),
        qtd_efetivo=int(row["Efetivo"] or 0),
        valor_potencial=row["ValorPotencial"] or Decimal(0),
        valor_efetivo=row["ValorEfetivo"] or Decimal(0),
    )


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


def _preparar(dados: dict[str, Any]) -> dict[str, Any]:
    dados = {k: v for k, v in dados.items() if k in CAMPOS}
    if dados.get("valor_quantidade") is not None:
        dados["valor_quantidade"] = Decimal(str(dados["valor_quantidade"]))
    if dados.get("numero_processo_decisao"):
        num = str(dados["numero_processo_decisao"]).strip()
        dados["numero_processo_decisao"] = num.zfill(6) if num.isdigit() else num
    return dados


def criar(session: Session, *, dados: dict[str, Any], id_usuario: int) -> int:
    """Cadastro manual (Origem='MANUAL', Status='RASCUNHO')."""
    dados = _preparar(dados)
    colunas = list(dados)
    sql = text(
        f"""
        INSERT INTO dbo.CCDBeneficio
            ({", ".join(CAMPOS[c] for c in colunas)}, IdUsuarioAtualizacao)
        OUTPUT inserted.IdCCDBeneficio
        VALUES ({", ".join(f":{c}" for c in colunas)}, :id_usuario)
        """
    )
    novo_id = int(session.execute(sql, {**dados, "id_usuario": id_usuario}).scalar_one())
    session.commit()
    return novo_id


def atualizar(
    session: Session, id_beneficio: int, *, dados: dict[str, Any], id_usuario: int
) -> str:
    """Retorna 'ok', 'not_found' ou 'enviado' (registro ENVIADO é imutável)."""
    atual = session.execute(
        text("SELECT Status FROM dbo.CCDBeneficio WHERE IdCCDBeneficio = :id AND Ativo = 1"),
        {"id": id_beneficio},
    ).first()
    if atual is None:
        return "not_found"
    if atual[0] == "ENVIADO":
        return "enviado"
    dados = _preparar(dados)
    if not dados:
        return "ok"
    sets = ", ".join(f"{CAMPOS[c]} = :{c}" for c in dados)
    session.execute(
        text(
            f"""
            UPDATE dbo.CCDBeneficio
            SET {sets},
                DataAtualizacao = SYSUTCDATETIME(),
                IdUsuarioAtualizacao = :id_usuario
            WHERE IdCCDBeneficio = :id
            """
        ),
        {**dados, "id_usuario": id_usuario, "id": id_beneficio},
    )
    session.commit()
    return "ok"


def _validar_para_validado(session: Session, id_beneficio: int) -> str | None:
    """Campos mínimos + coerência tipo/subtipo antes de VALIDADO. None = ok."""
    row = (
        session.execute(
            text(
                "SELECT DescricaoPropostaBeneficio, IdTipoBeneficio, IdSubTipoBeneficio, "
                "IdCaracterizacaoBeneficio, IdAreaTematica, IdBeneficioSituacaoEfetivacao "
                "FROM dbo.CCDBeneficio WHERE IdCCDBeneficio = :id"
            ),
            {"id": id_beneficio},
        )
        .mappings()
        .one()
    )
    faltando = [
        campo
        for campo, coluna in (
            ("idTipo", "IdTipoBeneficio"),
            ("idCaracterizacao", "IdCaracterizacaoBeneficio"),
            ("idAreaTematica", "IdAreaTematica"),
            ("idSituacaoEfetivacao", "IdBeneficioSituacaoEfetivacao"),
        )
        if row[coluna] is None
    ]
    if faltando:
        return f"missing fields for validation: {', '.join(faltando)}"
    if row["IdSubTipoBeneficio"] is not None:
        dominios = obter_dominios(session)
        permitidos = dominios.tipo_subtipos.get(int(row["IdTipoBeneficio"]), [])
        if int(row["IdSubTipoBeneficio"]) not in permitidos:
            return "subtipo does not belong to tipo (Beneficio_Tipo_Subtipo)"
    return None


def transicionar(session: Session, id_beneficio: int, *, novo_status: str, id_usuario: int) -> str:
    """Retorna 'ok', 'not_found', 'invalid_transition' ou mensagem de validação."""
    atual = session.execute(
        text("SELECT Status FROM dbo.CCDBeneficio WHERE IdCCDBeneficio = :id AND Ativo = 1"),
        {"id": id_beneficio},
    ).first()
    if atual is None:
        return "not_found"
    if novo_status not in TRANSICOES.get(atual[0], set()):
        return "invalid_transition"
    if novo_status == "VALIDADO" and atual[0] == "RASCUNHO":
        erro = _validar_para_validado(session, id_beneficio)
        if erro:
            return erro
    # Desfazer envio limpa o lote; demais transições não mexem em DataEnvio.
    limpar_envio = ", DataEnvio = NULL, LoteEnvio = NULL" if atual[0] == "ENVIADO" else ""
    session.execute(
        text(
            f"""
            UPDATE dbo.CCDBeneficio
            SET Status = :status{limpar_envio},
                DataAtualizacao = SYSUTCDATETIME(),
                IdUsuarioAtualizacao = :id_usuario
            WHERE IdCCDBeneficio = :id
            """
        ),
        {"status": novo_status, "id_usuario": id_usuario, "id": id_beneficio},
    )
    session.commit()
    return "ok"


def deletar(session: Session, id_beneficio: int, *, id_usuario: int) -> str:
    """Soft delete — só para registro MANUAL criado por engano. Candidato de
    detecção usa DESCARTADO (mantém a ChaveOrigem ocupada). Retorna 'ok',
    'not_found' ou 'nao_manual'."""
    row = session.execute(
        text("SELECT Origem FROM dbo.CCDBeneficio WHERE IdCCDBeneficio = :id AND Ativo = 1"),
        {"id": id_beneficio},
    ).first()
    if row is None:
        return "not_found"
    if row[0] != "MANUAL":
        return "nao_manual"
    session.execute(
        text(
            """
            UPDATE dbo.CCDBeneficio
            SET Ativo = 0,
                DataAtualizacao = SYSUTCDATETIME(),
                IdUsuarioAtualizacao = :id_usuario
            WHERE IdCCDBeneficio = :id
            """
        ),
        {"id": id_beneficio, "id_usuario": id_usuario},
    )
    session.commit()
    return "ok"
