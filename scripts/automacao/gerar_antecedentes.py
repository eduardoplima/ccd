"""Gera os despachos de antecedentes (docx + pdf) dos processos na CCD.

Pipeline (porta de web/backend/app/ccd/antecedentes/service.py::gerar_documentos,
no venv principal via pacote `ccd`): descobre os processos com marcador
`%antecedente%` no CCD -> pega o despacho-fonte mais recente de cada -> LLM
extrai os responsáveis -> busca os débitos transitados em julgado por nome ->
renderiza templates/antecedentes.docx -> converte para PDF `NNNNNN_YYYY.pdf`
(padrão consumido por `area_restrita.py informacao-lote`).

Uso:
    python -m scripts.automacao.gerar_antecedentes --dry-run          # só lista os candidatos
    python -m scripts.automacao.gerar_antecedentes                    # gera todos os candidatos
    python -m scripts.automacao.gerar_antecedentes 000206/2026 ...    # gera só estes
"""

from __future__ import annotations

import argparse
import contextlib
import locale
import math
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import bindparam, text

from ccd.config import REPO_ROOT, informacoes_dir, read_sql
from ccd.db import get_connection
from ccd.docs import docx_to_pdf, render_template
from ccd.pdf import extract_text_from_pdf

ID_SETOR_CCD = 762
DEFAULT_LLM_MODEL = "gpt-4.1"  # endpoint /openai/v1 → ChatOpenAI(base_url=), não AzureChatOpenAI
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE = BASE_DIR / "templates" / "antecedentes.docx"
SAIDA_DEFAULT = REPO_ROOT / "saidas" / "automacao" / "antecedentes" / f"gaana_{datetime.now():%Y%m%d}"

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


class PessoaAntecedentes(BaseModel):
    nome_pessoa: str = Field(description="Nome da pessoa para buscar antecedentes")


class PessoasAntecedentes(BaseModel):
    pessoas: list[PessoaAntecedentes] = Field(description="Lista de pessoas para buscar antecedentes")


def descobrir_candidatos(conn) -> list[dict[str, Any]]:
    sql = text(read_sql("antecedentes_candidatos.sql"))
    rows = conn.execute(sql, {"id_setor": ID_SETOR_CCD, "todos": 0}).mappings().all()
    return [dict(r) for r in rows]


def build_llm(model: str = DEFAULT_LLM_MODEL):
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        base_url=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        model=model,
        temperature=0.0,
    )


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


def _extrair_pessoas(llm, texto_despacho: str) -> list[str]:
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


# Transitos por nome (LIKE) ou por CPF exato do devedor. A variante por CPF
# (gp.Documento = :cpf) evita HOMÔNIMOS — nomes iguais com CPFs diferentes
# misturariam débitos de pessoas distintas (o mesmo processo de origem pode ter
# débitos de dois homônimos). Ancorar no CPF da pessoa relacionada ao processo.
_TRANSITO_NOME = read_sql("processos_transito_nome.sql")
_TRANSITO_CPF = _TRANSITO_NOME.replace(
    "AND lower(gp.Nome) LIKE :nome_pattern", "AND gp.Documento = :cpf"
)

# CPF da pessoa relacionada ao processo (responsável de despesa) cujo nome casa.
_SQL_CPF_RELACIONADO = text("""
    SELECT DISTINCT gp.Documento AS cpf, gp.Nome AS nome
    FROM processo.dbo.Processos p
    INNER JOIN processo.dbo.Pro_ProcessosResponsavelDespesa pprd ON pprd.IdProcesso = p.IdProcesso
    INNER JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = pprd.IdPessoa
    WHERE p.numero_processo = :numero AND p.ano_processo = :ano
      AND lower(gp.Nome) LIKE :nome_pattern
""")


def _cpf_relacionado(conn, nome: str, numero: str, ano: str) -> str:
    """CPF da pessoa relacionada ao processo cujo nome casa com `nome`.
    '' se não houver correspondência única (ex.: nome só aparece no despacho)."""
    rows = conn.execute(
        _SQL_CPF_RELACIONADO,
        {"numero": numero, "ano": ano, "nome_pattern": f"%{nome.lower()}%"},
    ).mappings().all()
    cpfs = {r["cpf"] for r in rows if r["cpf"]}
    return next(iter(cpfs)) if len(cpfs) == 1 else ""


def _transitos(conn, nome: str, cpf: str) -> list[dict[str, Any]]:
    if cpf:
        sql, params = text(_TRANSITO_CPF), {"nome_pattern": f"%{nome.lower()}%", "cpf": cpf}
    else:
        sql, params = text(_TRANSITO_NOME), {"nome_pattern": f"%{nome.lower()}%"}
    rows = conn.execute(sql, params).mappings().all()
    transitos = []
    for r in rows:
        d = dict(r)
        d["valor_original"] = _format_currency(d.get("valor_original"))
        d["valor_atualizado"] = _format_currency(d.get("valor_atualizado"))
        for k, v in d.items():
            if v is None:
                d[k] = ""
        transitos.append(d)
    return transitos


def _valores_pessoa(conn, nome: str, numero: str, ano: str) -> dict[str, Any]:
    # ancora no CPF da pessoa relacionada ao processo (anti-homônimo); se o nome
    # não estiver entre os relacionados, cai para busca por nome (com aviso).
    cpf = _cpf_relacionado(conn, nome, numero, ano)
    if not cpf:
        print(f"    aviso: {nome!r} não está nas pessoas relacionadas ao processo "
              f"{numero}/{ano}; usando busca por nome (risco de homônimo).")
    transitos = _transitos(conn, nome, cpf)
    if not cpf:
        cpfs = {t["cpf"] for t in transitos if t.get("cpf")}
        cpf = next(iter(cpfs)) if len(cpfs) == 1 else ""
    return {"nome": nome, "cpf": cpf or "", "transitos": transitos}


def _responsaveis_str(nomes: list[str]) -> str:
    if not nomes:
        return ""
    if len(nomes) == 1:
        return nomes[0]
    return ", ".join(nomes[:-1]) + " e " + nomes[-1]


def gerar(processos: list[str], out_dir: Path) -> list[Path]:
    with contextlib.suppress(locale.Error):
        locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
    engine = get_connection()
    base_dir = informacoes_dir()

    sql_info = text(read_sql("antecedentes_info_despacho.sql")).bindparams(
        bindparam("processos", expanding=True)
    )
    with engine.connect() as conn:
        info_rows = conn.execute(sql_info, {"processos": processos}).mappings().all()
    if not info_rows:
        raise ValueError("Nenhum despacho encontrado para os processos selecionados.")

    llm = build_llm()
    pdfs: list[Path] = []
    for row in info_rows:
        processo = row["processo"]
        try:
            caminho = base_dir / (row["setor"] or "").strip() / row["arquivo"]
            texto = extract_text_from_pdf(caminho)
            if not texto:
                print(f"  {processo}: PDF-fonte ausente ou sem texto ({caminho})")
                continue
            nomes = _extrair_pessoas(llm, texto)
            with engine.connect() as conn:
                valores = [
                    _valores_pessoa(conn, nome, row["numero_processo"], row["ano_processo"])
                    for nome in nomes
                ]
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
            docx_path = render_template(TEMPLATE, context, out_dir / f"{stem}.docx")
            pdf = docx_to_pdf(str(docx_path), str(out_dir))
            pdfs.append(pdf)
            n_deb = sum(len(v["transitos"]) for v in valores)
            print(f"  {processo}: OK — responsáveis={nomes or '(nenhum)'}, {n_deb} débito(s)")
        except Exception as e:  # segue para o próximo do lote
            print(f"  {processo}: ERRO — {type(e).__name__}: {e}")
    return pdfs


def main() -> int:
    ap = argparse.ArgumentParser(description="Gera os despachos de antecedentes (docx+pdf)")
    ap.add_argument("processos", nargs="*", help="numero/ano; vazio = descobre no CCD")
    ap.add_argument("--saida", default=str(SAIDA_DEFAULT), help=f"pasta de saída (default: {SAIDA_DEFAULT})")
    ap.add_argument("--dry-run", action="store_true", help="só lista os candidatos; não gera")
    args = ap.parse_args()

    engine = get_connection()
    if args.processos:
        processos = args.processos
    else:
        with engine.connect() as conn:
            cands = descobrir_candidatos(conn)
        processos = [c["processo"] for c in cands]
        print(f"{len(processos)} candidato(s) de antecedentes no CCD:")
        for c in cands:
            print(f"  {c['processo']}  | {str(c['assunto'])[:40]} | {str(c['interessado'])[:40]}")

    if args.dry_run:
        print("dry-run: nada gerado.")
        return 0
    if not processos:
        print("nenhum processo para gerar.")
        return 1

    out_dir = Path(args.saida)
    print(f"\nGerando em {out_dir} ...")
    pdfs = gerar(processos, out_dir)
    print(f"\n{len(pdfs)}/{len(processos)} PDF(s) gerado(s) em {out_dir}")
    return 0 if len(pdfs) == len(processos) else 1


if __name__ == "__main__":
    sys.exit(main())
