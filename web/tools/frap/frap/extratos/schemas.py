"""Schemas do registro canônico de lançamento."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Lancamento:
    conta: str               # "700000-6" ou "600000-2"
    periodo: str             # "MMYYYY" do arquivo de origem
    ordem_no_arquivo: int    # 1..N — posição no arquivo após parsing
    dt_movimento: date
    ag_origem: str
    lote: str
    historico: str
    documento: str           # com pontos, como vem no extrato
    valor: Decimal
    valor_dc: str            # "C" ou "D"
    descricao: str
    doc_data: date | None    # YYYYMMDD decodificado dos 8 primeiros dígitos
    seq_bb: str | None       # 7 últimos dígitos do `documento` (autenticação sequencial diária do BB)
    categoria: str           # Categoria.value
    cpfcnpj_depositante: str | None  # só dígitos; extraído de `descricao`
    cpfcnpj_ambiguo: bool            # >1 candidato em `descricao`
