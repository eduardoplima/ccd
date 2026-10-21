"""Monitoramentos na CCD: processos MON + os de qualquer tipo com o marcador CCD
"Monitorar obrigação de fazer" (5734), com natureza e próximo passo.

O job diário (`tasks.task_atualizar_monitoramentos`) recalcula a parte do banco
(universo, marcadores, dias na CCD, última peça) e só chama o LLM para o processo
cuja última peça mudou desde a análise guardada. A semente (`seed.json`) é a análise
humana de 21/10/2026 (docs/notas/MONITORAMENTOS_CCD.md): vale até surgir peça nova.
"""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Callable
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.ccd.monitoramentos.schemas import (
    Analise,
    AnaliseLLM,
    MonitoramentoOut,
    MonitoramentosResponse,
)

log = logging.getLogger(__name__)

ID_SETOR_CCD = 762
ID_MARCADOR_OBRIGACAO_FAZER = 5734
SNAPSHOT_KEY = "ccd:monitoramentos:snapshot"
ANALISES_KEY = "ccd:monitoramentos:analises"  # {processo: Analise} — sobrevive aos snapshots
_SEED = Path(__file__).with_name("seed.json")
_MAX_CHARS = 80_000

_SQL_UNIVERSO = """
WITH entrada AS (
    SELECT ie.IdProcesso, MAX(ie.recebido_em) AS recebido_em
    FROM dbo.Itens_Lote ie JOIN dbo.Lotes lt ON lt.IdLote = ie.IdLote
    WHERE lt.destino = 'CCD'
    GROUP BY ie.IdProcesso
)
SELECT p.IdProcesso AS id_processo,
       RTRIM(p.numero_processo) AS numero, RTRIM(p.ano_processo) AS ano,
       RTRIM(p.codigo_tipo_processo) AS tipo, RTRIM(r.nome) AS relator,
       RTRIM(p.assunto) AS assunto,
       DATEDIFF(DAY, ent.recebido_em, GETDATE()) AS dias_ccd
FROM dbo.Processos p
LEFT JOIN dbo.Relator r ON r.codigo = p.codigo_relator
LEFT JOIN entrada ent ON ent.IdProcesso = p.IdProcesso
WHERE p.setor_atual = 'CCD' AND p.IdProcessoApensador IS NULL
  AND (p.codigo_tipo_processo = 'MON' OR EXISTS (
        SELECT 1 FROM dbo.Pro_MarcadorProcesso mp
        WHERE mp.IdProcesso = p.IdProcesso AND mp.DataExclusao IS NULL
          AND mp.IdMarcador = :marcador))
ORDER BY p.codigo_tipo_processo, p.ano_processo, p.numero_processo
"""

_SQL_MARCADORES = """
SELECT mp.IdProcesso AS id_processo, RTRIM(m.Descricao) AS marcador
FROM dbo.Pro_MarcadorProcesso mp JOIN dbo.Pro_Marcador m ON m.IdMarcador = mp.IdMarcador
WHERE m.IdSetor = :setor AND mp.DataExclusao IS NULL AND mp.IdProcesso IN :ids
ORDER BY mp.DataInclusao DESC
"""

# vw_ata_informacao.IdProcesso vem NULL em parte das linhas: casar por número/ano.
_SQL_PECAS = """
SELECT ppe.SequencialProcessoEvento AS evento, RTRIM(inf.setor) AS setor,
       CONCAT(RTRIM(inf.setor), '_', inf.numero_processo, '_', inf.ano_processo, '_',
              RIGHT(CONCAT('0000', inf.ordem), 4), '.pdf') AS arquivo,
       inf.data_resumo, inf.resumo, inf.Titulo_Modelo_informacao AS modelo
FROM dbo.vw_ata_informacao inf
JOIN dbo.Pro_ProcessoEvento ppe ON ppe.IdInformacao = inf.idInformacao
WHERE inf.numero_processo = :numero AND inf.ano_processo = :ano
  AND (inf.Inativa IS NULL OR inf.Inativa = 0)
ORDER BY ppe.SequencialProcessoEvento
"""

_RELEVANTE = re.compile(
    r"ac[óo]rd|decis|monitor|relat[óo]rio|instrutiv|parecer|resposta|cumpr", re.I
)

_PROMPT = """Você é analista da Coordenadoria de Controle de Decisões (CCD) do TCE/RN. A CCD monitora o
cumprimento de decisões: obrigações de fazer, determinações, multas cominatórias (multa diária).
Hoje é {hoje}. Leia as peças do processo {processo} ({tipo}, relator {relator}) e produza:
- jurisdicionado: o órgão/entidade cujo cumprimento é aferido;
- natureza: UMA linha — decisão-âncora (Acórdão nº/ano, processo de origem) e o que se monitora;
- proximo_passo: UMA linha — a próxima ação concreta da CCD (ex.: notificar, analisar a resposta do
  Ev. N e fazer informação de cumprimento, liquidar a cominatória e cadastrar débito tipo 5,
  remeter ao relator, aguardar prazo até dd/mm/aaaa);
- urgencia: alta (prazo vencido com multa correndo, ordem do relator parada, cobrança parada),
  media ou baixa;
- ficha_md: Markdown com exatamente estes itens em lista:
  "- **Natureza:** ...", "- **Situação atual:** ..." (última peça relevante com evento e data, prazo
  e se venceu, se o órgão respondeu), "- **Próximo passo (CCD):** ...", "- **Urgência:** ... (motivo)".
Use só o que está no texto. Não invente número de acórdão, data, valor ou prazo: se não achar,
escreva "não localizado". Em multa diária, não calcule teto: diga que o teto deve ser conferido.
Marcadores CCD ativos: {marcadores}. Dias na CCD: {dias}.

Peças (evento | setor | data | modelo | resumo):
{lista}

Textos:
{textos}
"""


def processo_de(row: dict[str, Any]) -> str:
    return f"{row['numero']}/{row['ano']}"


def carregar_universo(session: Session) -> list[dict[str, Any]]:
    rows = [
        dict(r)
        for r in session.execute(
            text(_SQL_UNIVERSO), {"marcador": ID_MARCADOR_OBRIGACAO_FAZER}
        ).mappings()
    ]
    if not rows:
        return rows
    marc: dict[int, list[str]] = {}
    q = text(_SQL_MARCADORES).bindparams(bindparam("ids", expanding=True))
    for m in session.execute(
        q, {"setor": ID_SETOR_CCD, "ids": [r["id_processo"] for r in rows]}
    ).mappings():
        marc.setdefault(m["id_processo"], []).append(m["marcador"])
    for r in rows:
        r["marcadores"] = marc.get(r["id_processo"], [])
    return rows


def carregar_pecas(session: Session, row: dict[str, Any]) -> list[dict[str, Any]]:
    params = {"numero": row["numero"], "ano": row["ano"]}
    return [dict(p) for p in session.execute(text(_SQL_PECAS), params).mappings()]


def montar_contexto(row: dict[str, Any], pecas: list[dict[str, Any]], ler_pdf: Callable) -> str:
    """Lista de todas as peças + texto das 6 últimas e de até 4 anteriores relevantes."""
    lista = "\n".join(
        f"- Ev {p['evento']} | {p['setor']} | {str(p['data_resumo'])[:10]} | {p['modelo']} | "
        f"{str(p['resumo'] or '')[:200]}"
        for p in pecas
    )
    ultimas = pecas[-6:]
    anteriores = [p for p in pecas[:-6] if _RELEVANTE.search(f"{p['modelo']} {p['resumo']}")][-4:]
    textos = []
    for p in anteriores + ultimas:
        try:
            t = ler_pdf(p["setor"], p["arquivo"]) or ""
        except Exception as e:  # PDF ausente no share não derruba a análise
            t = f"[PDF não lido: {e}]"
        t = re.sub(r"\n\s*\n+", "\n", t)[: 9000 if p in ultimas else 6000]
        textos.append(f"===== Ev {p['evento']} {p['arquivo']} ({p['modelo']}) =====\n{t}")
    return _PROMPT.format(
        hoje=date.today().strftime("%d/%m/%Y"),
        processo=processo_de(row),
        tipo=row["tipo"],
        relator=row["relator"],
        marcadores="; ".join(row["marcadores"]) or "nenhum",
        dias=row["dias_ccd"],
        lista=lista,
        textos="\n\n".join(textos),
    )[:_MAX_CHARS]


def analisador_llm() -> Callable[[str], AnaliseLLM] | None:
    """Chain prompt→AnaliseLLM, ou None sem LLM configurado (só a parte do banco)."""
    from frap.llm import structured

    chain = structured(AnaliseLLM)
    if chain is None:
        return None
    return lambda prompt: chain.invoke(prompt)


def ler_pdf_share(setor: str, arquivo: str) -> str:
    from frap.ccd.pdf import extract_text_from_pdf, informacoes_dir

    return extract_text_from_pdf(informacoes_dir() / setor / arquivo)


def carregar_seed() -> dict[str, Analise]:
    if not _SEED.exists():
        return {}
    bruto = json.loads(_SEED.read_text(encoding="utf-8"))
    return {k: Analise.model_validate(v) for k, v in bruto.items()}


def montar(
    session: Session,
    analises: dict[str, Analise],
    *,
    analisar: Callable[[str], AnaliseLLM] | None = None,
    ler_pdf: Callable[[str, str], str] = ler_pdf_share,
) -> tuple[MonitoramentosResponse, dict[str, Analise]]:
    """Snapshot + análises atualizadas. `analises` = guardadas (Redis) sobre a semente."""
    novas: dict[str, Analise] = {}
    items: list[MonitoramentoOut] = []
    for row in carregar_universo(session):
        proc = processo_de(row)
        pecas = carregar_pecas(session, row)
        ultima = pecas[-1] if pecas else None
        ev = ultima["evento"] if ultima else None
        a = analises.get(proc)
        if analisar is not None and (a is None or a.evento_analisado != ev):
            try:
                r = analisar(montar_contexto(row, pecas, ler_pdf))
                a = Analise(
                    **r.model_dump(),
                    fonte="llm",
                    evento_analisado=ev,
                    analisado_em=datetime.now(UTC).replace(microsecond=0),
                )
            except Exception:
                log.exception("monitoramentos: falha na análise de %s", proc)
        if a is not None:
            novas[proc] = a
        items.append(
            MonitoramentoOut(
                processo=proc,
                tipo=row["tipo"],
                relator=row["relator"],
                assunto=row["assunto"],
                marcadores=row["marcadores"],
                dias_ccd=row["dias_ccd"],
                ultima_peca_evento=ev,
                ultima_peca_data=ultima["data_resumo"] if ultima else None,
                ultima_peca_resumo=str(ultima["resumo"] or "")[:300] if ultima else None,
                jurisdicionado=a.jurisdicionado if a else None,
                natureza=a.natureza if a else None,
                proximo_passo=a.proximo_passo if a else None,
                urgencia=a.urgencia if a else None,
                ficha_md=a.ficha_md if a else None,
                fonte=a.fonte if a else "pendente",
                analisado_em=a.analisado_em if a else None,
                desatualizada=a is not None and a.evento_analisado != ev,
            )
        )
    resp = MonitoramentosResponse(
        items=items, total=len(items), calculado_em=datetime.now(UTC).replace(microsecond=0)
    )
    return resp, novas


def analises_de_json(bruto: str | bytes | None) -> dict[str, Analise]:
    if not bruto:
        return {}
    return {k: Analise.model_validate(v) for k, v in json.loads(bruto).items()}


def analises_para_json(analises: dict[str, Analise]) -> str:
    return json.dumps({k: v.model_dump(mode="json") for k, v in analises.items()})
