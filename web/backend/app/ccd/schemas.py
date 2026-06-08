from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ProcessoCCDOut(BaseModel):
    processo: str  # numero_processo/ano_processo
    numero_processo: str
    ano_processo: str
    marcador: str | None
    data_marcador: datetime | None
    origem: str | None
    relator: str | None
    tipo: str | None
    assunto: str | None


class ProcessoCCDListResponse(BaseModel):
    items: list[ProcessoCCDOut]
    total: int
    page: int
    size: int


class RelatorOption(BaseModel):
    codigo: str
    nome: str


class MarcadorOption(BaseModel):
    descricao: str
    quantidade: int


class FiltrosCCDResponse(BaseModel):
    marcadores: list[MarcadorOption]
    sem_marcador: int
    relatores: list[RelatorOption]
