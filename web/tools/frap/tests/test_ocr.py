"""Métrica de qualidade do OCR (sem Tesseract)."""

from frap.ccd.ocr import plausibilidade, score


def test_plausibilidade_separa_texto_de_ruido() -> None:
    assert (
        plausibilidade("A COMPROMITENTE obriga-se a encaminhar projeto de Lei em 120 dias") >= 0.9
    )
    assert plausibilidade("//Qkfá\" ” xZv9) ;;; !zv, Mnn ///") < 0.5
    assert plausibilidade("") == 0.0


def test_score_pondera_confianca_pelo_tamanho() -> None:
    assert score([]) == 0.0
    assert score([("termo", 90.0), ("de", 50.0)]) > score([("termo", 50.0), ("de", 90.0)])
