from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


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


class UserOut(BaseModel):
    id_usuario: int = Field(validation_alias="IdUsuario", serialization_alias="idUsuario")
    login: str = Field(validation_alias="Login")
    email: EmailStr | None = Field(default=None, validation_alias="Email")
    nome_completo: str = Field(validation_alias="NomeCompleto", serialization_alias="nomeCompleto")
    papel: str = Field(validation_alias="Papel")
    ativo: bool = Field(validation_alias="Ativo")
    deve_trocar_senha: bool = Field(
        validation_alias="DeveTrocarSenha", serialization_alias="deveTrocarSenha"
    )
    data_criacao: datetime = Field(
        validation_alias="DataCriacao", serialization_alias="dataCriacao"
    )

    model_config = {"from_attributes": True, "populate_by_name": True}
