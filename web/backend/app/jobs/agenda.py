"""Registro dos jobs do worker ARQ: fonte única para `worker.cron_jobs` e para a
tela ADMIN › Jobs. Só metadados — a API não importa as tasks (o CGAD puxa spacy).

O container do worker roda em UTC: os crons abaixo estão em UTC (Brasília = UTC−3,
sem horário de verão desde 2019).
"""

from __future__ import annotations

from typing import Any, TypedDict

_CAMPOS = ("minute", "hour", "day", "month", "weekday")
_UTC_PARA_BRASILIA = -3


class Job(TypedDict):
    nome: str
    descricao: str
    cron: dict[str, Any] | None  # kwargs de `arq.cron.cron`; None = sob demanda


JOBS: list[Job] = [
    {
        "nome": "task_calcular_alertas",
        "descricao": "Calcula os alertas da CCD (parcelamento cancelado com marcador ativo) "
        "e grava o resultado que a tela de Alertas exibe.",
        "cron": {"hour": {3}, "minute": {0}},
    },
    {
        "nome": "task_atualizar_monitoramentos",
        "descricao": "Refaz a tela de Monitoramentos da CCD (MON + obrigação de fazer); o LLM "
        "só reanalisa os processos com peça nova.",
        "cron": {"hour": {4}, "minute": {0}},
    },
    {
        "nome": "task_detectar_beneficios",
        "descricao": "Varre as fontes do SisBenefícios e insere os candidatos novos em "
        "CCDBeneficio (idempotente por ChaveOrigem).",
        "cron": {"day": {1, 15}, "hour": {7}, "minute": {30}},
    },
    {
        "nome": "task_detectar_cadastros_desconto_folha",
        "descricao": "Cria cadastros de desconto em folha para notificações novas e desativa "
        "os com débito enviado à PGE.",
        "cron": {"hour": {7}, "minute": {45}},
    },
    {
        "nome": "task_conciliar_desconto_folha",
        "descricao": "Match automático dos cadastros de desconto em folha com créditos do "
        "FRAP ainda sem conciliação.",
        "cron": {"hour": {8}, "minute": {0}},
    },
    {
        "nome": "task_parse_e_publicar",
        "descricao": "FRAP: lê os extratos enviados e publica os lançamentos.",
        "cron": None,
    },
    {
        "nome": "task_conciliar_mes",
        "descricao": "FRAP: conciliação de um mês.",
        "cron": None,
    },
    {
        "nome": "run_full_extraction",
        "descricao": "CGAD: extração NER → obrigação → recomendação.",
        "cron": None,
    },
    {
        "nome": "task_gerar_desconto_folha",
        "descricao": "Automação: gera os despachos de desconto em folha.",
        "cron": None,
    },
    {
        "nome": "task_gerar_antecedentes",
        "descricao": "Automação: gera as informações de antecedentes.",
        "cron": None,
    },
    {
        "nome": "task_extrair_resposta_desconto_folha",
        "descricao": "Desconto em folha: extrai (LLM) o valor da resposta no apensado.",
        "cron": None,
    },
    {
        "nome": "task_localizar_notificacoes_desconto_folha",
        "descricao": "Desconto em folha: localiza notificação e recebimento no banco processo.",
        "cron": None,
    },
]


def expressao_cron(cron: dict[str, Any]) -> str:
    """kwargs do arq → `min hora dia mês dia-da-semana` (campo ausente = `*`)."""
    return " ".join(",".join(map(str, sorted(cron[c]))) if c in cron else "*" for c in _CAMPOS)


def horario_brasilia(cron: dict[str, Any]) -> str:
    # ponytail: só desloca a hora; um cron com dia fixo perto da meia-noite UTC mostraria
    # o dia errado — nenhum hoje
    horas = sorted((h + _UTC_PARA_BRASILIA) % 24 for h in cron.get("hour", ()))
    minutos = sorted(cron.get("minute", {0}))
    quando = ", ".join(f"{h:02d}:{m:02d}" for h in horas for m in minutos) or "toda hora"
    dias = cron.get("day")
    return f"dias {', '.join(map(str, sorted(dias)))} às {quando}" if dias else f"diário {quando}"
