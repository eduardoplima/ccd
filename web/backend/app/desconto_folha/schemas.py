from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Eixo: Por pessoa
# ---------------------------------------------------------------------------


class PessoaAgregadaItem(BaseModel):
    cpfcnpj: str | None = Field(default=None, serialization_alias="cpfCnpj")
    nome_pessoa: str | None = Field(default=None, serialization_alias="nomePessoa")
    id_orgao_notificado: int | None = Field(default=None, serialization_alias="idOrgaoNotificado")
    nome_orgao_notificado: str | None = Field(
        default=None, serialization_alias="nomeOrgaoNotificado"
    )
    qtd_parcelas: int = Field(serialization_alias="qtdParcelas")
    qtd_conciliadas: int = Field(default=0, serialization_alias="qtdConciliadas")
    origens: list[str] = Field(default_factory=list)
    valor_atualizado_total: Decimal = Field(
        default=Decimal(0), serialization_alias="valorAtualizadoTotal"
    )
    qtd_processos_notificados: int = Field(default=0, serialization_alias="qtdProcessosNotificados")
    qtd_debitos_notificados: int = Field(default=0, serialization_alias="qtdDebitosNotificados")
    valor_debitos_notificados_total: Decimal = Field(
        default=Decimal(0), serialization_alias="valorDebitosNotificadosTotal"
    )
    total_esperado: Decimal = Field(serialization_alias="totalEsperado")
    total_quitado: Decimal = Field(serialization_alias="totalQuitado")
    saldo_aberto: Decimal = Field(serialization_alias="saldoAberto")

    model_config = {"populate_by_name": True}


class PessoaAgregadaListResponse(BaseModel):
    items: list[PessoaAgregadaItem]
    total: int
    page: int
    size: int


class ParcelaPessoaItem(BaseModel):
    id_parcela: int | None = Field(default=None, serialization_alias="idParcela")
    id_desconto_folha: int = Field(serialization_alias="idDescontoFolha")
    origem: str  # 'P' processo / 'M' manual
    numero_parcela: int | None = Field(default=None, serialization_alias="numeroParcela")
    mes_referencia: int | None = Field(default=None, serialization_alias="mesReferencia")
    ano_referencia: int | None = Field(default=None, serialization_alias="anoReferencia")
    valor_esperado: Decimal = Field(serialization_alias="valorEsperado")
    data_vencimento: date | None = Field(default=None, serialization_alias="dataVencimento")
    data_pagamento: date | None = Field(default=None, serialization_alias="dataPagamento")
    situacao_parcela: str | None = Field(default=None, serialization_alias="situacaoParcela")
    tipo_baixa: int | None = Field(default=None, serialization_alias="tipoBaixa")

    status_codigo: str | None = Field(default=None, serialization_alias="statusCodigo")
    status_descricao: str | None = Field(default=None, serialization_alias="statusDescricao")
    is_manual: bool = Field(default=False, serialization_alias="isManual")
    valor_contracheque: Decimal | None = Field(
        default=None, serialization_alias="valorContracheque"
    )
    id_lancamento_frap: int | None = Field(default=None, serialization_alias="idLancamentoFrap")
    id_match: int | None = Field(default=None, serialization_alias="idMatch")
    observacao: str | None = None

    model_config = {"populate_by_name": True}


class ParcelasPessoaResponse(BaseModel):
    cpfcnpj: str | None = Field(default=None, serialization_alias="cpfCnpj")
    nome_pessoa: str | None = Field(default=None, serialization_alias="nomePessoa")
    id_orgao_notificado: int | None = Field(default=None, serialization_alias="idOrgaoNotificado")
    nome_orgao_notificado: str | None = Field(
        default=None, serialization_alias="nomeOrgaoNotificado"
    )
    parcelas: list[ParcelaPessoaItem]

    model_config = {"populate_by_name": True}


class AtribuirOrgaoInput(BaseModel):
    id_orgao: int = Field(alias="idOrgao")

    model_config = {"populate_by_name": True}


class AtribuirOrgaoResultado(BaseModel):
    qtd_atualizados: int = Field(serialization_alias="qtdAtualizados")
    id_orgao: int = Field(serialization_alias="idOrgao")
    nome_orgao: str = Field(serialization_alias="nomeOrgao")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Eixo: Por órgão
# ---------------------------------------------------------------------------


class OrgaoAgregadoItem(BaseModel):
    id_orgao: int | None = Field(default=None, serialization_alias="idOrgao")
    nome_orgao: str | None = Field(default=None, serialization_alias="nomeOrgao")
    qtd_pessoas: int = Field(serialization_alias="qtdPessoas")
    qtd_parcelas: int = Field(serialization_alias="qtdParcelas")
    qtd_conciliadas: int = Field(serialization_alias="qtdConciliadas")
    total_esperado: Decimal = Field(serialization_alias="totalEsperado")
    total_quitado: Decimal = Field(serialization_alias="totalQuitado")

    model_config = {"populate_by_name": True}


class OrgaoAgregadoListResponse(BaseModel):
    items: list[OrgaoAgregadoItem]
    total: int
    page: int
    size: int


class PessoaDoOrgaoItem(BaseModel):
    cpfcnpj: str | None = Field(default=None, serialization_alias="cpfCnpj")
    nome_pessoa: str | None = Field(default=None, serialization_alias="nomePessoa")
    qtd_parcelas: int = Field(serialization_alias="qtdParcelas")
    qtd_conciliadas: int = Field(serialization_alias="qtdConciliadas")
    total_esperado: Decimal = Field(serialization_alias="totalEsperado")

    model_config = {"populate_by_name": True}


class PessoasDoOrgaoResponse(BaseModel):
    id_orgao: int = Field(serialization_alias="idOrgao")
    nome_orgao: str | None = Field(default=None, serialization_alias="nomeOrgao")
    pessoas: list[PessoaDoOrgaoItem]


class DepositosOrgaoResponse(BaseModel):
    id_orgao: int = Field(serialization_alias="idOrgao")
    cnpj: str | None = None
    qtd: int
    total: Decimal
    is_estadual: bool = Field(default=False, serialization_alias="isEstadual")


class LancamentoDoOrgaoItem(BaseModel):
    id_lancamento: int = Field(serialization_alias="idLancamento")
    dt_movimento: date | None = Field(default=None, serialization_alias="dtMovimento")
    conta: str
    valor: Decimal
    historico: str
    documento: str | None = None
    descricao: str | None = None
    cpfcnpj_depositante: str | None = Field(default=None, serialization_alias="cpfCnpjDepositante")
    via_cnpj: bool = Field(default=False, serialization_alias="viaCnpj")
    via_inferencia: bool = Field(default=False, serialization_alias="viaInferencia")

    model_config = {"populate_by_name": True}


class LancamentosDoOrgaoResponse(BaseModel):
    id_orgao: int = Field(serialization_alias="idOrgao")
    items: list[LancamentoDoOrgaoItem]


# ---------------------------------------------------------------------------
# Cadastro manual
# ---------------------------------------------------------------------------


class ParcelaManualInput(BaseModel):
    numero_parcela: int = Field(ge=1, alias="numeroParcela")
    mes_referencia: int = Field(ge=1, le=12, alias="mesReferencia")
    ano_referencia: int = Field(ge=2000, le=2100, alias="anoReferencia")
    valor_esperado: Decimal = Field(gt=0, alias="valorEsperado")
    data_vencimento: date | None = Field(default=None, alias="dataVencimento")

    model_config = {"populate_by_name": True}


class CadastroManualInput(BaseModel):
    cpfcnpj: str = Field(min_length=11, max_length=14, alias="cpfCnpj")
    nome_pessoa: str = Field(min_length=1, max_length=200, alias="nomePessoa")
    id_orgao_notificado: int = Field(alias="idOrgaoNotificado")
    nome_orgao_notificado: str = Field(min_length=1, max_length=200, alias="nomeOrgaoNotificado")
    parcelas: list[ParcelaManualInput] = Field(min_length=1)
    observacao: str | None = Field(default=None, max_length=500)

    model_config = {"populate_by_name": True}


class CadastroManualItem(BaseModel):
    id_desconto_folha: int = Field(serialization_alias="idDescontoFolha")
    cpfcnpj: str | None = Field(default=None, serialization_alias="cpfCnpj")
    nome_pessoa: str | None = Field(default=None, serialization_alias="nomePessoa")
    id_orgao_notificado: int | None = Field(default=None, serialization_alias="idOrgaoNotificado")
    nome_orgao_notificado: str | None = Field(
        default=None, serialization_alias="nomeOrgaoNotificado"
    )
    qtd_parcelas: int = Field(serialization_alias="qtdParcelas")
    valor_total: Decimal = Field(serialization_alias="valorTotal")
    data_inclusao: datetime | None = Field(default=None, serialization_alias="dataInclusao")

    model_config = {"populate_by_name": True}


class CadastroManualListResponse(BaseModel):
    items: list[CadastroManualItem]
    total: int
    page: int
    size: int


# ---------------------------------------------------------------------------
# Match manual
# ---------------------------------------------------------------------------


class MatchManualInput(BaseModel):
    id_lancamento_frap: int = Field(alias="idLancamentoFrap")
    ids_parcela: list[int] = Field(min_length=1, alias="idsParcela")
    observacao: str | None = Field(default=None, max_length=500)

    model_config = {"populate_by_name": True}


class MatchManualResultado(BaseModel):
    matches_criados: int = Field(serialization_alias="matchesCriados")
    ids_match: list[int] = Field(serialization_alias="idsMatch")


# ---------------------------------------------------------------------------
# Órgãos disponíveis (dropdown do cadastro manual)
# ---------------------------------------------------------------------------


class OrgaoDisponivel(BaseModel):
    id_orgao: int = Field(serialization_alias="idOrgao")
    nome_orgao: str = Field(serialization_alias="nomeOrgao")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Tipologias de análise
# ---------------------------------------------------------------------------


# 1.2 Repasse multi-parcela
class CandidatoRepasseMulti(BaseModel):
    ids_parcela: list[int] = Field(serialization_alias="idsParcela")
    soma_candidata: Decimal = Field(serialization_alias="somaCandidata")
    descricao_combinacao: str = Field(serialization_alias="descricaoCombinacao")

    model_config = {"populate_by_name": True}


class RepasseMultiParcelaItem(BaseModel):
    id_lancamento: int = Field(serialization_alias="idLancamento")
    dt_movimento: date = Field(serialization_alias="dtMovimento")
    valor: Decimal
    historico: str | None = None
    cpfcnpj: str | None = Field(default=None, serialization_alias="cpfCnpj")
    nome_pessoa: str | None = Field(default=None, serialization_alias="nomePessoa")
    candidatos: list[CandidatoRepasseMulti]

    model_config = {"populate_by_name": True}


class RepasseMultiParcelaResponse(BaseModel):
    items: list[RepasseMultiParcelaItem]


# 1.3 CPF sem cadastro SIAIPessoal
class CpfSemSiaiItem(BaseModel):
    id_desconto_folha: int = Field(serialization_alias="idDescontoFolha")
    cpfcnpj: str | None = Field(default=None, serialization_alias="cpfCnpj")
    nome_pessoa: str | None = Field(default=None, serialization_alias="nomePessoa")
    origem: str
    qtd_parcelas: int = Field(serialization_alias="qtdParcelas")
    nome_orgao_notificado: str | None = Field(
        default=None, serialization_alias="nomeOrgaoNotificado"
    )

    model_config = {"populate_by_name": True}


class CpfSemSiaiResponse(BaseModel):
    items: list[CpfSemSiaiItem]


# 1.4 Parcela duplicada
class ParcelaDuplicadaItem(BaseModel):
    id_desconto_folha: int = Field(serialization_alias="idDescontoFolha")
    cpfcnpj: str | None = Field(default=None, serialization_alias="cpfCnpj")
    nome_pessoa: str | None = Field(default=None, serialization_alias="nomePessoa")
    numero_parcela: int = Field(serialization_alias="numeroParcela")
    mes_referencia: int = Field(serialization_alias="mesReferencia")
    ano_referencia: int = Field(serialization_alias="anoReferencia")
    valor_esperado: Decimal = Field(serialization_alias="valorEsperado")
    qtd: int
    ids_parcela: list[int] = Field(serialization_alias="idsParcela")

    model_config = {"populate_by_name": True}


class ParcelaDuplicadaResponse(BaseModel):
    items: list[ParcelaDuplicadaItem]


# 1.5 Atraso sistemático por órgão
class AtrasoSistemicoMes(BaseModel):
    ano: int
    mes: int
    pct_atraso: float = Field(serialization_alias="pctAtraso")
    qtd_parcelas: int = Field(serialization_alias="qtdParcelas")
    qtd_em_atraso: int = Field(serialization_alias="qtdEmAtraso")

    model_config = {"populate_by_name": True}


class AtrasoSistemicoItem(BaseModel):
    id_orgao: int | None = Field(default=None, serialization_alias="idOrgao")
    nome_orgao: str | None = Field(default=None, serialization_alias="nomeOrgao")
    qtd_meses_consecutivos: int = Field(serialization_alias="qtdMesesConsecutivos")
    pct_medio: float = Field(serialization_alias="pctMedio")
    detalhe_meses: list[AtrasoSistemicoMes] = Field(serialization_alias="detalheMeses")

    model_config = {"populate_by_name": True}


class AtrasoSistemicoResponse(BaseModel):
    items: list[AtrasoSistemicoItem]


# ---------------------------------------------------------------------------
# 4 fases (atribuído / enviado / agendado / pago)
# ---------------------------------------------------------------------------


class FaseStats(BaseModel):
    qtd: int
    total: Decimal | None = None

    model_config = {"populate_by_name": True}


class FasesResumo(BaseModel):
    totais: FaseStats
    debitos_notificados: FaseStats = Field(serialization_alias="debitosNotificados")
    enviados: FaseStats
    agendados: FaseStats
    pagos: FaseStats

    model_config = {"populate_by_name": True}


class DebitoFase(BaseModel):
    id_debito: int = Field(serialization_alias="idDebito")
    id_processo_origem: int | None = Field(default=None, serialization_alias="idProcessoOrigem")
    numero_processo_origem: str | None = Field(
        default=None, serialization_alias="numeroProcessoOrigem"
    )
    ano_processo_origem: str | None = Field(default=None, serialization_alias="anoProcessoOrigem")
    id_processo_execucao: int | None = Field(default=None, serialization_alias="idProcessoExecucao")
    numero_processo_execucao: str | None = Field(
        default=None, serialization_alias="numeroProcessoExecucao"
    )
    ano_processo_execucao: str | None = Field(
        default=None, serialization_alias="anoProcessoExecucao"
    )
    valor_original: Decimal = Field(serialization_alias="valorOriginal")
    valor_atualizado: Decimal | None = Field(default=None, serialization_alias="valorAtualizado")
    tipo_debito: str | None = Field(default=None, serialization_alias="tipoDebito")
    status_divida: str | None = Field(default=None, serialization_alias="statusDivida")

    model_config = {"populate_by_name": True}


class DebitosFaseResumo(BaseModel):
    qtd_debitos: int = Field(serialization_alias="qtdDebitos")
    valor_original_total: Decimal = Field(serialization_alias="valorOriginalTotal")
    debitos: list[DebitoFase]

    model_config = {"populate_by_name": True}


class NotificacaoEnviada(BaseModel):
    id_notif: int = Field(serialization_alias="idNotif")
    numero_processo: str = Field(serialization_alias="numeroProcesso")
    ano_processo: str = Field(serialization_alias="anoProcesso")
    id_debito: int | None = Field(default=None, serialization_alias="idDebito")
    id_evento_ccd: int = Field(serialization_alias="idEventoCcd")
    data_publicacao_ccd: datetime | None = Field(
        default=None, serialization_alias="dataPublicacaoCcd"
    )
    resumo_ccd: str | None = Field(default=None, serialization_alias="resumoCcd")

    model_config = {"populate_by_name": True}


class EnviadosListResponse(BaseModel):
    items: list[NotificacaoEnviada]
