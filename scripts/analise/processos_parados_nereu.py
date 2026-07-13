"""Processos de EXECUÇÃO do Nereu parados na CCD: resumo + sugestão de próximos passos.

Para cada processo de execução do Nereu que está na CCD e parado (a última informação
da CCD foi a última ação, ou nem houve informação da CCD), monta o histórico das
informações, lê o texto da última informação da CCD (e da última movimentação) e pede
à LLM um resumo do processo + sugestão de próximos passos, comparando com o que a CCD
já instruiu. Gera docs/processos_parados_nereu.xlsx.

ponytail: get_informacoes_processo leria TODOS os PDFs de cada processo (~4,5k PDFs no
share). Aqui usamos o mesmo extrator (ccd.processo.get_info_file_path + ccd.pdf), mas só
nos PDFs que importam p/ a comparação (última info da CCD + última movimentação). O
histórico vem dos `resumo` das informações (sem ler PDF). Mesmo resultado, ~1/35 do custo.

Rodar (na rede do TCE):
  .venv/Scripts/python.exe scripts/analise/processos_parados_nereu.py
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from sqlalchemy import bindparam, text

from ccd.notebook import setup
from ccd.pdf import extract_text_from_pdf
from ccd.processo import get_info_file_path

CPF = "13006444434"
OUT = Path(__file__).resolve().parent / "docs" / "processos_parados_nereu.xlsx"


class Analise(BaseModel):
    resumo: str = Field(description="Resumo concreto do processo em 2-4 frases (o que é, origem, "
                        "situação atual), com base no histórico das informações.")
    sugestao: str = Field(description="Sugestão objetiva dos próximos passos que a CCD deve adotar "
                          "agora, à luz da última informação da CCD, do marcador e do estado atual.")


def coletar(engine):
    """Parados de execução do Nereu na CCD + infos + marcadores."""
    with engine.connect() as c:
        proc = pd.DataFrame(c.execute(text("""
            WITH pn AS (SELECT DISTINCT e.IdProcessoExecucao idp FROM processo.dbo.Exe_Debito e
              JOIN processo.dbo.Exe_DebitoPessoa edp ON edp.IDDebito=e.IdDebito
              JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa=edp.IDPessoa
              WHERE gp.Documento=:cpf AND e.IdDebitoAnterior IS NULL AND e.IdProcessoExecucao IS NOT NULL)
            SELECT p.IdProcesso, CONCAT(RTRIM(p.numero_processo),'/',RTRIM(p.ano_processo)) processo,
                   RTRIM(p.assunto) assunto, RTRIM(r.nome) relator
            FROM processo.dbo.Processos p JOIN pn ON pn.idp=p.IdProcesso
            LEFT JOIN processo.dbo.Relator r ON r.codigo=p.codigo_relator
            WHERE p.setor_atual='CCD' AND p.IdProcessoApensador IS NULL"""), {"cpf": CPF}).mappings().all())
        procos = proc["processo"].tolist()
        inf = pd.DataFrame(c.execute(text("""
            SELECT CONCAT(RTRIM(numero_processo),'/',RTRIM(ano_processo)) processo, RTRIM(setor) setor,
                   ordem, LTRIM(RTRIM(resumo)) resumo, data_ultima_atualizacao dt,
                   CONCAT(RTRIM(setor),'_',numero_processo,'_',ano_processo,'_',RIGHT(CONCAT('0000',ordem),4),'.pdf') arquivo
            FROM processo.dbo.vw_ata_informacao
            WHERE CONCAT(RTRIM(numero_processo),'/',RTRIM(ano_processo)) IN :p""")
            .bindparams(bindparam("p", expanding=True)), {"p": procos}).mappings().all())
        marc = pd.DataFrame(c.execute(text("""
            SELECT mp.IdProcesso, RTRIM(m.Descricao) marcador FROM processo.dbo.Pro_MarcadorProcesso mp
            JOIN processo.dbo.Pro_Marcador m ON m.IdMarcador=mp.IdMarcador
            WHERE mp.DataExclusao IS NULL AND mp.IdProcesso IN :ids""")
            .bindparams(bindparam("ids", expanding=True)), {"ids": proc["IdProcesso"].tolist()}).mappings().all())
    return proc, inf, marc


def main() -> None:
    ctx = setup()
    proc, inf, marc = coletar(ctx.engine)
    inf["dt"] = pd.to_datetime(inf["dt"], errors="coerce")
    marc_by = marc.groupby("IdProcesso")["marcador"].apply(lambda s: "; ".join(sorted(set(s)))).to_dict()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é o Coordenador de Controle de Decisões (CCD) do TCE-RN. Analise um processo "
         "de execução parado na CCD e responda em pt-BR, de forma concreta e prática. Compare o estado "
         "atual com o que a última informação da CCD já instruiu; não invente fatos."),
        ("human", "Processo {processo} | Assunto: {assunto} | Relator: {relator}\nMarcador: {marcador}\n\n"
         "HISTÓRICO (informações, mais recentes ao fim):\n{timeline}\n\n"
         "ÚLTIMA INFORMAÇÃO DA CCD (texto):\n{texto_ccd}\n\nÚLTIMA MOVIMENTAÇÃO (texto):\n{texto_ult}"),
    ])
    chain = prompt | ctx.llm.with_structured_output(schema=Analise)

    rows = []
    parados = []
    for _, p in proc.iterrows():
        s = inf[inf.processo == p.processo].sort_values("ordem")
        ccd = s[s.setor == "CCD"]
        mc = ccd.ordem.max() if len(ccd) else None
        if mc is not None and s.ordem.max() > mc:
            continue  # houve info após a CCD -> não está parado
        parados.append((p, s, ccd))

    print(f"Parados (execução, CCD): {len(parados)}")
    for i, (p, s, ccd) in enumerate(parados, 1):
        try:
            def ler(row):
                return extract_text_from_pdf(get_info_file_path(
                    {"setor": row["setor"], "arquivo": row["arquivo"]}))[:5000]
            texto_ccd = ler(ccd.loc[ccd.ordem.idxmax()]) if len(ccd) else "(sem informação da CCD)"
            ult = s.loc[s.ordem.idxmax()]
            texto_ult = ler(ult) if (not len(ccd) or ult.ordem != ccd.ordem.max()) else "(= última info da CCD)"
            timeline = "\n".join(
                f"  [{r.setor} ord {r.ordem} {r.dt:%d/%m/%Y}] {str(r.resumo)[:90]}"
                for r in s.itertuples() if pd.notna(r.ordem))
            a: Analise = chain.invoke({
                "processo": p.processo, "assunto": p.assunto or "", "relator": p.relator or "",
                "marcador": marc_by.get(p.IdProcesso, "(sem marcador)"),
                "timeline": timeline or "(sem informações)", "texto_ccd": texto_ccd, "texto_ult": texto_ult})
            rows.append({"processo": p.processo, "marcador": marc_by.get(p.IdProcesso, "(sem marcador)"),
                         "resumo": a.resumo, "sugestao": a.sugestao})
            print(f"  [{i}/{len(parados)}] {p.processo} ok")
        except Exception as e:
            rows.append({"processo": p.processo, "marcador": marc_by.get(p.IdProcesso, ""),
                         "resumo": f"[erro: {type(e).__name__} {str(e)[:80]}]", "sugestao": ""})
            print(f"  [{i}/{len(parados)}] {p.processo} ERRO: {type(e).__name__}")

    df = pd.DataFrame(rows)[["processo", "marcador", "resumo", "sugestao"]]
    _ctrl = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")  # openpyxl recusa chars de controle
    df = df.map(lambda v: _ctrl.sub("", v) if isinstance(v, str) else v)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(OUT, index=False, sheet_name="Parados Nereu")
    print(f"\nSalvo: {OUT} ({len(df)} processos)")


if __name__ == "__main__":
    main()
