from app.jobs.agenda import JOBS, expressao_cron, horario_brasilia


def test_expressao_e_horario():
    alerta = next(j["cron"] for j in JOBS if j["nome"] == "task_calcular_alertas")
    assert expressao_cron(alerta) == "0 3 * * *"
    assert horario_brasilia(alerta) == "diário 00:00"
    assert expressao_cron({"day": {15, 1}, "hour": {7}, "minute": {30}}) == "30 7 1,15 * *"


def test_nomes_unicos():
    nomes = [j["nome"] for j in JOBS]
    assert len(nomes) == len(set(nomes))
