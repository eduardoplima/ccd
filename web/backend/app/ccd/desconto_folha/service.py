"""Listagem de candidatos (lado HTTP) e geração de documentos (lado worker).

Espelha o notebook `scripts/automacao/desconto_folha.ipynb`:
- candidatos = processos no setor CCD com o marcador
  "DESCONTO EM FOLHA - Implementar" (ou todos os processos da CCD, com `todos`);
- geração = uma query parametrizada por processo selecionado, filtragem por
  dívida em aberto, agregação do valor da multa e render do template
  `desconto_folha.docx` → PDF por linha resultante.
"""

from __future__ import annotations

import locale
from collections import defaultdict
from pathlib import Path

from num2words import num2words
from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.ccd.desconto_folha.schemas import (
    CandidatoOut,
    CandidatosResponse,
)
from app.ccd.gen.render import docx_to_pdf, render_docx, set_pt_br_locale

# Setor CCD no banco `processo` (Pro_Marcador.IdSetor).
ID_SETOR_CCD = 762
MARCADOR_DESCONTO_FOLHA = "DESCONTO EM FOLHA - Implementar"


# ---------------------------------------------------------------------------
# Listagem de candidatos (lado HTTP, sessão somente leitura do `processo`)
# ---------------------------------------------------------------------------


def listar_candidatos(session: Session, *, todos: bool = False) -> CandidatosResponse:
    """Processos do setor CCD candidatos à geração de despacho de desconto.

    Por padrão filtra pelo marcador-CCD mais recente
    "DESCONTO EM FOLHA - Implementar". Com `todos=True`, retorna todos os
    processos do setor CCD.
    """
    if todos:
        sql = text(
            """
            SELECT
                RTRIM(p.numero_processo) AS numero_processo,
                RTRIM(p.ano_processo)    AS ano_processo,
                RTRIM(p.assunto)         AS assunto
            FROM dbo.Processos p
            WHERE p.setor_atual = 'CCD' AND p.IdProcessoApensador IS NULL
            ORDER BY p.ano_processo DESC, p.numero_processo DESC
            """
        )
        params: dict[str, object] = {}
    else:
        sql = text(
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
            SELECT
                RTRIM(p.numero_processo) AS numero_processo,
                RTRIM(p.ano_processo)    AS ano_processo,
                RTRIM(p.assunto)         AS assunto
            FROM dbo.Processos p
            JOIN marc mc ON mc.IdProcesso = p.IdProcesso AND mc.rn = 1
            WHERE p.setor_atual = 'CCD'
              AND p.IdProcessoApensador IS NULL
              AND mc.marcador = :marcador
            ORDER BY p.ano_processo DESC, p.numero_processo DESC
            """
        )
        params = {"id_setor": ID_SETOR_CCD, "marcador": MARCADOR_DESCONTO_FOLHA}

    rows = session.execute(sql, params).mappings().all()
    items = [
        CandidatoOut(
            processo=f"{r['numero_processo']}/{r['ano_processo']}",
            assunto=r["assunto"],
        )
        for r in rows
    ]
    return CandidatosResponse(items=items, total=len(items))


# ---------------------------------------------------------------------------
# Geração de documentos (lado worker — sem DI; engine própria do `processo`)
# ---------------------------------------------------------------------------

_QUERY_DESCONTOS = text(
    """
    SELECT
        RTRIM(pro.numero_processo) AS numero_processo,
        RTRIM(pro.ano_processo)    AS ano_processo,
        pro.assunto,
        CONCAT(gp.Nome, ' (CPF: ', gp.Documento, ')') AS nome,
        processo.dbo.fn_Exe_RetornaValorAtualizado(ed.IdDebito) AS valor_multa,
        orgao_info.nome_orgao,
        ed.CodigoStatusDivida AS status_divida,
        ed.IdDebito
    FROM processo.dbo.Processos pro
    INNER JOIN processo.dbo.Pro_MarcadorProcesso pmp ON pmp.IdProcesso = pro.IdProcesso
    INNER JOIN processo.dbo.Pro_Marcador pm        ON pmp.IdMarcador = pm.IdMarcador
    LEFT JOIN processo.dbo.Exe_Debito ed           ON ed.IdProcessoExecucao = pro.IdProcesso
    LEFT JOIN processo.dbo.Exe_DebitoPessoa edp    ON edp.IDDebito = ed.IdDebito
    LEFT JOIN processo.dbo.GenPessoa gp            ON gp.IdPessoa = edp.IDPessoa
    OUTER APPLY (
        SELECT TOP 1 vspfr.nome_orgao
        FROM BdDIP.dbo.vwSiaiPessoalFolhaResumida vspfr
        WHERE vspfr.cpf = gp.Documento COLLATE SQL_Latin1_General_CP1_CI_AS
        ORDER BY vspfr.ano DESC, vspfr.mes DESC
    ) AS orgao_info
    WHERE pro.setor_atual = 'CCD'
      AND CONCAT(RTRIM(pro.numero_processo), '/', RTRIM(pro.ano_processo)) IN :processos
    """
).bindparams(bindparam("processos", expanding=True))


def _criar_valor_extenso(x: float) -> str:
    if x and x > 1:
        f = lambda c: num2words(int(c), lang="pt_BR")  # noqa: E731
        return " reais e ".join(f(y) for y in "{:.2f}".format(x).split(".")) + " centavos"
    return ""


def _converter_valor(x: float) -> str:
    if x:
        return locale.currency(x, grouping=True) + " (" + _criar_valor_extenso(x) + ")"
    return "R$ 0,00 (zero)"


def gerar_documentos(processos: list[str], out_dir: Path) -> list[Path]:
    """Gera um despacho `.docx`→PDF por processo com dívida em aberto.

    Espelha o notebook (sem a "Manobra Nereu"): mantém apenas linhas com
    `status_divida == 1`, agrega o valor da multa por (processo, pessoa, órgão)
    e renderiza o template `desconto_folha.docx`. Retorna os PDFs gerados.
    Levanta `ValueError` em pt-BR se nada for gerado.
    """
    from app.db import get_processo_engine

    if not processos:
        raise ValueError("Nenhum processo informado para geração.")

    engine = get_processo_engine()
    with engine.connect() as conn:
        rows = conn.execute(_QUERY_DESCONTOS, {"processos": processos}).mappings().all()

    set_pt_br_locale()

    # Mantém só dívida em aberto e agrega o valor da multa por chave do despacho.
    # chave: (numero, ano, assunto, nome, nome_orgao, status_divida) -> soma valor_multa
    agregado: dict[tuple, float] = defaultdict(float)
    for r in rows:
        if r["status_divida"] != 1:
            continue
        chave = (
            r["numero_processo"],
            r["ano_processo"],
            r["assunto"],
            r["nome"],
            r["nome_orgao"],
            r["status_divida"],
        )
        agregado[chave] += float(r["valor_multa"] or 0)

    pdfs: list[Path] = []
    for (numero, ano, assunto, nome, nome_orgao, _status), valor_multa in agregado.items():
        processo = f"{numero}/{ano}"
        context = {
            "processo": processo,
            "assunto": assunto,
            "nome": nome,
            "orgao": nome_orgao or "",
            "valor": _converter_valor(valor_multa),
        }
        primeiro_nome = nome.split()[0].lower() if nome else "sem_nome"
        stem = f"{processo.replace('/', '_')}_{primeiro_nome}"
        docx_path = out_dir / f"{stem}.docx"
        render_docx("desconto_folha.docx", context, docx_path)
        pdf = docx_to_pdf(docx_path, out_dir)
        pdfs.append(pdf)

    if not pdfs:
        raise ValueError(
            "Nenhum dos processos selecionados possui débito em aberto "
            "(dívida com status 1). Nada foi gerado."
        )
    return pdfs
