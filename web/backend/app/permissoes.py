"""Permissões por módulo (matriz usuário × módulo em `UsuarioPermissoes`).

- `admin`: vê e edita tudo;
- `user`: vê tudo; edita os módulos com `PodeEditar`;
- `restrito`: só vê os módulos com linha; edita os com `PodeEditar`.

"Editar" cobre tudo do módulo (criar, alterar, excluir, disparar jobs). As
chaves espelham o subnav do frontend (`src/lib/permissoes.ts`).
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status

from app.auth.models import FRAPUsuario
from app.deps import get_current_user

MODULOS: tuple[str, ...] = (
    "ccd.inicio",
    "ccd.desconto-folha",
    "ccd.beneficios",
    "ccd.automacao",
    "ccd.alertas",
    "cgad.reviews",
    "cgad.etl",
    "cgad.dashboards",
    "cgad.dataset",
    "frap.extratos",
    "frap.jobs",
    "wiki",
)


def pode(user: FRAPUsuario, modulo: str, *, editar: bool = False) -> bool:
    if user.Papel == "admin":
        return True
    # getattr: os testes do CGAD injetam o `UserORM` de tools/cgad, que não tem a relação.
    linha = next((p for p in getattr(user, "permissoes", ()) if p.Modulo == modulo), None)
    if editar:
        return linha is not None and linha.PodeEditar
    return user.Papel != "restrito" or linha is not None


def require_modulo(modulo: str, *, editar: bool = False):
    assert modulo in MODULOS, modulo

    def _enforce(user: FRAPUsuario = Depends(get_current_user)) -> FRAPUsuario:
        if not pode(user, modulo, editar=editar):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="module not authorized"
            )
        return user

    return _enforce
