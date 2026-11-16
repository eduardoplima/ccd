"""Levantamento do Despacho do Evento 63 do Processo 000096/2022 (GCAED, 11/11/2026).

Cruza, somente leitura:
  - Evento 103 da APR 003474/2021 (planilha DAP_BEN: processos originários no escopo da APR);
  - Tabelas 1 (78 execuções a apensar) e 2 (19 originários a desconsiderar) do Despacho;
  - todas as execuções do Nereu no banco `processo` (relator, setor, situação do débito,
    protesto, desconto em folha, PGE).
Produz levantamento_96_2022.xlsx (anexo: uma aba por grupo de execuções),
anexo_ev103_fluxograma.xlsx (anexo: uma linha por originário do Ev. 103, colunas = etapas da
Figura 1), levantamento.json (entrada de gerar_documentos.py) e levantamento.md (resumo).

Rodar: .venv/Scripts/python.exe processos/projetos/nereu_apensamento_96_2022/levantamento.py
"""
import json
import re
from pathlib import Path

import fitz
import pandas as pd

from ccd.config import cpf
from ccd.db import run_query_df
from ccd.processo import _query_informacoes

BASE = Path(__file__).resolve().parent
PRINCIPAL = "000096/2022"
APR = "003474/2021"
EV_DESPACHO, EV_PLANILHA = 63, 103
CPF = cpf("NEREU")
# nº do processo ocupa uma linha só; a planilha mistura "N / A" e "N/A" e nem sempre tem zeros à esquerda
PROC = re.compile(r"^\s*(\d{1,7})\s*/\s*(\d{4})\s*$", re.M)

SQL_UNIVERSO = """
SELECT e.IdDebito, e.CodigoTipoDebito tipo, e.valorOriginalDebito valor,
       esd.DescricaoStatusDivida situacao, esp.Descricao protesto,
       CONCAT(po.numero_processo,'/',po.ano_processo) origem,
       CONCAT(pe.numero_processo,'/',pe.ano_processo) execucao,
       RTRIM(pe.setor_atual) setor, RTRIM(re.nome) relator,
       (SELECT CONCAT(pa.numero_processo,'/',pa.ano_processo) FROM Processos pa
         WHERE pa.IdProcesso = pe.IdProcessoApensador) apensado_a,
       (SELECT COUNT(*) FROM Exe_DescontoFolha d WHERE d.IdDebito = e.IdDebito AND d.Ativo = 1) desconto,
       (SELECT COUNT(*) FROM PGE_Processo pg WHERE pg.IdDebitoExecucao = e.IdDebito) pge
FROM Exe_Debito e
JOIN Exe_DebitoPessoa edp ON edp.IDDebito = e.IdDebito
JOIN GenPessoa gp ON gp.IdPessoa = edp.IDPessoa
LEFT JOIN Exe_StatusDivida esd ON esd.CodigoStatusDivida = e.CodigoStatusDivida
LEFT JOIN Exe_StatusProtesto esp ON esp.IdExe_StatusProtesto = e.StatusProtesto
LEFT JOIN Processos pe ON pe.IdProcesso = e.IdProcessoExecucao
LEFT JOIN Processos po ON po.IdProcesso = e.IdProcessoOrigem
LEFT JOIN Relator re ON re.codigo = pe.codigo_relator
WHERE gp.Documento = :cpf AND e.IdDebitoAnterior IS NULL AND e.IdProcessoExecucao IS NOT NULL
"""


def texto_evento(processo: str, evento: int) -> str:
    df = _query_informacoes(processo, None)
    r = df[df.evento == evento].iloc[0]
    return "\n".join(pg.get_text() for pg in fitz.open(r["caminho_arquivo"]))


def tabelas_despacho(t: str) -> tuple[list, list]:
    def pares(s: str) -> list[tuple[str, str]]:
        toks = re.findall(r"(\d{6}/\d{4})-TC", s)
        return [(toks[i], toks[i + 1]) for i in range(0, len(toks) - 1, 2)]
    t1 = pares(t[t.index("Tabela 1 – Processos de execução"):t.index("b) Em seguida, a remessa")])
    t2 = pares(t[t.index("Situação da execução"):t.index("c) Ainda à DIP")])
    assert len(t1) == 78 and len(t2) == 19, (len(t1), len(t2))
    return t1, t2


if __name__ == "__main__":
    orig103 = {f"{int(n):06d}/{a}" for n, a in PROC.findall(texto_evento(APR, EV_PLANILHA))}
    tab1, tab2 = tabelas_despacho(texto_evento(PRINCIPAL, EV_DESPACHO))
    d1, d2 = dict(tab1), dict(tab2)

    df = run_query_df(SQL_UNIVERSO, cpf=CPF)
    df["gcaed"] = df.relator.fillna("").str.contains("ED SOUZA", case=False)
    df["no_ev103"] = df.origem.isin(orig103)
    df["tabela"] = df.execucao.map(lambda e: "1" if e in d1 else ("2" if e in d2 else ""))
    df["ato_efetivo"] = (df.desconto > 0) | (df.pge > 0) | df.setor.isin(["PROC_EXE", "PGE"])
    ex = df.sort_values(["execucao", "IdDebito"]).drop_duplicates("execucao", keep="last")

    # conferências do despacho contra o banco
    for nome, tab in (("Tabela 1", d1), ("Tabela 2", d2)):
        falt = sorted(set(tab) - set(ex.execucao))
        assert not falt, f"{nome}: execuções fora do banco {falt}"
        dif = [(e, o, ex.set_index("execucao").origem[e]) for e, o in tab.items()
               if ex.set_index("execucao").origem[e] != o]
        assert not dif, f"{nome}: origem diverge do banco {dif}"
    assert ex[ex.tabela == "1"].gcaed.all(), "Tabela 1 com relator ≠ GCAED"

    divergencias = [(n, e, o) for n, tab in (("1", d1), ("2", d2)) for e, o in tab.items()
                    if o not in orig103]
    assert not divergencias, f"originários do despacho fora do Ev. 103: {divergencias}"
    remanescentes = ex[ex.gcaed & ex.no_ev103 & (ex.tabela == "") & (ex.execucao != PRINCIPAL)]
    reuniao = ex[ex.execucao.isin(set(d1) | {PRINCIPAL})]
    com_ato = reuniao[reuniao.ato_efetivo]
    assert com_ato.empty, f"Tabela 1 com ato efetivo de cobrança: {com_ato.execucao.tolist()}"

    def quadro(sub: pd.DataFrame) -> pd.DataFrame:
        cols = ["execucao", "origem", "setor", "relator", "situacao", "protesto", "tipo", "valor",
                "desconto", "pge", "apensado_a", "no_ev103"]
        return sub[cols].rename(columns={
            "execucao": "Processo de execução", "origem": "Processo originário", "setor": "Setor atual",
            "relator": "Relator", "situacao": "Situação do débito", "protesto": "Protesto",
            "tipo": "Tipo (2=multa, 5=cominatória)", "valor": "Valor original (R$)",
            "desconto": "Desconto em folha", "pge": "PGE", "apensado_a": "Apensado a",
            "no_ev103": "Originário no Ev. 103"}).sort_values("Processo de execução")

    fora_apr = ex[ex.gcaed & ~ex.no_ev103 & (ex.tabela == "")]
    outros = ex[~ex.gcaed & ex.no_ev103]
    with pd.ExcelWriter(BASE / "levantamento_96_2022.xlsx") as xw:
        quadro(reuniao).to_excel(xw, sheet_name="Tabela 1 (reunião)", index=False)
        quadro(ex[ex.tabela == "2"]).to_excel(xw, sheet_name="Tabela 2 (desconsiderar)", index=False)
        quadro(remanescentes).to_excel(xw, sheet_name="Remanescentes (item c)", index=False)
        quadro(fora_apr).to_excel(xw, sheet_name="GCAED fora da APR", index=False)
        quadro(outros).to_excel(xw, sheet_name="Outros relatores na APR", index=False)

    # anexo por originário do Ev. 103: cada linha percorre as decisões do fluxograma (Figura 1)
    assert not ex[ex.no_ev103].origem.duplicated().any(), "originário com mais de uma execução"
    sn = {True: "Sim", False: "Não"}
    ev = pd.DataFrame({"origem": sorted(orig103)}).merge(ex, on="origem", how="left")
    tem = ev.execucao.notna()

    def destino(r) -> str:
        if pd.isna(r.execucao):
            return "Sem execução de multa em face do responsável"
        if not r.gcaed:
            return "Outro relator – não alcançada pelo Despacho"
        if r.tabela == "1" or r.execucao == PRINCIPAL:
            return "Reunião ao 000096/2022 e arquivamento (itens a e d)"
        if r.tabela == "2":
            return "Memorando à DAP: desconsiderar na multa diária global (item b)"
        return "Ato efetivo de cobrança – não reunir" if r.ato_efetivo else "Remanescente a reunir (item c)"

    anexo = pd.DataFrame({
        "Processo originário (Ev. 103)": ev.origem,
        "Execução de multa em face do responsável": ev.execucao.fillna("Não"),
        "Relator": ev.relator.fillna(""),
        "Relatoria do Cons. Antonio Ed?": ev.gcaed.map(sn).where(tem, ""),
        "Relacionada no Despacho Ev. 63": ev.tabela.map({"1": "Tabela 1", "2": "Tabela 2", "": "Não relacionada"})
        .mask(ev.execucao == PRINCIPAL, "Processo principal").where(tem, ""),
        "Desconto em folha": (ev.desconto > 0).map(sn).where(tem, ""),
        "PGE / MPC": ((ev.pge > 0) | ev.setor.isin(["PROC_EXE", "PGE"])).map(sn).where(tem, ""),
        "Ato efetivo de cobrança": ev.ato_efetivo.map(sn).where(tem, ""),
        "Setor atual": ev.setor.fillna(""), "Apensado a": ev.apensado_a.fillna(""),
        "Situação do débito": ev.situacao.fillna(""), "Protesto": ev.protesto.fillna(""),
        "Valor original (R$)": ev.valor,
        "Destino": ev.apply(destino, axis=1),
    })
    anexo.to_excel(BASE / "anexo_ev103_fluxograma.xlsx", sheet_name="Ev. 103 x fluxograma", index=False)
    por_destino = anexo.Destino.value_counts().to_dict()
    assert len(anexo) == len(orig103)
    assert por_destino.get("Ato efetivo de cobrança – não reunir", 0) == 0, por_destino  # Figura 1: "sim: nenhuma"
    assert por_destino["Reunião ao 000096/2022 e arquivamento (itens a e d)"] == len(reuniao)
    assert por_destino["Memorando à DAP: desconsiderar na multa diária global (item b)"] == len(d2)
    assert por_destino["Remanescente a reunir (item c)"] == len(remanescentes)
    assert por_destino["Outro relator – não alcançada pelo Despacho"] == len(outros)

    resumo = {
        "originarios_ev103": len(orig103), "execucoes_nereu": int(ex.execucao.nunique()),
        "gcaed": int(ex.gcaed.sum()), "gcaed_na_apr": int((ex.gcaed & ex.no_ev103).sum()),
        "remanescentes": remanescentes.execucao.tolist(),
        "remanescentes_detalhe": remanescentes[["execucao", "origem", "setor", "situacao", "tipo", "valor"]]
        .astype(str).to_dict("records"),
        "gcaed_fora_apr": int(len(fora_apr)),
        "outros_relatores_na_apr": int(len(outros)),
        "protestadas_t1": int((reuniao.protesto == "Protestada").sum()),
        "suspensas_t1": int((reuniao.situacao == "Suspenso").sum()),
        "setor_principal": ex.set_index("execucao").setor[PRINCIPAL],
        "setor_apr": run_query_df("SELECT RTRIM(setor_atual) s FROM Processos WHERE numero_processo='003474' "
                                  "AND ano_processo='2021'").s.iloc[0],
        "tabela1": tab1, "tabela2": tab2,
    }
    (BASE / "levantamento.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1), encoding="utf-8")
    md = [f"# Levantamento Ev. 63 do {PRINCIPAL}", "",
          f"- Originários no Ev. 103 da APR: {len(orig103)}",
          f"- Execuções do Nereu: {resumo['execucoes_nereu']} (GCAED: {resumo['gcaed']}; GCAED na APR: {resumo['gcaed_na_apr']})",
          f"- Tabela 1: {len(d1)} conferidas (relator GCAED, origem igual ao banco, sem desconto/PGE); "
          f"suspensas {resumo['suspensas_t1']}, protestadas {resumo['protestadas_t1']}",
          f"- Tabela 2: {len(d2)} conferidas",
          f"- Remanescentes (item c): {resumo['remanescentes']}",
          f"- GCAED fora da APR (trâmite regular): {len(fora_apr)}; outros relatores com origem na APR: {len(outros)}",
          f"- Setor atual: {PRINCIPAL} = {resumo['setor_principal']}; {APR} = {resumo['setor_apr']}",
          "- Anexo por originário do Ev. 103 (Destino): " + "; ".join(f"{k} = {v}" for k, v in por_destino.items())]
    (BASE / "levantamento.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
