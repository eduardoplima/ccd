"""Notificação da DE/DAE → SEAD para implantar desconto em folha.

Para os processos do Nereu que NÃO estão recebendo (todos exceto os 10
"Descontando + recebendo (OK)" do panorama), verifica se existe a notificação
à SEAD para implantar o desconto em folha — lendo o PDF da informação
"Promover o desconto em folha…" e confirmando o destinatário SEAD — e se há
informação de "Impossibilidade…/ADI" (motivo de bloqueio).

Acrescenta a aba "Notificação SEAD" em
docs/checagem_planilhas_desconto_folha/estado_nereu_desconto_folha.xlsx.
Somente leitura do banco e do share de PDFs.

Rodar (da raiz do repo):
  .venv/Scripts/python.exe scripts/analise/notificacao_sead_nereu.py
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
XLSX = BASE / "estado_nereu_desconto_folha.xlsx"

_RE_PROMOVER = re.compile(r"promover.*desconto|implant.*desconto|desconto em folha do d.bito"
                          r"|efetiv.*desconto|proceda.*desconto|realiz.*desconto", re.I)
_RE_IMPOSS = re.compile(r"impossibilidade.*(?:desconto|folha)", re.I)
# "DE"/DAE notifica a SEARH/SEAD (Secretaria de Estado da Administração e Recursos
# Humanos) p/ implantar o desconto. Texto do PDF tem espaços/quebras irregulares,
# por isso normalizamos o whitespace antes de casar.
_RE_SEAD = re.compile(r"\bSEAD\b|\bSEARH\b|Secretaria de Estado da Administra", re.I)
_RE_NOTIFIQUE = re.compile(r"notifique-se a Secretaria de Estado da Administra[^.]{0,80}", re.I)
_RE_ADI = re.compile(r"\bADI\b|0808846-43\.2020", re.I)
_RE_OFICIO = re.compile(r"of[ií]cio[^\n]{0,40}", re.I)


def _grupo(status: str) -> str:
    if "suspenso" in status.lower():
        return "suspenso"
    return "em aberto"


# --- processos não-recebendo (do panorama) -----------------------------------
pan = pd.read_excel(XLSX, sheet_name="Panorama")
nao = pan[~pan["STATUS_CONSOLIDADO"].str.contains("OK")].copy()
nao["grupo"] = nao["STATUS_CONSOLIDADO"].map(_grupo)
procos = sorted(nao["processo"].unique())
print(f"Processos não-recebendo: {len(procos)}")

# --- informações de folha (promover + impossibilidade) -----------------------
sql = text(
    """
    SELECT CONCAT(RTRIM(inf.numero_processo),'/',RTRIM(inf.ano_processo)) AS processo,
           RTRIM(inf.setor) AS setor, inf.ordem, inf.resumo,
           inf.data_ultima_atualizacao AS data,
           CONCAT(RTRIM(inf.setor),'_',inf.numero_processo,'_',inf.ano_processo,
                  '_',RIGHT(CONCAT('0000',inf.ordem),4),'.pdf') AS arquivo
    FROM processo.dbo.vw_ata_informacao inf
    WHERE CONCAT(RTRIM(inf.numero_processo),'/',RTRIM(inf.ano_processo)) IN :procos
      AND (LOWER(inf.resumo) LIKE '%desconto%' OR LOWER(inf.resumo) LIKE '%folha%'
           OR LOWER(inf.resumo) LIKE '%impossibilidade%')
    """
).bindparams(bindparam("procos", expanding=True))
with get_connection().connect() as conn:
    info = pd.DataFrame(conn.execute(sql, {"procos": procos}).mappings().all())
info["resumo"] = info["resumo"].fillna("")
info["data"] = pd.to_datetime(info["data"], errors="coerce")
info["is_promover"] = info["resumo"].str.contains(_RE_PROMOVER)
info["is_imposs"] = info["resumo"].str.contains(_RE_IMPOSS)
print(f"Informações de folha encontradas: {len(info)}")

rows = []
for proc in procos:
    g = nao[nao["processo"] == proc].iloc[0]
    sub = info[info["processo"] == proc]
    prom = sub[sub["is_promover"]].sort_values(["data", "ordem"]).tail(1)
    imp = sub[sub["is_imposs"]].sort_values(["data", "ordem"]).tail(1)

    rec = {
        "processo": proc, "grupo": g["grupo"],
        "tem_notificacao_sead": "não", "setor": "", "ordem": pd.NA,
        "data_notificacao": "", "evidencia_sead": "", "oficio": "",
        "tem_impossibilidade": "sim" if len(imp) else "não",
        "adi_ref": "", "data_impossibilidade": "",
    }

    if len(imp):
        ir = imp.iloc[0]
        rec["data_impossibilidade"] = ir["data"].strftime("%d/%m/%Y") if pd.notna(ir["data"]) else ""
        m = _RE_ADI.search(str(ir["resumo"]))
        rec["adi_ref"] = "0808846-43.2020" if (m or "0808846" in str(ir["resumo"])) else (
            "ADI" if m else "")

    if len(prom):
        pr = prom.iloc[0]
        rec["setor"] = pr["setor"]
        rec["ordem"] = int(pr["ordem"]) if pd.notna(pr["ordem"]) else pd.NA
        rec["data_notificacao"] = pr["data"].strftime("%d/%m/%Y") if pd.notna(pr["data"]) else ""
        # lê o PDF da "promover" e confirma destinatário SEAD
        caminho = get_info_file_path({"setor": pr["setor"], "arquivo": pr["arquivo"]})
        raw = extract_text_from_pdf(caminho) if Path(caminho).exists() else ""
        texto = re.sub(r"\s+", " ", raw)  # normaliza espaços/quebras antes de casar
        if texto and _RE_SEAD.search(texto):
            rec["tem_notificacao_sead"] = "sim"
            mn = _RE_NOTIFIQUE.search(texto)
            if mn:
                rec["evidencia_sead"] = mn.group(0).strip()
            else:
                m = _RE_SEAD.search(texto)
                rec["evidencia_sead"] = texto[max(0, m.start() - 30):m.end() + 50].strip()
            of = _RE_OFICIO.search(texto)
            rec["oficio"] = of.group(0).strip() if of else ""
        elif texto:
            rec["tem_notificacao_sead"] = "promover s/ SEAD no PDF"
        else:
            rec["tem_notificacao_sead"] = "promover (PDF ausente)"

    # conclusão
    if rec["tem_notificacao_sead"] == "não" and rec["tem_impossibilidade"] == "não":
        rec["CONCLUSAO"] = "Sem notificação à SEAD"
    elif rec["tem_notificacao_sead"].startswith(("sim", "promover")):
        if rec["tem_impossibilidade"] == "sim":
            rec["CONCLUSAO"] = "Notificada à SEAD; consta impossibilidade/ADI"
        else:
            rec["CONCLUSAO"] = "Notificada à SEAD; sem confirmação de desconto"
    else:
        rec["CONCLUSAO"] = "Sem notificação à SEAD (só impossibilidade)"
    rows.append(rec)

res = pd.DataFrame(rows)[[
    "processo", "grupo", "tem_notificacao_sead", "setor", "ordem", "data_notificacao",
    "oficio", "evidencia_sead", "tem_impossibilidade", "adi_ref", "data_impossibilidade",
    "CONCLUSAO",
]]

with pd.ExcelWriter(XLSX, engine="openpyxl", mode="a", if_sheet_exists="replace") as w:
    res.to_excel(w, sheet_name="Notificação SEAD", index=False)

print(f"\nAba 'Notificação SEAD' gravada em {XLSX} ({len(res)} processos)\n")
print("== tem_notificacao_sead ==")
print(res["tem_notificacao_sead"].value_counts().to_string())
print("\n== CONCLUSAO ==")
print(res["CONCLUSAO"].value_counts().to_string())
print(f"\ncom impossibilidade/ADI: {(res['tem_impossibilidade']=='sim').sum()} | "
      f"citam ADI: {(res['adi_ref']!='').sum()}")
print("\n== processos SEM notificação à SEAD ==")
semn = res[res["tem_notificacao_sead"].isin(["não"]) | res["CONCLUSAO"].str.startswith("Sem")]
print(semn[["processo", "grupo", "tem_impossibilidade", "CONCLUSAO"]].to_string(index=False))
