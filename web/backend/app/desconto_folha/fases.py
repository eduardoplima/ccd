"""Service das 4 fases do desconto em folha: totais, notificados, enviados, agendado/pago.

- **Totais**: débitos ativos da pessoa sem Custas (DataCancelamento IS NULL,
  CodigoStatusDivida=1, CodigoTipoDebito<>1). Mesmo recorte de
  ValorAtualizadoTotal — valor exibido vem dessa coluna.
- **Notificados**: débitos cujo processo de execução aparece em
  `FRAPNotificacaoDescontoFolha`. Subconjunto dos Totais.
- **Enviados**: lê `FRAPNotificacaoDescontoFolha` (populado pelo CLI
  `scan-notificacoes-ccd`).
- **Agendados / Pagos**: contagem via `FRAPDescontoFolhaParcela` + `FRAPMatchDescontoFolha`.
  Mantém o mesmo critério usado em `service.list_pessoas`.
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.desconto_folha.schemas import (
    DebitoFase,
    DebitosFaseResumo,
    FasesResumo,
    FaseStats,
    NotificacaoEnviada,
)

_STATUS_PAGOS = ("OK_TUDO", "MATCH_MANUAL", "REPASSE_VIA_ORGAO")

# Normalização do GenPessoa.Documento — só dígitos, pra casar com CpfCnpj 11/14.
_DOC_NORM = "REPLACE(REPLACE(REPLACE(REPLACE(gp.Documento, '.', ''), '-', ''), '/', ''), ' ', '')"


# ---------------------------------------------------------------------------
# Resumo (4 cards)
# ---------------------------------------------------------------------------


def resumo_fases(session: Session, *, cpfcnpj: str) -> FasesResumo:
    """Conta + total de cada fase. Totais/Notificados/Enviados materializados em
    FRAPMetricaPessoa (recalc via `frap recalcular-metricas-pessoa`).
    Agendados/Pagos: ainda direto de FRAPDescontoFolha* — pequeno e indexado.
    """
    metrica = session.execute(
        text(
            """
            SELECT
                ISNULL(QtdDebitosTotais, 0)                AS qtd_totais,
                ISNULL(ValorAtualizadoTotal, 0)            AS total_totais,
                ISNULL(QtdDebitosNotificados, 0)           AS qtd_debitos_notificados,
                ISNULL(ValorDebitosNotificadosTotal, 0)    AS total_debitos_notificados,
                ISNULL(QtdProcessosNotificados, 0)         AS qtd_enviados
            FROM dbo.FRAPMetricaPessoa
            WHERE CpfCnpj = :cpf
            """
        ),
        {"cpf": cpfcnpj},
    ).first()

    qtd_totais = int(metrica[0]) if metrica else 0
    total_totais = Decimal(str(metrica[1] if metrica else 0))
    qtd_debitos_notificados = int(metrica[2]) if metrica else 0
    total_debitos_notificados = Decimal(str(metrica[3] if metrica else 0))
    qtd_enviados = int(metrica[4]) if metrica else 0

    sql_status_ok = ", ".join(f"'{s}'" for s in _STATUS_PAGOS)
    agendado_pago = session.execute(
        text(
            f"""
            SELECT
                COUNT(*) AS qtd_agendado,
                COALESCE(SUM(p.ValorEsperado), 0) AS total_agendado,
                SUM(CASE WHEN st.Codigo IN ({sql_status_ok}) THEN 1 ELSE 0 END) AS qtd_pago,
                SUM(CASE WHEN st.Codigo IN ({sql_status_ok})
                         THEN COALESCE(m.ValorContracheque, p.ValorEsperado) ELSE 0 END) AS total_pago
            FROM dbo.FRAPDescontoFolha df
            JOIN dbo.FRAPDescontoFolhaParcela p
              ON p.IdFRAPDescontoFolha = df.IdFRAPDescontoFolha
            OUTER APPLY (
                SELECT TOP 1 m2.* FROM dbo.FRAPMatchDescontoFolha m2
                WHERE m2.IdFRAPDescontoFolhaParcela = p.IdFRAPDescontoFolhaParcela
                ORDER BY m2.IsManual DESC, m2.IdMatchDescontoFolha DESC
            ) m
            LEFT JOIN dbo.FRAPStatusMatch st ON st.IdStatusMatch = m.IdStatusMatch
            WHERE df.CpfCnpj = :cpf
            """
        ),
        {"cpf": cpfcnpj},
    ).first()

    return FasesResumo(
        totais=FaseStats(qtd=qtd_totais, total=total_totais),
        debitos_notificados=FaseStats(qtd=qtd_debitos_notificados, total=total_debitos_notificados),
        enviados=FaseStats(qtd=qtd_enviados, total=None),
        agendados=FaseStats(
            qtd=int(agendado_pago[0] or 0),
            total=Decimal(str(agendado_pago[1] or 0)),
        ),
        pagos=FaseStats(
            qtd=int(agendado_pago[2] or 0),
            total=Decimal(str(agendado_pago[3] or 0)),
        ),
    )


# ---------------------------------------------------------------------------
# Totais (detalhe)
# ---------------------------------------------------------------------------


def totais_detalhe(session: Session, *, cpfcnpj: str) -> DebitosFaseResumo:
    """Lista débitos ativos da pessoa sem Custas — mesmo recorte de
    FRAPMetricaPessoa.QtdDebitosTotais / ValorAtualizadoTotal.
    """
    rows = (
        session.execute(
            text(
                f"""
                SELECT
                    ed.IdDebito,
                    ed.IdProcessoOrigem,
                    LTRIM(RTRIM(po.numero_processo)) AS NumeroProcessoOrigem,
                    LTRIM(RTRIM(po.ano_processo))   AS AnoProcessoOrigem,
                    ed.IdProcessoExecucao,
                    LTRIM(RTRIM(pe.numero_processo)) AS NumeroProcessoExecucao,
                    LTRIM(RTRIM(pe.ano_processo))   AS AnoProcessoExecucao,
                    ed.valorOriginalDebito,
                    BdDIP.dbo.fn_Exe_RetornaValorAtualizado(ed.IdDebito) AS valor_atualizado,
                    td.Descricao AS TipoDebito,
                    sd.DescricaoStatusDivida AS StatusDivida
                FROM processo.dbo.Exe_Debito ed
                JOIN processo.dbo.Exe_DebitoPessoa edp ON edp.IDDebito = ed.IdDebito
                JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = edp.IDPessoa
                LEFT JOIN processo.dbo.Processos po ON po.IdProcesso = ed.IdProcessoOrigem
                LEFT JOIN processo.dbo.Processos pe ON pe.IdProcesso = ed.IdProcessoExecucao
                LEFT JOIN processo.dbo.Exe_TipoDebito td
                       ON td.CodigoTipoDebito = ed.CodigoTipoDebito
                LEFT JOIN processo.dbo.Exe_StatusDivida sd
                       ON sd.CodigoStatusDivida = ed.CodigoStatusDivida
                WHERE {_DOC_NORM} = :cpf
                  AND ed.DataCancelamento IS NULL
                  AND ed.CodigoStatusDivida = 1
                  AND ed.CodigoTipoDebito <> 1
                ORDER BY ed.IdDebito DESC
                """
            ),
            {"cpf": cpfcnpj},
        )
        .mappings()
        .all()
    )
    debitos = [
        DebitoFase(
            id_debito=int(r["IdDebito"]),
            id_processo_origem=r["IdProcessoOrigem"],
            numero_processo_origem=r["NumeroProcessoOrigem"],
            ano_processo_origem=r["AnoProcessoOrigem"],
            id_processo_execucao=r["IdProcessoExecucao"],
            numero_processo_execucao=r["NumeroProcessoExecucao"],
            ano_processo_execucao=r["AnoProcessoExecucao"],
            valor_original=Decimal(str(r["valorOriginalDebito"] or 0)),
            valor_atualizado=(
                Decimal(str(r["valor_atualizado"])) if r["valor_atualizado"] is not None else None
            ),
            tipo_debito=(r["TipoDebito"].strip() if r["TipoDebito"] else None),
            status_divida=(r["StatusDivida"].strip() if r["StatusDivida"] else None),
        )
        for r in rows
    ]
    return DebitosFaseResumo(
        qtd_debitos=len(debitos),
        valor_original_total=sum((d.valor_original for d in debitos), Decimal(0)),
        debitos=debitos,
    )


# ---------------------------------------------------------------------------
# Enviados (detalhe)
# ---------------------------------------------------------------------------


def enviados_detalhe(session: Session, *, cpfcnpj: str) -> list[NotificacaoEnviada]:
    rows = (
        session.execute(
            text(
                f"""
                SELECT
                    n.IdFRAPNotifDF,
                    n.NumeroProcesso, n.AnoProcesso, n.IdDebito, n.IdEventoCCD,
                    n.DataPublicacaoCCD, n.ResumoCCD
                FROM dbo.FRAPNotificacaoDescontoFolha n
                WHERE EXISTS (
                    SELECT 1 FROM processo.dbo.Exe_Debito ed
                    JOIN processo.dbo.Exe_DebitoPessoa edp ON edp.IDDebito = ed.IdDebito
                    JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = edp.IDPessoa
                    WHERE ed.IdProcessoExecucao = n.IdProcesso
                      AND {_DOC_NORM} = :cpf
                      AND ed.CodigoTipoDebito <> 1
                )
                ORDER BY n.DataPublicacaoCCD DESC
                """
            ),
            {"cpf": cpfcnpj},
        )
        .mappings()
        .all()
    )
    return [
        NotificacaoEnviada(
            id_notif=int(r["IdFRAPNotifDF"]),
            numero_processo=str(r["NumeroProcesso"]).strip(),
            ano_processo=str(r["AnoProcesso"]).strip(),
            id_debito=r["IdDebito"],
            id_evento_ccd=int(r["IdEventoCCD"]),
            data_publicacao_ccd=r["DataPublicacaoCCD"],
            resumo_ccd=r["ResumoCCD"],
        )
        for r in rows
    ]


def debitos_notificados_detalhe(session: Session, *, cpfcnpj: str) -> DebitosFaseResumo:
    """Lista débitos da pessoa cujo IdProcessoExecucao aparece em
    FRAPNotificacaoDescontoFolha — mesmo critério da contagem
    FRAPMetricaPessoa.QtdDebitosNotificados.
    """
    rows = (
        session.execute(
            text(
                f"""
                SELECT
                    ed.IdDebito,
                    ed.IdProcessoOrigem,
                    LTRIM(RTRIM(po.numero_processo)) AS NumeroProcessoOrigem,
                    LTRIM(RTRIM(po.ano_processo))   AS AnoProcessoOrigem,
                    ed.IdProcessoExecucao,
                    LTRIM(RTRIM(pe.numero_processo)) AS NumeroProcessoExecucao,
                    LTRIM(RTRIM(pe.ano_processo))   AS AnoProcessoExecucao,
                    ed.valorOriginalDebito,
                    BdDIP.dbo.fn_Exe_RetornaValorAtualizado(ed.IdDebito) AS valor_atualizado,
                    td.Descricao AS TipoDebito,
                    sd.DescricaoStatusDivida AS StatusDivida
                FROM processo.dbo.Exe_Debito ed
                JOIN processo.dbo.Exe_DebitoPessoa edp ON edp.IDDebito = ed.IdDebito
                JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = edp.IDPessoa
                LEFT JOIN processo.dbo.Processos po ON po.IdProcesso = ed.IdProcessoOrigem
                LEFT JOIN processo.dbo.Processos pe ON pe.IdProcesso = ed.IdProcessoExecucao
                LEFT JOIN processo.dbo.Exe_TipoDebito td
                       ON td.CodigoTipoDebito = ed.CodigoTipoDebito
                LEFT JOIN processo.dbo.Exe_StatusDivida sd
                       ON sd.CodigoStatusDivida = ed.CodigoStatusDivida
                WHERE {_DOC_NORM} = :cpf
                  AND ed.CodigoTipoDebito <> 1
                  AND ed.IdProcessoExecucao IN (
                      SELECT DISTINCT n.IdProcesso FROM dbo.FRAPNotificacaoDescontoFolha n
                  )
                ORDER BY ed.IdDebito DESC
                """
            ),
            {"cpf": cpfcnpj},
        )
        .mappings()
        .all()
    )
    debitos = [
        DebitoFase(
            id_debito=int(r["IdDebito"]),
            id_processo_origem=r["IdProcessoOrigem"],
            numero_processo_origem=r["NumeroProcessoOrigem"],
            ano_processo_origem=r["AnoProcessoOrigem"],
            id_processo_execucao=r["IdProcessoExecucao"],
            numero_processo_execucao=r["NumeroProcessoExecucao"],
            ano_processo_execucao=r["AnoProcessoExecucao"],
            valor_original=Decimal(str(r["valorOriginalDebito"] or 0)),
            valor_atualizado=(
                Decimal(str(r["valor_atualizado"])) if r["valor_atualizado"] is not None else None
            ),
            tipo_debito=(r["TipoDebito"].strip() if r["TipoDebito"] else None),
            status_divida=(r["StatusDivida"].strip() if r["StatusDivida"] else None),
        )
        for r in rows
    ]
    return DebitosFaseResumo(
        qtd_debitos=len(debitos),
        valor_original_total=sum((d.valor_original for d in debitos), Decimal(0)),
        debitos=debitos,
    )


__all__ = [
    "resumo_fases",
    "totais_detalhe",
    "debitos_notificados_detalhe",
    "enviados_detalhe",
    "_STATUS_PAGOS",
]
