"""Gera docs/debitos_nereu_02072026.xlsx a partir de analise_debitos_nereu_atualizada.xlsx.

Colunas: nprocorig, anoprocorig, nprocexe, anoprocexe, órgão, relator,
verba transitório, setor atual, natureza, valor original, valor atualizado,
situação do débito, dívida ativa, protesto, desconto em folha.

Dados vêm da planilha já atualizada (aba TodosDebitos); `setor atual`,
`valor original`, `dívida ativa` (Status_PGE), `protesto` (StatusProtesto) e
`desconto em folha` (Exe_DescontoFolha) — que não estão na planilha — são
buscados no banco por id_debito / processo.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from ccd.db import get_connection

DOCS = Path(__file__).resolve().parent / "docs"
SRC = DOCS / "analise_debitos_nereu_atualizada.xlsx"
FINAL = DOCS / "debitos_nereu_planilha_final.xlsx"
OUT = DOCS / "debitos_nereu_02072026.xlsx"

COLS = [
    "nprocorig", "anoprocorig", "nprocexe", "anoprocexe", "órgão", "relator",
    "verba transitório", "setor atual", "natureza", "valor original",
    "valor atualizado", "situação do débito", "dívida ativa", "protesto",
    "desconto em folha",
]


def _split(proc):
    """'015303/2006' -> ('015303', '2006'); vazio/'/'/'Sem...' -> ('', '')."""
    s = str(proc)
    if "/" not in s or s.startswith("Sem"):
        return "", ""
    n, _, a = s.partition("/")
    n, a = n.strip(), a.strip()
    return (n, a) if n and a else ("", "")


def _conselheiro(relator) -> str:
    """Slug do conselheiro p/ nome de arquivo (convenção do notebook, cell 56)."""
    import unicodedata
    r = str(relator)
    if "ANTONIO ED SOUZA SANTANA" in r:
        return "antonio_ed"
    if "GILBERTO" in r:
        return "gilberto"
    if "POTI" in r:
        return "poti"
    first = r.split()[0].lower() if r.split() else "sem_relator"
    return "".join(c for c in unicodedata.normalize("NFKD", first) if not unicodedata.combining(c))


def build_enriched_df() -> pd.DataFrame:
    """Tabela enriquecida (colunas de saída + `sesap`/`id_debito` internos)."""
    df = pd.read_excel(SRC, sheet_name="TodosDebitos")
    eng = get_connection()

    ids = ", ".join(str(int(i)) for i in df["id_debito"].dropna().unique())
    val_orig = pd.read_sql(
        f"SELECT IdDebito as id_debito, valorOriginalDebito as valor_original "
        f"FROM processo.dbo.Exe_Debito WHERE IdDebito IN ({ids})",
        eng,
    ).drop_duplicates("id_debito")
    df = df.merge(val_orig, how="left", on="id_debito")

    procs = pd.unique(pd.concat([df["processo_origem"], df["processo_execucao"]]).dropna())
    lista = ", ".join(f"'{p}'" for p in procs if "/" in str(p) and not str(p).startswith("Sem"))
    setor = pd.read_sql(
        f"SELECT CONCAT(p.numero_processo, '/', p.ano_processo) as processo, "
        f"       p.setor_atual, o.nome as orgao "
        f"FROM processo.dbo.Processos p "
        f"LEFT JOIN processo.dbo.Orgaos o ON o.IdOrgao = p.IdOrgaoEnvolvido "
        f"WHERE CONCAT(p.numero_processo, '/', p.ano_processo) IN ({lista})",
        eng,
    ).drop_duplicates("processo")
    smap = setor.set_index("processo")["setor_atual"].to_dict()
    omap = setor.set_index("processo")["orgao"].dropna().to_dict()

    # protesto (StatusProtesto) por id_debito
    st = pd.read_sql(
        f"SELECT IdDebito as id_debito, StatusProtesto "
        f"FROM processo.dbo.Exe_Debito WHERE IdDebito IN ({ids})",
        eng,
    ).drop_duplicates("id_debito")
    df = df.merge(st, how="left", on="id_debito")

    # domínio oficial dos códigos (antes só 0/3 eram traduzidos; os demais
    # vazavam como número cru — ex.: "7" no despacho do 003661/2022)
    dominio_protesto = pd.read_sql(
        "SELECT IdExe_StatusProtesto, Descricao FROM processo.dbo.Exe_StatusProtesto",
        eng,
    ).set_index("IdExe_StatusProtesto")["Descricao"].str.strip().to_dict()

    def protesto_status(x):  # cell 27 do notebook
        if pd.isna(x) or x == 0:
            return "Sem Protesto"
        return dominio_protesto.get(int(x), f"Status {int(x)} (não catalogado)")

    # dívida ativa: Status_PGE da Exe_Debito está sempre NULL; o envio real está em
    # PGE_Processo (join por IdDebitoExecucao = id_debito). Rótulo = status do processo
    # PGE quando enviado com sucesso (IdStatusEnvio=2), senão o status do envio.
    pge = pd.read_sql(
        f"""SELECT p.IdDebitoExecucao as id_debito, p.IdStatusEnvio,
                   se.DescricaoStatusEnvio, sp.DescricaoStatusProcessoPGE
            FROM processo.dbo.PGE_Processo p
            LEFT JOIN processo.dbo.PGE_StatusEnvio se ON se.IdStatusEnvio = p.IdStatusEnvio
            LEFT JOIN processo.dbo.PGE_StatusProcesso sp ON sp.IdStatusProcessoPGE = p.IdStatusProcessoPGE
            WHERE p.IdDebitoExecucao IN ({ids})""",
        eng,
    ).drop_duplicates("id_debito")

    def _pge_label(r):
        if r.IdStatusEnvio == 2:
            return r.DescricaoStatusProcessoPGE or "Enviado à Dívida Ativa"
        return f"Envio: {r.DescricaoStatusEnvio}"
    pge_map = {int(r.id_debito): _pge_label(r) for r in pge.itertuples()}

    # desconto em folha: "implantado" (registro ativo em Exe_DescontoFolha) tem precedência;
    # "notificado" vem da aba "Notificações desconto em folha" de debitos_nereu_planilha_final.xlsx,
    # por id_debito (ids_debitos) com fallback por processo_execucao — ex.: 003677/2022, cujo
    # débito 23295 não tem id na notificação mas o processo foi notificado.
    implantado = set(pd.read_sql(
        f"SELECT DISTINCT IdDebito FROM processo.dbo.Exe_DescontoFolha "
        f"WHERE Ativo = 1 AND IdDebito IN ({ids})",
        eng,
    )["IdDebito"])
    nf = pd.read_excel(FINAL, sheet_name="Notificações desconto em folha")
    notif_ids = set(pd.to_numeric(nf["ids_debitos"], errors="coerce").dropna().astype(int))
    notif_procs = set(nf["processo"].astype(str))

    def _desconto(row):
        if row["id_debito"] in implantado:
            return "Desconto em folha implantado"
        if row["id_debito"] in notif_ids or str(row["processo_execucao"]) in notif_procs:
            return "Notificado desconto em folha"
        return "Sem desconto em folha"

    def setor_atual(row):
        exe = str(row["processo_execucao"])
        if "/" in exe and not exe.startswith("Sem") and exe in smap:
            return smap[exe]
        return smap.get(str(row["processo_origem"]))

    orig = df["processo_origem"].apply(_split)
    exe = df["processo_execucao"].apply(_split)
    out = pd.DataFrame({
        "nprocorig": orig.str[0],
        "anoprocorig": orig.str[1],
        "nprocexe": exe.str[0],
        "anoprocexe": exe.str[1],
        # órgão do processo de origem; se em branco, cai no órgão do processo de execução.
        "órgão": df["orgao_envolvido_processo_origem"]
        .fillna(df["processo_origem"].astype(str).map(omap))
        .fillna(df["processo_execucao"].astype(str).map(omap)),
        "relator": df["relator"],
        "verba transitório": df["vt1"],
        "setor atual": df.apply(setor_atual, axis=1),
        "natureza": df["tipo_multa"],
        "valor original": df["valor_original"],
        "valor atualizado": df["valor_multa"],
        "situação do débito": df["status_divida"],
        "dívida ativa": df["id_debito"].map(pge_map).fillna("Sem envio à Dívida Ativa"),
        "protesto": df["StatusProtesto"].apply(protesto_status),
        "desconto em folha": df.apply(_desconto, axis=1),
    })
    out["sesap"] = df["sesap"].values
    out["id_debito"] = df["id_debito"].values
    return out


def main() -> None:
    out = build_enriched_df()
    out[COLS].to_excel(OUT, index=False)
    print(f"Gravado: {OUT}  ({len(out)} débitos)")
    print(out[COLS].head(5).to_string(index=False))


if __name__ == "__main__":
    main()
