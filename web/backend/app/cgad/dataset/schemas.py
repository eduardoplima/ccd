"""DTOs do conjunto de dados anotado (CGAD)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, model_validator


# Mesmo esquema de 4 classes de `cgad.ner_metrics.ENTITY_LABELS` — repetido aqui
# de propósito: aquele módulo importa spacy no topo e não cabe no processo da API.
Label = Literal["MULTA", "OBRIGACAO", "RECOMENDACAO", "RESSARCIMENTO"]
StatusAnotacao = Literal["pending", "done"]
Origem = Literal["decicontas", "ampliacao"]


class Span(BaseModel):
    """Um span de caractere. Mesmo formato do campo ``entities`` do
    ``decicontas.json`` — o export é um passthrough."""

    start: int
    end: int
    label: Label

    @model_validator(mode="after")
    def _check(self) -> "Span":
        if self.start < 0 or self.end <= self.start:
            raise ValueError("span inválido: exige 0 <= start < end")
        return self


class AnotacaoPayload(BaseModel):
    spans: list[Span]
    status: StatusAnotacao = "done"

    @model_validator(mode="after")
    def _no_overlap(self) -> "AnotacaoPayload":
        ordenados = sorted(self.spans, key=lambda s: (s.start, s.end))
        for anterior, atual in zip(ordenados, ordenados[1:]):
            if atual.start < anterior.end:
                raise ValueError(
                    f"spans sobrepostos: [{anterior.start},{anterior.end}) "
                    f"e [{atual.start},{atual.end})"
                )
        return self


class DocumentoListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    processo: Optional[str] = None
    codigo_tipo_processo: Optional[str] = None
    data_sessao: Optional[datetime] = None
    origem: Origem
    trecho: str
    status: StatusAnotacao
    total_spans: int


class DocumentoListPage(BaseModel):
    items: list[DocumentoListItem]
    page: int
    page_size: int
    total: int
    pendentes: int
    concluidos: int
    com_entidades: int = 0


class DocumentoDetail(BaseModel):
    id: int
    processo: Optional[str] = None
    codigo_tipo_processo: Optional[str] = None
    data_sessao: Optional[datetime] = None
    origem: Origem
    texto: str
    spans: list[Span]
    status: StatusAnotacao
    data_conclusao: Optional[datetime] = None
    proximo_pendente: Optional[int] = None


class ProgressoAnotador(BaseModel):
    anotador: str
    total: int
    concluidos: int
    spans: int


class ConcordanciaPar(BaseModel):
    """F1 de span com IoU >= 0.5 sobre os documentos que os DOIS concluíram."""

    a: str
    b: str
    documentos_comuns: int
    f1: Optional[float] = None


class Progresso(BaseModel):
    documentos: int
    anotadores: list[ProgressoAnotador]
    concordancia: list[ConcordanciaPar]


TipoDivergencia = Literal["rotulo", "fronteira", "ausente"]


class DivergenciaPorRotulo(BaseModel):
    label: Label
    acertos: int
    divergencias: int
    f1: Optional[float] = None


class DivergenciaPorTipo(BaseModel):
    tipo: TipoDivergencia
    total: int


class DivergenciaDoc(BaseModel):
    id: int
    processo: Optional[str] = None
    codigo_tipo_processo: Optional[str] = None
    score: float
    divergencias: int
    spans_por_anotador: dict[str, int]
    rotulos: list[Label]
    tipos: list[TipoDivergencia]


class Divergencias(BaseModel):
    anotadores: list[str]
    documentos_comuns: int
    por_rotulo: list[DivergenciaPorRotulo]
    por_tipo: list[DivergenciaPorTipo]
    documentos: list[DivergenciaDoc]


class AnotacaoAnotador(BaseModel):
    anotador: str
    spans: list[Span]


class DivergenciaDetail(BaseModel):
    id: int
    processo: Optional[str] = None
    codigo_tipo_processo: Optional[str] = None
    texto: str
    anotacoes: list[AnotacaoAnotador]


class DocumentoExport(BaseModel):
    """Shape do ``decicontas.json``, para o corpus sair pronto para publicação."""

    id: int
    text: str
    tokens: list[str]
    ner_tags: list[str]
    token_offsets: list[list[int]]
    entities: list[Span]
