"""Unit tests da lógica pura de app.ccd.beneficios (sem MSSQL).

O CRUD/detecção usa T-SQL específico (OFFSET/FETCH, CTE recursiva, cross-db) e
fica fora daqui — verificação em dev na rede do TCE.
"""

from __future__ import annotations

from decimal import Decimal

from app.ccd.beneficios.export import _COLUNAS_EXPORT, _linha_export
from app.ccd.beneficios.schemas import BeneficioInput
from app.ccd.beneficios.service import CAMPOS, TRANSICOES


def test_transicoes_cobrem_todos_os_status() -> None:
    status = {"RASCUNHO", "VALIDADO", "ENVIADO", "DESCARTADO"}
    assert set(TRANSICOES) == status
    for destinos in TRANSICOES.values():
        assert destinos <= status
    # ENVIADO é quase-terminal: só desfaz para VALIDADO.
    assert TRANSICOES["ENVIADO"] == {"VALIDADO"}
    # DESCARTADO recupera para RASCUNHO (nunca pula direto a ENVIADO).
    assert TRANSICOES["DESCARTADO"] == {"RASCUNHO"}


def test_linha_export_usa_nomes_do_bdbeneficio() -> None:
    row = {origem: None for origem, _ in _COLUNAS_EXPORT}
    row.update(
        {
            "IdCCDBeneficio": 7,
            "DescricaoPropostaBeneficio": "Multa recolhida",
            "ValorQuantidade": Decimal("100.50"),
            "IdTipoBeneficio": 1,
            "IdSubTipoBeneficio": 1,
        }
    )
    linha = _linha_export(row, id_setor=42)
    # nomes de campo exatamente como em Beneficio_PropostaBeneficio + correlação
    assert set(linha) == {destino for _, destino in _COLUNAS_EXPORT} | {
        "IdBeneficioAnterior",
        "IdStatusBeneficio",
        "IdSetorUsuarioCadastro",
    }
    assert linha["IdInterno"] == 7
    assert linha["IdStatusBeneficio"] == 1  # Cadastrado
    assert linha["IdSetorUsuarioCadastro"] == 42
    assert linha["ValorQuantidade"] == Decimal("100.50")
    assert linha["IdBeneficioAnterior"] is None  # só origem PROPOSTA preenche


def test_linha_export_proposta_vincula_beneficio_anterior() -> None:
    row = {origem: None for origem, _ in _COLUNAS_EXPORT}
    row.update(
        {
            "IdCCDBeneficio": 8,
            "DescricaoPropostaBeneficio": "Proposta da UTCE convertida em potencial",
            "Origem": "PROPOSTA",
            "ChaveOrigem": "PROPOSTA:59",
        }
    )
    linha = _linha_export(row, id_setor=None)
    assert linha["IdBeneficioAnterior"] == 59


def test_campos_crud_todos_no_export_ou_meta() -> None:
    # Todo campo editável que espelha o BdBeneficio precisa sair no export.
    exportados = {origem for origem, _ in _COLUNAS_EXPORT}
    espelho = set(CAMPOS.values()) - {"CpfCnpj", "NomePessoa", "DataOcorrencia"}
    espelho = {c if c != "IdCCDBeneficioPotencial" else "IdCCDBeneficioPotencial" for c in espelho}
    assert espelho <= exportados


def test_beneficio_input_aceita_camel_case() -> None:
    payload = BeneficioInput.model_validate(
        {
            "descricao": "TAG homologado cumprido",
            "idTipo": 5,
            "idSituacaoEfetivacao": 1,
            "valorQuantidade": "1234.56",
            "numeroProcessoDecisao": "4917",
            "anoProcessoDecisao": 2024,
        }
    )
    assert payload.id_tipo == 5
    assert payload.valor_quantidade == Decimal("1234.56")
