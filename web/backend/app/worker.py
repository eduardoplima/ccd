"""Configuração do worker ARQ. Lê o `.env` da raiz para que `tools/frap`
encontre as credenciais do SQL Server via `os.environ`."""

from __future__ import annotations

from pathlib import Path

from arq.connections import RedisSettings
from arq.cron import cron
from dotenv import load_dotenv

from app.ccd.automacao.antecedentes.tasks import task_gerar_antecedentes
from app.ccd.automacao.desconto_folha.tasks import task_gerar_desconto_folha
from app.ccd.beneficios.tasks import task_detectar_beneficios
from app.cgad.tasks import run_full_extraction
from app.config import get_settings
from app.jobs.tasks import task_conciliar_mes, task_parse_e_publicar, task_verificar_siai_folha

_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_ROOT / ".env", override=False)


def _redis_settings() -> RedisSettings:
    url = get_settings().redis_url
    if not url:
        raise RuntimeError("REDIS_URL não configurado — worker não pode iniciar")
    return RedisSettings.from_dsn(url)


class WorkerSettings:
    # FRAP (parse/conciliação) + CGAD (extração NER→obrigação→recomendação)
    # + CCD (geração de despachos: desconto em folha, antecedentes)
    functions = [
        task_parse_e_publicar,
        task_conciliar_mes,
        run_full_extraction,
        task_gerar_desconto_folha,
        task_gerar_antecedentes,
        task_verificar_siai_folha,
        task_detectar_beneficios,
    ]
    # Dia 10: dá tempo de a remessa SIAI da competência anterior chegar; a task
    # re-varre as 3 últimas competências, então atrasos maiores se autocorrigem.
    # Benefícios (dias 1 e 15): detecção é insert-only e idempotente por
    # ChaveOrigem; roda depois que a verificação SIAI do dia 10 materializou a
    # competência anterior.
    cron_jobs = [
        cron(task_verificar_siai_folha, day={10}, hour={7}, minute={0}),
        cron(task_detectar_beneficios, day={1, 15}, hour={7}, minute={30}),
    ]
    redis_settings = _redis_settings()
    allow_abort_jobs = True
    job_timeout = 60 * 60  # NER do CGAD pode demorar em janelas largas
    max_tries = 3
