from app.ccd.monitoramentos import service
from app.ccd.monitoramentos.schemas import Analise, AnaliseLLM

_ROW = {
    "id_processo": 1,
    "numero": "000001",
    "ano": "2026",
    "tipo": "MON",
    "relator": "R",
    "assunto": "A",
    "dias_ccd": 10,
    "marcadores": ["Monitorar obrigação de fazer"],
}


def _analise(ev: int) -> Analise:
    return Analise(
        jurisdicionado="J",
        natureza="N",
        proximo_passo="P",
        urgencia="alta",
        ficha_md="- f",
        fonte="manual",
        evento_analisado=ev,
        analisado_em=None,
    )


def test_reanalisa_so_com_peca_nova(monkeypatch):
    pecas = [
        {
            "evento": 5,
            "setor": "CCD",
            "arquivo": "a.pdf",
            "data_resumo": None,
            "resumo": "r",
            "modelo": "Despacho",
        }
    ]
    monkeypatch.setattr(service, "carregar_universo", lambda s: [dict(_ROW)])
    monkeypatch.setattr(service, "carregar_pecas", lambda s, r: pecas)
    chamadas = []

    def fake(prompt: str) -> AnaliseLLM:
        chamadas.append(prompt)
        return AnaliseLLM(
            jurisdicionado="J2", natureza="N2", proximo_passo="P2", urgencia="baixa", ficha_md="- g"
        )

    def montar(analises):
        return service.montar(None, analises, analisar=fake, ler_pdf=lambda s, a: "texto")

    resp, novas = montar({"000001/2026": _analise(5)})
    assert not chamadas and resp.items[0].fonte == "manual" and not resp.items[0].desatualizada

    resp, novas = montar({"000001/2026": _analise(4)})
    assert (
        len(chamadas) == 1
        and resp.items[0].fonte == "llm"
        and novas["000001/2026"].evento_analisado == 5
    )

    # sem LLM: mantém a análise antiga, marcada como desatualizada
    resp, _ = service.montar(None, {"000001/2026": _analise(4)}, ler_pdf=lambda s, a: "")
    assert resp.items[0].desatualizada and resp.items[0].natureza == "N"

    assert service.analises_de_json(service.analises_para_json(novas)) == novas


def test_seed_cobre_formato():
    seed = service.carregar_seed()
    assert seed and all(a.ficha_md and a.urgencia for a in seed.values())
