"""Cadastro Geral de TAGs (RI art. 431, IV, "d"): `/api/v1/ccd/tags`.

Extração por OCR + LLM no worker → rascunho → revisão e edição na tela.
Leitura e escrita seguem a matriz do módulo `ccd.tags` (`app.permissoes`).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.models import FRAPUsuario
from app.ccd.tags import schemas, service
from app.deps import get_arq_pool, get_current_user, get_db_session, get_processo_session
from app.jobs import service as jobs_service
from app.jobs.schemas import JobOut
from app.permissoes import require_modulo

router = APIRouter(
    prefix="/api/v1/ccd/tags",
    tags=["ccd:tags"],
    dependencies=[Depends(require_modulo("ccd.tags"))],
)


@router.get("", response_model=schemas.TagListResponse)
def listar(
    q: str | None = Query(default=None, max_length=100),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> schemas.TagListResponse:
    return service.listar(session, q=q)


@router.get("/{id_tag}", response_model=schemas.TagDetalhe)
def detalhe(
    id_tag: int,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> schemas.TagDetalhe:
    return service.detalhe(session, id_tag)


@router.post("/extrair", response_model=JobOut, status_code=status.HTTP_202_ACCEPTED)
async def extrair(
    payload: schemas.ExtrairInput,
    pool=Depends(get_arq_pool),
    session: Session = Depends(get_db_session),
    sessao_processo: Session = Depends(get_processo_session),
    user: FRAPUsuario = Depends(require_modulo("ccd.tags", editar=True)),
) -> JobOut:
    numero, ano = service.parse_processo(payload.processo)
    processo = f"{numero}/{ano}"
    # banco processo pode estar fora nos testes (override → None): aí só o worker valida
    if sessao_processo is not None:
        p = service.resolver_processo(sessao_processo, processo)
        if p is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="processo not found")
        if service.existe_ativo(session, int(p["IdProcesso"]), payload.evento):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="tag already exists for this event"
            )
    job = await jobs_service.enqueue_job(
        pool,
        session,
        user=user,
        tipo="ccd-tags-extrair",
        funcao="task_extrair_tag",
        argumentos={"processo": processo, "evento": payload.evento, "id_usuario": user.IdUsuario},
    )
    return JobOut.model_validate(job)


@router.patch("/{id_tag}", response_model=schemas.TagDetalhe)
def atualizar(
    id_tag: int,
    patch: schemas.TagPatch,
    session: Session = Depends(get_db_session),
    user: FRAPUsuario = Depends(require_modulo("ccd.tags", editar=True)),
) -> schemas.TagDetalhe:
    return service.atualizar(session, id_tag, patch, id_usuario=user.IdUsuario)


@router.put("/{id_tag}/obrigacoes", response_model=schemas.TagDetalhe)
def salvar_obrigacoes(
    id_tag: int,
    payload: schemas.ObrigacoesInput,
    session: Session = Depends(get_db_session),
    user: FRAPUsuario = Depends(require_modulo("ccd.tags", editar=True)),
) -> schemas.TagDetalhe:
    return service.salvar_obrigacoes(session, id_tag, payload, id_usuario=user.IdUsuario)


@router.delete("/{id_tag}", status_code=status.HTTP_204_NO_CONTENT)
def remover(
    id_tag: int,
    session: Session = Depends(get_db_session),
    user: FRAPUsuario = Depends(require_modulo("ccd.tags", editar=True)),
) -> None:
    service.remover(session, id_tag, id_usuario=user.IdUsuario)
