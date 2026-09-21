from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth.models import FRAPUsuario, UsuarioPermissao
from app.ccd.desconto_folha.router import router as desconto_folha_router
from app.deps import get_current_user, get_db_session
from app.lancamentos.router import router as lancamentos_router
from app.permissoes import pode
from app.usuarios.router import router as usuarios_router

DF = "ccd.desconto-folha"
# Sem `cpf` → 422: passou do gate de leitura e parou na validação (não toca o banco).
VER_DF = "/api/v1/ccd/desconto-folha/retencoes"


def _linhas(modulos: dict[str, tuple[bool, bool]]) -> list[UsuarioPermissao]:
    return [UsuarioPermissao(Modulo=m, PodeVer=v, PodeEditar=e) for m, (v, e) in modulos.items()]


def _usuario(papel: str, **modulos: tuple[bool, bool]) -> FRAPUsuario:
    """`modulos`: módulo → (ver, editar)."""
    return FRAPUsuario(
        Login=papel, SenhaHash="x", Papel=papel, Ativo=True, permissoes=_linhas(modulos)
    )


@pytest.mark.parametrize(
    ("usuario", "ver", "editar"),
    [
        (_usuario("admin"), True, True),
        (_usuario("admin", wiki=(False, False)), True, True),
        (_usuario("user"), True, False),
        (_usuario("user", wiki=(True, True)), True, True),
        (_usuario("user", wiki=(False, False)), False, False),
        (_usuario("user", wiki=(False, True)), False, False),
    ],
)
def test_pode_tabela_verdade(usuario: FRAPUsuario, ver: bool, editar: bool) -> None:
    assert pode(usuario, "wiki") is ver
    assert pode(usuario, "wiki", editar=True) is editar


@pytest.fixture
def factory(in_memory_engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=in_memory_engine, autoflush=False, expire_on_commit=False)


def _client(factory: sessionmaker[Session], usuario: FRAPUsuario) -> TestClient:
    def override_db() -> Iterator[Session]:
        with factory() as s:
            yield s

    app = FastAPI()
    for r in (desconto_folha_router, lancamentos_router, usuarios_router):
        app.include_router(r)
    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_current_user] = lambda: usuario
    return TestClient(app)


def _seed(factory: sessionmaker[Session], papel: str, **modulos: tuple[bool, bool]) -> FRAPUsuario:
    with factory() as s:
        u = FRAPUsuario(Login=papel, SenhaHash="x", Papel=papel, Ativo=True)
        u.permissoes = _linhas(modulos)
        s.add(u)
        s.commit()
        s.refresh(u)
        return u


def test_user_so_cadastra_com_editar(factory: sessionmaker[Session]) -> None:
    with _client(factory, _seed(factory, "user")) as c:
        assert c.get(VER_DF).status_code == 422
        assert c.post("/api/v1/ccd/desconto-folha", json={}).status_code == 403


def test_user_com_editar_passa_do_gate(factory: sessionmaker[Session]) -> None:
    with _client(factory, _seed(factory, "user", **{DF: (True, True)})) as c:
        # 422 = passou do gate de permissão e parou na validação do payload vazio
        assert c.post("/api/v1/ccd/desconto-folha", json={}).status_code == 422


def test_visualizacao_removida_barra_o_modulo(factory: sessionmaker[Session]) -> None:
    with _client(factory, _seed(factory, "user", **{"frap.extratos": (False, False)})) as c:
        assert c.get(VER_DF).status_code == 422
        assert c.post("/api/v1/ccd/desconto-folha", json={}).status_code == 403
        assert c.get("/api/v1/frap/lancamentos").status_code == 403


def test_admin_substitui_matriz_do_usuario(factory: sessionmaker[Session]) -> None:
    alvo = _seed(factory, "user", wiki=(True, True))
    admin = _seed(factory, "admin")
    with _client(factory, admin) as c:
        r = c.patch(
            f"/api/v1/usuarios/{alvo.IdUsuario}",
            json={
                "permissoes": [
                    {"modulo": DF, "ver": True, "editar": True},
                    {"modulo": "wiki", "ver": False, "editar": False},
                    {"modulo": "frap.jobs", "ver": True, "editar": False},  # default: não grava
                ]
            },
        )
        assert r.status_code == 200, r.text
        assert sorted(r.json()["permissoes"], key=lambda p: p["modulo"]) == [
            {"modulo": DF, "ver": True, "editar": True},
            {"modulo": "wiki", "ver": False, "editar": False},
        ]
        assert (
            c.patch(f"/api/v1/usuarios/{alvo.IdUsuario}", json={"papel": "restrito"}).status_code
            == 422
        )
        r = c.patch(
            f"/api/v1/usuarios/{alvo.IdUsuario}",
            json={"permissoes": [{"modulo": "nao.existe", "editar": False}]},
        )
        assert r.status_code == 422
