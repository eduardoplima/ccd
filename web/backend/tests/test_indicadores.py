from app.ccd.indicadores.service import _linha_base


def test_linha_base_media_dos_dois_anos_anteriores() -> None:
    assert _linha_base({2024: 10.0, 2025: 20.0, 2026: 99.0}, 2026) == 15.0


def test_linha_base_ignora_ano_sem_dado() -> None:
    assert _linha_base({2024: None, 2025: 8.0, 2026: 1.0}, 2026) == 8.0
    assert _linha_base({2026: 1.0}, 2026) is None
