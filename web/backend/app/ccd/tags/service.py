"""CGTAG: leitura e escrita em CCDTAG / CCDTAGObrigacao (SQL cru, sem ORM)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ccd.tags import schemas

_URL_EVENTO = (
    "https://processos.tce.rn.gov.br/#/dashboard/processos/{id_processo}/autos/evento/{id_evento}"
)


def _agora() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None, microsecond=0)


def parse_processo(texto: str) -> tuple[str, int]:
    """'14254/2015' → ('014254', 2015)."""
    numero, ano = texto.strip().split("/")
    return numero.zfill(6), int(ano)


def _item(r: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": r["IdCCDTAG"],
        "id_processo": r["IdProcesso"],
        "processo": f"{str(r['NumeroProcesso']).strip()}/{r['AnoProcesso']}",
        "evento": r["Evento"],
        "url_evento": (
            _URL_EVENTO.format(id_processo=r["IdProcesso"], id_evento=r["IdEvento"])
            if r.get("IdEvento")
            else None
        ),
        "numero": r["Numero"],
        "orgao": r["Orgao"],
        "responsavel": r["Responsavel"],
        "prazo": r["Prazo"],
        "situacao": r["Situacao"],
        "revisado": bool(r["Revisado"]),
        "qtd_obrigacoes": int(r.get("QtdObrigacoes") or 0),
        "proxima_data_limite": r.get("ProximaDataLimite"),
        "data_inclusao": r["DataInclusao"],
    }


_SQL_LISTA = """
SELECT t.*,
       (SELECT COUNT(*) FROM CCDTAGObrigacao o WHERE o.IdCCDTAG = t.IdCCDTAG) AS QtdObrigacoes,
       (SELECT MIN(o.DataLimite) FROM CCDTAGObrigacao o
         WHERE o.IdCCDTAG = t.IdCCDTAG AND o.Situacao = 'PENDENTE') AS ProximaDataLimite
FROM CCDTAG t
WHERE t.Ativo = 1 {filtro}
ORDER BY t.DataInclusao DESC
"""


def listar(session: Session, q: str | None = None) -> schemas.TagListResponse:
    filtro, params = "", {}
    if q:
        filtro = (
            "AND (t.Numero LIKE :q OR t.Orgao LIKE :q OR t.Responsavel LIKE :q "
            "OR CONCAT(t.NumeroProcesso, '/', t.AnoProcesso) LIKE :q)"
        )
        params["q"] = f"%{q.strip()}%"
    rows = [
        dict(r) for r in session.execute(text(_SQL_LISTA.format(filtro=filtro)), params).mappings()
    ]
    items = [schemas.TagListItem.model_validate(_item(r)) for r in rows]
    return schemas.TagListResponse(items=items, total=len(items))


def _carregar(session: Session, id_tag: int) -> dict[str, Any]:
    r = (
        session.execute(text(_SQL_LISTA.format(filtro="AND t.IdCCDTAG = :id")), {"id": id_tag})
        .mappings()
        .first()
    )
    if r is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tag not found")
    return dict(r)


def detalhe(session: Session, id_tag: int) -> schemas.TagDetalhe:
    r = _carregar(session, id_tag)
    obrigacoes = [
        schemas.ObrigacaoOut(
            id=o["IdCCDTAGObrigacao"],
            ordem=o["Ordem"],
            clausula=o["Clausula"],
            descricao=o["Descricao"],
            prazo_texto=o["PrazoTexto"],
            data_limite=o["DataLimite"],
            situacao=o["Situacao"],
            data_cumprimento=o["DataCumprimento"],
            evento_comprovacao=o["EventoComprovacao"],
            observacoes=o["Observacoes"],
        )
        for o in session.execute(
            text("SELECT * FROM CCDTAGObrigacao WHERE IdCCDTAG = :id ORDER BY Ordem"),
            {"id": id_tag},
        ).mappings()
    ]
    return schemas.TagDetalhe.model_validate(
        {
            **_item(r),
            "id_informacao": r["IdInformacao"],
            "cargo_responsavel": r["CargoResponsavel"],
            "cpf_responsavel": r["CpfResponsavel"],
            "compromissario": r["Compromissario"],
            "data_celebracao": r["DataCelebracao"],
            "homologacao": r["Homologacao"],
            "valor_multa_descumprimento": r["ValorMultaDescumprimento"],
            "observacoes": r["Observacoes"],
            "texto_ocr": r["TextoOCR"],
            "obrigacoes": obrigacoes,
        }
    )


def existe_ativo(session: Session, id_processo: int, evento: int) -> bool:
    return (
        session.execute(
            text("SELECT 1 FROM CCDTAG WHERE Ativo = 1 AND IdProcesso = :p AND Evento = :e"),
            {"p": id_processo, "e": evento},
        ).first()
        is not None
    )


_COLS_TAG = (
    "IdProcesso, NumeroProcesso, AnoProcesso, Evento, IdEvento, IdInformacao, Numero, Orgao, "
    "Responsavel, CargoResponsavel, Compromissario, DataCelebracao, Prazo, "
    "ValorMultaDescumprimento, TextoOCR, PayloadLLM, Revisado, Ativo, DataInclusao, "
    "IdUsuarioInclusao"
)


def criar(
    session: Session,
    *,
    cabecalho: dict[str, Any],
    obrigacoes: list[dict[str, Any]],
    id_usuario: int | None,
) -> int:
    """Insere o TAG (rascunho, Revisado=0) e as obrigações. Devolve o id novo."""
    agora = _agora()
    session.execute(
        text(
            f"INSERT INTO CCDTAG ({_COLS_TAG}) VALUES ("
            ":IdProcesso, :NumeroProcesso, :AnoProcesso, :Evento, :IdEvento, :IdInformacao, "
            ":Numero, :Orgao, :Responsavel, :CargoResponsavel, :Compromissario, "
            ":DataCelebracao, :Prazo, :ValorMultaDescumprimento, :TextoOCR, :PayloadLLM, "
            "0, 1, :agora, :usuario)"
        ),
        {**cabecalho, "agora": agora, "usuario": id_usuario},
    )
    novo = session.execute(
        text(
            "SELECT MAX(IdCCDTAG) FROM CCDTAG WHERE IdProcesso = :p AND Evento = :e "
            "AND DataInclusao = :agora"
        ),
        {"p": cabecalho["IdProcesso"], "e": cabecalho["Evento"], "agora": agora},
    ).scalar_one()
    _inserir_obrigacoes(session, int(novo), obrigacoes)
    session.commit()
    return int(novo)


def _inserir_obrigacoes(session: Session, id_tag: int, obrigacoes: list[dict[str, Any]]) -> None:
    for ordem, o in enumerate(obrigacoes, 1):
        session.execute(
            text(
                "INSERT INTO CCDTAGObrigacao (IdCCDTAG, Ordem, Clausula, Descricao, PrazoTexto, "
                "DataLimite, Situacao, DataCumprimento, EventoComprovacao, Observacoes) VALUES "
                "(:id, :ordem, :Clausula, :Descricao, :PrazoTexto, :DataLimite, :Situacao, "
                ":DataCumprimento, :EventoComprovacao, :Observacoes)"
            ),
            {
                "id": id_tag,
                "ordem": ordem,
                "Clausula": o["Clausula"][:80],
                "Descricao": o["Descricao"],
                "PrazoTexto": (o.get("PrazoTexto") or None) and o["PrazoTexto"][:255],
                "DataLimite": o.get("DataLimite"),
                "Situacao": o.get("Situacao") or "PENDENTE",
                "DataCumprimento": o.get("DataCumprimento"),
                "EventoComprovacao": o.get("EventoComprovacao"),
                "Observacoes": o.get("Observacoes"),
            },
        )


_PATCH_COLS = {
    "numero": "Numero",
    "orgao": "Orgao",
    "responsavel": "Responsavel",
    "cargo_responsavel": "CargoResponsavel",
    "cpf_responsavel": "CpfResponsavel",
    "compromissario": "Compromissario",
    "data_celebracao": "DataCelebracao",
    "prazo": "Prazo",
    "homologacao": "Homologacao",
    "valor_multa_descumprimento": "ValorMultaDescumprimento",
    "situacao": "Situacao",
    "revisado": "Revisado",
    "observacoes": "Observacoes",
}


def atualizar(
    session: Session, id_tag: int, patch: schemas.TagPatch, id_usuario: int | None
) -> schemas.TagDetalhe:
    _carregar(session, id_tag)
    sets = ["DataAtualizacao = :agora", "IdUsuarioAtualizacao = :usuario"]
    params: dict[str, Any] = {"id": id_tag, "agora": _agora(), "usuario": id_usuario}
    for campo, valor in patch.model_dump(exclude_unset=True).items():
        col = _PATCH_COLS[campo]
        sets.append(f"{col} = :{col}")
        if campo == "cpf_responsavel" and valor:
            valor = "".join(ch for ch in valor if ch.isdigit()) or None
        params[col] = int(valor) if campo == "revisado" and valor is not None else valor
    session.execute(text(f"UPDATE CCDTAG SET {', '.join(sets)} WHERE IdCCDTAG = :id"), params)
    session.commit()
    return detalhe(session, id_tag)


def salvar_obrigacoes(
    session: Session, id_tag: int, payload: schemas.ObrigacoesInput, id_usuario: int | None
) -> schemas.TagDetalhe:
    """Substitui a lista inteira (ponytail: um endpoint, sem CRUD por linha)."""
    _carregar(session, id_tag)
    session.execute(text("DELETE FROM CCDTAGObrigacao WHERE IdCCDTAG = :id"), {"id": id_tag})
    _inserir_obrigacoes(
        session,
        id_tag,
        [
            {
                "Clausula": o.clausula,
                "Descricao": o.descricao,
                "PrazoTexto": o.prazo_texto,
                "DataLimite": o.data_limite,
                "Situacao": o.situacao,
                "DataCumprimento": o.data_cumprimento,
                "EventoComprovacao": o.evento_comprovacao,
                "Observacoes": o.observacoes,
            }
            for o in payload.obrigacoes
        ],
    )
    session.execute(
        text(
            "UPDATE CCDTAG SET DataAtualizacao = :agora, IdUsuarioAtualizacao = :usuario "
            "WHERE IdCCDTAG = :id"
        ),
        {"id": id_tag, "agora": _agora(), "usuario": id_usuario},
    )
    session.commit()
    return detalhe(session, id_tag)


def remover(session: Session, id_tag: int, id_usuario: int | None) -> None:
    _carregar(session, id_tag)
    session.execute(
        text(
            "UPDATE CCDTAG SET Ativo = 0, DataAtualizacao = :agora, "
            "IdUsuarioAtualizacao = :usuario WHERE IdCCDTAG = :id"
        ),
        {"id": id_tag, "agora": _agora(), "usuario": id_usuario},
    )
    session.commit()


def resolver_processo(sessao_processo: Session, processo: str) -> Optional[dict[str, Any]]:
    numero, ano = parse_processo(processo)
    r = (
        sessao_processo.execute(
            text(
                "SELECT IdProcesso, numero_processo AS numero, ano_processo AS ano "
                "FROM dbo.Processos WHERE numero_processo = :n AND ano_processo = :a"
            ),
            {"n": numero, "a": ano},
        )
        .mappings()
        .first()
    )
    return dict(r) if r else None
