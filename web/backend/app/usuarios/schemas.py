from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


_LOGIN_PATTERN = r"^[a-z0-9][a-z0-9._-]{1,63}$"


class UsuarioOut(BaseModel):
    id_usuario: int = Field(validation_alias="IdUsuario", serialization_alias="idUsuario")
    login: str = Field(validation_alias="Login")
    email: EmailStr = Field(validation_alias="Email")
    nome_completo: str = Field(validation_alias="NomeCompleto", serialization_alias="nomeCompleto")
    papel: str = Field(validation_alias="Papel")
    ativo: bool = Field(validation_alias="Ativo")
    data_criacao: datetime = Field(
        validation_alias="DataCriacao", serialization_alias="dataCriacao"
    )
    data_atualizacao: datetime = Field(
        validation_alias="DataAtualizacao", serialization_alias="dataAtualizacao"
    )

    model_config = {"from_attributes": True, "populate_by_name": True}


class UsuarioListResponse(BaseModel):
    items: list[UsuarioOut]
    total: int
    page: int
    size: int


class UsuarioCreateRequest(BaseModel):
    login: str = Field(min_length=3, max_length=64, pattern=_LOGIN_PATTERN)
    email: EmailStr
    nome_completo: str = Field(min_length=1, max_length=255, validation_alias="nomeCompleto")
    papel: Literal["user", "admin"] = "user"

    model_config = {"populate_by_name": True}


class UsuarioCreateResponse(BaseModel):
    usuario: UsuarioOut
    senha_temporaria: str = Field(serialization_alias="senhaTemporaria")

    model_config = {"populate_by_name": True}


class UsuarioUpdateRequest(BaseModel):
    nome_completo: str | None = Field(
        default=None, min_length=1, max_length=255, validation_alias="nomeCompleto"
    )
    papel: Literal["user", "admin"] | None = None
    ativo: bool | None = None

    model_config = {"populate_by_name": True}


class ResetSenhaResponse(BaseModel):
    senha_temporaria: str = Field(serialization_alias="senhaTemporaria")

    model_config = {"populate_by_name": True}


class TrocarSenhaRequest(BaseModel):
    senha_atual: str = Field(min_length=1, max_length=72, validation_alias="senhaAtual")
    senha_nova: str = Field(min_length=8, max_length=72, validation_alias="senhaNova")

    model_config = {"populate_by_name": True}
