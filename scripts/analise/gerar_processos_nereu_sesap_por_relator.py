"""Gera uma planilha por relator (conselheiro) com os débitos SESAP do Nereu,
excluídos os cancelados. Um arquivo por conselheiro: processos_nereu_sesap_<conselheiro>.xlsx.

Reutiliza o enriquecimento de gerar_debitos_nereu_02072026.build_enriched_df()
(banco: valor original, setor atual, dívida ativa via PGE_Processo, protesto,
desconto em folha via Exe_DescontoFolha + notificações).

--todos inclui débitos não-SESAP também (nome do arquivo continua ...sesap...).
"""
from __future__ import annotations

import argparse

import pandas as pd

from ccd.db import get_connection
from scripts.analise.gerar_debitos_nereu_02072026 import (
    DOCS,
    _conselheiro,
    _split,
    build_enriched_df,
)

# renomeia as colunas de build_enriched_df para o padrão snake_case sem acento.
# `verba transitório` (=vt1) vira `verba_transitoria`; `sesap` (interno) é mantido.
# `setor atual` é substituído por setor_atual_origem/execucao, calculados no main.
RENAME = {
    "nprocorig": "numero_processo_origem", "anoprocorig": "ano_processo_origem",
    "nprocexe": "numero_processo_execucao", "anoprocexe": "ano_processo_execucao",
    "órgão": "orgao", "natureza": "natureza",
    "valor original": "valor_original", "valor atualizado": "valor_atualizado",
    "situação do débito": "situacao_debito", "dívida ativa": "divida_ativa",
    "protesto": "protesto", "desconto em folha": "desconto_folha", "sesap": "sesap",
    "verba transitório": "verba_transitoria",
}
COLS_RELATOR = [
    "numero_processo_origem", "ano_processo_origem",
    "numero_processo_execucao", "ano_processo_execucao", "orgao",
    "setor_atual_origem", "setor_atual_execucao", "natureza",
    "valor_original", "valor_atualizado", "situacao_debito", "divida_ativa",
    "protesto", "desconto_folha", "sesap", "verba_transitoria",
]

# conselheiras (nome de arquivo com dra_); demais recebem dr_.
DRA = {"ana", "maria"}

_VAZIO = {"", "nan", "None", "NaT"}


def _procstr(n: pd.Series, a: pd.Series) -> pd.Series:
    """('000232','2026') -> '000232/2026'; número vazio -> ''."""
    n, a = n.astype(str).str.strip(), a.astype(str).str.strip()
    return (n + "/" + a).where(~n.isin(_VAZIO), "")


def _preenche_execucao(df: pd.DataFrame, eng) -> None:
    """Preenche nprocexe/anoprocexe em branco a partir de Exe_Debito.IdProcessoExecucao
    (fonte autoritativa da execução do débito). Não sobrescreve valores já preenchidos."""
    ids = ", ".join(str(int(i)) for i in df["id_debito"].dropna().unique())
    exe = pd.read_sql(
        f"SELECT ed.IdDebito AS id_debito, "
        f"CONCAT(pe.numero_processo,'/',pe.ano_processo) AS exe "
        f"FROM processo.dbo.Exe_Debito ed "
        f"LEFT JOIN processo.dbo.Processos pe ON ed.IdProcessoExecucao = pe.IdProcesso "
        f"WHERE ed.IdDebito IN ({ids})",
        eng,
    ).drop_duplicates("id_debito")
    exe_map = {
        int(r.id_debito): r.exe for r in exe.itertuples()
        if r.exe and "/" in str(r.exe) and not str(r.exe).startswith("/")
    }
    mask = df["nprocexe"].astype(str).str.strip().isin(_VAZIO)
    n = 0
    for idx in df.index[mask]:
        idd = df.at[idx, "id_debito"]
        val = exe_map.get(int(idd)) if pd.notna(idd) else None
        if val:
            df.at[idx, "nprocexe"], df.at[idx, "anoprocexe"] = _split(val)
            n += 1
    print(f"Execução preenchida do banco: {n} débitos que estavam sem processo de execução")


def _processos_map(procs: list[str], eng) -> pd.DataFrame:
    """Setor atual e relator de cada processo 'numero/ano' via `Processos` (localização
    oficialmente recebida — fonte autoritativa segundo o usuário). Indexado por numproc."""
    lst = ", ".join(f"'{p}'" for p in procs)
    q = (
        "SELECT CONCAT(RTRIM(p.numero_processo),'/',RTRIM(p.ano_processo)) AS numproc, "
        "RTRIM(p.setor_atual) AS setoratual, r.nome AS relator "
        "FROM processo.dbo.Processos p "
        "LEFT JOIN processo.dbo.Relator r ON r.codigo = p.codigo_relator "
        f"WHERE CONCAT(RTRIM(p.numero_processo),'/',RTRIM(p.ano_processo)) IN ({lst})"
    )
    return pd.read_sql(q, eng).drop_duplicates("numproc").set_index("numproc")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--todos", action="store_true", help="não filtrar por SESAP")
    args = ap.parse_args()

    df = build_enriched_df()
    antes = len(df)
    df = df[~df["situação do débito"].astype(str).str.contains("Cancel", case=False, na=False)]
    print(f"Débitos: {antes} -> {len(df)} (removidos {antes - len(df)} cancelados)")
    if not args.todos:
        df = df[df["sesap"] == "SESAP"]
        print(f"Filtro SESAP: {len(df)} débitos")
    df = df.copy()

    eng = get_connection()
    _preenche_execucao(df, eng)

    # setor atual de origem e de execução em colunas separadas (destino do último lote).
    proc_orig = _procstr(df["nprocorig"], df["anoprocorig"])
    proc_exe = _procstr(df["nprocexe"], df["anoprocexe"])
    todos = sorted({p for p in pd.concat([proc_orig, proc_exe]) if p})
    pmap = _processos_map(todos, eng)
    smap = pmap["setoratual"]
    df["setor_atual_origem"] = proc_orig.map(smap).fillna("")
    df["setor_atual_execucao"] = proc_exe.map(smap).fillna("")

    # gabinete destinatário = relator do processo de execução (quando existe);
    # fallback: relator da origem no banco, depois a coluna da planilha (origem).
    relmap = pmap["relator"]
    rel_efetivo = proc_exe.map(relmap).fillna(proc_orig.map(relmap)).fillna(df["relator"])

    df = df.rename(columns=RENAME)
    df["conselheiro"] = rel_efetivo.apply(_conselheiro)
    for cons, g in df.groupby("conselheiro"):
        prefixo = "dra_" if cons in DRA else "dr_"
        out = DOCS / f"processos_nereu_sesap_{prefixo}{cons}.xlsx"
        g = g.sort_values(["numero_processo_origem", "ano_processo_origem"])[COLS_RELATOR]
        g.to_excel(out, index=False)
        print(f"  {out.name}: {len(g)} débitos  "
              f"(orig R$ {g['valor_original'].sum():,.2f} | atual R$ {g['valor_atualizado'].sum():,.2f})")


if __name__ == "__main__":
    main()
