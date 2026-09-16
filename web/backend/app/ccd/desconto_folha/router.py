"""Desconto em folha: `/api/v1/ccd/desconto-folha`.

Cadastro (processo + débito) → resposta do órgão no apensado (extração pela
LLM no worker) → match com o FRAP. Escrita é de admin; leitura, de qualquer
usuário autenticado.
"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.models import FRAPUsuario
from app.ccd.desconto_folha import schemas, service
from app.deps import (
    get_arq_pool,
    get_current_user,
    get_db_session,
    get_processo_session,
    require_role,
)
from app.jobs import service as jobs_service
from app.jobs.schemas import JobOut

router = APIRouter(prefix="/api/v1/ccd/desconto-folha", tags=["ccd:desconto-folha"])


@router.get("", response_model=schemas.CadastroListResponse)
def listar(
    q: str | None = Query(default=None, max_length=100),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    com_notificacao: bool = Query(default=False),
    com_recebimento: bool = Query(default=False),
    com_resposta: bool = Query(default=False),
    com_valores: bool = Query(default=False),
    com_conciliacao: bool = Query(default=False),
    cpf: str | None = Query(default=None, max_length=14),
    orgao: str | None = Query(default=None, max_length=200),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> schemas.CadastroListResponse:
    return service.listar(
        session,
        q=q,
        page=page,
        size=size,
        com_notificacao=com_notificacao,
        com_recebimento=com_recebimento,
        com_resposta=com_resposta,
        com_valores=com_valores,
        com_conciliacao=com_conciliacao,
        cpf=cpf,
        orgao=orgao,
    )


@router.get("/sugestoes", response_model=schemas.SugestoesOut)
def sugestoes(
    q: str = Query(..., min_length=2, max_length=100),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> schemas.SugestoesOut:
    return service.sugestoes(session, q)


@router.get("/retencoes", response_model=schemas.RetencoesOut)
def retencoes(
    cpf: str = Query(..., min_length=11, max_length=14, pattern=r"^\d+$"),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> schemas.RetencoesOut:
    return service.retencoes(session, cpf)


@router.get("/retencoes/mapa", response_model=schemas.MapaRetencoesOut)
def mapa_retencoes(
    cpf: str = Query(..., min_length=11, max_length=14, pattern=r"^\d+$"),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> schemas.MapaRetencoesOut:
    return service.mapa_retencoes(session, cpf)


@router.get("/lookup", response_model=schemas.ProcessoLookup)
def lookup(
    processo: str = Query(..., max_length=20),
    sessao_processo: Session = Depends(get_processo_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> schemas.ProcessoLookup:
    return service.lookup(sessao_processo, processo)


@router.post("", response_model=schemas.CadastroDetalhe, status_code=status.HTTP_201_CREATED)
def criar(
    payload: schemas.CadastroInput,
    session: Session = Depends(get_db_session),
    sessao_processo: Session = Depends(get_processo_session),
    user: FRAPUsuario = Depends(require_role("admin")),
) -> schemas.CadastroDetalhe:
    return service.criar(session, sessao_processo, payload, id_usuario=user.IdUsuario)


@router.get("/{id_cadastro}", response_model=schemas.CadastroDetalhe)
def detalhe(
    id_cadastro: int,
    session: Session = Depends(get_db_session),
    sessao_processo: Session = Depends(get_processo_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> schemas.CadastroDetalhe:
    return service.detalhe(session, id_cadastro, sessao_processo)


@router.patch("/{id_cadastro}", response_model=schemas.CadastroDetalhe)
def atualizar(
    id_cadastro: int,
    payload: schemas.CadastroPatch,
    session: Session = Depends(get_db_session),
    sessao_processo: Session = Depends(get_processo_session),
    _: FRAPUsuario = Depends(require_role("admin")),
) -> schemas.CadastroDetalhe:
    return service.atualizar(session, sessao_processo, id_cadastro, payload)


@router.post("/{id_cadastro}/atualizar-processo", response_model=schemas.CadastroDetalhe)
def atualizar_processo(
    id_cadastro: int,
    session: Session = Depends(get_db_session),
    sessao_processo: Session = Depends(get_processo_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> schemas.CadastroDetalhe:
    """Reconsulta notificação, AR e apensado no banco `processo`."""
    return service.atualizar_dados_processo(session, sessao_processo, id_cadastro)


@router.delete("/{id_cadastro}", status_code=status.HTTP_204_NO_CONTENT)
def remover(
    id_cadastro: int,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(require_role("admin")),
) -> None:
    service.remover(session, id_cadastro)


@router.post("/{id_cadastro}/extrair", response_model=JobOut, status_code=status.HTTP_202_ACCEPTED)
async def extrair(
    id_cadastro: int,
    pool=Depends(get_arq_pool),
    session: Session = Depends(get_db_session),
    user: FRAPUsuario = Depends(require_role("admin")),
) -> JobOut:
    service.detalhe(session, id_cadastro)  # 404 antes de enfileirar
    job = await jobs_service.enqueue_job(
        pool,
        session,
        user=user,
        tipo="ccd-desconto-folha-extrair",
        funcao="task_extrair_resposta_desconto_folha",
        argumentos={"id_cadastro": id_cadastro},
    )
    return JobOut.model_validate(job)


@router.post("/localizar-notificacoes", response_model=JobOut, status_code=status.HTTP_202_ACCEPTED)
async def localizar_notificacoes(
    pool=Depends(get_arq_pool),
    session: Session = Depends(get_db_session),
    user: FRAPUsuario = Depends(require_role("admin")),
) -> JobOut:
    """Varre os cadastros ativos e localiza notificação e recebimento no banco `processo` (worker)."""
    job = await jobs_service.enqueue_job(
        pool,
        session,
        user=user,
        tipo="ccd-desconto-folha-notificacoes",
        funcao="task_localizar_notificacoes_desconto_folha",
    )
    return JobOut.model_validate(job)


@router.post("/{id_cadastro}/valores", response_model=schemas.CadastroDetalhe)
def criar_valor(
    id_cadastro: int,
    payload: schemas.ValorInput,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(require_role("admin")),
) -> schemas.CadastroDetalhe:
    return service.criar_valor(session, id_cadastro, payload)


@router.patch("/{id_cadastro}/valores/{id_valor}", response_model=schemas.CadastroDetalhe)
def atualizar_valor(
    id_cadastro: int,
    id_valor: int,
    payload: schemas.ValorInput,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(require_role("admin")),
) -> schemas.CadastroDetalhe:
    return service.atualizar_valor(session, id_cadastro, id_valor, payload)


@router.delete("/{id_cadastro}/valores/{id_valor}", response_model=schemas.CadastroDetalhe)
def remover_valor(
    id_cadastro: int,
    id_valor: int,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(require_role("admin")),
) -> schemas.CadastroDetalhe:
    return service.remover_valor(session, id_cadastro, id_valor)


@router.post("/{id_cadastro}/valores/{id_valor}/match", response_model=schemas.CadastroDetalhe)
def vincular(
    id_cadastro: int,
    id_valor: int,
    payload: schemas.MatchInput,
    session: Session = Depends(get_db_session),
    user: FRAPUsuario = Depends(get_current_user),
) -> schemas.CadastroDetalhe:
    return service.vincular(session, id_cadastro, id_valor, payload, id_usuario=user.IdUsuario)


@router.delete("/{id_cadastro}/valores/{id_valor}/match", response_model=schemas.CadastroDetalhe)
def desvincular(
    id_cadastro: int,
    id_valor: int,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(require_role("admin")),
) -> schemas.CadastroDetalhe:
    return service.desvincular(session, id_cadastro, id_valor)


@router.post("/{id_cadastro}/match-automatico", response_model=schemas.MatchAutomaticoResultado)
def match_automatico(
    id_cadastro: int,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> schemas.MatchAutomaticoResultado:
    return service.match_automatico(session, id_cadastro)


@router.get("/{id_cadastro}/frap-creditos", response_model=schemas.CreditosFrapResponse)
def creditos_frap(
    id_cadastro: int,
    texto: str | None = Query(default=None, max_length=60),
    valor: float | None = Query(default=None, gt=0),
    desde: date | None = Query(default=None),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> schemas.CreditosFrapResponse:
    return service.creditos_frap(session, id_cadastro, texto=texto, valor=valor, desde=desde)


@router.post("/{id_cadastro}/frap-creditos", response_model=schemas.CadastroDetalhe)
def adotar_creditos_frap(
    id_cadastro: int,
    payload: schemas.AdotarCreditosInput,
    session: Session = Depends(get_db_session),
    user: FRAPUsuario = Depends(require_role("admin")),
) -> schemas.CadastroDetalhe:
    return service.adotar_creditos_frap(session, id_cadastro, payload, id_usuario=user.IdUsuario)
