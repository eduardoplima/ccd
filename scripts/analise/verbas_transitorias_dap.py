"""Verbas transitórias nos processos de Nereu que estão na CCD.

O grupo "Encaminhamento à DAP" já foi analisado e consta no topo de
saidas/verbas_transitorias_dap.md. Este script cobre os DEMAIS processos de
Nereu na CCD (outros grupos de tarefa) e ANEXA a análise ao mesmo relatório.

Para cada processo de Nereu (que aparece na planilha de débitos do MS —
build_enriched_df) fora do grupo DAP:
1. identifica o processo de ORIGEM (da planilha; fallback: parse do assunto);
2. localiza a primeira informação DAP_BEN do processo de origem;
3. lê o PDF e classifica via LLM se trata de incorporação de verbas transitórias.

Saída: anexa a saidas/verbas_transitorias_dap.md + cache saidas/verbas_transitorias_dap.csv.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# rodar direto (python scripts/analise/x.py) tira a raiz do repo do sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from ccd.config import REPO_ROOT  # noqa: E402
from ccd.db import run_query_df  # noqa: E402
from ccd.pdf import extract_text_from_pdf  # noqa: E402
from ccd.processo import get_info_file_path  # noqa: E402
from scripts.analise.gerar_debitos_nereu_02072026 import build_enriched_df  # noqa: E402

CSV_IN = REPO_ROOT / "saidas" / "instrucao_ccd.csv"
MD_OUT = REPO_ROOT / "saidas" / "verbas_transitorias_dap.md"
CACHE = REPO_ROOT / "saidas" / "verbas_transitorias_dap.csv"

GRUPO_JA_FEITO = "Encaminhamento à DAP"
LLM_MODEL = "gpt-4.1"  # endpoint /openai/v1 → ChatOpenAI(base_url=), não AzureChatOpenAI
MAX_CHARS = 12_000

_SQL_PRIMEIRA_DAP_BEN = """
SELECT TOP 1
    RTRIM(setor) AS setor,
    ordem,
    data_resumo,
    nome_informacao,
    resumo,
    CONCAT(
        RTRIM(setor), '_', numero_processo, '_', ano_processo, '_',
        RIGHT(CONCAT('0000', ordem), 4), '.pdf'
    ) AS arquivo
FROM processo.dbo.vw_ata_informacao
WHERE numero_processo = :numero AND ano_processo = :ano AND RTRIM(setor) = 'DAP_BEN'
ORDER BY ordem
"""

_PROMPT = """Você é servidor da CCD do TCE/RN. O texto abaixo é a análise inicial da DAP_BEN
(Diretoria de Administração de Pessoal - Benefícios) em um processo do TCE/RN.
Diga se o processo trata de INCORPORAÇÃO DE VANTAGENS (VERBAS) DE NATUREZA TRANSITÓRIA
(ex.: incorporação de insalubridade, gratificações, adicionais pós EC 13/2014) ou não.

Título da informação: {titulo}

Texto:
\"\"\"{texto}\"\"\"
"""


class ClassificacaoVT(BaseModel):
    verbas_transitorias: bool = Field(
        description="True se o processo trata de incorporação de vantagens/verbas transitórias"
    )
    observacao: str = Field(description="Uma frase justificando, citando o objeto do processo")


def build_llm():
    import os

    from langchain_openai import ChatOpenAI

    from ccd.config import load_env

    load_env()
    return ChatOpenAI(
        base_url=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        model=LLM_MODEL,
        temperature=0.0,
    )


def _chave(n, a) -> str:
    n, a = str(n).strip(), str(a).strip()
    if not n or not a or n == "nan" or a == "nan":
        return ""
    try:
        return f"{int(n):06d}/{a}"
    except ValueError:
        return f"{n}/{a}"


def mapa_origem() -> tuple[set[str], dict[str, str]]:
    """Da planilha de débitos: conjunto de processos de Nereu (origem/execução)
    e mapa processo->origem. ponytail: se um processo for execução numa linha e
    origem noutra, fica a última vista — raro, aceitável."""
    deb = build_enriched_df()
    nereu: set[str] = set()
    orig_de: dict[str, str] = {}
    for i in range(len(deb)):
        r = deb.iloc[i]
        o = _chave(r["nprocorig"], r["anoprocorig"])
        e = _chave(r["nprocexe"], r["anoprocexe"])
        for p in (o, e):
            if p:
                nereu.add(p)
                if o:
                    orig_de[p] = o
    return nereu, orig_de


def classificar(origem: str, chain) -> dict:
    numero, ano = origem.split("/")
    info = run_query_df(_SQL_PRIMEIRA_DAP_BEN, numero=numero, ano=ano)
    if info.empty:
        return {"info_dap_ben": "-", "vt": "N/A", "obs": "origem sem informação DAP_BEN"}
    row = info.iloc[0]
    out = {"info_dap_ben": f"ordem {row['ordem']} ({row['data_resumo']:%d/%m/%Y})"}

    texto = ""
    try:
        caminho = get_info_file_path(row)
        if caminho.exists():
            texto = (extract_text_from_pdf(caminho) or "").strip()[:MAX_CHARS]
    except Exception as exc:
        print(f"  [pdf] {origem}: {exc}", file=sys.stderr)
    if not texto:
        texto = " ".join(str(v) for v in (row["nome_informacao"], row["resumo"]) if pd.notna(v))

    try:
        c: ClassificacaoVT = chain.invoke({"titulo": row["nome_informacao"], "texto": texto})
        out["vt"] = "Sim" if c.verbas_transitorias else "Não"
        out["obs"] = c.observacao.strip()
    except Exception as exc:
        print(f"  [llm] {origem}: {exc}", file=sys.stderr)
        out["vt"] = "?"
        out["obs"] = "(erro llm)"
    return out


def main() -> None:
    from langchain_core.prompts import PromptTemplate

    nereu, orig_de = mapa_origem()
    df = pd.read_csv(CSV_IN)
    alvo = df[df.processo.isin(nereu) & (df.grupo != GRUPO_JA_FEITO)].copy()
    alvo = alvo.sort_values(["grupo", "processo"])
    print(f"{len(alvo)} processos de Nereu fora do grupo '{GRUPO_JA_FEITO}'")

    # json_schema (default) degenera em loop de 32k tokens neste gateway; function_calling não
    llm = build_llm().bind(max_tokens=500)
    chain = PromptTemplate.from_template(_PROMPT) | llm.with_structured_output(
        schema=ClassificacaoVT, method="function_calling"
    )

    cache: dict[str, dict] = {}
    if CACHE.exists():
        prev = pd.read_csv(CACHE, dtype=str)
        cache = {r["origem"]: dict(r) for _, r in prev.iterrows() if r.get("vt") in ("Sim", "Não", "N/A")}
        print(f"cache: {len(cache)} origens já classificadas")

    linhas = []
    for i, (_, r) in enumerate(alvo.iterrows(), 1):
        proc = r["processo"]
        origem = orig_de.get(proc, "")
        if not origem:
            m = re.search(r"PROCESSO N.{0,2}\s*(\d{6})/(\d{4})", str(r["assunto"]))
            origem = f"{m.group(1)}/{m.group(2)}" if m else proc
        out = {"grupo": r["grupo"], "processo": proc, "origem": origem}

        if origem in cache:
            c = cache[origem]
            out.update({"info_dap_ben": c["info_dap_ben"], "vt": c["vt"], "obs": c["obs"]})
        else:
            c = classificar(origem, chain)
            out.update(c)
            cache[origem] = {"origem": origem, **c}
            if i % 10 == 0:
                print(f"{i}/{len(alvo)}...")
                pd.DataFrame(cache.values()).to_csv(CACHE, index=False, encoding="utf-8")
        linhas.append(out)

    res = pd.DataFrame(linhas)
    pd.DataFrame(cache.values()).to_csv(CACHE, index=False, encoding="utf-8")

    partes = [
        "",
        "---",
        "",
        "# Verbas transitórias — demais processos de Nereu na CCD (outros grupos)",
        "",
        "Processos da CCD que constam na planilha de débitos do MS de Nereu Batista Linhares "
        f"(nº 0807247-93.2025.8.20.0000) e que estão FORA do grupo \"{GRUPO_JA_FEITO}\" "
        "(analisado na seção acima). Mesma metodologia: primeira informação DAP_BEN do "
        f"processo de origem lida e classificada via LLM ({LLM_MODEL}).",
        "",
        f"Total: {len(res)} processos. Verbas transitórias — {dict(res['vt'].value_counts())}.",
        "",
    ]
    for grupo, sub in sorted(res.groupby("grupo"), key=lambda kv: -len(kv[1])):
        vt_sim = int((sub["vt"] == "Sim").sum())
        partes.append(f"## {grupo} ({len(sub)} processos, {vt_sim} verba transitória)")
        partes.append("")
        partes.append(
            "| Processo (CCD) | Origem | Informação DAP_BEN | Verbas transitórias? | Observação |"
        )
        partes.append("|---|---|---|---|---|")
        for _, r in sub.sort_values("processo").iterrows():
            obs = str(r["obs"]).replace("|", "/")
            partes.append(
                f"| {r['processo']} | {r['origem']} | {r['info_dap_ben']} | {r['vt']} | {obs} |"
            )
        partes.append("")

    with MD_OUT.open("a", encoding="utf-8") as f:
        f.write("\n".join(partes))
    print(f"anexado a: {MD_OUT}")
    print(res.groupby(["grupo", "vt"]).size().to_string())


if __name__ == "__main__":
    main()
