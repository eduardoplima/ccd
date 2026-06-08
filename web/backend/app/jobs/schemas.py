from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class JobOut(BaseModel):
    id_job: int = Field(validation_alias="IdFRAPJob", serialization_alias="idJob")
    arq_job_id: str = Field(validation_alias="ArqJobId", serialization_alias="arqJobId")
    tipo: str = Field(validation_alias="Tipo")
    argumentos: str | None = Field(default=None, validation_alias="Argumentos")
    status: str = Field(validation_alias="Status")
    id_usuario: int = Field(validation_alias="IdUsuario", serialization_alias="idUsuario")
    data_criacao: datetime = Field(
        validation_alias="DataCriacao", serialization_alias="dataCriacao"
    )
    data_inicio: datetime | None = Field(
        default=None, validation_alias="DataInicio", serialization_alias="dataInicio"
    )
    data_fim: datetime | None = Field(
        default=None, validation_alias="DataFim", serialization_alias="dataFim"
    )
    erro_mensagem: str | None = Field(
        default=None, validation_alias="ErroMensagem", serialization_alias="erroMensagem"
    )
    resultado: str | None = Field(default=None, validation_alias="Resultado")

    model_config = {"from_attributes": True, "populate_by_name": True}


class JobListResponse(BaseModel):
    items: list[JobOut]
    total: int
    page: int
    size: int


class ConciliarRequest(BaseModel):
    ano: int = Field(ge=2000, le=2100)
    mes: int = Field(ge=1, le=12)


class ConciliarTodosResponse(BaseModel):
    ano: int
    jobs: list[JobOut]


class UploadExtratoResponse(BaseModel):
    conta: str
    periodo: str
    bytes: int
    caminho: str


class DeletarFinalizadosResponse(BaseModel):
    deletados: int
