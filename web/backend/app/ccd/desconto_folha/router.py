from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.models import FRAPUsuario
from app.deps import get_current_user, get_db_session, require_role
from app.ccd.desconto_folha import fases as fases_service
from app.ccd.desconto_folha import monitoramento as monitoramento_service
from app.ccd.desconto_folha import service
from app.ccd.desconto_folha.schemas import (
    AtrasoSistemicoResponse,
    AtribuirOrgaoInput,
    AtribuirOrgaoResultado,
    CadastroManualDetail,
    CadastroManualInput,
    CadastroManualListResponse,
    CadastroManualUpdate,
    MonitoramentoInput,
    MonitoramentoItem,
    MonitoramentoListResponse,
    MonitoramentoResumo,
    MonitoramentoUpdate,
    ParcelaManualInput,
    ParcelaManualUpdate,
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

router = APIRouter(prefix="/api/v1/ccd/desconto-folha", tags=["ccd:desconto-folha"])


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


@router.get("/cadastro/{id_desconto_folha}", response_model=CadastroManualDetail)
def obter_cadastro(
    id_desconto_folha: int,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> CadastroManualDetail:
    detail = service.obter_cadastro_manual(session, id_desconto_folha)
    if detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    return detail


def _raise_guard(res: str) -> None:
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
            detail="parcela has matches; delete matches first",
        )


@router.patch("/cadastro/{id_desconto_folha}", status_code=status.HTTP_204_NO_CONTENT)
def atualizar_cadastro(
    id_desconto_folha: int,
    payload: CadastroManualUpdate,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(require_role("admin")),
) -> None:
    res = service.atualizar_cadastro_manual(
        session, id_desconto_folha, dados=payload.model_dump(exclude_unset=True)
    )
    _raise_guard(res)


@router.post("/cadastro/{id_desconto_folha}/parcelas", status_code=status.HTTP_201_CREATED)
def criar_parcela(
    id_desconto_folha: int,
    payload: ParcelaManualInput,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(require_role("admin")),
) -> dict[str, int]:
    res = service.criar_parcela_manual(session, id_desconto_folha, parcela=payload.model_dump())
    if isinstance(res, str):
        _raise_guard(res)
    return {"idFrapParcela": int(res)}  # type: ignore[arg-type]


@router.patch(
    "/cadastro/{id_desconto_folha}/parcelas/{id_parcela}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def atualizar_parcela(
    id_desconto_folha: int,
    id_parcela: int,
    payload: ParcelaManualUpdate,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(require_role("admin")),
) -> None:
    res = service.atualizar_parcela_manual(
        session, id_desconto_folha, id_parcela, dados=payload.model_dump(exclude_unset=True)
    )
    _raise_guard(res)


@router.delete(
    "/cadastro/{id_desconto_folha}/parcelas/{id_parcela}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deletar_parcela(
    id_desconto_folha: int,
    id_parcela: int,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(require_role("admin")),
) -> None:
    res = service.deletar_parcela_manual(session, id_desconto_folha, id_parcela)
    _raise_guard(res)


# ---------------------------------------------------------------------------
# Monitoramento (substitui a planilha "Monitoramento Desconto em Folha.xlsx")
# ---------------------------------------------------------------------------


@router.get("/monitoramento", response_model=MonitoramentoListResponse)
def listar_monitoramento(
    q: str | None = Query(default=None, max_length=200),
    grupo: Literal["GERAL", "ANTIGO", "NEREU"] | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    sort_by: Literal["processo", "nome", "grupo", "dataNotificacao", "valorOriginal"]
    | None = Query(default=None, alias="sortBy"),
    sort_dir: Literal["asc", "desc"] = Query(default="asc", alias="sortDir"),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> MonitoramentoListResponse:
    return monitoramento_service.listar(
        session, q=q, grupo=grupo, page=page, size=size, sort_by=sort_by, sort_dir=sort_dir
    )


@router.get("/monitoramento/resumo", response_model=MonitoramentoResumo)
def resumo_monitoramento(
    grupo: Literal["GERAL", "ANTIGO", "NEREU"] | None = Query(default=None),
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> MonitoramentoResumo:
    return monitoramento_service.resumo(session, grupo=grupo)


@router.get("/monitoramento/{id_monitoramento}", response_model=MonitoramentoItem)
def obter_monitoramento(
    id_monitoramento: int,
    session: Session = Depends(get_db_session),
    _: FRAPUsuario = Depends(get_current_user),
) -> MonitoramentoItem:
    item = monitoramento_service.obter(session, id_monitoramento)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    return item


def _validar_cpf_monitoramento(payload: MonitoramentoInput | MonitoramentoUpdate) -> None:
    if payload.cpfcnpj is not None:
        digits = "".join(c for c in payload.cpfcnpj if c.isdigit())
        if len(digits) not in (11, 14):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="cpfCnpj must have 11 or 14 digits",
            )
        payload.cpfcnpj = digits


@router.post("/monitoramento", status_code=status.HTTP_201_CREATED)
def criar_monitoramento(
    payload: MonitoramentoInput,
    session: Session = Depends(get_db_session),
    user: FRAPUsuario = Depends(require_role("admin")),
) -> dict[str, int]:
    _validar_cpf_monitoramento(payload)
    res = monitoramento_service.criar(
        session, dados=payload.model_dump(), id_usuario=user.IdUsuario
    )
    if res == "duplicado":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="processo already monitored in this grupo",
        )
    return {"idMonitoramento": int(res)}  # type: ignore[arg-type]


@router.patch("/monitoramento/{id_monitoramento}", response_model=MonitoramentoItem)
def atualizar_monitoramento(
    id_monitoramento: int,
    payload: MonitoramentoUpdate,
    session: Session = Depends(get_db_session),
    user: FRAPUsuario = Depends(require_role("admin")),
) -> MonitoramentoItem:
    _validar_cpf_monitoramento(payload)
    res = monitoramento_service.atualizar(
        session,
        id_monitoramento,
        dados=payload.model_dump(exclude_unset=True),
        id_usuario=user.IdUsuario,
    )
    if res == "not_found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    if res == "duplicado":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="processo already monitored in this grupo",
        )
    item = monitoramento_service.obter(session, id_monitoramento)
    if item is None:  # pragma: no cover — corrida improvável entre update e select
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    return item


@router.delete("/monitoramento/{id_monitoramento}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_monitoramento(
    id_monitoramento: int,
    session: Session = Depends(get_db_session),
    user: FRAPUsuario = Depends(require_role("admin")),
) -> None:
    res = monitoramento_service.deletar(session, id_monitoramento, id_usuario=user.IdUsuario)
    if res == "not_found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
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
