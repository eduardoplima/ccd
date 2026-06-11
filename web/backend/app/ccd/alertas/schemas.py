from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel


class TipoAlerta(StrEnum):
    PARCELAMENTO_CANCELADO = "parcelamento_cancelado"


class ParcelamentoCanceladoDetalhe(BaseModel):
    # Tudo nullable: o processo pode nunca ter tido parcelamento (marcador
    # aplicado mas parcelamento nunca efetivado).
    id_parcelamento: int | None
    situacao: str | None
    situacao_descricao: str | None
    data_cancelamento: datetime | None
    numero_parcelas: int | None
    parcelas_pagas: int | None


class AlertaParcelamentoCancelado(BaseModel):
    tipo: Literal[TipoAlerta.PARCELAMENTO_CANCELADO] = TipoAlerta.PARCELAMENTO_CANCELADO
    processo: str  # numero_processo/ano_processo
    numero_processo: str
    ano_processo: str
    relator: str | None
    data_marcador: datetime | None
    detalhe: ParcelamentoCanceladoDetalhe


# Hoje só há um tipo de alerta. Quando surgir o 2º, vira:
#   Annotated[Union[...], Field(discriminator="tipo")]
AlertaOut = AlertaParcelamentoCancelado


class TipoAlertaInfo(BaseModel):
    tipo: TipoAlerta
    titulo: str
    descricao: str
    quantidade: int


class AlertasResponse(BaseModel):
    tipos: list[TipoAlertaInfo]
    items: list[AlertaOut]
    total: int
