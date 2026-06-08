"""Scan da view `processo.dbo.vw_ata_informacao` para eventos CCD de desconto em folha.

Filtra por `inf.setor='CCD'` + resumo casando "%desconto%folha%". Cobre os
prefixos canônicos vistos na CCD: "Notificação para desconto em folha",
"Determinação para desconto em folha", "Desconto em Folha", "Suspensão do
desconto em folha", etc. Persiste em `FRAPNotificacaoDescontoFolha`,
idempotente via UNIQUE(NumeroProcesso, AnoProcesso, IdEventoCCD).

Resolução de IdDebito (ordem):
  1. Débito do processo com registro em `Exe_DescontoFolha` (marcador).
  2. Se o processo tem exatamente 1 débito, usa esse.
  3. Senão, IdDebito = NULL.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import Engine, text

logger = logging.getLogger(__name__)


_SQL_CANDIDATOS = """
SELECT
    inf.numero_processo,
    inf.ano_processo,
    inf.idInformacao,
    inf.DataPublicacao,
    inf.resumo,
    ppe.SequencialProcessoEvento AS IdEventoCCD,
    CONCAT(
        RTRIM(inf.setor), '_',
        inf.numero_processo, '_',
        inf.ano_processo, '_',
        RIGHT(CONCAT('0000', inf.ordem), 4),
        '.pdf'
    ) AS NomeArquivo
FROM processo.dbo.vw_ata_informacao inf
JOIN processo.dbo.Pro_ProcessoEvento ppe ON ppe.idinformacao = inf.idInformacao
WHERE inf.setor = 'CCD'
  AND inf.resumo LIKE '%desconto%folha%'
"""

_SQL_RESOLVE_PROCESSO = """
SELECT TOP 1 IdProcesso FROM processo.dbo.Processos
WHERE numero_processo = :num AND ano_processo = :ano
"""

_SQL_DEBITOS_PROCESSO = """
SELECT ed.IdDebito,
       CASE WHEN EXISTS (
           SELECT 1 FROM processo.dbo.Exe_DescontoFolha edf
           WHERE edf.IdDebito = ed.IdDebito AND edf.Ativo = 1
       ) THEN 1 ELSE 0 END AS marcador_df
FROM processo.dbo.Exe_Debito ed
WHERE ed.IdProcessoExecucao = :id_processo
  AND ed.DataCancelamento IS NULL
"""

_SQL_UPSERT = """
MERGE dbo.FRAPNotificacaoDescontoFolha AS tgt
USING (SELECT :num AS NumeroProcesso, :ano AS AnoProcesso, :evento AS IdEventoCCD) AS src
   ON tgt.NumeroProcesso = src.NumeroProcesso
  AND tgt.AnoProcesso    = src.AnoProcesso
  AND tgt.IdEventoCCD    = src.IdEventoCCD
WHEN MATCHED THEN UPDATE SET
    IdProcesso = :id_processo,
    IdDebito = :id_debito,
    DataPublicacaoCCD = :data_pub,
    ResumoCCD = :resumo,
    NomeArquivoPDF = :nome_arq
WHEN NOT MATCHED THEN
    INSERT (NumeroProcesso, AnoProcesso, IdProcesso, IdEventoCCD, IdDebito,
            DataPublicacaoCCD, ResumoCCD, NomeArquivoPDF)
    VALUES (:num, :ano, :id_processo, :evento, :id_debito,
            :data_pub, :resumo, :nome_arq);
"""


@dataclass
class ResultadoScan:
    candidatos: int = 0
    persistidos: int = 0
    sem_processo: int = 0
    sem_debito: int = 0
    erros: list[dict[str, Any]] = field(default_factory=list)

    def resumo(self) -> str:
        return (
            f"candidatos={self.candidatos} persistidos={self.persistidos} "
            f"sem_processo={self.sem_processo} sem_debito={self.sem_debito} "
            f"erros={len(self.erros)}"
        )


def _resolver_id_debito(conn, id_processo: int | None) -> int | None:
    """Aplica regra de resolução. Retorna None se ambíguo."""
    if id_processo is None:
        return None
    rows = conn.execute(text(_SQL_DEBITOS_PROCESSO), {"id_processo": id_processo}).fetchall()
    if not rows:
        return None
    com_marcador = sorted([int(r[0]) for r in rows if r[1] == 1])
    if com_marcador:
        return com_marcador[0]
    if len(rows) == 1:
        return int(rows[0][0])
    return None


def scan_notificacoes_ccd(
    engine: Engine,
    *,
    processo_filtro: tuple[str, str] | None = None,
    dry_run: bool = False,
) -> ResultadoScan:
    """Escaneia notificações CCD e persiste em FRAPNotificacaoDescontoFolha.

    `processo_filtro` = (numero_padded, ano) restringe a um único processo.
    """
    res = ResultadoScan()

    sql = _SQL_CANDIDATOS
    params: dict[str, Any] = {}
    if processo_filtro is not None:
        sql += " AND inf.numero_processo = :num AND inf.ano_processo = :ano"
        params["num"] = processo_filtro[0]
        params["ano"] = processo_filtro[1]

    with engine.begin() as conn:
        candidatos = conn.execute(text(sql), params).mappings().all()
        res.candidatos = len(candidatos)

        for c in candidatos:
            num = str(c["numero_processo"]).strip()
            ano = str(c["ano_processo"]).strip()
            id_processo: int | None = conn.execute(
                text(_SQL_RESOLVE_PROCESSO), {"num": num, "ano": ano}
            ).scalar_one_or_none()
            if id_processo is None:
                res.sem_processo += 1
            id_debito = _resolver_id_debito(conn, id_processo)
            if id_debito is None:
                res.sem_debito += 1

            if dry_run:
                continue

            try:
                conn.execute(
                    text(_SQL_UPSERT),
                    {
                        "num": num,
                        "ano": ano,
                        "id_processo": id_processo,
                        "evento": int(c["IdEventoCCD"]),
                        "id_debito": id_debito,
                        "data_pub": c["DataPublicacao"],
                        "resumo": c["resumo"],
                        "nome_arq": c["NomeArquivo"],
                    },
                )
                res.persistidos += 1
            except Exception as e:
                res.erros.append({"processo": f"{num}/{ano}", "motivo": str(e)})

    return res
