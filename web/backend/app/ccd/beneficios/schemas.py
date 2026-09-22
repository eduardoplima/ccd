"""DTOs dos benefícios da CCD (staging do SisBenefícios).

Os campos Id* de classificação carregam os IDs dos domínios do BdBeneficio
(Beneficio_TipoBeneficio, Beneficio_AreaTematica, ...) — ver `dominios.py`.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

OrigemBeneficio = Literal[
    "MANUAL", "DEBITO", "BOLETO", "PGE", "FOLHA", "DIVIDA_ATIVA", "FRAP", "PROPOSTA"
]


class _BeneficioCampos(BaseModel):
    memoria_calculo: str | None = Field(default=None, max_length=200, alias="memoriaCalculo")
    valor_quantidade: Decimal | None = Field(default=None, alias="valorQuantidade")
    justificativa: str | None = Field(default=None, max_length=500)
    id_situacao_efetivacao: Literal[1, 2] | None = Field(
        default=None, alias="idSituacaoEfetivacao"
    )  # 1=Efetivo, 2=Potencial (Beneficio_SituacaoEfetivacao)
    id_area_tematica: int | None = Field(default=None, alias="idAreaTematica")
    id_caracterizacao: int | None = Field(default=None, alias="idCaracterizacao")
    id_unidade_medida: int | None = Field(default=None, alias="idUnidadeMedida")
    id_situacao: int | None = Field(default=None, alias="idSituacao")
    id_tipo: int | None = Field(default=None, alias="idTipo")
    id_subtipo: int | None = Field(default=None, alias="idSubtipo")
    numero_processo_decisao: str | None = Field(
        default=None, max_length=6, alias="numeroProcessoDecisao"
    )
    ano_processo_decisao: int | None = Field(default=None, alias="anoProcessoDecisao")
    id_processo_decisao: int | None = Field(default=None, alias="idProcessoDecisao")
    descricao_motivo: str | None = Field(default=None, max_length=5000, alias="descricaoMotivo")
    id_beneficio_potencial: int | None = Field(default=None, alias="idBeneficioPotencial")
    cpfcnpj: str | None = Field(default=None, max_length=14, alias="cpfCnpj")
    nome_pessoa: str | None = Field(default=None, max_length=200, alias="nomePessoa")
    data_ocorrencia: date | None = Field(default=None, alias="dataOcorrencia")

    model_config = {"populate_by_name": True}


class BeneficioItem(_BeneficioCampos):
    id_beneficio: int = Field(alias="idBeneficio")
    descricao: str
    origem: OrigemBeneficio
    chave_origem: str | None = Field(default=None, alias="chaveOrigem")
    id_debito_execucao: int | None = Field(default=None, alias="idDebitoExecucao")
    data_inclusao: datetime | None = Field(default=None, alias="dataInclusao")
    data_atualizacao: datetime | None = Field(default=None, alias="dataAtualizacao")


class BeneficioListResponse(BaseModel):
    items: list[BeneficioItem]
    total: int
    page: int
    size: int


class BeneficioResumo(BaseModel):
    total: int
    qtd_potencial: int = Field(serialization_alias="qtdPotencial")
    qtd_efetivo: int = Field(serialization_alias="qtdEfetivo")
    valor_potencial: Decimal = Field(default=Decimal(0), serialization_alias="valorPotencial")
    valor_efetivo: Decimal = Field(default=Decimal(0), serialization_alias="valorEfetivo")

    model_config = {"populate_by_name": True}


class MesSerie(BaseModel):
    ano: int
    mes: int
    qtd: int


class ExportInput(BaseModel):
    formato: Literal["csv", "json"] = "csv"
    # mesmo recorte da lista
    q: str | None = Field(default=None, max_length=200)
    origem: OrigemBeneficio | None = None
    data_de: date | None = Field(default=None, alias="dataDe")
    data_ate: date | None = Field(default=None, alias="dataAte")

    model_config = {"populate_by_name": True}


class DominioItem(BaseModel):
    id: int
    descricao: str


class DominiosResponse(BaseModel):
    tipos: list[DominioItem]
    subtipos: list[DominioItem]
    tipo_subtipos: dict[int, list[int]] = Field(serialization_alias="tipoSubtipos")
    areas_tematicas: list[DominioItem] = Field(serialization_alias="areasTematicas")
    caracterizacoes: list[DominioItem]
    situacoes: list[DominioItem]
    situacoes_efetivacao: list[DominioItem] = Field(serialization_alias="situacoesEfetivacao")
    unidades_medida: list[DominioItem] = Field(serialization_alias="unidadesMedida")

    model_config = {"populate_by_name": True}
