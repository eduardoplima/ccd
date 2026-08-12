"""Tarefas de instrução dos processos hoje na CCD.

Para cada processo com setor_atual='CCD' (sem apensados):
1. agrega os marcadores ativos do setor (IdSetor=762);
2. exclui os com marcador de permanência (parcelamento em curso, acompanhamentos,
   sobrestados, protesto efetivado/enviado, pagamento integral);
3. lê o despacho remetente (última informação de setor != CCD) no share de PDFs;
4. extrai a tarefa pedida via LLM (gpt-4.1) e agrupa tarefas semelhantes.

Saídas: saidas/analise/instrucao_ccd.csv (por processo) e saidas/analise/instrucao_ccd.md (relatório).
Reexecutar retoma do CSV parcial (não reprocessa PDFs/LLM já feitos).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, Field

from ccd.config import REPO_ROOT
from ccd.db import run_query_df
from ccd.pdf import extract_text_from_pdf
from ccd.processo import get_info_file_path

BASE_DIR = Path(__file__).resolve().parent
CSV_OUT = REPO_ROOT / "saidas" / "analise" / "instrucao_ccd.csv"
MD_OUT = REPO_ROOT / "saidas" / "analise" / "instrucao_ccd.md"

ID_SETOR_CCD = 762
LLM_MODEL = "gpt-4.1"  # endpoint /openai/v1 → ChatOpenAI(base_url=), não AzureChatOpenAI
MAX_CHARS = 12_000

# Marcadores que indicam permanência na CCD (acompanhamento/aguardando/suspenso).
MARCADORES_PERMANENCIA = {
    5032,  # PARCELAMENTO EM CURSO
    5684,  # DESCONTO EM FOLHA - ACOMPANHAMENTO
    5469,  # DESCONTO EM FOLHA - Acompanhamento Nereu
    5846,  # Nereu - SOBRESTADO
    5591,  # SOBRESTADO - Decisão judicial
    5966,  # DECISÃO JUDICIAL - Acompanhamento
    5020,  # DECISÃO JUDICIAL - Suspender os efeitos do Acórdão
    6127,  # EXECUÇÃO - aguardando determinações ou impedimentos
    5790,  # Chamados abertos aguardando solução
    5593,  # Protesto Efetivo Junho/2026
    5712,  # Protesto Efetivo Julho/2026
    5797,  # PAGAMENTO INTEGRAL
    5040,  # PROTESTO - Confirmação de envio
    5041,  # PROTESTO - Enviado
}

_SQL_MARCADORES = """
SELECT p.IdProcesso,
       CONCAT(p.numero_processo, '/', p.ano_processo) AS processo,
       p.assunto,
       m.IdMarcador,
       m.Descricao AS marcador
FROM processo.dbo.Processos p
LEFT JOIN processo.dbo.Pro_MarcadorProcesso mp
    ON mp.IdProcesso = p.IdProcesso AND mp.DataExclusao IS NULL
LEFT JOIN processo.dbo.Pro_Marcador m
    ON m.IdMarcador = mp.IdMarcador AND m.IdSetor = :id_setor
WHERE p.setor_atual = 'CCD' AND p.IdProcessoApensador IS NULL
"""

# Última informação de setor != CCD por processo: o despacho do remetente.
_SQL_DESPACHO_REMETENTE = """
WITH ranked AS (
    SELECT
        p.IdProcesso,
        ai.setor,
        ai.resumo,
        ai.nome_informacao,
        CONCAT(
            RTRIM(ai.setor), '_', ai.numero_processo, '_', ai.ano_processo, '_',
            RIGHT(CONCAT('0000', ai.ordem), 4), '.pdf'
        ) AS arquivo,
        ROW_NUMBER() OVER (
            PARTITION BY p.IdProcesso
            ORDER BY ppe.SequencialProcessoEvento DESC
        ) AS rn
    FROM processo.dbo.Processos p
    -- join por numero/ano: ai.IdProcesso é esparso (~27% preenchido)
    JOIN processo.dbo.vw_ata_informacao ai
        ON ai.numero_processo = p.numero_processo AND ai.ano_processo = p.ano_processo
    LEFT JOIN processo.dbo.Pro_ProcessoEvento ppe ON ppe.IdInformacao = ai.idInformacao
    WHERE p.setor_atual = 'CCD' AND p.IdProcessoApensador IS NULL
      AND RTRIM(ai.setor) <> 'CCD'
)
SELECT IdProcesso, setor, resumo, nome_informacao, arquivo
FROM ranked WHERE rn = 1
"""

_PROMPT_TAREFA = """Você é servidor da Coordenadoria de Controle de Decisões (CCD) do TCE/RN.
O texto abaixo é o despacho/decisão que encaminhou um processo à CCD.
Identifique a tarefa que a CCD deve executar nesse processo.

Responda com um rótulo curto e padronizado da tarefa (ex.: "cadastrar débito",
"substituir informação (Nereu)", "instaurar execução", "implementar desconto em folha",
"emitir despacho de arquivamento", "verificar cumprimento de obrigação") e um detalhe de uma frase.

Assunto do processo: {assunto}

Texto do despacho:
\"\"\"{texto}\"\"\"
"""

_PROMPT_GRUPOS = """Você é servidor da CCD do TCE/RN. Abaixo está a lista de rótulos de tarefas
extraídos de despachos que encaminharam processos à CCD, com a contagem de processos de cada rótulo.
Consolide-os em grupos de tarefas semelhantes (mesma atividade de instrução), com um nome curto
por grupo. Todo rótulo deve aparecer em exatamente um grupo.

Rótulos:
{rotulos}
"""


class Tarefa(BaseModel):
    tarefa: str = Field(description="Rótulo curto e padronizado da tarefa pedida à CCD")
    detalhe: str = Field(description="Uma frase detalhando a tarefa")


class Grupo(BaseModel):
    nome: str = Field(description="Nome curto do grupo de tarefas")
    rotulos: list[str] = Field(description="Rótulos de tarefa pertencentes ao grupo")


class Grupos(BaseModel):
    grupos: list[Grupo]


def build_llm():
    import os

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        base_url=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        model=LLM_MODEL,
        temperature=0.0,
    )


def carregar_base() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Retorna (analisar, excluidos), com coluna `marcadores` agregada."""
    raw = run_query_df(_SQL_MARCADORES, id_setor=ID_SETOR_CCD)
    agg = (
        raw.groupby(["IdProcesso", "processo", "assunto"], dropna=False)
        .agg(
            marcadores=("marcador", lambda s: "; ".join(sorted(set(s.dropna())))),
            ids_marcador=("IdMarcador", lambda s: set(s.dropna().astype(int))),
        )
        .reset_index()
    )
    permanece = agg["ids_marcador"].apply(lambda ids: bool(ids & MARCADORES_PERMANENCIA))
    return agg[~permanece].copy(), agg[permanece].copy()


def texto_despacho(row: pd.Series) -> str:
    try:
        caminho = get_info_file_path(row)
        if caminho.exists():
            texto = (extract_text_from_pdf(caminho) or "").strip()
            if texto:
                return texto[:MAX_CHARS]
    except Exception as exc:  # PDF ausente/corrompido → fallback resumo
        print(f"  [pdf] {row['processo']}: {exc}", file=sys.stderr)
    return " ".join(
        str(v) for v in (row.get("nome_informacao"), row.get("resumo")) if v and pd.notna(v)
    )


def extrair_tarefas(df: pd.DataFrame, llm) -> pd.DataFrame:
    from langchain_core.prompts import PromptTemplate

    chain = PromptTemplate.from_template(_PROMPT_TAREFA) | llm.with_structured_output(schema=Tarefa)

    feitos: dict[str, dict] = {}
    if CSV_OUT.exists():
        prev = pd.read_csv(CSV_OUT, dtype=str)
        feitos = {
            r["processo"]: r
            for _, r in prev.iterrows()
            if pd.notna(r.get("tarefa")) and not str(r["tarefa"]).startswith("(")
        }
        print(f"cache: {len(feitos)} processos já extraídos")

    linhas = []
    for i, (_, row) in enumerate(df.iterrows(), 1):
        if row["processo"] in feitos:
            linhas.append(dict(feitos[row["processo"]]))
            continue
        out = {
            "processo": row["processo"],
            "assunto": row["assunto"],
            "marcadores": row["marcadores"],
            "setor_remetente": row["setor"].strip() if isinstance(row.get("setor"), str) else "",
            "tarefa": "(sem texto)",
            "detalhe": "",
        }
        texto = texto_despacho(row)
        if not texto and pd.notna(row.get("assunto")):
            # sem informação de outro setor: processo criado na própria CCD
            # (ex. execuções de decisão) — o assunto+marcadores definem a tarefa
            texto = (
                "(Não há despacho remetente; processo autuado na própria CCD.) "
                f"Assunto: {row['assunto']}. Marcadores da CCD: {row['marcadores']}"
            )
        if texto:
            try:
                t: Tarefa = chain.invoke({"assunto": row["assunto"], "texto": texto})
                out["tarefa"] = t.tarefa.strip().lower()
                out["detalhe"] = t.detalhe.strip()
            except Exception as exc:
                print(f"  [llm] {row['processo']}: {exc}", file=sys.stderr)
                out["tarefa"] = "(erro llm)"
        linhas.append(out)
        if i % 20 == 0:
            print(f"{i}/{len(df)} processos...")
            pd.DataFrame(linhas).to_csv(CSV_OUT, index=False, encoding="utf-8")
    return pd.DataFrame(linhas)


def agrupar(df: pd.DataFrame, llm) -> pd.DataFrame:
    from langchain_core.prompts import PromptTemplate

    contagens = df["tarefa"].value_counts()
    rotulos = "\n".join(f"- {t} ({n} processos)" for t, n in contagens.items())
    chain = PromptTemplate.from_template(_PROMPT_GRUPOS) | llm.with_structured_output(schema=Grupos)
    grupos: Grupos = chain.invoke({"rotulos": rotulos})

    mapa = {r: g.nome for g in grupos.grupos for r in g.rotulos}
    df["grupo"] = df["tarefa"].map(mapa).fillna(df["tarefa"])
    return df


def relatorio(df: pd.DataFrame, excluidos: pd.DataFrame) -> str:
    linhas = ["# Tarefas de instrução — processos na CCD", ""]
    linhas.append(
        f"Total na CCD: {len(df) + len(excluidos)} | analisados: {len(df)} | "
        f"excluídos (permanência): {len(excluidos)}"
    )
    linhas.append("\n## Grupos de tarefas\n")
    for grupo, sub in sorted(df.groupby("grupo"), key=lambda kv: -len(kv[1])):
        linhas.append(f"### {grupo} ({len(sub)} processos)\n")
        for _, r in sub.sort_values("processo").iterrows():
            marc = f" — marcadores: {r['marcadores']}" if r["marcadores"] else ""
            linhas.append(f"- **{r['processo']}** [{r['tarefa']}] {r['detalhe']}{marc}")
        linhas.append("")
    linhas.append("## Excluídos (marcador de permanência)\n")
    for marcadores, sub in sorted(excluidos.groupby("marcadores"), key=lambda kv: -len(kv[1])):
        procs = ", ".join(sorted(sub["processo"]))
        linhas.append(f"- **{marcadores}** ({len(sub)}): {procs}")
    return "\n".join(linhas)


def main() -> None:
    analisar, excluidos = carregar_base()
    print(f"na CCD: {len(analisar) + len(excluidos)} | analisar: {len(analisar)} | excluídos: {len(excluidos)}")

    despachos = run_query_df(_SQL_DESPACHO_REMETENTE)
    analisar = analisar.merge(despachos, on="IdProcesso", how="left")

    llm = build_llm()
    df = extrair_tarefas(analisar, llm)
    df = agrupar(df, llm)
    df.to_csv(CSV_OUT, index=False, encoding="utf-8")

    MD_OUT.write_text(relatorio(df, excluidos), encoding="utf-8")
    print(f"ok: {CSV_OUT}\nok: {MD_OUT}")
    print("\nResumo por grupo:")
    print(df.groupby("grupo").size().sort_values(ascending=False).to_string())


if __name__ == "__main__":
    main()
