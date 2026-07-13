"""Carga única dos extratos .pdf antigos da conta FRAP 700000-6 no BdDIP.

Os anos 2017–2019 e mar–dez/2020 só existem em PDF (o pipeline normal lê .txt).
Este script:
  1. parseia os PDFs (`frap.extratos.ingest.ingest_pdf_conta`),
  2. acrescenta abril/2020 — cujo PDF tem fonte ilegível (mojibake), transcrito
     visualmente a partir do render (validado: créditos == débitos, saldo 0→0),
  3. publica só os períodos AINDA ausentes (`publica_extrato`, gap-fill),
em FRAPExtratoArquivo + FRAPLancamento.

Conexão via `ccd.db` (pymssql) — evita a dependência pyodbc do frap neste host.
Uso:
  python -m scripts.automacao.carga_extratos_pdf_700000_6 --dry-run
  python -m scripts.automacao.carga_extratos_pdf_700000_6 --ano 2017
  python -m scripts.automacao.carga_extratos_pdf_700000_6            # tudo que falta
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

# frap não é instalado na venv do ccd; importa via path do pacote.
_FRAP = Path(__file__).resolve().parents[2] / "web" / "tools" / "frap"
sys.path.insert(0, str(_FRAP))

from frap.extratos import ingest  # noqa: E402
from frap.persistencia.extrato import publica_extrato  # noqa: E402

from ccd.db import get_connection  # noqa: E402

PASTA = Path(__file__).resolve().parents[1] / "docs" / "extratos_700000_6"
CONTA = "700000-6"

# --- abril/2020: transcrição visual do PDF ilegível (render via PyMuPDF) ---
# (data, ag, lote, historico, documento, valor, dc, descricao)
_ABRIL_2020 = [
    ("31/03/2020", "0000", "00000", "Saldo Anterior", "", "0,00", "C", ""),
    ("06/04/2020", "2731", "99015", "Transferência recebida", "552.731.000.025.455", "141,80", "C", "06/04 2731 25455-X SERVICO AUTONO"),
    ("06/04/2020", "0000", "00000", "BB CP Automatico S P", "70", "141,80", "D", ""),
    ("08/04/2020", "0984", "99015", "Transferência recebida", "550.984.000.033.202", "458,96", "C", "08/04 0984 33202-X RN 241110 FMS"),
    ("08/04/2020", "0000", "00000", "BB CP Automatico S P", "70", "458,96", "D", ""),
    ("14/04/2020", "0000", "14138", "Ordem Bancária", "202.004.130.002.672", "121,81", "C", "082417390001-05 ESTADO DO RIO GRANDE D"),
    ("14/04/2020", "0000", "00000", "BB CP Automatico S P", "70", "121,81", "D", ""),
    ("16/04/2020", "0727", "99015", "Transferência recebida", "550.727.000.027.693", "100,00", "C", "16/04 0727 27693-6 FUNDO MUNICIPA"),
    ("16/04/2020", "0727", "99015", "Transferência recebida", "550.727.000.027.693", "100,00", "C", "16/04 0727 27693-6 FUNDO MUNICIPA"),
    ("16/04/2020", "0727", "99015", "Transferência recebida", "550.727.000.027.693", "104,50", "C", "16/04 0727 27693-6 FUNDO MUNICIPA"),
    ("16/04/2020", "0727", "99015", "Transferência recebida", "550.727.000.027.693", "100,00", "C", "16/04 0727 27693-6 FUNDO MUNICIPA"),
    ("16/04/2020", "0727", "99015", "Transferência recebida", "550.727.000.027.693", "104,50", "C", "16/04 0727 27693-6 FUNDO MUNICIPA"),
    ("16/04/2020", "0727", "99015", "Transferência recebida", "550.727.000.027.693", "103,90", "C", "16/04 0727 27693-6 FUNDO MUNICIPA"),
    ("16/04/2020", "0000", "00000", "BB CP Automatico S P", "70", "612,90", "D", ""),
    ("17/04/2020", "0477", "99015", "Transferência recebida", "550.477.000.005.643", "186,23", "C", "17/04 0477 5643-X CAMARA MUNICIP"),
    ("17/04/2020", "0000", "00000", "BB CP Automatico S P", "70", "186,23", "D", ""),
    ("20/04/2020", "1021", "99015", "Transferência recebida", "551.021.000.005.013", "248,80", "C", "20/04 1021 5013-X CAMARA MUN DE"),
    ("20/04/2020", "1140", "99015", "Transferência recebida", "551.140.000.031.423", "184,53", "C", "20/04 1140 31423-4 CAMARA MUNICIP"),
    ("20/04/2020", "0000", "00000", "BB CP Automatico S P", "70", "433,33", "D", ""),
    ("23/04/2020", "1066", "99015", "Transferência recebida", "551.066.000.001.313", "1.020,00", "C", "23/04 1066 1313-7 CAMARA MUNIC E"),
    ("23/04/2020", "2703", "99015", "Transferência recebida", "552.703.000.013.409", "527,38", "C", "23/04 2703 13409-0 CAMARA MUNICIP"),
    ("23/04/2020", "0000", "14175", "TED-Crédito em Conta", "1.656.300", "870,00", "C", "104 0763 12993580000144 AGUA NOVA CAMA"),
    ("23/04/2020", "0000", "00000", "BB CP Automatico S P", "70", "2.417,38", "D", ""),
    ("27/04/2020", "0000", "14138", "Ordem Bancária", "202.004.240.001.218", "340,70", "C", "084933710001-64 RIO G DO NORTE ASSEMBL"),
    ("27/04/2020", "0000", "14138", "Ordem Bancária", "202.004.240.001.219", "1.006,59", "C", "084933710001-64 RIO G DO NORTE ASSEMBL"),
    ("27/04/2020", "0000", "00000", "BB CP Automatico S P", "70", "1.347,29", "D", ""),
    ("28/04/2020", "0000", "14138", "Ordem Bancária", "202.004.270.001.953", "100,00", "C", "129780370001-78 NATAL TRIBUNAL DE CONT"),
    ("28/04/2020", "0000", "14138", "Ordem Bancária", "202.004.270.001.954", "4,88", "C", "129780370001-78 NATAL TRIBUNAL DE CONT"),
    ("28/04/2020", "0000", "00000", "BB CP Automatico S P", "70", "104,88", "D", ""),
    ("29/04/2020", "2703", "99015", "Transferência recebida", "552.703.000.015.325", "255,35", "C", "29/04 2703 15325-7 P M PASSA E FI"),
    ("29/04/2020", "0000", "00000", "BB CP Automatico S P", "70", "255,35", "D", ""),
    ("30/04/2020", "0879", "99015", "Transferência recebida", "550.879.000.012.026", "287,12", "C", "30/04 0879 12026-X PREF MUN DE LU"),
    ("30/04/2020", "5871", "99015", "Transferência recebida", "555.871.000.004.367", "74,32", "C", "30/04 5871 4367-2 FME ALTO DO RO"),
    ("30/04/2020", "0000", "14105", "Transferência Agendada", "110.600.000.013.287", "187,86", "C", "30/04 1106 13287-X PMSS FUNDO P-"),
    ("30/04/2020", "0000", "00000", "BB CP Automatico S P", "70", "549,30", "D", ""),
    ("30/04/2020", "0000", "00000", "S A L D O", "", "0,00", "C", ""),
]


def _val(s: str) -> float | None:
    return float(s.replace(".", "").replace(",", ".")) if s else None


def _abril_df() -> pd.DataFrame:
    rows = [
        {
            "ordem_no_arquivo": i, "dt_movimento": d, "dt_balancete": d, "ag_origem": ag,
            "lote": lote, "historico": h, "documento": doc, "valor": _val(v),
            "valor_dc": dc, "descricao": desc, "periodo": "042020",
        }
        for i, (d, ag, lote, h, doc, v, dc, desc) in enumerate(_ABRIL_2020, start=1)
    ]
    return ingest._enriquece(pd.DataFrame(rows), CONTA)


def _is_saldo(h: str) -> bool:
    h = h.lower()
    return "saldo" in h or "s a l d o" in h


def _checa_abril(df: pd.DataFrame) -> None:
    tx = df[~df["historico"].apply(_is_saldo)]
    c = round(tx.loc[tx.valor_dc == "C", "valor"].sum(), 2)
    d = round(tx.loc[tx.valor_dc == "D", "valor"].sum(), 2)
    assert abs(c - d) < 0.005, f"abril/2020 não fecha: C={c} D={d}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--ano", type=str, default=None, help="Filtra um ano (ex.: 2017).")
    args = ap.parse_args()

    pdf = ingest.ingest_pdf_conta(PASTA, CONTA)
    abril = _abril_df()
    _checa_abril(abril)
    df = pd.concat([pdf, abril], ignore_index=True)

    if args.ano:
        df = df[df["periodo"].str.endswith(args.ano)]

    engine = get_connection(db="BdDIP")
    with engine.connect() as c:
        from sqlalchemy import text
        existentes = {
            r[0] for r in c.execute(
                text(
                    "SELECT a.Periodo FROM dbo.FRAPExtratoArquivo a "
                    "JOIN dbo.FRAPConta ct ON ct.IdConta = a.IdConta WHERE ct.Conta = :c"
                ),
                {"c": CONTA},
            )
        }

    pulados = sorted(set(df["periodo"]) & existentes)
    df = df[~df["periodo"].isin(existentes)]
    novos = sorted(df["periodo"].unique(), key=lambda p: (p[2:], p[:2]))
    print(f"períodos já presentes (pulados): {len(pulados)}")
    print(f"períodos a publicar ({len(novos)}): {', '.join(novos)}")
    print(f"lançamentos a publicar: {len(df)}")

    if args.dry_run or df.empty:
        print("[dry-run] nada gravado." if args.dry_run else "nada novo.")
        return

    resultado = publica_extrato(engine, df, extensao="pdf")
    print(f"publicados {len(resultado)} períodos.")


if __name__ == "__main__":
    main()
