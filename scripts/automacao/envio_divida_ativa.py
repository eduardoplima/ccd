"""Gera o despacho de envio à dívida ativa (cobrança judicial) para os processos de
EXECUÇÃO do Nereu no marcador "DESCONTO EM FOLHA - Implementar Nereu".

Template (nereu_divida_ativa.docx) só precisa de processo + relator; o texto é fixo.
Sinaliza processos suspensos judicialmente (não enviar à dívida ativa sem revisão).

Rodar (na rede do TCE):
  .venv/Scripts/python.exe scripts/automacao/envio_divida_ativa.py
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from docxtpl import DocxTemplate
from sqlalchemy import bindparam, text

from ccd.config import load_env
from ccd.db import get_connection
from ccd.pdf import extract_text_from_pdf
from ccd.processo import get_info_file_path

load_env()
CPF = "13006444434"
MARCADOR = "DESCONTO EM FOLHA - Implementar Nereu"
TEMPLATE = Path(__file__).resolve().parent / "templates" / "nereu_divida_ativa.docx"
SAIDA = Path(__file__).resolve().parent / "saidas" / "divida_ativa"
_SUSP = re.compile(r"suspens|mandado de seguran|liminar|sobrestam", re.I)

eng = get_connection("processo")
with eng.connect() as c:
    proc = pd.DataFrame(c.execute(text("""
        WITH pn AS (SELECT DISTINCT e.IdProcessoExecucao idp FROM processo.dbo.Exe_Debito e
          JOIN processo.dbo.Exe_DebitoPessoa edp ON edp.IDDebito=e.IdDebito
          JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa=edp.IDPessoa
          WHERE gp.Documento=:cpf AND e.IdDebitoAnterior IS NULL AND e.IdProcessoExecucao IS NOT NULL)
        SELECT p.IdProcesso, CONCAT(RTRIM(p.numero_processo),'/',RTRIM(p.ano_processo)) processo,
               RTRIM(r.nome) relator
        FROM processo.dbo.Processos p JOIN pn ON pn.idp=p.IdProcesso
        JOIN processo.dbo.Pro_MarcadorProcesso mp ON mp.IdProcesso=p.IdProcesso AND mp.DataExclusao IS NULL
        JOIN processo.dbo.Pro_Marcador m ON m.IdMarcador=mp.IdMarcador AND RTRIM(m.Descricao)=:marc
        LEFT JOIN processo.dbo.Relator r ON r.codigo=p.codigo_relator
        WHERE p.setor_atual='CCD' AND p.IdProcessoApensador IS NULL"""),
        {"cpf": CPF, "marc": MARCADOR}).mappings().all())
    procos = proc["processo"].tolist()
    inf = pd.DataFrame(c.execute(text("""
        SELECT CONCAT(RTRIM(numero_processo),'/',RTRIM(ano_processo)) processo, RTRIM(setor) setor,
               ordem, CONCAT(RTRIM(setor),'_',numero_processo,'_',ano_processo,'_',
                             RIGHT(CONCAT('0000',ordem),4),'.pdf') arquivo
        FROM processo.dbo.vw_ata_informacao
        WHERE CONCAT(RTRIM(numero_processo),'/',RTRIM(ano_processo)) IN :p""")
        .bindparams(bindparam("p", expanding=True)), {"p": procos}).mappings().all())

SAIDA.mkdir(parents=True, exist_ok=True)
print(f"Processos de execução do Nereu no marcador '{MARCADOR}': {len(proc)}\n")
for _, p in proc.sort_values("processo").iterrows():
    # alerta de suspensão judicial (última info do processo)
    s = inf[inf.processo == p.processo].sort_values("ordem")
    susp = ""
    if len(s):
        ult = s.iloc[-1]
        if _SUSP.search(extract_text_from_pdf(get_info_file_path(dict(ult)))[:3000]):
            susp = "  [ALERTA] possivel SUSPENSAO JUDICIAL - revisar antes de enviar"
    doc = DocxTemplate(str(TEMPLATE))
    doc.render({"processo": p.processo, "relator": p.relator or ""})
    out = SAIDA / f"{p.processo.replace('/', '_')}.docx"
    doc.save(str(out))
    print(f"  {p.processo} -> {out.name}{susp}")
print(f"\nGerados em: {SAIDA}")
