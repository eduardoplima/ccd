from __future__ import annotations

from pydantic import BaseModel


class CandidatoAntecedentes(BaseModel):
    processo: str  # numero_processo/ano_processo
    assunto: str | None
    interessado: str | None


class CandidatosAntecedentesResponse(BaseModel):
    items: list[CandidatoAntecedentes]
    total: int


class GerarAntecedentesRequest(BaseModel):
    processos: list[str]
