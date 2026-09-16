"""DTOs do desconto em folha: cadastro → resposta do órgão → match FRAP.

JSON em camelCase (alias_generator); os modelos aceitam os dois nomes na
entrada. Datas saem como ISO sem fuso (MSSQL DATETIME é naive).
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

StatusExtracao = Literal["PENDENTE", "OK", "SEM_RESPOSTA", "ERRO"]


class _Camel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


# ----- leitura ---------------------------------------------------------------


class NotificacaoOut(_Camel):
    numero: Optional[str] = None  # "001940/2024"
    data: Optional[datetime] = None
    tipo: Optional[Literal["E", "F"]] = None  # eletrônica / física (postal)
    evento: Optional[int] = None
    url: Optional[str] = None  # autos do e-Contas no evento


class ArOut(_Camel):
    """Recebimento da notificação (o nome ArOut ficou por compatibilidade do JSON `ar`)."""

    numero_postagem: Optional[str] = None
    data: Optional[datetime] = None
    tipo: Optional[Literal["E", "T", "AR", "DE"]] = None
    evento: Optional[int] = None
    url: Optional[str] = None


class RespostaOut(_Camel):
    processo: Optional[str] = None  # apensado, "300031/2025"
    evento: Optional[int] = None  # evento de apensamento no principal
    data: Optional[datetime] = None
    url: Optional[str] = None  # autos do processo de resposta no e-Contas, no 1º evento


class RetencaoMesOut(_Camel):
    orgao: Optional[str] = None
    codigo: Optional[str] = None
    rubrica: str
    valor: float


class ParcelaMesOut(_Camel):
    id_cadastro: int
    processo: str
    numero_parcela: int
    valor: float
    conciliado: bool = False
    competencia_inferida: bool = False  # parcela sem mês: mês anterior ao crédito
    credito_compartilhado: bool = False  # a mesma OB está vinculada a outra parcela/processo
    lancamento: Optional[LancamentoOut] = None


class MesRetencaoOut(_Camel):
    ano: int
    mes: int
    retencoes: list[RetencaoMesOut] = []
    total_retido: float = 0.0
    parcelas: list[ParcelaMesOut] = []
    total_conciliado: float = 0.0
    conciliado: bool = False


class MapaRetencoesOut(_Camel):
    """Meses com rubrica TCE/FRAP retida no SIAI Pessoal e a conciliação FRAP de cada um."""

    cpf: str
    nome: Optional[str] = None
    total_retido: float = 0.0
    total_conciliado: float = 0.0
    meses: list[MesRetencaoOut] = []


class RetencoesOut(_Camel):
    """Rubricas TCE/FRAP já retidas no SIAI Pessoal para o CPF (todas as competências)."""

    cpf: str
    total: float = 0.0
    competencias: int = 0
    ultimo_ano: Optional[int] = None
    ultimo_mes: Optional[int] = None


class CadastroListItem(_Camel):
    id: int
    id_processo: int
    processo: str
    id_debito: Optional[int] = None
    id_pessoa: Optional[int] = None
    cpf_cnpj: Optional[str] = None
    responsavel: Optional[str] = None
    id_orgao: Optional[int] = None
    orgao: Optional[str] = None
    notificacao: NotificacaoOut
    ar: ArOut
    resposta: RespostaOut
    status_extracao: StatusExtracao
    valor_total: Optional[float] = None
    parcelado: bool = False
    qtd_valores: int = 0
    qtd_matches: int = 0


class TotaisOut(_Camel):
    """Totais do recorte listado; valores pelas parcelas (CCDDescontoFolhaValor)."""

    cadastros: int = 0
    processos: int = 0
    pessoas: int = 0
    valor_esperado: float = 0.0
    valor_recebido: float = 0.0  # parcelas conciliadas com lançamento do FRAP
    valor_a_receber: float = 0.0


class CadastroListResponse(_Camel):
    items: list[CadastroListItem]
    total: int
    page: int
    size: int
    totais: TotaisOut = TotaisOut()


class SugestaoPessoa(_Camel):
    cpf: str
    nome: Optional[str] = None
    qtd: int


class SugestaoOrgao(_Camel):
    nome: str
    qtd: int


class SugestoesOut(_Camel):
    pessoas: list[SugestaoPessoa] = []
    orgaos: list[SugestaoOrgao] = []


class LancamentoOut(_Camel):
    id_lancamento: int
    dt_movimento: Optional[date] = None
    documento: Optional[str] = None
    historico: Optional[str] = None
    valor: float


class MatchOut(_Camel):
    id_match: int
    lancamento: LancamentoOut
    automatico: bool
    data_match: Optional[datetime] = None
    observacao: Optional[str] = None


class ValorOut(_Camel):
    id_valor: int
    numero_parcela: int
    mes: Optional[int] = None
    ano: Optional[int] = None
    valor: float
    origem: Literal["L", "M"]
    valor_siai: Optional[float] = None  # rubrica TCE/FRAP no SIAI Pessoal, mesma competência
    match: Optional[MatchOut] = None
    candidatos: list[LancamentoOut] = []


class EventoRespostaOut(_Camel):
    processo: Optional[str] = None  # apensado "300031/2025"; None = evento do próprio principal
    id_evento: int  # Pro_ProcessoEvento.IdProcessoEvento
    evento: int  # SequencialProcessoEvento (o "Ev. N" exibido)
    nome: Optional[str] = None  # nome_informacao sem a extensão
    data: Optional[datetime] = None
    url: str  # autos do e-Contas abertos nesse evento


class CadastroDetalhe(CadastroListItem):
    trecho_resposta: Optional[str] = None
    arquivo_resposta: Optional[str] = None
    data_extracao: Optional[datetime] = None
    observacoes: Optional[str] = None
    valores: list[ValorOut] = []
    eventos_resposta: list[EventoRespostaOut] = []


# ----- lookup do processo (formulário) --------------------------------------


class DebitoLookup(_Camel):
    id_debito: int
    valor_original: Optional[float] = None
    tipo: Optional[str] = None
    status: Optional[str] = None
    cancelado: bool = False
    desdobrado: bool = False  # substituído por filhos vivos na cadeia IdDebitoAnterior
    id_pessoa: Optional[int] = None
    nome_pessoa: Optional[str] = None
    documento: Optional[str] = None


class ProcessoLookup(_Camel):
    id_processo: int
    processo: str
    orgao: Optional[str] = None
    debitos: list[DebitoLookup]


# ----- escrita ---------------------------------------------------------------


class CadastroInput(_Camel):
    id_processo: int
    id_debito: Optional[int] = None
    id_pessoa: Optional[int] = None
    nome_orgao: Optional[str] = None
    observacoes: Optional[str] = None


class CadastroPatch(_Camel):
    id_debito: Optional[int] = None
    id_pessoa: Optional[int] = None
    nome_orgao: Optional[str] = None
    observacoes: Optional[str] = None


class ValorInput(_Camel):
    numero_parcela: int = Field(1, ge=1)
    mes: Optional[int] = Field(None, ge=1, le=12)
    ano: Optional[int] = Field(None, ge=2000, le=2100)
    valor: float = Field(gt=0)


class MatchInput(_Camel):
    id_lancamento: int
    observacao: Optional[str] = None


class MatchAutomaticoResultado(_Camel):
    vinculados: int


class CreditoFrapOut(LancamentoOut):
    descricao: Optional[str] = None
    id_cadastro_vinculado: Optional[int] = None


class CreditosFrapResponse(_Camel):
    texto: Optional[str] = None  # filtro efetivamente aplicado (default vem do órgão)
    desde: Optional[date] = None
    valor: Optional[float] = None
    aviso: Optional[str] = None  # ex.: órgão estadual sem valor → lista ficaria com todo o Estado
    items: list[CreditoFrapOut] = []


class AdotarCreditosInput(_Camel):
    ids_lancamento: list[int] = Field(min_length=1)
