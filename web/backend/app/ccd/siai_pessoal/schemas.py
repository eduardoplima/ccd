"""DTOs do contracheque do SIAI Pessoal (JSON em camelCase)."""

from __future__ import annotations

from typing import Literal, Optional

from app.ccd.desconto_folha.schemas import _Camel


class ItemContrachequeOut(_Camel):
    codigo: Optional[str] = None
    descricao: str
    tipo: Literal["V", "D"]  # vantagem / desconto (SiaiDp_Rubrica.Tipo 1 / 2)
    valor: float
    tce: bool = False  # rubrica de desconto TCE/FRAP


class FolhaContrachequeOut(_Camel):
    id_contracheque: int
    tipo_folha: str  # Normal / Complementar / Gratificação Natalina / PLR
    id_orgao: Optional[int] = None
    orgao: Optional[str] = None
    matricula: Optional[str] = None
    cargo: Optional[str] = None
    lotacao: Optional[str] = None
    total_vantagens: Optional[float] = None
    total_descontos: Optional[float] = None
    remessas: int = 1  # > 1 = folha reenviada (retificações); mostrada a última
    itens: list[ItemContrachequeOut] = []


class ContrachequeMes(_Camel):
    cpf: str
    nome: Optional[str] = None
    ano: int
    mes: int
    folhas: list[FolhaContrachequeOut] = []
