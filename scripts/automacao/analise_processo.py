"""Redige a INFORMAÇÃO INSTRUTIVA (CCD) de um processo, no estilo dos exemplos.

Cabeçalho (assunto + relator) vem da tabela Processos (connection `processo`).
Para o §1 ("Trata-se de…") ser CONCRETO, busca a quota ministerial mais recente
(ou, na falta, um voto) nas informações do processo e resume seu início.
Os demais fatos (ação realizada) vêm de --contexto. Renderiza modelo_informacao.docx.

Rodar:
  .venv/Scripts/python.exe scripts/automacao/analise_processo.py \
      --processo 223/2026 --contexto "última informação da CONJU à DIP para parar a execução; ..."
"""

from __future__ import annotations

import argparse
from pathlib import Path

from docxtpl import DocxTemplate
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from sqlalchemy import text

from ccd.notebook import setup
from ccd.pdf import extract_text_from_pdf
from ccd.processo import get_info_file_path

AUTOMACAO = Path(__file__).resolve().parent
TEMPLATES = AUTOMACAO / "templates"
EXEMPLOS = TEMPLATES / "exemplos_informacoes"


class Informacao(BaseModel):
    paragrafos: list[str] = Field(
        description="Parágrafos da informação instrutiva, SEM numeração (o modelo numera). "
        "O primeiro começa com 'Trata-se de' e resume o caso concreto; os do meio explicam "
        "a ação realizada; o último é o encerramento (ex.: 'Ante o exposto, remetem-se os autos...')."
    )


def header(engine, numero: str, ano: str) -> dict:
    sql = text(
        """
        SELECT RTRIM(p.assunto) AS assunto, RTRIM(r.nome) AS relator
        FROM processo.dbo.Processos p
        LEFT JOIN processo.dbo.Relator r ON r.codigo = p.codigo_relator
        WHERE p.numero_processo = :n AND p.ano_processo = :a
        """
    )
    with engine.connect() as c:
        row = c.execute(sql, {"n": numero, "a": ano}).mappings().first()
    return dict(row) if row else {"assunto": "", "relator": ""}


def fonte_resumo(engine, numero: str, ano: str) -> tuple[str, str]:
    """Texto-base p/ o §1: quota ministerial mais recente; senão, voto. ('' se nada)."""
    sql = text(
        """
        SELECT RTRIM(setor) AS setor, ordem, LOWER(resumo) AS resumo,
               CONCAT(RTRIM(setor),'_',numero_processo,'_',ano_processo,
                      '_',RIGHT(CONCAT('0000',ordem),4),'.pdf') AS arquivo
        FROM processo.dbo.vw_ata_informacao
        WHERE numero_processo = :n AND ano_processo = :a
        ORDER BY ordem DESC
        """
    )
    with engine.connect() as c:
        rows = [dict(r) for r in c.execute(sql, {"n": numero, "a": ano}).mappings().all()]

    def primeiro(match) -> dict | None:
        return next((r for r in rows if match((r["resumo"] or ""))), None)

    alvo = primeiro(lambda s: "quota" in s or "cota minist" in s)
    tipo = "quota ministerial"
    if alvo is None:
        alvo = primeiro(lambda s: "voto" in s)
        tipo = "voto"
    if alvo is None:
        return "", ""
    texto = extract_text_from_pdf(get_info_file_path(alvo))
    return (tipo, texto.strip()[:6000]) if texto.strip() else ("", "")


def exemplos() -> str:
    blocos = [f"--- EXEMPLO ({p.stem}) ---\n{extract_text_from_pdf(p).strip()}"
              for p in sorted(EXEMPLOS.glob("*.pdf")) if extract_text_from_pdf(p).strip()]
    return "\n\n".join(blocos)


def redigir(llm, hdr: dict, processo: str, contexto: str, fonte: tuple[str, str]) -> list[str]:
    tipo_fonte, texto_fonte = fonte
    base_msg = (
        f"BASE PARA O §1 — início da {tipo_fonte} mais recente (resuma de forma CONCRETA: "
        f"partes/responsável, acórdão de origem, natureza do débito/irregularidade, valores):\n{texto_fonte}"
        if texto_fonte else
        "BASE PARA O §1: (não foi possível obter quota/voto — escreva o §1 a partir do CONTEXTO, "
        "mas seja específico ao caso e evite frases genéricas.)"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Você é o Coordenador de Controle de Decisões (CCD) do Tribunal de Contas do RN e redige "
         "a INFORMAÇÃO INSTRUTIVA de um processo de execução, em pt-BR formal, imitando o estilo dos "
         "exemplos. O §1 começa com 'Trata-se de' e deve ser CONCRETO sobre o caso (evite frases vagas "
         "como 'cumprimento de decisão emanada deste Tribunal'); os §§ do meio explicam a ação realizada; "
         "o último § é o encerramento. Não invente fatos além da BASE e do CONTEXTO. Não numere os parágrafos."),
        ("human",
         "EXEMPLOS (estilo a imitar):\n\n{exemplos}\n\n===="
         "\nPROCESSO: {processo}\nAssunto: {assunto}\nRelator: {relator}\n\n{base}\n\n"
         "AÇÃO REALIZADA / CONTEXTO (verdade para os §§ do meio e encerramento):\n{contexto}\n\n"
         "Redija a INFORMAÇÃO INSTRUTIVA."),
    ])
    out: Informacao = (prompt | llm.with_structured_output(schema=Informacao)).invoke({
        "exemplos": exemplos(), "processo": processo, "contexto": contexto, "base": base_msg,
        "assunto": hdr["assunto"], "relator": hdr["relator"],
    })
    return [p.strip() for p in out.paragrafos if p.strip()]


def main() -> None:
    ap = argparse.ArgumentParser(prog="analise_processo")
    ap.add_argument("--processo", required=True, help="numero/ano, ex.: 223/2026")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--contexto", help="ação realizada / fatos (texto livre)")
    g.add_argument("--contexto-file", help="arquivo com os fatos")
    ap.add_argument("--saida", help="caminho do .docx de saída")
    ap.add_argument("--modelo", default=str(TEMPLATES / "modelo_informacao.docx"))
    args = ap.parse_args()

    numero, ano = args.processo.split("/")
    numero, ano = numero.strip().zfill(6), ano.strip()
    contexto = (Path(args.contexto_file).read_text(encoding="utf-8")
                if args.contexto_file else args.contexto)

    ctx = setup()  # engine (processo) + Azure LLM
    try:
        hdr = header(ctx.engine, numero, ano)
        fonte = fonte_resumo(ctx.engine, numero, ano)
    except Exception as e:  # ponytail: banco/rede do TCE indisponível — mensagem clara, sem stack trace
        raise SystemExit(
            f"[erro] banco `processo` (SQL Server) inacessível — rode dentro da rede/VPN do TCE.\n"
            f"  detalhe: {type(e).__name__}: {str(e)[:120]}"
        ) from None
    if not fonte[1]:
        print("[aviso] quota/voto não encontrados — §1 sairá só do contexto (menos específico).")
    paragrafos = redigir(ctx.llm, hdr, f"{numero}/{ano}", contexto, fonte)

    # check (ponytail)
    assert len(paragrafos) >= 3, f"poucos parágrafos: {len(paragrafos)}"
    assert paragrafos[0].lower().startswith("trata-se"), "§1 não começa com 'Trata-se'"
    assert "ante o exposto" in paragrafos[-1].lower(), "último § não é encerramento"

    doc = DocxTemplate(args.modelo)
    doc.render({
        "processo": f"{numero}/{ano}", "assunto": hdr["assunto"], "relator": hdr["relator"],
        "parágrafos": paragrafos,  # sem numerar: o modelo numera
    })
    saida = Path(args.saida) if args.saida else (
        AUTOMACAO / "saidas" / "analise_processo" / f"{numero}_{ano}.docx")
    saida.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(saida))
    print(f"Gerado: {saida} (fonte §1: {fonte[0] or 'nenhuma'})\n\n" + "\n\n".join(paragrafos))


if __name__ == "__main__":
    main()
