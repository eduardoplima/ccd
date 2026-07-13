"""Panorama dos processos do Nereu que foram para desconto em folha (2025+2026).

Para cada processo da aba "Monitoramento NEREU" (DATA IMPLEMENTAÇÃO em 2025/2026),
cruza:
  - aba NEREU: valor implementado (parcela), verificação na folha (SIAIDP) e no FRAP;
  - banco `processo`: situação dos débitos do Nereu naquele processo de execução
    (em aberto / suspenso / pago parcial / cancelado), valor atualizado, setor atual;
  - FRAP (docs/debitos_conciliados_nereu.xlsx): total conciliado / data de pagamento.

Gera docs/checagem_planilhas_desconto_folha/estado_nereu_desconto_folha.xlsx
(abas "Panorama" e "Resumo"). Somente leitura do banco.

Rodar (da raiz do repo):
  .venv/Scripts/python.exe scripts/analise/estado_nereu_desconto_folha.py
"""

from __future__ import annotations

import locale
from collections import Counter
from pathlib import Path

import pandas as pd
from sqlalchemy import bindparam, text

from ccd.config import load_env
from ccd.db import get_connection

load_env()

CPF_NEREU = "13006444434"
BASE = Path(__file__).resolve().parent / "docs" / "checagem_planilhas_desconto_folha"
MON = BASE / "Monitoramento Desconto em Folha.xlsx"
FRAP = Path(__file__).resolve().parent / "docs" / "debitos_conciliados_nereu.xlsx"
OUT = BASE / "estado_nereu_desconto_folha.xlsx"

for name in ("pt_BR.UTF-8", "pt_BR.utf8", "Portuguese_Brazil.1252", "pt_BR"):
    try:
        locale.setlocale(locale.LC_ALL, name)
        break
    except locale.Error:
        continue


def _brl(v: float) -> str:
    try:
        return locale.currency(float(v), grouping=True)
    except (locale.Error, TypeError, ValueError):
        return f"R$ {float(v):,.2f}"


# --- 1) aba NEREU: processos implementados em desconto em folha ----------------
ner = pd.read_excel(MON, sheet_name="Monitoramento NEREU")
ner.columns = [
    "num", "ano", "valor_implem", "data_implem", "col1",
    "sei", "relator", "obs", "verif_siaidp", "verif_frap",
]
ner = ner.dropna(subset=["num", "ano"]).copy()
ner["processo"] = (
    ner["num"].astype(int).astype(str).str.zfill(6) + "/" + ner["ano"].astype(int).astype(str)
)
ner["data_implem"] = pd.to_datetime(ner["data_implem"], errors="coerce")
ner["ano_impl"] = ner["data_implem"].dt.year
procos = sorted(ner["processo"].unique())
print(f"Processos NEREU (desconto em folha): {len(procos)}")

# --- 2) banco: débitos do Nereu por processo de execução ----------------------
sql = text(
    """
    SELECT
        (SELECT CONCAT(RTRIM(p.numero_processo),'/',RTRIM(p.ano_processo))
            FROM processo.dbo.Processos p WHERE p.IdProcesso = e.IdProcessoExecucao) AS processo,
        (SELECT RTRIM(p.setor_atual)
            FROM processo.dbo.Processos p WHERE p.IdProcesso = e.IdProcessoExecucao) AS setor_atual,
        esd.DescricaoStatusDivida AS situacao,
        processo.dbo.fn_Exe_RetornaValorAtualizado(e.IdDebito) AS valor_atual
    FROM processo.dbo.Exe_Debito e
    JOIN processo.dbo.Exe_DebitoPessoa edp ON edp.IDDebito = e.IdDebito
    JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = edp.IDPessoa
    LEFT JOIN processo.dbo.Exe_StatusDivida esd ON esd.CodigoStatusDivida = e.CodigoStatusDivida
    WHERE gp.Documento = :cpf AND e.IdDebitoAnterior IS NULL
      AND e.IdProcessoExecucao IN (
          SELECT p2.IdProcesso FROM processo.dbo.Processos p2
          WHERE CONCAT(RTRIM(p2.numero_processo),'/',RTRIM(p2.ano_processo)) IN :procos
      )
    """
).bindparams(bindparam("procos", expanding=True))

with get_connection().connect() as conn:
    deb = pd.DataFrame(conn.execute(sql, {"cpf": CPF_NEREU, "procos": procos}).mappings().all())

# agrega por processo
banco_rows = {}
for proc, g in deb.groupby("processo"):
    cnt = Counter(g["situacao"].fillna("(sem situação)"))
    breakdown = "; ".join(f"{k}: {v}" for k, v in cnt.most_common())
    banco_rows[proc] = dict(
        situacao_debito=breakdown,
        valor_atualizado=float(g["valor_atual"].sum()),
        n_debitos=int(len(g)),
        setor_atual=g["setor_atual"].dropna().iloc[0] if g["setor_atual"].notna().any() else "",
    )

# --- 3) FRAP conciliado (total / última data) ---------------------------------
frap = pd.read_excel(FRAP)
frap_total = float(frap["valor_ordem_bancaria"].drop_duplicates().sum()) if len(frap) else 0.0
frap_parcelas = float(frap["valor_parcela"].sum()) if len(frap) else 0.0
print(f"FRAP conciliado: {len(frap)} parcelas | soma parcelas {_brl(frap_parcelas)}")


# --- 4) status consolidado ----------------------------------------------------
def _ok(v) -> bool:
    return isinstance(v, str) and v.strip().upper().startswith("OK")


def status_consolidado(row) -> str:
    sit = (row["situacao_debito"] or "").lower()
    so_cancelada = "cancel" in sit and "aberto" not in sit and "suspenso" not in sit \
        and "pago" not in sit
    folha = _ok(row["verif_siaidp"])
    frp = _ok(row["verif_frap"])
    if not row["situacao_debito"]:
        return "Sem débito do Nereu no banco (verificar vínculo)"
    if so_cancelada:
        return "Débito cancelado no banco"
    if folha and frp:
        return "Descontando + recebendo (OK)"
    if folha and not frp:
        return "Descontando na folha; FRAP não verificado"
    if "suspenso" in sit:
        return "Implementado; débito suspenso no banco"
    return "Implementado; sem verificação folha/FRAP"


# --- 5) panorama (1 linha por processo) ---------------------------------------
out = []
for _, r in ner.sort_values("data_implem").iterrows():
    b = banco_rows.get(r["processo"], {})
    row = dict(
        processo=r["processo"],
        ano_processo=int(r["ano"]),
        data_implementacao=r["data_implem"].strftime("%d/%m/%Y") if pd.notna(r["data_implem"]) else "",
        ano_implementacao=int(r["ano_impl"]) if pd.notna(r["ano_impl"]) else None,
        valor_implementado=round(float(r["valor_implem"]), 2) if pd.notna(r["valor_implem"]) else None,
        verif_siaidp=("" if pd.isna(r["verif_siaidp"]) else str(r["verif_siaidp"])),
        verif_frap=("" if pd.isna(r["verif_frap"]) else str(r["verif_frap"])),
        relator=("" if pd.isna(r["relator"]) else str(r["relator"])),
        processo_sei=("" if pd.isna(r["sei"]) else str(r["sei"])),
        situacao_debito=b.get("situacao_debito", ""),
        valor_atualizado=round(b.get("valor_atualizado", 0.0), 2),
        n_debitos=b.get("n_debitos", 0),
        setor_atual=b.get("setor_atual", ""),
    )
    row["STATUS_CONSOLIDADO"] = status_consolidado(row)
    out.append(row)

pan = pd.DataFrame(out)

# --- 6) resumo ----------------------------------------------------------------
resumo_status = (
    pan.groupby("STATUS_CONSOLIDADO")
    .agg(qtd=("processo", "size"), valor_implementado=("valor_implementado", "sum"))
    .reset_index()
    .sort_values("qtd", ascending=False)
)
resumo_ano = (
    pan.groupby("ano_implementacao")
    .agg(qtd=("processo", "size"), valor_implementado=("valor_implementado", "sum"))
    .reset_index()
)

with pd.ExcelWriter(OUT, engine="openpyxl") as w:
    pan.to_excel(w, sheet_name="Panorama", index=False)
    resumo_status.to_excel(w, sheet_name="Resumo", index=False, startrow=1)
    resumo_ano.to_excel(w, sheet_name="Resumo", index=False, startrow=len(resumo_status) + 5)

print(f"\nSalvo: {OUT}  ({len(pan)} processos)\n")
print("== STATUS_CONSOLIDADO ==")
for _, x in resumo_status.iterrows():
    print(f"  {x['STATUS_CONSOLIDADO']:48} {x['qtd']:>3}  | parcela total {_brl(x['valor_implementado'])}")
print("\n== por ano de implementação ==")
for _, x in resumo_ano.iterrows():
    print(f"  {int(x['ano_implementacao'])}: {x['qtd']} processos | parcela total {_brl(x['valor_implementado'])}")
print(f"\nValor atualizado (banco) dos débitos nesses processos: {_brl(pan['valor_atualizado'].sum())}")
