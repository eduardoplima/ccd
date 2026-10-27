from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Urgencia = Literal["alta", "media", "baixa"]
# manual = ficha da análise humana de 21/10/2026 (semente); llm = reanálise do job;
# pendente = processo sem análise (LLM fora ou erro)
Fonte = Literal["manual", "llm", "pendente"]


class AnaliseLLM(BaseModel):
    """Saída estruturada do LLM para um processo."""

    jurisdicionado: str = Field(description="Órgão/entidade cujo cumprimento é aferido")
    natureza: str = Field(
        description="Uma linha: decisão-âncora (Acórdão nº/ano) e o que se monitora"
    )
    proximo_passo: str = Field(description="Uma linha: a próxima ação concreta da CCD")
    urgencia: Urgencia
    ficha_md: str = Field(
        description="Ficha em Markdown com os itens Natureza, Situação atual, "
        "Próximo passo (CCD) e Urgência"
    )


class Analise(AnaliseLLM):
    fonte: Fonte
    evento_analisado: int | None  # última peça considerada; muda → reanalisa
    analisado_em: datetime | None


class MonitoramentoOut(BaseModel):
    processo: str
    id_processo: int | None = None  # link ao e-Contas
    tipo: str | None
    relator: str | None
    assunto: str | None
    distribuido_a: str | None = None  # servidor da CCD com distribuição aberta
    distribuido_em: datetime | None = None
    marcadores: list[str]
    dias_ccd: int | None
    ultima_peca_evento: int | None
    ultima_peca_data: datetime | None
    ultima_peca_resumo: str | None
    jurisdicionado: str | None
    natureza: str | None
    proximo_passo: str | None
    urgencia: Urgencia | None
    ficha_md: str | None
    fonte: Fonte
    analisado_em: datetime | None
    desatualizada: bool  # há peça nova depois da análise exibida


class MonitoramentosResponse(BaseModel):
    items: list[MonitoramentoOut]
    total: int
    calculado_em: datetime | None = None
