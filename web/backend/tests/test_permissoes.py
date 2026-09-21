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


def _usuario(papel: str, **modulos: bool) -> FRAPUsuario:
    return FRAPUsuario(
        Login=papel,
        SenhaHash="x",
        Papel=papel,
        Ativo=True,
        permissoes=[
            UsuarioPermissao(Modulo=m.replace("_", "."), PodeEditar=e) for m, e in modulos.items()
        ],
    )


@pytest.mark.parametrize(
    ("usuario", "ver", "editar"),
    [
        (_usuario("admin"), True, True),
        (_usuario("user"), True, False),
        (_usuario("user", wiki=True), True, True),
        (_usuario("user", wiki=False), True, False),
        (_usuario("restrito"), False, False),
        (_usuario("restrito", wiki=False), True, False),
        (_usuario("restrito", wiki=True), True, True),
        (_usuario("restrito", frap_jobs=True), False, False),
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


def _seed(factory: sessionmaker[Session], papel: str, **modulos: bool) -> FRAPUsuario:
    with factory() as s:
        u = FRAPUsuario(Login=papel, SenhaHash="x", Papel=papel, Ativo=True)
        u.permissoes = [UsuarioPermissao(Modulo=m, PodeEditar=e) for m, e in modulos.items()]
        s.add(u)
        s.commit()
        s.refresh(u)
        return u


def test_user_so_cadastra_com_editar(factory: sessionmaker[Session]) -> None:
    with _client(factory, _seed(factory, "user")) as c:
        assert c.get(VER_DF).status_code == 422
        assert c.post("/api/v1/ccd/desconto-folha", json={}).status_code == 403


def test_user_com_editar_passa_do_gate(factory: sessionmaker[Session]) -> None:
    with _client(factory, _seed(factory, "user", **{DF: True})) as c:
        # 422 = passou do gate de permissão e parou na validação do payload vazio
        assert c.post("/api/v1/ccd/desconto-folha", json={}).status_code == 422


def test_restrito_so_ve_o_modulo_marcado(factory: sessionmaker[Session]) -> None:
    with _client(factory, _seed(factory, "restrito", **{DF: False})) as c:
        assert c.get(VER_DF).status_code == 422
        assert c.post("/api/v1/ccd/desconto-folha", json={}).status_code == 403
        assert c.get("/api/v1/frap/lancamentos").status_code == 403


def test_admin_substitui_matriz_do_usuario(factory: sessionmaker[Session]) -> None:
    alvo = _seed(factory, "user", wiki=True)
    admin = _seed(factory, "admin")
    with _client(factory, admin) as c:
        r = c.patch(
            f"/api/v1/usuarios/{alvo.IdUsuario}",
            json={"papel": "restrito", "permissoes": [{"modulo": DF, "editar": True}]},
        )
        assert r.status_code == 200, r.text
        assert r.json()["papel"] == "restrito"
        assert r.json()["permissoes"] == [{"modulo": DF, "editar": True}]
        r = c.patch(
            f"/api/v1/usuarios/{alvo.IdUsuario}",
            json={"permissoes": [{"modulo": "nao.existe", "editar": False}]},
        )
        assert r.status_code == 422
