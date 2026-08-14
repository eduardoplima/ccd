"""Pré-triagem do conjunto (``cgad.dataset_pretag``): descrição do modelo -> span.

O script mora em ``tools/cgad``, mas o único harness de pytest do workspace é o
do backend.
"""

from __future__ import annotations

from cgad.dataset_pretag import spans_do
from cgad.schema import NERDecisao, NERMulta, NERObrigacao, NERRecomendacao

TEXTO = "DECIDEM aplicar multa de R$ 1.000 ao gestor e recomendar a revisão do edital."


def test_descricoes_viram_spans_no_texto():
    ner = NERDecisao(
        multas=[NERMulta(descricao_multa="multa de R$ 1.000")],
        recomendacoes=[NERRecomendacao(descricao_recomendacao="revisão do edital")],
    )
    spans, perdidos = spans_do(ner, TEXTO)

    assert perdidos == 0
    assert [s["label"] for s in spans] == ["MULTA", "RECOMENDACAO"]  # ordem do texto
    for span in spans:
        assert TEXTO[span["start"] : span["end"]] in TEXTO
    assert TEXTO[spans[0]["start"] : spans[0]["end"]] == "multa de R$ 1.000"


def test_sobreposicao_e_descartada():
    ner = NERDecisao(
        multas=[NERMulta(descricao_multa="multa de R$ 1.000 ao gestor")],
        obrigacoes=[NERObrigacao(descricao_obrigacao="R$ 1.000 ao gestor")],
    )
    spans, _ = spans_do(ner, TEXTO)

    assert [s["label"] for s in spans] == ["MULTA"]


def test_descricao_inventada_nao_vira_span():
    ner = NERDecisao(multas=[NERMulta(descricao_multa="determina o protesto da certidão")])
    spans, perdidos = spans_do(ner, TEXTO)

    assert spans == []
    assert perdidos == 1
