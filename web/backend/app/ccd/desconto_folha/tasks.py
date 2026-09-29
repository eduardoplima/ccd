from __future__ import annotations

import asyncio
from datetime import date
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

_SQL_UPDATE_NOTIFICACAO = """
UPDATE CCDDescontoFolha SET
    NumeroNotificacao = COALESCE(:NumeroNotificacao, NumeroNotificacao),
    DataNotificacao = COALESCE(:DataNotificacao, DataNotificacao),
    TipoNotificacao = COALESCE(:TipoNotificacao, TipoNotificacao),
    EventoNotificacao = COALESCE(:EventoNotificacao, EventoNotificacao),
    IdEventoNotificacao = COALESCE(:IdEventoNotificacao, IdEventoNotificacao),
    NumeroPostagemAr = COALESCE(:NumeroPostagemAr, NumeroPostagemAr),
    DataAr = COALESCE(:DataAr, DataAr),
    TipoRecebimento = COALESCE(:TipoRecebimento, TipoRecebimento),
    EventoRecebimento = COALESCE(:EventoRecebimento, EventoRecebimento),
    IdEventoRecebimento = COALESCE(:IdEventoRecebimento, IdEventoRecebimento),
    DataAtualizacao = :agora
WHERE IdCCDDescontoFolha = :c
"""


def localizar_notificacoes(ids: list[int] | None = None) -> str:
    """Varre os cadastros ativos (ou `ids`) e grava notificação/recebimento achados
    no banco `processo`. Sobrescreve o que encontrou; preserva o que não encontrou."""
    from datetime import datetime

    from app.ccd.desconto_folha import notificacao, processo_lookup
    from app.db import get_processo_engine
    from app.jobs.tasks import _session_factory

    factory = _session_factory()
    with factory() as s:
        sql = "SELECT IdCCDDescontoFolha AS id, IdProcesso FROM CCDDescontoFolha WHERE Ativo = 1"
        if ids:
            marcas = ", ".join(f":i{n}" for n in range(len(ids)))
            rows = (
                s.execute(
                    text(f"{sql} AND IdCCDDescontoFolha IN ({marcas})"),
                    {f"i{n}": v for n, v in enumerate(ids)},
                )
                .mappings()
                .all()
            )
        else:
            rows = s.execute(text(sql)).mappings().all()
        cadastros = [dict(r) for r in rows]

    total = com_notif = eletronicas = com_receb = sem_nada = 0
    with Session(get_processo_engine()) as sp, factory() as s:
        for cad in cadastros:
            total += 1
            p = processo_lookup.processo_por_id(sp, int(cad["IdProcesso"]))
            if p is None:
                sem_nada += 1
                continue
            achado = notificacao.localizar(
                sp,
                id_processo=int(p["IdProcesso"]),
                numero=p["numero"],
                ano=p["ano"],
                id_origem=p["id_origem"],
            )
            tem_notif = bool(achado["DataNotificacao"] or achado["NumeroNotificacao"])
            com_notif += tem_notif
            eletronicas += tem_notif and achado["TipoNotificacao"] == "E"
            com_receb += bool(achado["DataAr"])
            sem_nada += not (tem_notif or achado["DataAr"])
            s.execute(
                text(_SQL_UPDATE_NOTIFICACAO),
                {**achado, "agora": datetime.utcnow().replace(microsecond=0), "c": cad["id"]},
            )
            s.commit()
    return (
        f"{total} cadastro(s): {com_notif} com notificação (eletrônica: {eletronicas}, "
        f"física: {com_notif - eletronicas}), {com_receb} com recebimento, {sem_nada} sem nada"
    )


async def task_localizar_notificacoes_desconto_folha(
    ctx: dict[str, Any], id_frap_job: int, ids: list[int] | None = None
) -> str:
    from app.jobs.tasks import _session_factory, _set_done, _set_failed, _set_running

    factory = _session_factory()
    _set_running(factory, id_frap_job)
    try:
        resultado = await asyncio.to_thread(localizar_notificacoes, ids)
        _set_done(factory, id_frap_job, resultado)
        return resultado
    except Exception as exc:
        _set_failed(factory, id_frap_job, repr(exc))
        raise


# Mesmo critério de processo_lookup.notificacao: informação de notificação alusiva a folha.
_SQL_NOTIFICADOS = """
SELECT DISTINCT p.IdProcesso
FROM dbo.vw_ata_informacao inf
JOIN dbo.Processos p
  ON RTRIM(p.numero_processo) = RTRIM(inf.numero_processo)
 AND RTRIM(p.ano_processo) = RTRIM(inf.ano_processo)
WHERE (inf.nome_informacao LIKE '%NOTIFICA%' OR inf.resumo LIKE '%Notifica%')
  AND (inf.nome_informacao LIKE '%FOLHA%' OR inf.resumo LIKE '%folha%')
  AND inf.data_resumo >= :desde
"""

# Envio vivo à PGE (qualquer status lá): a cobrança deixou de ser da CCD. 4 = Cancelado.
_PGE_VIVO = "p.DataCancelamento IS NULL AND p.IdStatusEnvio <> 4"
_SQL_NA_PGE = f"SELECT DISTINCT p.IdDebitoExecucao FROM dbo.PGE_Processo p WHERE {_PGE_VIVO}"

# Débito vigente da pessoa do cadastro no processo (folha da cadeia, não cancelado).
_DEBITOS_DA_PESSOA = """
    FROM processo.dbo.Exe_Debito d
    JOIN processo.dbo.Exe_DebitoPessoa dp ON dp.IDDebito = d.IdDebito
    WHERE dp.IDPessoa = c.IdPessoa
      AND (d.IdProcessoExecucao = c.IdProcesso OR d.IdProcessoOrigem = c.IdProcesso)
      AND d.DataCancelamento IS NULL
      AND NOT EXISTS (SELECT 1 FROM processo.dbo.Exe_Debito f
                      WHERE f.IdDebitoAnterior = d.IdDebito AND f.DataCancelamento IS NULL)
"""
_PGE_DO = (
    "EXISTS (SELECT 1 FROM processo.dbo.PGE_Processo p WHERE p.IdDebitoExecucao = {deb} AND {vivo})"
)

# ponytail: match pelo IdDebito exato; envio feito no filho de cadeia desdobrada não é visto.
_WHERE_ENVIADOS_PGE = f"""
WHERE c.Ativo = 1 AND (
    (c.IdDebito IS NOT NULL AND {_PGE_DO.format(deb="c.IdDebito", vivo=_PGE_VIVO)})
    OR (c.IdDebito IS NULL AND c.IdPessoa IS NOT NULL
        AND EXISTS (SELECT 1 {_DEBITOS_DA_PESSOA}
                    AND {_PGE_DO.format(deb="d.IdDebito", vivo=_PGE_VIVO)})
        AND NOT EXISTS (SELECT 1 {_DEBITOS_DA_PESSOA}
                        AND NOT {_PGE_DO.format(deb="d.IdDebito", vivo=_PGE_VIVO)}))
)
"""


def desativar_enviados_pge(s: Session) -> int:
    """Desativa cadastros cujo débito (ou todos os vigentes da pessoa) foi enviado à PGE.

    Sem débito e sem pessoa: fica, revisão manual.
    """
    from datetime import datetime

    agora = datetime.utcnow().replace(microsecond=0)
    n = s.execute(
        text(
            "UPDATE c SET Ativo = 0, DataAtualizacao = :agora,"
            " Observacoes = COALESCE(c.Observacoes + ' | ', '') + :obs"
            f" FROM CCDDescontoFolha c {_WHERE_ENVIADOS_PGE}"
        ),
        {"agora": agora, "obs": f"desativado: débito enviado à PGE ({date.today():%d/%m/%Y})"},
    ).rowcount
    s.commit()
    return int(n or 0)


def _pessoas_novas(
    debitos: list[dict[str, Any]],
    existentes: set[int | None],
    na_pge: frozenset[int] | set[int] = frozenset(),
) -> list[tuple[int, int | None]]:
    """(id_pessoa, id_debito) a cadastrar: pessoa física com débito vigente fora da PGE e
    sem cadastro.

    id_debito só quando a pessoa tem um único débito vigente (convenção da migração 0024).
    `None` em `existentes` = cadastro migrado sem pessoa: o processo inteiro já está coberto.
    """
    if None in existentes:
        return []
    por_pessoa: dict[int, list[int]] = {}
    for d in debitos:
        doc = "".join(ch for ch in str(d.get("documento") or "") if ch.isdigit())
        if d["data_cancelamento"] is not None or d.get("desdobrado") or len(doc) != 11:
            continue
        if int(d["id_debito"]) in na_pge:
            continue
        if d["id_pessoa"] is None or int(d["id_pessoa"]) in existentes:
            continue
        por_pessoa.setdefault(int(d["id_pessoa"]), []).append(int(d["id_debito"]))
    return [(p, ds[0] if len(ds) == 1 else None) for p, ds in por_pessoa.items()]


def detectar_cadastros(desde: date = date(2024, 1, 1)) -> str:
    """Cria cadastro para cada processo notificado desde `desde` que ainda não está na tela.

    Antes, desativa os cadastros enviados à PGE. Pares (processo, pessoa) já existentes,
    inclusive removidos ou desativados (Ativo = 0), não voltam.
    """
    from fastapi import HTTPException

    from app.ccd.desconto_folha import processo_lookup, schemas, service
    from app.db import get_processo_engine
    from app.jobs.tasks import _session_factory

    factory = _session_factory()
    obs = f"detectado automaticamente em {date.today():%d/%m/%Y}"
    criados = sem_pessoa = 0
    with Session(get_processo_engine()) as sp, factory() as s:
        desativados = desativar_enviados_pge(s)
        na_pge = {int(i) for i in sp.execute(text(_SQL_NA_PGE)).scalars()}
        ids = [int(i) for i in sp.execute(text(_SQL_NOTIFICADOS), {"desde": desde}).scalars()]
        existentes: dict[int, set[int | None]] = {}
        for idp, idpes in s.execute(text("SELECT IdProcesso, IdPessoa FROM CCDDescontoFolha")):
            existentes.setdefault(int(idp), set()).add(None if idpes is None else int(idpes))
        for idp in ids:
            debitos = processo_lookup.debitos_do_processo(sp, idp)
            novas = _pessoas_novas(debitos, existentes.get(idp, set()), na_pge)
            if not novas and idp not in existentes:
                sem_pessoa += 1
            for id_pessoa, id_debito in novas:
                payload = schemas.CadastroInput(
                    id_processo=idp, id_debito=id_debito, id_pessoa=id_pessoa, observacoes=obs
                )
                try:
                    service.criar(s, sp, payload, id_usuario=None)
                except HTTPException:  # 409: o débito já tem cadastro de outra pessoa
                    continue
                criados += 1
    return (
        f"{desativados} cadastro(s) desativado(s) por envio à PGE; {len(ids)} processo(s) "
        f"notificado(s) desde {desde:%d/%m/%Y}: {criados} cadastro(s) criado(s), {sem_pessoa} "
        "sem pessoa física com débito vigente fora da PGE"
    )


async def task_detectar_cadastros_desconto_folha(ctx: dict[str, Any]) -> str:
    """Cron diário: notificações emitidas depois da carga de 14/09/2026 não entravam na tela."""
    return await asyncio.to_thread(detectar_cadastros)


def conciliar_pendentes() -> str:
    """Roda o match automático nos cadastros ativos com valor ainda sem conciliação."""
    from app.ccd.desconto_folha import match
    from app.jobs.tasks import _session_factory

    factory = _session_factory()
    with factory() as s:
        ids = (
            s.execute(
                text(
                    """
                SELECT DISTINCT d.IdCCDDescontoFolha
                FROM CCDDescontoFolha d
                JOIN CCDDescontoFolhaValor v ON v.IdCCDDescontoFolha = d.IdCCDDescontoFolha
                LEFT JOIN CCDDescontoFolhaMatch m
                    ON m.IdCCDDescontoFolhaValor = v.IdCCDDescontoFolhaValor
                WHERE d.Ativo = 1 AND m.IdCCDDescontoFolhaMatch IS NULL
                """
                )
            )
            .scalars()
            .all()
        )
        vinculados = sum(match.match_automatico(s, id_cadastro=int(i)) for i in ids)
    return f"{len(ids)} cadastro(s) com valor pendente, {vinculados} conciliação(ões) nova(s)"


async def task_conciliar_desconto_folha(ctx: dict[str, Any]) -> str:
    """Cron diário: créditos que entram no FRAP depois da extração não eram
    conciliados sem alguém clicar em "Match automático"."""
    return await asyncio.to_thread(conciliar_pendentes)


async def task_extrair_resposta_desconto_folha(
    ctx: dict[str, Any], id_frap_job: int, id_cadastro: int
) -> str:
    from app.ccd.desconto_folha.extracao import extrair_resposta
    from app.jobs.tasks import _session_factory, _set_done, _set_failed, _set_running

    factory = _session_factory()
    _set_running(factory, id_frap_job)
    try:
        resultado = await asyncio.to_thread(extrair_resposta, id_cadastro)
        _set_done(factory, id_frap_job, resultado)
        return resultado
    except Exception as exc:
        _set_failed(factory, id_frap_job, repr(exc))
        raise
