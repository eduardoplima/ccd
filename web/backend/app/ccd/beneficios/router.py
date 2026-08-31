from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.auth.models import FRAPUsuario
from app.ccd.beneficios import export as export_service
from app.ccd.beneficios import service
from app.ccd.beneficios.dominios import obter_dominios
from app.ccd.beneficios.schemas import (
    BeneficioInput,
    BeneficioItem,
    BeneficioListResponse,
    BeneficioResumo,
    BeneficioUpdate,
    DominiosResponse,
    ExportInput,
    TransicaoInput,
)
from app.deps import get_arq_pool, get_current_user, get_db_session, require_role
from app.jobs import service as jobs_service
from app.jobs.schemas import JobOut

router = APIRouter(prefix="/api/v1/ccd/beneficios", tags=["ccd:beneficios"])


@router.get("", response_model=BeneficioListResponse)
def listar(
    q: str | None = Query(default=None, max_length=200),
    status_: str | None = Query(default=None, alias="status"),
    situacao_efetivacao: int | None = Query(default=None, alias="situacaoEfetivacao", ge=1, le=2),
    id_tipo: int | None = Query(default=None, alias="idTipo"),
    origem: str | None = Query(default=None, max_length=20),
    fonte: Literal["propostas", "carteira"] | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    sort_by: Literal["processo", "nome", "valor", "dataOcorrencia", "origem", "dataInclusao"]
    | None = Query(default=None, alias="sortBy"),
    sort_dir: Literal["asc", "desc"] = Query(default="desc", alias="sortDir"),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> BeneficioListResponse:
    return service.listar(
        session,
        q=q,
        status=status_,
        situacao_efetivacao=situacao_efetivacao,
        id_tipo=id_tipo,
        origem=origem,
        fonte=fonte,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@router.get("/resumo", response_model=BeneficioResumo)
def resumo(
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> BeneficioResumo:
    return service.resumo(session)


@router.get("/dominios", response_model=DominiosResponse)
def dominios(
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> DominiosResponse:
    return obter_dominios(session)


@router.get("/{id_beneficio}", response_model=BeneficioItem)
def obter(
    id_beneficio: int,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> BeneficioItem:
    item = service.obter(session, id_beneficio)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="beneficio not found")
    return item


@router.post("", status_code=status.HTTP_201_CREATED)
def criar(
    payload: BeneficioInput,
    session: Session = Depends(get_db_session),
    user: FRAPUsuario = Depends(get_current_user),
) -> dict[str, int]:
    novo_id = service.criar(
        session, dados=payload.model_dump(exclude_unset=True), id_usuario=user.IdUsuario
    )
    return {"idBeneficio": novo_id}


@router.patch("/{id_beneficio}", response_model=BeneficioItem)
def atualizar(
    id_beneficio: int,
    payload: BeneficioUpdate,
    session: Session = Depends(get_db_session),
    user: FRAPUsuario = Depends(get_current_user),
) -> BeneficioItem:
    resultado = service.atualizar(
        session,
        id_beneficio,
        dados=payload.model_dump(exclude_unset=True),
        id_usuario=user.IdUsuario,
    )
    if resultado == "not_found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="beneficio not found")
    if resultado == "enviado":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="beneficio already sent (ENVIADO)"
        )
    item = service.obter(session, id_beneficio)
    assert item is not None
    return item


@router.delete("/{id_beneficio}", status_code=status.HTTP_204_NO_CONTENT)
def deletar(
    id_beneficio: int,
    session: Session = Depends(get_db_session),
    user: FRAPUsuario = Depends(get_current_user),
) -> Response:
    resultado = service.deletar(session, id_beneficio, id_usuario=user.IdUsuario)
    if resultado == "not_found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="beneficio not found")
    if resultado == "nao_manual":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="detected candidates must be discarded (status), not deleted",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{id_beneficio}/status", response_model=BeneficioItem)
def transicionar(
    id_beneficio: int,
    payload: TransicaoInput,
    session: Session = Depends(get_db_session),
    user: FRAPUsuario = Depends(get_current_user),
) -> BeneficioItem:
    if payload.status == "VALIDADO":
        # desfazer envio (ENVIADO -> VALIDADO) é restrito a admin
        atual = service.obter(session, id_beneficio)
        if atual is not None and atual.status == "ENVIADO" and user.Papel != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="undo send requires admin"
            )
    resultado = service.transicionar(
        session, id_beneficio, novo_status=payload.status, id_usuario=user.IdUsuario
    )
    if resultado == "not_found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="beneficio not found")
    if resultado != "ok":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=resultado)
    item = service.obter(session, id_beneficio)
    assert item is not None
    return item


@router.post("/export")
def exportar(
    payload: ExportInput,
    session: Session = Depends(get_db_session),
    user: FRAPUsuario = Depends(get_current_user),
) -> Response:
    try:
        nome, conteudo, media = export_service.exportar(
            session,
            ids=payload.ids,
            formato=payload.formato,
            marcar_enviado=payload.marcar_enviado,
            id_usuario=user.IdUsuario,
        )
    except export_service.ExportVazio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="no VALIDADO beneficios to export"
        ) from None
    return Response(
        content=conteudo,
        media_type=media,
        headers={"Content-Disposition": f'attachment; filename="{nome}"'},
    )


@router.post("/deteccao", response_model=JobOut, status_code=status.HTTP_202_ACCEPTED)
async def disparar_deteccao(
    pool=Depends(get_arq_pool),
    session: Session = Depends(get_db_session),
    user: FRAPUsuario = Depends(require_role("admin")),
) -> JobOut:
    """Disparo manual da detecção (o cron quinzenal roda sem FRAPJob)."""
    job = await jobs_service.enqueue_job(
        pool,
        session,
        user=user,
        tipo="detectar-beneficios",
        funcao="task_detectar_beneficios",
    )
    return JobOut.model_validate(job)
