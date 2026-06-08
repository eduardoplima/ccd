"""Recalcula `dbo.FRAPLancamentoOrgao` a partir da inferência regex + LLM.

Estratégia DELETE+INSERT por IdLancamento. A inferência regex/alias é barata
(pass único por lançamento sobre índice em memória); o fallback LLM é caro,
então só dispara para lançamentos sem hit regex e tem cache em memória por
texto normalizado.

Cobertura: **todos** os FRAPLancamento — sem filtro de ValorDC ou IdConta.
O endpoint backend `depositos_do_orgao` continua filtrando `ValorDC='C'`
no momento da query (depósitos = crédito).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import Engine, text

from frap.config import ID_ORGAO_SUPERIOR_ESTADO
from frap.matching import inferencia_orgao as ifr_mod
from frap.matching.inferencia_orgao_llm import infer_via_llm

logger = logging.getLogger(__name__)


@dataclass
class Resultado:
    qtd_total: int = 0
    qtd_via_regex: int = 0
    qtd_via_llm: int = 0
    qtd_sem_match: int = 0
    tempo_segundos: float = 0.0
    llm_disponivel: bool = True
    amostras_sem_match: list[dict[str, Any]] = field(default_factory=list)

    def resumo(self) -> str:
        return (
            f"total={self.qtd_total} regex={self.qtd_via_regex} "
            f"llm={self.qtd_via_llm} sem_match={self.qtd_sem_match} "
            f"llm_disponivel={self.llm_disponivel} tempo={self.tempo_segundos:.1f}s"
        )


_SQL_LANCAMENTOS = """
SELECT L.IdLancamento, L.Historico, L.Descricao, L.CpfCnpjDepositante
FROM dbo.FRAPLancamento L
{filtro}
"""

_SQL_DELETE = "DELETE FROM dbo.FRAPLancamentoOrgao WHERE IdLancamento = :id_lanc"

_SQL_INSERT = """
INSERT INTO dbo.FRAPLancamentoOrgao (IdLancamento, IdOrgao, FonteInferencia)
VALUES (:id_lanc, :id_orgao, :fonte)
"""


def _fonte_regex(
    cpfcnpj_dep: str | None,
    cands: set[int],
    indice: list[ifr_mod.OrgaoIndex],
) -> str:
    """Distingue 'cnpj_direto' de 'regex'."""
    if not cpfcnpj_dep:
        return "regex"
    digits = "".join(c for c in str(cpfcnpj_dep) if c.isdigit())
    if len(digits) != 14:
        return "regex"
    org = ifr_mod.buscar_orgao_por_cnpj(digits, indice)
    if org is not None and org.id_orgao in cands:
        return "cnpj_direto"
    return "regex"


def recalcular(
    engine: Engine,
    *,
    only_id_lancamento: int | None = None,
    dry_run: bool = False,
    log_amostras: int = 10,
) -> Resultado:
    """Reinferi órgãos para todo FRAPLancamento (ou filtrado).

    Args:
        engine: engine BdDIP.
        only_id_lancamento: se informado, processa só esse lançamento.
        dry_run: não persiste; só conta.
        log_amostras: quantos lançamentos sem-match registrar em
            `Resultado.amostras_sem_match`.

    LLM sempre invocado como fallback quando regex não acha — só pula se
    `get_llm_client()` retornar None (env ausente ou langchain não instalado).
    """
    inicio = time.perf_counter()
    indice = ifr_mod.carregar_indice_orgaos(engine)

    if only_id_lancamento is not None:
        filtro_sql = "WHERE L.IdLancamento = :id_lanc"
        params: dict[str, Any] = {"id_lanc": only_id_lancamento}
    else:
        filtro_sql = ""
        params = {}

    res = Resultado()

    # 1ª passada: lê tudo, aplica regex/alias/CNPJ direto, separa pendentes para LLM
    matches_finais: dict[int, set[tuple[int, str]]] = {}
    pendentes_llm: list[dict[str, Any]] = []

    with engine.connect() as conn:
        rows = (
            conn.execute(text(_SQL_LANCAMENTOS.format(filtro=filtro_sql)), params)
            .mappings()
            .all()
        )

    for r in rows:
        id_lanc = int(r["IdLancamento"])
        cands = ifr_mod.inferir_orgaos_lancamento(
            r["Historico"],
            r["Descricao"],
            indice,
            cpfcnpj_depositante=r["CpfCnpjDepositante"],
        )
        # expande Estado-RN para subordinados
        if cands:
            expandido = ifr_mod.expandir_estado_rn(
                {id_lanc: cands}, indice, ID_ORGAO_SUPERIOR_ESTADO
            )[id_lanc]
        else:
            expandido = set()

        if expandido:
            fonte = _fonte_regex(r["CpfCnpjDepositante"], expandido, indice)
            matches_finais[id_lanc] = {(c, fonte) for c in expandido}
            res.qtd_via_regex += 1
        else:
            pendentes_llm.append(dict(r))
        res.qtd_total += 1

    # 2ª passada: LLM para os pendentes (cache em memória dedup pelo texto)
    from frap.llm import get_llm_client

    llm_ok = get_llm_client() is not None
    res.llm_disponivel = llm_ok
    if not llm_ok and pendentes_llm:
        logger.warning(
            "AZURE_OPENAI_* ausente — %d lançamentos sem match não passarão pelo LLM.",
            len(pendentes_llm),
        )

    for r in pendentes_llm:
        id_lanc = int(r["IdLancamento"])
        if llm_ok:
            id_orgao = infer_via_llm(r["Historico"], r["Descricao"], indice)
        else:
            id_orgao = None
        if id_orgao is not None:
            matches_finais[id_lanc] = {(id_orgao, "llm")}
            res.qtd_via_llm += 1
        else:
            res.qtd_sem_match += 1
            if len(res.amostras_sem_match) < log_amostras:
                res.amostras_sem_match.append(
                    {
                        "id_lancamento": id_lanc,
                        "historico": r["Historico"],
                        "descricao": r["Descricao"],
                    }
                )

    if dry_run:
        res.tempo_segundos = time.perf_counter() - inicio
        return res

    # 3ª passada: persiste — DELETE+INSERT por IdLancamento, transação única
    with engine.begin() as conn:
        for id_lanc, pares in matches_finais.items():
            conn.execute(text(_SQL_DELETE), {"id_lanc": id_lanc})
            conn.execute(
                text(_SQL_INSERT),
                [
                    {"id_lanc": id_lanc, "id_orgao": id_o, "fonte": fonte}
                    for (id_o, fonte) in pares
                ],
            )
        # Também limpa entradas de lançamentos que perderam todos os matches
        # nessa rodada (regex regrediu / mudança no índice).
        ids_sem_match_persistir = {int(r["IdLancamento"]) for r in pendentes_llm} - {
            id_l for id_l in matches_finais
        }
        for id_lanc in ids_sem_match_persistir:
            conn.execute(text(_SQL_DELETE), {"id_lanc": id_lanc})

    res.tempo_segundos = time.perf_counter() - inicio
    return res
