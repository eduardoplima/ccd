from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.models import FRAPUsuario
from app.deps import get_current_user, get_db_session, require_role
from app.desconto_folha import fases as fases_service
from app.desconto_folha import service
from app.desconto_folha.schemas import (
    AtrasoSistemicoResponse,
    AtribuirOrgaoInput,
    AtribuirOrgaoResultado,
    CadastroManualInput,
    CadastroManualListResponse,
    CpfSemSiaiResponse,
    DebitosFaseResumo,
    DepositosOrgaoResponse,
    EnviadosListResponse,
    LancamentosDoOrgaoResponse,
    FasesResumo,
    MatchManualInput,
    MatchManualResultado,
    OrgaoAgregadoListResponse,
    OrgaoDisponivel,
    ParcelaDuplicadaResponse,
    ParcelasPessoaResponse,
    PessoaAgregadaListResponse,
    PessoasDoOrgaoResponse,
    RepasseMultiParcelaResponse,
)

router = APIRouter(prefix="/api/v1/frap/desconto-folha", tags=["frap:desconto-folha"])


# ---------------------------------------------------------------------------
# Por pessoa
# ---------------------------------------------------------------------------


@router.get("/pessoas", response_model=PessoaAgregadaListResponse)
def listar_pessoas(
    ano: int | None = Query(default=None, ge=2000, le=2100),
    mes: int | None = Query(default=None, ge=1, le=12),
    status_: str | None = Query(default=None, alias="status"),
    q: str | None = Query(default=None, max_length=200),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    sort_by: Literal[
        "nome",
        "cpf",
        "orgao",
        "valor_atualizado",
        "qtd_notificacoes",
        "qtd_debitos_notificados",
        "valor_debitos_notificados",
        "esperado",
    ]
    | None = Query(default=None, alias="sortBy"),
    sort_dir: Literal["asc", "desc"] = Query(default="desc", alias="sortDir"),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> PessoaAgregadaListResponse:
    return service.list_pessoas(
        session,
        ano=ano,
        mes=mes,
        status=status_,
        q=q,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@router.get("/pessoas/{cpfcnpj}/parcelas", response_model=ParcelasPessoaResponse)
def parcelas_da_pessoa(
    cpfcnpj: str,
    ano: int | None = Query(default=None, ge=2000, le=2100),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> ParcelasPessoaResponse:
    return service.parcelas_da_pessoa(session, cpfcnpj=cpfcnpj, ano=ano)


@router.patch("/pessoas/{cpfcnpj}/orgao", response_model=AtribuirOrgaoResultado)
def atribuir_orgao_pessoa(
    cpfcnpj: str,
    payload: AtribuirOrgaoInput,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(require_role("admin")),
) -> AtribuirOrgaoResultado:
    resultado = service.atribuir_orgao_pessoa(session, cpfcnpj=cpfcnpj, id_orgao=payload.id_orgao)
    if resultado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="pessoa or orgao not found",
        )
    return resultado


# ---------------------------------------------------------------------------
# Fases (atribuído / enviado / agendado / pago) — eixo por pessoa
# ---------------------------------------------------------------------------


@router.get("/pessoas/{cpfcnpj}/fases", response_model=FasesResumo)
def fases_resumo(
    cpfcnpj: str,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> FasesResumo:
    return fases_service.resumo_fases(session, cpfcnpj=cpfcnpj)


@router.get("/pessoas/{cpfcnpj}/fases/totais", response_model=DebitosFaseResumo)
def fases_totais(
    cpfcnpj: str,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> DebitosFaseResumo:
    return fases_service.totais_detalhe(session, cpfcnpj=cpfcnpj)


@router.get("/pessoas/{cpfcnpj}/fases/debitos-notificados", response_model=DebitosFaseResumo)
def fases_debitos_notificados(
    cpfcnpj: str,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> DebitosFaseResumo:
    return fases_service.debitos_notificados_detalhe(session, cpfcnpj=cpfcnpj)


@router.get("/pessoas/{cpfcnpj}/fases/enviados", response_model=EnviadosListResponse)
def fases_enviados(
    cpfcnpj: str,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> EnviadosListResponse:
    return EnviadosListResponse(items=fases_service.enviados_detalhe(session, cpfcnpj=cpfcnpj))


# ---------------------------------------------------------------------------
# Por órgão
# ---------------------------------------------------------------------------


@router.get("/orgaos", response_model=OrgaoAgregadoListResponse)
def listar_orgaos(
    ano: int | None = Query(default=None, ge=2000, le=2100),
    mes: int | None = Query(default=None, ge=1, le=12),
    q: str | None = Query(default=None, max_length=200),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> OrgaoAgregadoListResponse:
    return service.list_orgaos(session, ano=ano, mes=mes, q=q, page=page, size=size)


@router.get("/orgaos/{id_orgao}/pessoas", response_model=PessoasDoOrgaoResponse)
def pessoas_do_orgao(
    id_orgao: int,
    ano: int | None = Query(default=None, ge=2000, le=2100),
    mes: int | None = Query(default=None, ge=1, le=12),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> PessoasDoOrgaoResponse:
    # 0 é o sentinela para "sem órgão notificado" (df.IdOrgaoNotificado IS NULL).
    alvo = None if id_orgao == 0 else id_orgao
    res = service.pessoas_do_orgao(session, id_orgao=alvo, ano=ano, mes=mes)
    if res is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="orgão sem parcelas")
    return res


@router.get("/orgaos/{id_orgao}/depositos", response_model=DepositosOrgaoResponse)
def depositos_orgao(
    id_orgao: int,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> DepositosOrgaoResponse:
    if id_orgao <= 0:
        return DepositosOrgaoResponse(id_orgao=id_orgao, cnpj=None, qtd=0, total=0)  # type: ignore[arg-type]
    return service.depositos_do_orgao(session, id_orgao=id_orgao)


@router.get(
    "/orgaos/{id_orgao}/depositos/lancamentos",
    response_model=LancamentosDoOrgaoResponse,
)
def depositos_orgao_lancamentos(
    id_orgao: int,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> LancamentosDoOrgaoResponse:
    if id_orgao <= 0:
        return LancamentosDoOrgaoResponse(id_orgao=id_orgao, items=[])
    return service.lancamentos_do_orgao(session, id_orgao=id_orgao)


@router.get("/orgaos-disponiveis", response_model=list[OrgaoDisponivel])
def orgaos_disponiveis(
    q: str | None = Query(default=None),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> list[OrgaoDisponivel]:
    rows = service.list_orgaos_disponiveis(session, busca=q)
    return [OrgaoDisponivel(id_orgao=r["idOrgao"], nome_orgao=r["nomeOrgao"]) for r in rows]


# ---------------------------------------------------------------------------
# Cadastro manual
# ---------------------------------------------------------------------------


@router.get("/cadastro", response_model=CadastroManualListResponse)
def listar_cadastro(
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> CadastroManualListResponse:
    return service.listar_cadastro_manual(session, busca=q, page=page, size=size)


@router.post("/cadastro", status_code=status.HTTP_201_CREATED)
def criar_cadastro(
    payload: CadastroManualInput,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(require_role("admin")),
) -> dict[str, int]:
    cpf = "".join(c for c in payload.cpfcnpj if c.isdigit())
    if len(cpf) not in (11, 14):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="cpfCnpj must have 11 or 14 digits"
        )
    id_pai = service.criar_cadastro_manual(
        session,
        cpfcnpj=cpf,
        nome_pessoa=payload.nome_pessoa,
        id_orgao_notificado=payload.id_orgao_notificado,
        nome_orgao_notificado=payload.nome_orgao_notificado,
        parcelas=[p.model_dump() for p in payload.parcelas],
    )
    return {"idDescontoFolha": id_pai}


@router.delete("/cadastro/{id_desconto_folha}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_cadastro(
    id_desconto_folha: int,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(require_role("admin")),
) -> None:
    res = service.deletar_cadastro_manual(session, id_desconto_folha)
    if res == "not_found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    if res == "not_manual":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="record is not manual (Origem != 'M')",
        )
    if res == "has_match":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="cadastro has matches; delete matches first",
        )
    return None


# ---------------------------------------------------------------------------
# Match manual
# ---------------------------------------------------------------------------


@router.post(
    "/matches/manual",
    response_model=MatchManualResultado,
    status_code=status.HTTP_201_CREATED,
)
def criar_match_manual(
    payload: MatchManualInput,
    session: Session = Depends(get_db_session),
    user: FRAPUsuario = Depends(require_role("admin")),
) -> MatchManualResultado:
    return service.criar_match_manual(
        session,
        id_lancamento_frap=payload.id_lancamento_frap,
        ids_parcela=payload.ids_parcela,
        id_usuario=user.IdUsuario,
        observacao=payload.observacao,
    )


@router.delete("/matches/manual/{id_match}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_match_manual(
    id_match: int,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(require_role("admin")),
) -> None:
    res = service.deletar_match_manual(session, id_match)
    if res == "not_found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    if res == "not_manual":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="match is not manual; cannot delete via this endpoint",
        )
    return None


# ---------------------------------------------------------------------------
# Tipologias de análise
# ---------------------------------------------------------------------------


@router.get("/tipologias/repasse-multi-parcela", response_model=RepasseMultiParcelaResponse)
def tipologia_repasse_multi(
    ano: int | None = Query(default=None, ge=2000, le=2100),
    mes: int | None = Query(default=None, ge=1, le=12),
    cpfcnpj: str | None = Query(default=None, alias="cpfCnpj", min_length=11, max_length=14),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> RepasseMultiParcelaResponse:
    return service.tipologia_repasse_multi_parcela(session, ano=ano, mes=mes, cpfcnpj=cpfcnpj)


@router.get("/tipologias/cpf-sem-siaipessoal", response_model=CpfSemSiaiResponse)
def tipologia_cpf_sem_siai(
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> CpfSemSiaiResponse:
    return service.tipologia_cpf_sem_siaipessoal(session)


@router.get("/tipologias/parcela-duplicada", response_model=ParcelaDuplicadaResponse)
def tipologia_parcela_duplicada(
    ano: int | None = Query(default=None, ge=2000, le=2100),
    mes: int | None = Query(default=None, ge=1, le=12),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> ParcelaDuplicadaResponse:
    return service.tipologia_parcela_duplicada(session, ano=ano, mes=mes)


@router.get("/tipologias/atraso-sistemico", response_model=AtrasoSistemicoResponse)
def tipologia_atraso_sistemico(
    ano: int | None = Query(default=None, ge=2000, le=2100),
    meses_consecutivos: int = Query(default=3, ge=2, le=24, alias="mesesConsecutivos"),
    pct_minimo: float = Query(default=0.2, ge=0.0, le=1.0, alias="pctMinimo"),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> AtrasoSistemicoResponse:
    return service.tipologia_atraso_sistemico(
        session, ano=ano, meses_consecutivos=meses_consecutivos, pct_minimo=pct_minimo
    )
