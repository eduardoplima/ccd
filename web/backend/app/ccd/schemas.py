from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class ProcessoCCDOut(BaseModel):
    processo: str  # numero_processo/ano_processo
    numero_processo: str
    ano_processo: str
    marcador: str | None
    data_marcador: datetime | None
    entrada_ccd: datetime | None = None  # última entrada na CCD (Lotes/Itens_Lote)
    dias_ccd: int | None = None
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


class PrescricaoCCDOut(BaseModel):
    processo: str
    numero_processo: str
    ano_processo: str
    relator: str | None
    assunto: str | None
    responsaveis: str | None  # nomes distintos dos débitos abertos, separados por ", "
    categoria: str  # "prescrito" | "risco" | "ok" | "sem_referencia"
    fonte_base: str | None  # "citação" | "trânsito"
    data_base: datetime | None
    data_prescricao: date | None
    dias_decorridos: int | None
    qtd_debitos: int
    valor_total: float


class PrescricaoCCDListResponse(BaseModel):
    items: list[PrescricaoCCDOut]
    total: int
