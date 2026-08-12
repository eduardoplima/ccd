"""Audita se os processos do trabalho nereu_ms tratam mesmo de verbas
transitórias de servidores da saúde.

Critério: no processo de ORIGEM da execução deve haver informação do setor
DAP_BEN cujo teor trate de vantagens remuneratórias transitórias de servidor
da área da saúde. Veredito: LLM (gpt-4.1) em TODAS as origens com texto —
órgão da origem e keywords ficam só como cross-check (o 003070/2022 mostrou
que keyword sem semântica dá falso OK: "vantagens transitórias" em frase
imprecisa do monitoramento, quando a irregularidade era erro de cálculo).
A coluna `vt1`/`sesap` da planilha analise_debitos_nereu_atualizada.xlsx
também entra só como cross-check.

Somente leitura — não altera nada no banco nem na Área Restrita.
Saídas: saidas/analise/verificacao_verbas_saude_nereu.{xlsx,md}
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import pandas as pd

from ccd.config import REPO_ROOT, informacoes_dir, load_env
from ccd.db import run_query_df
from ccd.pdf import extract_text_from_pdf

sys.path.insert(0, str(REPO_ROOT))
from scripts.automacao.gerar_info_nereu_ms import PROCESSOS as ROUND_1  # noqa: E402

ROUND_2 = [
    ln.strip()
    for ln in (REPO_ROOT / "saidas/nereu_ms/round_2/assinar_pendentes.txt").read_text().splitlines()
    if ln.strip()
]
PLANILHA = REPO_ROOT / "scripts/analise/docs/analise_debitos_nereu_atualizada.xlsx"
OUT_DIR = REPO_ROOT / "saidas/analise"
OUT_XLSX = OUT_DIR / "verificacao_verbas_saude_nereu.xlsx"
OUT_MD = OUT_DIR / "verificacao_verbas_saude_nereu.md"

RE_TRANSITORIA = re.compile(r"transit[óo]ri", re.IGNORECASE)
# vínculo com a SESAP explícito — 'saúde' genérico não basta (ex.: gratificação
# de área terapêutica de servidor da FUNDASE não é alcançada pelo MS)
RE_SESAP = re.compile(r"SESAP|SECRETARIA\s+DE\s+ESTADO\s+DA\s+SA[ÚU]DE", re.IGNORECASE)
RE_ORGAO_SAUDE = re.compile(r"SA[ÚU]DE|HOSPITAL", re.IGNORECASE)

LLM_PROMPT = """Você analisa uma informação técnica do setor de benefícios (DAP_BEN) de um
Tribunal de Contas, extraída de um processo de aposentadoria. O débito em
execução decorre de multa por descumprimento de determinação desse processo.

Órgão do processo de origem: {orgao}
Assunto: {assunto}

Responda se a determinação/análise trata de vantagens remuneratórias
TRANSITÓRIAS (verbas transitórias, ex.: gratificações, adicionais por condição
temporária) de servidor VINCULADO À SESAP (Secretaria de Estado da Saúde
Pública) ou à rede estadual de saúde. Atenção: verba de natureza sanitária
(ex.: insalubridade, área terapêutica) paga a servidor de OUTRO órgão
(FUNDASE, educação etc.) NÃO conta — o vínculo é que decide. Também NÃO conta
irregularidade que seja apenas ERRO DE CÁLCULO dos proventos (ex.:
inobservância da média das 80% maiores remunerações de contribuição, Lei
10.887/2004), mesmo que alguma peça a chame imprecisamente de "vantagens
transitórias": a irregularidade central deve ser a percepção de verba
transitória nos proventos.

Responda APENAS neste formato:
VEREDITO: sim|nao|indeterminado
JUSTIFICATIVA: <uma linha>

Texto da informação:
{texto}
"""


def fetch_debitos() -> pd.DataFrame:
    """Débitos cujo processo de execução OU de origem está nas listas do trabalho."""
    todos = sorted(set(ROUND_1) | set(ROUND_2))
    ph = {f"p{i}": p for i, p in enumerate(todos)}
    inc = ", ".join(f":{k}" for k in ph)
    sql = f"""
    SELECT d.IdDebito AS id_debito,
           CONCAT(RIGHT('000000'+CAST(pe.numero_processo AS varchar),6),'/',pe.ano_processo) AS execucao,
           CONCAT(RIGHT('000000'+CAST(po.numero_processo AS varchar),6),'/',po.ano_processo) AS origem,
           po.IdProcesso AS id_origem,
           RTRIM(po.assunto) AS assunto_origem,
           o.nome AS orgao_origem,
           d.DataCancelamento
    FROM processo.dbo.Exe_Debito d
    LEFT JOIN processo.dbo.Processos pe ON pe.IdProcesso = d.IdProcessoExecucao
    LEFT JOIN processo.dbo.Processos po ON po.IdProcesso = d.IdProcessoOrigem
    LEFT JOIN processo.dbo.Orgaos o ON o.IdOrgao = po.IdOrgaoEnvolvido
    WHERE CONCAT(RIGHT('000000'+CAST(pe.numero_processo AS varchar),6),'/',pe.ano_processo) IN ({inc})
       OR CONCAT(RIGHT('000000'+CAST(po.numero_processo AS varchar),6),'/',po.ano_processo) IN ({inc})
    """
    df = run_query_df(sql, **ph)
    lista = set(todos)
    # processo da lista (o que está/esteve na CCD): execução quando é ela que consta
    df["processo_ccd"] = df["execucao"].where(df["execucao"].isin(lista), df["origem"])
    df["round"] = df["processo_ccd"].map(
        lambda p: "1+2" if p in set(ROUND_1) & set(ROUND_2)
        else "1" if p in set(ROUND_1) else "2"
    )
    df["cancelado"] = df["DataCancelamento"].notna().map({True: "S", False: "N"})
    return df.drop(columns=["DataCancelamento"])


def fetch_dap_ben(origens: list[str]) -> pd.DataFrame:
    """Informações DAP_BEN* dos processos de origem, por número/ano.

    Não filtrar por IdProcesso: a vw_ata_informacao traz IdProcesso NULL nas
    informações mais novas (ex.: 011525/2009 ordens 59/80/86), que sumiam do
    filtro por id — o LLM via só as antigas e errava o veredito.
    """
    ph = {f"i{k}": v for k, v in enumerate(origens)}
    inc = ", ".join(f":{k}" for k in ph)
    sql = f"""
    SELECT CONCAT(RTRIM(inf.numero_processo), '/', RTRIM(inf.ano_processo)) AS origem,
           RTRIM(inf.setor) AS setor, inf.ordem,
           CONVERT(varchar, inf.data_resumo, 103) AS data, inf.resumo,
           inf.numero_processo, inf.ano_processo
    FROM processo.dbo.vw_ata_informacao inf
    WHERE inf.setor LIKE 'DAP_BEN%'
      AND CONCAT(RTRIM(inf.numero_processo), '/', RTRIM(inf.ano_processo)) IN ({inc})
    """
    return run_query_df(sql, **ph)


def texto_dap_ben(row) -> str:
    """Extrai o texto do PDF da informação no share (convenção de ccd.processo)."""
    arquivo = (
        f"{row.setor}_{row.numero_processo}_{row.ano_processo}_"
        f"{int(row.ordem):04d}.pdf"
    )
    path = informacoes_dir() / row.setor / arquivo
    try:
        return extract_text_from_pdf(path) or ""
    except Exception:
        return ""


def veredito_llm(llm, texto: str, orgao: str, assunto: str) -> tuple[str, str]:
    resp = llm.invoke(
        LLM_PROMPT.format(texto=texto[:8000], orgao=orgao, assunto=assunto)
    ).content
    m = re.search(r"VEREDITO:\s*(sim|nao|não|indeterminado)", resp, re.IGNORECASE)
    j = re.search(r"JUSTIFICATIVA:\s*(.+)", resp)
    v = (m.group(1).lower().replace("não", "nao")) if m else "indeterminado"
    return v, j.group(1).strip() if j else ""


def main() -> None:
    load_env()
    df = fetch_debitos()
    print(f"{len(df)} débitos, {df['processo_ccd'].nunique()} processos da lista cobertos")

    todos = set(ROUND_1) | set(ROUND_2)
    # coberto = aparece como execução OU origem de algum débito (quando ambos os
    # lados estão na lista, processo_ccd fica com um só — 019033/2017 é a origem
    # do débito da execução 002162/2025 e não é "sem débito")
    cobertos = set(df["processo_ccd"]) | set(df["execucao"].dropna()) | set(df["origem"].dropna())
    sem_debito = sorted(todos - cobertos)
    if sem_debito:
        print(f"AVISO: {len(sem_debito)} processo(s) da lista sem débito no banco: {sem_debito}")

    infos = fetch_dap_ben(sorted(set(df["origem"].dropna())))
    print(f"{len(infos)} informações DAP_BEN em {infos['origem'].nunique()} origens")

    # texto + keywords por informação (cache por arquivo)
    infos["texto"] = [texto_dap_ben(r) for r in infos.itertuples()]
    infos["kw_transitoria"] = infos["texto"].str.contains(RE_TRANSITORIA)
    infos["kw_sesap"] = infos["texto"].str.contains(RE_SESAP)

    # agrega sinais por origem (qualquer informação DAP_BEN conta)
    por_origem = infos.groupby("origem").agg(
        dap_ben=("setor", "size"),
        kw_transitoria=("kw_transitoria", "any"),
        kw_sesap=("kw_sesap", "any"),
        sem_texto=("texto", lambda s: bool((s.str.len() == 0).all())),
        resumo_dap_ben=("resumo", lambda s: " | ".join(str(x)[:60] for x in s[:3])),
    )
    df = df.merge(por_origem, how="left", left_on="origem", right_index=True)
    df["dap_ben"] = df["dap_ben"].fillna(0).astype(int)

    # cross-check da planilha
    plan = pd.read_excel(PLANILHA, sheet_name="TodosDebitos")[["id_debito", "vt1", "sesap"]]
    df = df.merge(plan.drop_duplicates("id_debito"), how="left", on="id_debito")

    # keyword+órgão não decidem mais (003070/2022 saiu OK com "vantagens
    # transitórias" em frase imprecisa do monitoramento) — todo veredito de
    # mérito vem do LLM; aqui só os casos sem texto para julgar
    def veredito(r) -> tuple[str, str]:
        if r.dap_ben == 0:
            return "NAO_SAUDE", "sem informação DAP_BEN na origem"
        if bool(r.sem_texto):
            return "MANUAL", "PDF da DAP_BEN sem texto extraível"
        return "AMBIGUO", "aguardando LLM"

    df[["veredito", "fonte_veredito"]] = df.apply(
        lambda r: pd.Series(veredito(r)), axis=1
    )

    # LLM em todas as origens com texto
    amb = df[df["veredito"] == "AMBIGUO"]
    if not amb.empty:
        from scripts.analise.atualizar_debitos_nereu_definitiva import build_llm
        llm = build_llm("gpt-4.1")
        print(f"LLM: classificando {amb['origem'].nunique()} origens…")
        textos = infos.groupby("origem")["texto"].apply(" ".join)
        mapa = {"sim": "OK", "nao": "NAO_SAUDE", "indeterminado": "MANUAL"}
        for origem in amb["origem"].unique():
            ctx = amb[amb["origem"] == origem].iloc[0]
            v, just = veredito_llm(llm, textos.get(origem, ""),
                                   str(ctx.orgao_origem), str(ctx.assunto_origem))
            sel = df["origem"] == origem
            df.loc[sel, "veredito"] = mapa[v]
            df.loc[sel, "fonte_veredito"] = f"LLM: {just}"[:200]
            print(f"  origem {origem}: {mapa[v]} — {just}")

    # cross-check: divergências entre o LLM e os sinais keyword/órgão
    det_ok = df["kw_transitoria"].fillna(False) & (
        df["kw_sesap"].fillna(False)
        | df["orgao_origem"].fillna("").str.contains(RE_ORGAO_SAUDE)
    )
    div = df.loc[df["veredito"].isin(["OK", "NAO_SAUDE"])
                 & ((df["veredito"] == "OK") != det_ok),
                 ["processo_ccd", "origem", "veredito", "fonte_veredito"]
                 ].drop_duplicates("origem")
    if not div.empty:
        print(f"\ncross-check: LLM diverge dos sinais keyword/órgão em {len(div)} origem(ns):")
        print(div.to_string(index=False))

    # agregado por processo da lista: pior veredito prevalece
    ordem = {"NAO_SAUDE": 0, "MANUAL": 1, "OK": 2}
    agg = df.groupby("processo_ccd")["veredito"].agg(lambda s: min(s, key=lambda v: ordem[v]))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cols = ["processo_ccd", "round", "execucao", "origem", "id_debito", "cancelado",
            "orgao_origem", "assunto_origem", "dap_ben", "resumo_dap_ben",
            "kw_transitoria", "kw_sesap", "vt1", "sesap", "veredito", "fonte_veredito"]
    df[cols].sort_values(["veredito", "processo_ccd"]).to_excel(OUT_XLSX, index=False)

    linhas = [
        "# Verificação: verbas transitórias de servidores da saúde (nereu_ms)", "",
        f"Débitos analisados: {len(df)} | Processos: {df['processo_ccd'].nunique()}", "",
        "## Veredito por processo", "",
        agg.value_counts().to_string(), "",
        "## Processos NÃO-saúde ou pendentes de revisão", "",
    ]
    for v in ("NAO_SAUDE", "MANUAL"):
        procs = sorted(agg[agg == v].index)
        linhas.append(f"### {v} ({len(procs)})")
        for p in procs:
            sub = df[df["processo_ccd"] == p].iloc[0]
            linhas.append(f"- **{p}** (round {sub['round']}, origem {sub.origem}, "
                          f"órgão: {sub.orgao_origem}) — {sub.fonte_veredito}")
        linhas.append("")
    if sem_debito:
        linhas += [f"### Sem débito no banco ({len(sem_debito)})",
                   ", ".join(sem_debito), ""]
    OUT_MD.write_text("\n".join(linhas), encoding="utf-8")

    print(f"\nVereditos (por processo):\n{agg.value_counts().to_string()}")
    print(f"\nSaídas: {OUT_XLSX}\n        {OUT_MD}")

    # sanity: erros conhecidos não podem sair OK; 000098/2022 (SESAP) deve ser OK.
    # 002038/2024 saiu da lista: o "sem DAP_BEN" era artefato do IdProcesso NULL
    # na view — a origem 100762/2020 trata de Adicional Noturno de servidora SESAP.
    # 003070/2022 (origem 007245/2017): erro de cálculo (média das 80%) que o
    # monitoramento chamou de "vantagens transitórias" — derrubou a regra keyword
    conhecidos = ["000119/2022", "000134/2022", "003006/2022", "003709/2022",
                  "001390/2023", "003070/2022"]
    for p in conhecidos:
        assert agg.get(p) != "OK", f"sanity: {p} deveria ser suspeito, saiu {agg.get(p)}"
    assert agg.get("000098/2022") == "OK", f"sanity: 000098/2022 saiu {agg.get('000098/2022')}"
    print("sanity ok: erros conhecidos não-OK; 000098/2022 OK")


if __name__ == "__main__":
    main()
