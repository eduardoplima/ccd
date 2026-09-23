"""Unit tests da lógica pura de app.ccd.beneficios (sem MSSQL).

O CRUD/detecção usa T-SQL específico (OFFSET/FETCH, CTE recursiva, cross-db) e
fica fora daqui — verificação em dev na rede do TCE.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.ccd.beneficios.export import _COLUNAS_EXPORT, _csv, _linha_export
from app.ccd.beneficios.service import CAMPOS, _preencher_meses, _where_lista, filtro_periodo


def test_preencher_meses() -> None:
    assert _preencher_meses([]) == []
    serie = _preencher_meses([(2025, 11, 3), (2026, 2, 1)])
    assert [(s.ano, s.mes, s.qtd) for s in serie] == [
        (2025, 11, 3),
        (2025, 12, 0),
        (2026, 1, 0),
        (2026, 2, 1),
    ]


def test_filtro_periodo() -> None:
    where: list[str] = []
    params: dict = {}
    filtro_periodo(where, params, None, None)
    assert where == [] and params == {}

    filtro_periodo(where, params, date(2026, 1, 1), date(2026, 6, 30))
    assert len(where) == 2
    assert all("COALESCE(b.DataOcorrencia, CAST(b.DataInclusao AS DATE))" in w for w in where)
    assert params == {"data_de": date(2026, 1, 1), "data_ate": date(2026, 6, 30)}

    sem_alias: list[str] = []
    filtro_periodo(sem_alias, {}, date(2026, 1, 1), None, alias="")
    assert sem_alias == ["COALESCE(DataOcorrencia, CAST(DataInclusao AS DATE)) >= :data_de"]


def test_where_lista_mesmo_recorte() -> None:
    where, params = _where_lista(None, None, None, None)
    assert where == "WHERE b.Ativo = 1" and params == {}
    where, params = _where_lista("Silva", "PGE", date(2026, 1, 1), None, alias="")
    assert "NomePessoa LIKE :q" in where and "Origem = :origem" in where
    assert params == {"q": "%Silva%", "origem": "PGE", "data_de": date(2026, 1, 1)}


def test_csv_bom_delimitador_e_cabecalho() -> None:
    linha = _linha_export({origem: None for origem, _ in _COLUNAS_EXPORT}, id_setor=42)
    linha["ValorQuantidade"] = Decimal("10.50")
    bruto = _csv([linha])
    assert bruto[:3] == b"\xef\xbb\xbf"
    cab, dados = bruto.decode("utf-8-sig").splitlines()
    assert cab.split(";") == list(linha)
    assert "10.50" in dados.split(";")


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
    # Todo campo que espelha o BdBeneficio precisa sair no export.
    exportados = {origem for origem, _ in _COLUNAS_EXPORT}
    espelho = set(CAMPOS.values()) - {"CpfCnpj", "NomePessoa", "DataOcorrencia"}
    espelho = {c if c != "IdCCDBeneficioPotencial" else "IdCCDBeneficioPotencial" for c in espelho}
    assert espelho <= exportados


def test_deteccao_sem_pge_e_so_debito_valido() -> None:
    from app.ccd.beneficios import tasks

    # repasse PGE é atribuição do MPC, não benefício da CCD
    assert "PGE" not in tasks._ORIGENS
    # validade lida na FOLHA da cadeia (cancelada/suspensa fora), nunca na raiz
    assert tasks._FOLHA_VALIDA in tasks._SQL_DEBITO
    assert "r.DataCancelamento" not in tasks._SQL_DEBITO
    assert "StatusCancelamento = 1" in tasks._FOLHA_VALIDA
    assert "CodigoStatusDivida <> 20" in tasks._FOLHA_VALIDA
    # retirada roda antes do INSERT e só toca potenciais de DEBITO
    retirar, inserir = (sql for sql, _ in tasks._ORIGENS["DEBITO"])
    assert retirar is tasks._SQL_DEBITO_RETIRAR and inserir is tasks._SQL_DEBITO
    assert "Origem = 'DEBITO'" in retirar and f"NOT ({tasks._FOLHA_VALIDA})" in retirar


def test_boleto_retorno_em_dobro_fora() -> None:
    from app.ccd.beneficios import tasks

    # retorno bancário reimportado (mesmo IdBoleto+NumeroAutenticacao): fica só o 1º
    retirar, inserir = (sql for sql, _ in tasks._ORIGENS["BOLETO"])
    assert retirar is tasks._SQL_BOLETO_RETIRAR and inserir is tasks._SQL_BOLETO
    assert "Origem = 'BOLETO'" in retirar and f"AND {tasks._RETORNO_ANTERIOR}" in retirar
    assert f"NOT {tasks._RETORNO_ANTERIOR}" in inserir
    assert "rb2.NumeroAutenticacao = rb.NumeroAutenticacao" in tasks._RETORNO_ANTERIOR
    assert "rb2.IdRetornoBoleto < rb.IdRetornoBoleto" in tasks._RETORNO_ANTERIOR
