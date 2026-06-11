"""Listagem de candidatos (HTTP, somente leitura) + geração dos despachos de
antecedentes (worker ARQ). Espelha o notebook `antecedentes.ipynb`.
"""

from __future__ import annotations

import locale
import logging
import math
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from app.ccd.antecedentes.schemas import (
    CandidatoAntecedentes,
    CandidatosAntecedentesResponse,
)
from app.ccd.gen.render import docx_to_pdf, render_docx, set_pt_br_locale

logger = logging.getLogger(__name__)

# Setor CCD no banco `processo` (mesmo de app.ccd.service.ID_SETOR_CCD).
ID_SETOR_CCD = 762

_SQL_DIR = Path(__file__).resolve().parent / "sql"

# Query de fallback para o CPF do responsável quando o trânsito não traz nenhum.
# Espelha `get_cpf_responsavel` do notebook, mas com parâmetros nomeados.
_SQL_CPF_RESPONSAVEL = text(
    """
    SELECT gp.Documento as cpf
    FROM Processo.dbo.Processos p
    INNER JOIN Processo.dbo.Pro_ProcessosResponsavelDespesa pprd
        ON pprd.IdProcesso = p.IdProcesso
    INNER JOIN Processo.dbo.GenPessoa gp
        ON gp.IdPessoa = pprd.IdPessoa
    WHERE p.numero_processo = :numero
      AND p.ano_processo = :ano
      AND lower(gp.Nome) = :nome
    """
)


@lru_cache(maxsize=8)
def _read_sql(name: str) -> str:
    return (_SQL_DIR / name).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Schemas de saída estruturada do LLM (idênticos ao notebook).
# ---------------------------------------------------------------------------


class PessoaAntecedentes(BaseModel):
    nome_pessoa: str = Field(description="Nome da pessoa para buscar antecedentes")


class PessoasAntecedentes(BaseModel):
    pessoas: list[PessoaAntecedentes] = Field(
        description="Lista de pessoas para buscar antecedentes"
    )


_PROMPT_PESSOAS = """
    Você é um agente que identifica listas de pessoas em requisições de antecedentes.
      Você recebeu uma requisição para buscar antecedentes de pessoas em um processo. Remova qualquer vocativo do nome da pessoa, tal como Sr., Sra., Dr., Dra., etc.
      Não inclua nomes de conselheiros, advogados ou partes do processo. Ex: Sra. Conselheira Substituta Ana
Paula de Oliveira Gomes ou Sara Kalline da Silva Mat. 9.780-2 são exemplos para serem ignorados.

      O texto da requisição é o seguinte:
      "{input}"
      Encontre os antecedentes das pessoas listadas na requisição.

    Sua resposta:
    """


# ---------------------------------------------------------------------------
# Listagem de candidatos (lado HTTP, sessão somente leitura do banco `processo`).
# ---------------------------------------------------------------------------


def listar_candidatos(session: Session, *, todos: bool) -> CandidatosAntecedentesResponse:
    sql = text(_read_sql("candidatos.sql"))
    rows = (
        session.execute(sql, {"id_setor": ID_SETOR_CCD, "todos": 1 if todos else 0})
        .mappings()
        .all()
    )
    items = [
        CandidatoAntecedentes(
            processo=r["processo"],
            assunto=r["assunto"],
            interessado=r["interessado"],
        )
        for r in rows
    ]
    return CandidatosAntecedentesResponse(items=items, total=len(items))


# ---------------------------------------------------------------------------
# Geração dos despachos (lado worker) — engine própria contra o banco `processo`.
# ---------------------------------------------------------------------------


def _format_currency(value: Any) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "-"
    try:
        return locale.currency(value, grouping=True, symbol=False)
    except (locale.Error, TypeError, ValueError):
        try:
            return f"{float(value):,.2f}"
        except (TypeError, ValueError):
            return "-"


def _build_llm():
    from app.config import get_settings

    s = get_settings()
    if not (s.azure_openai_api_key and s.azure_openai_endpoint and s.openai_api_version):
        raise RuntimeError(
            "Azure OpenAI não configurado: defina AZURE_OPENAI_API_KEY, "
            "AZURE_OPENAI_ENDPOINT e OPENAI_API_VERSION para gerar antecedentes."
        )
    from langchain_openai import AzureChatOpenAI

    return AzureChatOpenAI(
        azure_deployment=s.azure_openai_deployment,
        api_key=s.azure_openai_api_key,
        azure_endpoint=s.azure_openai_endpoint,
        api_version=s.openai_api_version,
    )


def _extrair_pessoas(llm: Any, texto_despacho: str) -> list[str]:
    from langchain_core.prompts import PromptTemplate

    prompt = PromptTemplate.from_template(_PROMPT_PESSOAS)
    chain = prompt | llm.with_structured_output(schema=PessoasAntecedentes)
    resultado: PessoasAntecedentes = chain.invoke(texto_despacho)
    nomes: list[str] = []
    for p in resultado.pessoas:
        nome = (p.nome_pessoa or "").strip()
        if nome and nome not in nomes:
            nomes.append(nome)
    return nomes


def _transitos_pessoa(conn: Any, nome: str) -> list[dict[str, Any]]:
    sql = text(_read_sql("transito_nome.sql"))
    pattern = f"%{nome.lower()}%"
    rows = conn.execute(sql, {"nome_pattern": pattern}).mappings().all()
    transitos: list[dict[str, Any]] = []
    for r in rows:
        d = dict(r)
        d["valor_original"] = _format_currency(d.get("valor_original"))
        d["valor_atualizado"] = _format_currency(d.get("valor_atualizado"))
        for k, v in d.items():
            if v is None:
                d[k] = ""
        transitos.append(d)
    return transitos


def _cpf_responsavel(conn: Any, nome: str, numero: str, ano: str) -> str:
    row = conn.execute(
        _SQL_CPF_RESPONSAVEL,
        {"numero": numero, "ano": ano, "nome": nome.lower()},
    ).first()
    if row is None:
        return ""
    return (row[0] or "").strip()


def _valores_pessoa(conn: Any, nome: str, numero: str, ano: str) -> dict[str, Any]:
    transitos = _transitos_pessoa(conn, nome)
    cpfs = {t["cpf"] for t in transitos if t.get("cpf")}
    if len(cpfs) > 1:
        logger.warning("Mais de um CPF para %s; deixando em branco", nome)
        cpf = ""
    elif len(cpfs) == 1:
        cpf = next(iter(cpfs)) or ""
    else:
        cpf = _cpf_responsavel(conn, nome, numero, ano)
    return {"nome": nome, "cpf": cpf or "", "transitos": transitos}


def _responsaveis_str(nomes: list[str]) -> str:
    if not nomes:
        return ""
    if len(nomes) == 1:
        return nomes[0]
    return ", ".join(nomes[:-1]) + " e " + nomes[-1]


def gerar_documentos(processos: list[str], out_dir: Path) -> list[Path]:
    """Gera o despacho de antecedentes (PDF) para cada processo selecionado.

    Roda no worker ARQ. Falhas por processo são registradas e não abortam o
    lote; se nenhum PDF for produzido, levanta `ValueError`.
    """
    from app.db import get_processo_engine

    set_pt_br_locale()

    if not processos:
        raise ValueError("Nenhum processo informado para gerar antecedentes.")

    from frap.ccd.pdf import extract_text_from_pdf, informacoes_dir

    engine = get_processo_engine()
    base_dir = informacoes_dir()

    # 1) Informacao mais recente (último despacho) de cada processo.
    sql_info = text(_read_sql("info_despacho.sql")).bindparams(
        bindparam("processos", expanding=True)
    )
    with engine.connect() as conn:
        info_rows = conn.execute(sql_info, {"processos": processos}).mappings().all()

    if not info_rows:
        raise ValueError("Nenhum despacho encontrado para os processos selecionados.")

    llm = _build_llm()
    pdfs: list[Path] = []

    for row in info_rows:
        processo = row["processo"]
        try:
            setor = (row["setor"] or "").strip()
            arquivo = row["arquivo"]
            caminho = base_dir / setor / arquivo
            texto = extract_text_from_pdf(caminho)
            if not texto:
                logger.warning("Processo %s: PDF ausente ou sem texto (%s)", processo, caminho)
                continue

            nomes = _extrair_pessoas(llm, texto)

            with engine.connect() as conn:
                valores = [
                    _valores_pessoa(conn, nome, row["numero_processo"], row["ano_processo"])
                    for nome in nomes
                ]

            for v in valores:
                if v["cpf"] is None:
                    v["cpf"] = ""

            context = {
                "processo": processo,
                "assunto": row["assunto"],
                "interessado": row["interessado"],
                "valores": valores,
                "responsaveis": _responsaveis_str([v["nome"] for v in valores]),
                "data": datetime.now().strftime("%d/%m/%Y"),
                "sem_valores": all(not v["transitos"] for v in valores),
            }

            stem = processo.replace("/", "_")
            docx_path = out_dir / f"{stem}.docx"
            render_docx("antecedentes.docx", context, docx_path)
            pdf = docx_to_pdf(docx_path, out_dir)
            pdfs.append(pdf)
            logger.info("Processo %s: despacho de antecedentes gerado", processo)
        except Exception:
            logger.exception("Falha ao gerar antecedentes do processo %s", processo)

    if not pdfs:
        raise ValueError(
            "Nenhum despacho foi gerado (despachos ausentes, sem texto ou falha na extração)."
        )
    return pdfs
