from __future__ import annotations

from pydantic import BaseModel


class CandidatoOut(BaseModel):
    processo: str  # numero_processo/ano_processo
    assunto: str | None


class CandidatosResponse(BaseModel):
    items: list[CandidatoOut]
    total: int


class GerarRequest(BaseModel):
    processos: list[str]
