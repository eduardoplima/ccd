"""Configuração do worker ARQ. Lê o `.env` da raiz para que `tools/frap`
encontre as credenciais do SQL Server via `os.environ`."""

from __future__ import annotations

from pathlib import Path

from arq.connections import RedisSettings
from arq.cron import cron
from dotenv import load_dotenv

from app.ccd.alertas.tasks import task_calcular_alertas
from app.ccd.automacao.antecedentes.tasks import task_gerar_antecedentes
from app.ccd.automacao.desconto_folha.tasks import task_gerar_desconto_folha
from app.ccd.beneficios.tasks import task_detectar_beneficios
from app.ccd.monitoramentos.tasks import task_atualizar_monitoramentos
from app.ccd.desconto_folha.tasks import (
    task_conciliar_desconto_folha,
    task_detectar_cadastros_desconto_folha,
    task_extrair_resposta_desconto_folha,
    task_localizar_notificacoes_desconto_folha,
)
from app.cgad.tasks import run_full_extraction
from app.config import get_settings
from app.jobs.agenda import JOBS
from app.jobs.tasks import task_conciliar_mes, task_parse_e_publicar

_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_ROOT / ".env", override=False)


def _redis_settings() -> RedisSettings:
    url = get_settings().redis_url
    if not url:
        raise RuntimeError("REDIS_URL não configurado — worker não pode iniciar")
    return RedisSettings.from_dsn(url)


# FRAP (parse/conciliação) + CGAD (extração NER→obrigação→recomendação)
# + CCD (geração de despachos, extração da resposta do desconto em folha)
FUNCTIONS = [
    task_parse_e_publicar,
    task_conciliar_mes,
    run_full_extraction,
    task_gerar_desconto_folha,
    task_gerar_antecedentes,
    task_detectar_beneficios,
    task_extrair_resposta_desconto_folha,
    task_localizar_notificacoes_desconto_folha,
    task_conciliar_desconto_folha,
    task_detectar_cadastros_desconto_folha,
    task_calcular_alertas,
    task_atualizar_monitoramentos,
]
_POR_NOME = {f.__name__: f for f in FUNCTIONS}


class WorkerSettings:
    functions = FUNCTIONS
    # Horários em app/jobs/agenda.py (UTC), a mesma lista que a tela ADMIN › Jobs mostra.
    cron_jobs = [cron(_POR_NOME[j["nome"]], **j["cron"]) for j in JOBS if j["cron"]]
    redis_settings = _redis_settings()
    allow_abort_jobs = True
    job_timeout = 60 * 60  # NER do CGAD pode demorar em janelas largas
    max_tries = 3
