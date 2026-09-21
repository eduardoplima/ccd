from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    login: str = Field(min_length=1, max_length=64)
    senha: str = Field(min_length=1, max_length=72)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class PermissaoItem(BaseModel):
    modulo: str = Field(validation_alias="Modulo")
    ver: bool = Field(default=True, validation_alias="PodeVer")
    editar: bool = Field(default=False, validation_alias="PodeEditar")

    model_config = {"from_attributes": True, "populate_by_name": True}


class UserOut(BaseModel):
    id_usuario: int = Field(validation_alias="IdUsuario", serialization_alias="idUsuario")
    login: str = Field(validation_alias="Login")
    # str, não EmailStr: saída não revalida o que já está no banco (ex.: "admin@local").
    email: str | None = Field(default=None, validation_alias="Email")
    nome_completo: str = Field(validation_alias="NomeCompleto", serialization_alias="nomeCompleto")
    papel: str = Field(validation_alias="Papel")
    ativo: bool = Field(validation_alias="Ativo")
    deve_trocar_senha: bool = Field(
        validation_alias="DeveTrocarSenha", serialization_alias="deveTrocarSenha"
    )
    data_criacao: datetime = Field(
        validation_alias="DataCriacao", serialization_alias="dataCriacao"
    )
    permissoes: list[PermissaoItem] = []

    model_config = {"from_attributes": True, "populate_by_name": True}
