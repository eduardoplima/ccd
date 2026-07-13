"""Planilha: processos do Nereu em desconto em folha x data da notificação à SEAD.

Para cada um dos 43 processos (aba "Monitoramento NEREU"), localiza o despacho da
DAE "Promover o desconto em folha" (notificação à SEARH/SEAD), confirma o
destinatário lendo o PDF e registra a DATA da notificação.

Saída: docs/checagem_planilhas_desconto_folha/notificacoes_nereu_datas.xlsx
Somente leitura do banco e do share de PDFs.

Rodar (da raiz do repo):
  .venv/Scripts/python.exe scripts/analise/notificacoes_nereu_datas.py
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from sqlalchemy import bindparam, text

from ccd.config import load_env
from ccd.db import get_connection
from ccd.pdf import extract_text_from_pdf
from ccd.processo import get_info_file_path

load_env()

BASE = Path(__file__).resolve().parent / "docs" / "checagem_planilhas_desconto_folha"
PAN = BASE / "estado_nereu_desconto_folha.xlsx"
OUT = BASE / "notificacoes_nereu_datas.xlsx"

_RE_PROMOVER = re.compile(r"promover.*desconto|implant.*desconto|desconto em folha do d.bito"
                          r"|efetiv.*desconto|proceda.*desconto|realiz.*desconto", re.I)
_RE_SEAD = re.compile(r"\bSEAD\b|\bSEARH\b|Secretaria de Estado da Administra", re.I)

# panorama: 43 processos + status + data de implementação
pan = pd.read_excel(PAN, sheet_name="Panorama")
procos = sorted(pan["processo"].unique())

sql = text(
    """
    SELECT CONCAT(RTRIM(inf.numero_processo),'/',RTRIM(inf.ano_processo)) AS processo,
           RTRIM(inf.setor) AS setor, inf.ordem,
           inf.data_ultima_atualizacao AS data,
           CONCAT(RTRIM(inf.setor),'_',inf.numero_processo,'_',inf.ano_processo,
                  '_',RIGHT(CONCAT('0000',inf.ordem),4),'.pdf') AS arquivo
    FROM processo.dbo.vw_ata_informacao inf
    WHERE CONCAT(RTRIM(inf.numero_processo),'/',RTRIM(inf.ano_processo)) IN :procos
      AND LOWER(inf.resumo) LIKE '%promover%desconto%'
    """
).bindparams(bindparam("procos", expanding=True))
with get_connection().connect() as conn:
    info = pd.DataFrame(conn.execute(sql, {"procos": procos}).mappings().all())
info["data"] = pd.to_datetime(info["data"], errors="coerce")

rows = []
for _, p in pan.sort_values("data_implementacao").iterrows():
    proc = p["processo"]
    recebendo = "sim" if "OK" in str(p["STATUS_CONSOLIDADO"]) else "não"
    sub = info[info["processo"] == proc].sort_values(["data", "ordem"])
    if not len(sub):
        rows.append(dict(processo=proc, data_notificacao_sead="", setor="",
                         notifica_sead="não (sem despacho)", recebendo=recebendo,
                         data_implementacao=p["data_implementacao"]))
        continue
    pr = sub.iloc[-1]  # mais recente
    caminho = get_info_file_path({"setor": pr["setor"], "arquivo": pr["arquivo"]})
    raw = extract_text_from_pdf(caminho) if Path(caminho).exists() else ""
    confirma = bool(raw and _RE_SEAD.search(re.sub(r"\s+", " ", raw)))
    rows.append(dict(
        processo=proc,
        data_notificacao_sead=pr["data"].strftime("%d/%m/%Y") if pd.notna(pr["data"]) else "",
        setor=pr["setor"],
        notifica_sead="sim" if confirma else "despacho s/ SEAD confirmado",
        recebendo=recebendo,
        data_implementacao=p["data_implementacao"],
    ))

df = pd.DataFrame(rows)
df.to_excel(OUT, index=False, sheet_name="Notificações Nereu")
print(f"Salvo: {OUT} ({len(df)} processos)\n")
print("notifica_sead:", df["notifica_sead"].value_counts().to_dict())
print("com data de notificação:", int((df["data_notificacao_sead"] != "").sum()))
print("\n" + df[["processo", "data_notificacao_sead", "notifica_sead", "recebendo"]]
      .to_string(index=False))
