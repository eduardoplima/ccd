from app.ccd.desconto_folha.tasks import _pessoas_novas

CPF, CNPJ = "111.222.333-44", "11.222.333/0001-44"


def _d(id_debito, id_pessoa, doc=CPF, cancelado=False, desdobrado=0):
    return {
        "id_debito": id_debito,
        "id_pessoa": id_pessoa,
        "documento": doc,
        "data_cancelamento": "2025-01-01" if cancelado else None,
        "desdobrado": desdobrado,
    }


def test_pessoas_novas():
    # débito único → vai no cadastro; vários → None
    assert _pessoas_novas([_d(1, 10)], set()) == [(10, 1)]
    assert _pessoas_novas([_d(1, 10), _d(2, 10), _d(3, 10)], set()) == [(10, None)]
    # duas pessoas → dois cadastros
    assert sorted(_pessoas_novas([_d(1, 10), _d(2, 20)], set())) == [(10, 1), (20, 2)]
    # PJ, cancelado e desdobrado ficam de fora
    fora = [_d(1, 10, doc=CNPJ), _d(2, 20, cancelado=True), _d(3, 30, desdobrado=1)]
    assert _pessoas_novas(fora, set()) == []
    # vivo ao lado de cancelado da mesma pessoa: só o vivo conta
    assert _pessoas_novas([_d(1, 10, cancelado=True), _d(2, 10)], set()) == [(10, 2)]
    # já cadastrada (ativa ou removida) não volta; migrado sem pessoa cobre o processo
    assert _pessoas_novas([_d(1, 10), _d(2, 20)], {10}) == [(20, 2)]
    assert _pessoas_novas([_d(1, 10)], {None}) == []
