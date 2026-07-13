#!/usr/bin/env python3
"""Busca a última informação de Luzenildo nos 14 processos eletrônicos do CCD.

Usa o módulo ccd.processo.get_informacoes_processo para acessar o banco,
extrai texto dos PDFs, revisa ortografia/argumentação e gera relatório .md.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from ccd.processo import get_informacoes_processo

load_dotenv(Path(__file__).resolve().parent / ".env", override=False)

PROCESSOS_LUZENILDO = [
    "000120/2023",
    "000146/2023",
    "003066/2022",
    "003073/2022",
    "000501/2016",
    "000653/2016",
    "003147/2018",
    "003827/2017",
    "005224/2016",
    "006425/2017",
    "011807/2017",
    "016350/2016",
    "018555/2016",
    "023625/2016",
]

# Nomes que o banco pode usar para Luzenildo (CPF 10839844468)
LUIZENILDO_CPF = "10839844468"


def revisar_texto(texto: str) -> dict[str, Any]:
    rev: dict[str, Any] = {
        "alertas": [],
        "problemas": [],
        "sugestoes": [],
        "comprimento": len(texto),
        "paragrafos": len([p for p in texto.split("\n") if p.strip()]),
    }

    padroes = [
        (r"(?i)\bexcelentíssimo\b", "📝", "Verificar concordância"),
        (r"(?i)\bilustríssimo\b", "📝", "Verificar concordância"),
        (r"(?i)\btransitad[ao]\s+em\s+julgado\b", "👍", "Termo jurídico OK"),
        (r"(?i)\bpreclus[ao]\b", "👍", "Termo jurídico OK"),
        (r"(?i)\bporque\b(?=\s+[aeio])", "🔍", "'porque' junto no início?"),
        (r"(?i)\b([a-zà-ú]+)\s+e\s+\1\b", "🔍", "Possível repetição"),
        (r"(?i)\bconselheiro\b", "👍", "Tratamento OK"),
    ]

    for padrao, icone, desc in padroes:
        matches = re.findall(padrao, texto)
        if matches:
            rev["alertas"].append(f"{icone} {desc} ({len(matches)}x)")

    acentos_suspeitos = {
        "ocorrencia": "ocorrência", "ocorrencias": "ocorrências",
        "providencia": "providência", "providencias": "providências",
        "juridico": "jurídico", "juridica": "jurídica",
        "transito": "trânsito", "oficio": "ofício",
    }
    palavras = re.findall(r"\b[a-zà-ú]{4,}\b", texto.lower())
    for palavra in set(palavras):
        if palavra in acentos_suspeitos:
            rev["problemas"].append(
                f'✗ "{palavra}" → sugere-se "{acentos_suspeitos[palavra]}"'
            )

    if texto.strip() and not texto.strip().endswith("."):
        rev["problemas"].append("📌 Texto não termina com ponto final")

    conectivos = ["portanto", "assim", "destarte", "contudo", "entretanto",
                   "todavia", "ademais", "outrossim", "por conseguinte",
                   "diante do exposto"]
    if not any(c in texto.lower() for c in conectivos):
        rev["sugestoes"].append("💡 Sem conectivos argumentativos")

    return rev


def resumir_texto(texto: str) -> str:
    lines = [ln.strip() for ln in texto.split("\n") if ln.strip()]
    lines = [ln for ln in lines if len(ln) > 10
             and not re.match(r"^(oflcio|processo|interessado|assunto|n[°º]|data|página)", ln, re.I)]
    return " | ".join(lines[:5]) if lines else "(texto muito curto)"


def main() -> None:
    hoje = date.today().strftime("%d%m%Y")
    relatorio: list[str] = []
    relatorio.append(f"# Revisão das Informações de Luzenildo — {hoje}")
    relatorio.append(f"\nProcessos analisados: **{len(PROCESSOS_LUZENILDO)}**\n")
    relatorio.append("---\n")

    total_problemas = 0
    processos_com_info = 0
    erros = 0

    for processo in PROCESSOS_LUZENILDO:
        print(f"📄 {processo}...", end=" ", flush=True)

        try:
            df = get_informacoes_processo(processo)
        except Exception as e:
            print(f"ERRO: {e}")
            erros += 1
            relatorio.append(f"## {processo}")
            relatorio.append(f"\n❌ Erro: {e}\n")
            relatorio.append("---\n")
            continue

        if df.empty:
            print("sem dados")
            relatorio.append(f"## {processo}")
            relatorio.append("\nℹ️ Nenhuma informação no banco.\n")
            relatorio.append("---\n")
            continue

        # Filtra por CPF de Luzenildo (informacao_efetuada_por)
        col_resp = "informacao_efetuada_por"
        if col_resp not in df.columns:
            print("coluna responsável não encontrada")
            relatorio.append(f"## {processo}")
            relatorio.append(f"\nℹ️ Coluna '{col_resp}' não encontrada. Colunas: {list(df.columns)}\n")
            relatorio.append("---\n")
            continue

        df_luza = df[df[col_resp].astype(str).str.contains(LUIZENILDO_CPF, na=False)]
        if df_luza.empty:
            print("Luzenildo não encontrado")
            relatorio.append(f"## {processo}")
            relatorio.append("\nℹ️ Nenhuma informação de Luzenildo.\n")
            relatorio.append("---\n")
            continue

        # Última (maior evento)
        ultima = df_luza.sort_values("evento", ascending=False).iloc[0]
        texto = str(ultima.get("texto", "") or "").strip()
        evento = int(ultima.get("evento", 0))
        data = str(ultima.get("data_cadastro", "") or ultima.get("DataInclusao", "") or "")
        descricao = str(ultima.get("descricao", "") or ultima.get("resumo", "") or "")
        tipo = str(ultima.get("tipo_informacao", "") or ultima.get("nome_informacao", "") or "")

        if not texto:
            print(f"evento {evento}, PDF vazio")
            relatorio.append(f"## {processo}")
            relatorio.append(f"\n- **Evento:** {evento}")
            relatorio.append(f"\n- **Data:** {data}")
            relatorio.append(f"\n- **Tipo:** {tipo}")
            relatorio.append("\n\nℹ️ PDF sem texto extraível.\n")
            relatorio.append("---\n")
            continue

        processos_com_info += 1
        resumo = resumir_texto(texto)
        rev = revisar_texto(texto)

        print(f"evento {evento}, {rev['comprimento']} chars")

        relatorio.append(f"## {processo}")
        relatorio.append("")
        relatorio.append(f"- **Evento:** {evento}")
        relatorio.append(f"- **Data:** {data}")
        relatorio.append(f"- **Tipo:** {tipo}")
        relatorio.append(f"- **Descrição:** {descricao}")
        relatorio.append(f"- **Tamanho:** {rev['comprimento']} chars, {rev['paragrafos']} parágrafos")
        relatorio.append("")

        relatorio.append("### Resumo")
        relatorio.append("")
        relatorio.append(resumo)
        relatorio.append("")

        if rev["alertas"]:
            relatorio.append("### 📋 Padrões")
            relatorio.append("")
            for a in rev["alertas"]:
                relatorio.append(f"- {a}")
            relatorio.append("")

        if rev["problemas"]:
            total_problemas += len(rev["problemas"])
            relatorio.append("### ❌ Problemas")
            relatorio.append("")
            for p in rev["problemas"]:
                relatorio.append(f"- {p}")
            relatorio.append("")
        else:
            relatorio.append("### ✅ Ortografia")
            relatorio.append("")
            relatorio.append("Sem problemas ortográficos detectados.")
            relatorio.append("")

        if rev["sugestoes"]:
            relatorio.append("### 💡 Sugestões")
            relatorio.append("")
            for s in rev["sugestoes"]:
                relatorio.append(f"- {s}")
            relatorio.append("")

        relatorio.append("### Trecho")
        relatorio.append("")
        relatorio.append("```")
        relatorio.append(texto[:800])
        if len(texto) > 800:
            relatorio.append("...[truncado]")
        relatorio.append("```")
        relatorio.append("")
        relatorio.append("---")
        relatorio.append("")

    relatorio.append("## Sumário\n")
    relatorio.append(f"- Processos: {len(PROCESSOS_LUZENILDO)}")
    relatorio.append(f"- Com informação de Luzenildo: {processos_com_info}")
    relatorio.append(f"- Erros: {erros}")
    relatorio.append(f"- Problemas ortográficos: {total_problemas}\n")

    out_dir = Path(__file__).resolve().parent.parent / "docs" / "revisoes" / f"revisao_luzenildo_{hoje}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "resumo_revisao.md"
    out_path.write_text("\n".join(relatorio), encoding="utf-8")
    print(f"\n✅ Relatório salvo em: {out_path}")


if __name__ == "__main__":
    main()