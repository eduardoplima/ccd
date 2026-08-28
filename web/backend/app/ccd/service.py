from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.ccd.schemas import (
    FiltrosCCDResponse,
    MarcadorOption,
    PrescricaoCCDListResponse,
    PrescricaoCCDOut,
    ProcessoCCDListResponse,
    ProcessoCCDOut,
    RelatorOption,
)

# Setor CCD no banco `processo` (Setor.idSetor / Pro_Marcador.IdSetor).
ID_SETOR_CCD = 762

# Marcadores de permanência legítima na CCD (espelha scripts/analise/instrucao_ccd.py).
MARCADORES_PERMANENCIA = {
    5032,  # PARCELAMENTO EM CURSO
    5684,  # DESCONTO EM FOLHA - ACOMPANHAMENTO
    5469,  # DESCONTO EM FOLHA - Acompanhamento Nereu
    5846,  # Nereu - SOBRESTADO
    5591,  # SOBRESTADO - Decisão judicial
    5966,  # DECISÃO JUDICIAL - Acompanhamento
    5020,  # DECISÃO JUDICIAL - Suspender os efeitos do Acórdão
    6127,  # EXECUÇÃO - aguardando determinações ou impedimentos
    5790,  # Chamados abertos aguardando solução
    5593,  # Protesto Efetivo Junho/2026
    5712,  # Protesto Efetivo Julho/2026
    5797,  # PAGAMENTO INTEGRAL
    5040,  # PROTESTO - Confirmação de envio
    5041,  # PROTESTO - Enviado
}
# IDs vêm de constante interna (ints), não de input — interpolação segura.
_IDS_PERMANENCIA = ", ".join(str(i) for i in sorted(MARCADORES_PERMANENCIA))
_SQL_SEM_PERMANENCIA = f"""NOT EXISTS (
    SELECT 1 FROM dbo.Pro_MarcadorProcesso mpx
    WHERE mpx.IdProcesso = p.IdProcesso AND mpx.DataExclusao IS NULL
      AND mpx.IdMarcador IN ({_IDS_PERMANENCIA})
)"""

# Whitelist de ordenação: chave de coluna -> expressão SQL (nunca interpolar input).
_SORT_COLUMNS: dict[str, str] = {
    "processo": "p.ano_processo, p.numero_processo",
    "marcador": "mc.marcador",
    "data_marcador": "mc.DataInclusao",
    "dias_ccd": "dias_ccd",  # alias do SELECT; DESC manda os NULL para o fim
    "origem": "o.nome",
    "relator": "r.nome",
    "tipo": "t.descricao",
    "assunto": "p.assunto",
}
_DEFAULT_ORDER = "mc.DataInclusao DESC, p.ano_processo DESC, p.numero_processo DESC"


def listar_processos(
    session: Session,
    *,
    marcador: str | None = None,
    sem_marcador: bool = False,
    relator: str | None = None,
    assunto: str | None = None,
    sort: str | None = None,
    order: str = "asc",
    page: int = 1,
    size: int = 100,
    ocultar_permanencia: bool = False,
) -> ProcessoCCDListResponse:
    where: list[str] = ["p.setor_atual = 'CCD'", "p.IdProcessoApensador IS NULL"]
    params: dict[str, Any] = {"id_setor": ID_SETOR_CCD}

    if ocultar_permanencia:
        where.append(_SQL_SEM_PERMANENCIA)

    if sem_marcador:
        where.append("mc.marcador IS NULL")
    elif marcador:
        where.append("mc.marcador = :marcador")
        params["marcador"] = marcador
    if relator:
        where.append("p.codigo_relator = :relator_codigo")
        params["relator_codigo"] = relator
    if assunto:
        where.append("p.assunto LIKE :assunto")
        params["assunto"] = f"%{assunto}%"

    where_sql = " AND ".join(where)
    offset = (page - 1) * size
    page_params = {**params, "offset": offset, "size": size}

    if sort in _SORT_COLUMNS:
        direction = "DESC" if str(order).lower() == "desc" else "ASC"
        if sort == "processo":
            order_sql = f"p.ano_processo {direction}, p.numero_processo {direction}"
        else:
            # desempate estável por processo (colunas distintas da de ordenação)
            order_sql = (
                f"{_SORT_COLUMNS[sort]} {direction}, p.ano_processo DESC, p.numero_processo DESC"
            )
    else:
        order_sql = _DEFAULT_ORDER

    sql = text(
        f"""
        WITH marc AS (
            SELECT mp.IdProcesso, m.Descricao AS marcador, mp.DataInclusao,
                   ROW_NUMBER() OVER (
                       PARTITION BY mp.IdProcesso ORDER BY mp.DataInclusao DESC
                   ) AS rn
            FROM dbo.Pro_MarcadorProcesso mp
            JOIN dbo.Pro_Marcador m ON m.IdMarcador = mp.IdMarcador
            WHERE m.IdSetor = :id_setor AND mp.DataExclusao IS NULL
        ),
        entrada AS (
            SELECT ie.IdProcesso, MAX(ie.recebido_em) AS recebido_em
            FROM dbo.Itens_Lote ie
            JOIN dbo.Lotes lt ON lt.IdLote = ie.IdLote
            WHERE lt.destino = 'CCD'
            GROUP BY ie.IdProcesso
        )
        SELECT
            RTRIM(p.numero_processo) AS numero_processo,
            RTRIM(p.ano_processo)    AS ano_processo,
            RTRIM(mc.marcador)       AS marcador,
            mc.DataInclusao          AS data_marcador,
            ent.recebido_em          AS entrada_ccd,
            DATEDIFF(DAY, ent.recebido_em, GETDATE()) AS dias_ccd,
            RTRIM(o.nome)            AS origem,
            RTRIM(r.nome)            AS relator,
            RTRIM(t.descricao)       AS tipo,
            RTRIM(p.assunto)         AS assunto,
            COUNT(*) OVER()          AS total
        FROM dbo.Processos p
        LEFT JOIN marc mc      ON mc.IdProcesso = p.IdProcesso AND mc.rn = 1
        LEFT JOIN entrada ent  ON ent.IdProcesso = p.IdProcesso
        LEFT JOIN dbo.Relator r ON r.codigo = p.codigo_relator
        LEFT JOIN dbo.Tipo t    ON t.codigo = p.codigo_tipo_processo
        LEFT JOIN dbo.Orgaos o  ON o.codigo = p.sigla_origem
        WHERE {where_sql}
        ORDER BY {order_sql}
        OFFSET :offset ROWS FETCH NEXT :size ROWS ONLY
        """
    ).bindparams(bindparam("offset"), bindparam("size"))

    rows = session.execute(sql, page_params).mappings().all()
    total = int(rows[0]["total"]) if rows else 0

    items = [
        ProcessoCCDOut(
            processo=f"{r['numero_processo']}/{r['ano_processo']}",
            numero_processo=r["numero_processo"],
            ano_processo=r["ano_processo"],
            marcador=r["marcador"],
            data_marcador=r["data_marcador"],
            entrada_ccd=r["entrada_ccd"],
            dias_ccd=r["dias_ccd"],
            origem=r["origem"],
            relator=r["relator"],
            tipo=r["tipo"],
            assunto=r["assunto"],
        )
        for r in rows
    ]
    return ProcessoCCDListResponse(items=items, total=total, page=page, size=size)


_PRAZO_PRESCRICIONAL_DIAS = 5 * 365


def _classificar(
    data_base: datetime | date | None, hoje: date
) -> tuple[str, int | None, date | None]:
    """(categoria, dias_decorridos, data_prescricao). 5 anos da base (STF Tema 899)."""
    if data_base is None:
        return "sem_referencia", None, None
    if isinstance(data_base, datetime):
        data_base = data_base.date()
    dias = (hoje - data_base).days
    data_prescricao = data_base + timedelta(days=_PRAZO_PRESCRICIONAL_DIAS)
    if dias >= _PRAZO_PRESCRICIONAL_DIAS:
        return "prescrito", dias, data_prescricao
    if dias >= 4 * 365:
        return "risco", dias, data_prescricao
    return "ok", dias, data_prescricao


def listar_prescricao(
    session: Session, *, ocultar_permanencia: bool = True
) -> PrescricaoCCDListResponse:
    """Processos na CCD com débito aberto, ordenados pela proximidade da prescrição.

    Regra (STF Tema 899): multa E ressarcimento prescrevem em 5 anos, contados da
    citação C05 mais recente (interrompe) ou, na falta dela, do trânsito em julgado.
    Parcelamento vigente suspende — coberto pelo marcador 5032 no filtro de permanência.
    """
    filtro_permanencia = f"AND {_SQL_SEM_PERMANENCIA}" if ocultar_permanencia else ""
    # ponytail: "aberto" = folha da cadeia com status não cancelado; pagamento integral
    # aparece via marcador 5797 (filtrado por padrão). Se surgirem falsos positivos de
    # débito quitado, replicar a agregação de cadeia do scripts/analise/carteira_ipsas.py.
    sql = text(
        f"""
        WITH deb AS (
            -- débitos vigentes (folha da cadeia) e abertos de processos hoje na CCD;
            -- vínculo pelos DOIS papéis (origem OU execução), nunca COALESCE
            SELECT p.IdProcesso AS id_ccd, e.IdDebito, e.IdProcessoOrigem, e.IdProcessoExecucao,
                   e.valorOriginalDebito AS valor, e.dataTransito
            FROM dbo.Processos p
            JOIN dbo.Exe_Debito e
              ON e.IdProcessoOrigem = p.IdProcesso OR e.IdProcessoExecucao = p.IdProcesso
            JOIN dbo.Exe_StatusDivida sd ON sd.CodigoStatusDivida = e.CodigoStatusDivida
            WHERE p.setor_atual = 'CCD' AND p.IdProcessoApensador IS NULL
              AND NOT EXISTS (SELECT 1 FROM dbo.Exe_Debito g
                              WHERE g.IdDebitoAnterior = e.IdDebito)
              AND sd.StatusCancelamento IS NULL
              {filtro_permanencia}
        ),
        cit AS (
            -- citação C05 mais recente por processo (interrompe a prescrição);
            -- data via informação vinculada (Data_envio_AR é sempre vazia)
            SELECT c.IdProcesso,
                   MAX(COALESCE(inf.DataPublicacao, inf.data_ultima_atualizacao,
                                c.DataInclusao)) AS data_citacao
            FROM dbo.Cit_Citacoes c
            LEFT JOIN dbo.vw_ata_informacao inf ON inf.idInformacao = c.IdInformacao
            WHERE (c.Tipo = 'C05' OR (c.Tipo = 'C' AND c.Prazo = 5))
              AND c.DataExclusao IS NULL
            GROUP BY c.IdProcesso
        ),
        tj AS (
            -- trânsito por processo (fallback quando o débito não tem dataTransito)
            SELECT p2.IdProcesso, MAX(t.datatransito) AS data_transito
            FROM dbo.Processo_TransitoJulgado t
            JOIN dbo.Processos p2 ON p2.numero_processo = t.numero_processo
                                 AND p2.ano_processo = t.ano_processo
            WHERE t.inativo = 0
            GROUP BY p2.IdProcesso
        ),
        calc AS (
            SELECT d.id_ccd, d.valor,
                   (SELECT MAX(v) FROM (VALUES (co.data_citacao), (ce.data_citacao)) x(v))
                       AS data_citacao,
                   COALESCE(d.dataTransito, tjo.data_transito, tje.data_transito)
                       AS data_transito
            FROM deb d
            LEFT JOIN cit co ON co.IdProcesso = d.IdProcessoOrigem
            LEFT JOIN cit ce ON ce.IdProcesso = d.IdProcessoExecucao
            LEFT JOIN tj tjo ON tjo.IdProcesso = d.IdProcessoOrigem
            LEFT JOIN tj tje ON tje.IdProcesso = d.IdProcessoExecucao
        ),
        ranqueado AS (
            SELECT id_ccd,
                   COALESCE(data_citacao, data_transito) AS data_base,
                   CASE WHEN data_citacao IS NOT NULL THEN N'citação'
                        WHEN data_transito IS NOT NULL THEN N'trânsito' END AS fonte_base,
                   SUM(valor)   OVER (PARTITION BY id_ccd) AS valor_total,
                   COUNT(*)     OVER (PARTITION BY id_ccd) AS qtd_debitos,
                   ROW_NUMBER() OVER (
                       PARTITION BY id_ccd
                       ORDER BY CASE WHEN COALESCE(data_citacao, data_transito) IS NULL
                                     THEN 1 ELSE 0 END,
                                COALESCE(data_citacao, data_transito) ASC
                   ) AS rn  -- débito com base mais antiga = prescreve primeiro
            FROM calc
        )
        SELECT RTRIM(p.numero_processo) AS numero_processo,
               RTRIM(p.ano_processo)    AS ano_processo,
               RTRIM(r.nome)            AS relator,
               RTRIM(p.assunto)         AS assunto,
               q.data_base, q.fonte_base, q.qtd_debitos, q.valor_total,
               resp.responsaveis
        FROM ranqueado q
        JOIN dbo.Processos p    ON p.IdProcesso = q.id_ccd
        LEFT JOIN dbo.Relator r ON r.codigo = p.codigo_relator
        OUTER APPLY (
            -- responsáveis (distintos) dos débitos abertos do processo
            -- (FOR XML PATH: o servidor é pré-2017, sem STRING_AGG)
            SELECT STUFF((
                SELECT ', ' + x.nome
                FROM (SELECT DISTINCT RTRIM(gp.Nome) AS nome
                      FROM deb d2
                      JOIN dbo.Exe_DebitoPessoa dp ON dp.IDDebito = d2.IdDebito
                      JOIN dbo.GenPessoa gp ON gp.IdPessoa = dp.IDPessoa
                      WHERE d2.id_ccd = q.id_ccd) x
                ORDER BY x.nome
                FOR XML PATH(''), TYPE
            ).value('.', 'NVARCHAR(MAX)'), 1, 2, '') AS responsaveis
        ) resp
        WHERE q.rn = 1
        ORDER BY CASE WHEN q.data_base IS NULL THEN 1 ELSE 0 END, q.data_base ASC
        """
    )
    rows = session.execute(sql).mappings().all()

    hoje = date.today()
    items = []
    for r in rows:
        categoria, dias, data_prescricao = _classificar(r["data_base"], hoje)
        items.append(
            PrescricaoCCDOut(
                processo=f"{r['numero_processo']}/{r['ano_processo']}",
                numero_processo=r["numero_processo"],
                ano_processo=r["ano_processo"],
                relator=r["relator"],
                assunto=r["assunto"],
                responsaveis=r["responsaveis"],
                categoria=categoria,
                fonte_base=r["fonte_base"],
                data_base=r["data_base"],
                data_prescricao=data_prescricao,
                dias_decorridos=dias,
                qtd_debitos=int(r["qtd_debitos"]),
                valor_total=float(r["valor_total"] or 0),
            )
        )
    return PrescricaoCCDListResponse(items=items, total=len(items))


def listar_filtros(session: Session) -> FiltrosCCDResponse:
    # Contagem de processos do conjunto por marcador-CCD MAIS RECENTE. O grupo
    # NULL (marcador IS NULL) é a contagem de "sem marcador".
    rows = (
        session.execute(
            text(
                """
            WITH marc AS (
                SELECT mp.IdProcesso, m.Descricao AS marcador,
                       ROW_NUMBER() OVER (
                           PARTITION BY mp.IdProcesso ORDER BY mp.DataInclusao DESC
                       ) AS rn
                FROM dbo.Pro_MarcadorProcesso mp
                JOIN dbo.Pro_Marcador m ON m.IdMarcador = mp.IdMarcador
                WHERE m.IdSetor = :id_setor AND mp.DataExclusao IS NULL
            )
            SELECT RTRIM(mc.marcador) AS descricao, COUNT(*) AS quantidade
            FROM dbo.Processos p
            LEFT JOIN marc mc ON mc.IdProcesso = p.IdProcesso AND mc.rn = 1
            WHERE p.setor_atual = 'CCD' AND p.IdProcessoApensador IS NULL
            GROUP BY RTRIM(mc.marcador)
            ORDER BY descricao
            """
            ),
            {"id_setor": ID_SETOR_CCD},
        )
        .mappings()
        .all()
    )

    marcadores = [
        MarcadorOption(descricao=str(r["descricao"]).strip(), quantidade=int(r["quantidade"]))
        for r in rows
        if r["descricao"]
    ]
    sem_marcador = next((int(r["quantidade"]) for r in rows if not r["descricao"]), 0)

    relatores = [
        RelatorOption(codigo=str(r["codigo"]).strip(), nome=str(r["nome"]).strip())
        for r in session.execute(
            text(
                """
                SELECT DISTINCT RTRIM(r.codigo) AS codigo, RTRIM(r.nome) AS nome
                FROM dbo.Processos p
                JOIN dbo.Relator r ON r.codigo = p.codigo_relator
                WHERE p.setor_atual = 'CCD' AND p.IdProcessoApensador IS NULL
                ORDER BY nome
                """
            )
        )
        .mappings()
        .all()
    ]

    return FiltrosCCDResponse(marcadores=marcadores, sem_marcador=sem_marcador, relatores=relatores)
