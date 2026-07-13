"""Gera o despacho de MS (mandado de segurança) para os 10 processos fixos
do tema Nereu/Renato.

Consulta o banco `processo` pelos processos do setor CCD dentre a lista fixa
abaixo e, para cada um, renderiza
`templates/modelo_nereu_ms/modelo_nereu.docx` com as variáveis `processo`,
`relator`, `tratamento`, `resumo_debitos`, `debitos` (linhas da tabela),
`posicao` e `sobrestamento`, salvando `.docx` e `.pdf` em `saidas/nereu_ms/`.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd
from docxtpl import DocxTemplate

from ccd.db import run_query_df
from ccd.docs import docx_to_pdf
from ccd.pdf import merge_pdfs
from scripts.analise.gerar_debitos_nereu_02072026 import _conselheiro, build_enriched_df

SETOR = "CCD"

# conselheiras (tratamento no feminino no despacho); demais no masculino.
RELATORAS = {"ana", "maria"}


def _tratamento(relator) -> str:
    """'à Exma. Relatora' para conselheiras, 'ao Exmo. Relator' para os demais."""
    return "à Exma. Relatora" if _conselheiro(relator) in RELATORAS else "ao Exmo. Relator"

# Processos do Nereu na CCD alcançados pelo Acórdão do MS (débitos SESAP / verba
# transitória, sem cancelados) + os 10 originais. Número = processo que está de fato
# na CCD (execução quando existe, senão origem). Gerado por scratchpad/lista.py.
PROCESSOS = [
    "000094/2023", "000096/2023", "000099/2023", "000100/2023", "000103/2023",
    "000106/2023", "000117/2023", "000120/2023", "000146/2023", "000501/2016",
    "001368/2022", "001390/2023", "001391/2023", "001416/2023", "001417/2023",
    "001418/2023", "001420/2023", "001423/2023", "001843/2025", "001844/2017",
    "001846/2017", "001851/2017", "001855/2025", "001859/2025", "002037/2024",
    "002039/2024", "002041/2024", "002155/2025", "002159/2025", "002162/2025",
    "002164/2025", "002560/2024", "002564/2024", "002681/2022", "002683/2022",
    "002684/2022", "002685/2022", "002729/2022", "002738/2022", "002745/2022",
    "002746/2022", "002756/2022", "003066/2022", "003070/2022", "003073/2022",
    "003074/2022", "003077/2022", "003079/2022", "003080/2022", "003094/2017",
    "003112/2017", "003147/2017", "003230/2017", "003412/2024", "003457/2017",
    "003511/2017", "003515/2017", "003661/2022", "003663/2022", "003666/2022",
    "003673/2022", "003691/2022", "003790/2017", "004625/2016", "004658/2016",
    "005725/2016", "006181/2017", "008119/2017", "008943/2017",
    "008945/2017", "011144/2016", "011525/2009", "012521/2016", "012695/2016",
    "014147/2017", "015121/2016", "017208/2017", "018116/2017", "018142/2015",
    "018209/2017", "018929/2016", "019239/2016", "019247/2016", "022595/2016",
    "024989/2016", "025269/2016", "026373/2016", "100010/2019", "100730/2019",
    "100825/2019", "101026/2019", "102485/2018",
]

BASE_DIR = Path(__file__).resolve().parent
MODELO_DIR = BASE_DIR / "templates" / "modelo_nereu_ms"
TEMPLATE_PATH = MODELO_DIR / "modelo_nereu.docx"
ACORDAO_PDF = MODELO_DIR / "ACÓRDÃO_29.06.2026_Concessão da segurança.pdf"
OUT_DIR = BASE_DIR / "saidas" / "nereu_ms"


def fetch_processos() -> pd.DataFrame:
    placeholders = {f"p{i}": numero for i, numero in enumerate(PROCESSOS)}
    in_clause = ", ".join(f":{key}" for key in placeholders)
    sql = f"""
    SELECT
        CONCAT(pro.numero_processo, '/', pro.ano_processo) AS processo,
        pro.assunto,
        rel.nome AS relator
    FROM dbo.Processos pro
    INNER JOIN dbo.Relator rel ON pro.codigo_relator = rel.codigo
    WHERE pro.setor_atual = :setor
      AND CONCAT(pro.numero_processo, '/', pro.ano_processo) IN ({in_clause})
    """
    return run_query_df(sql, setor=SETOR, **placeholders)


def _chave(n, a) -> str:
    """('7433', '2005') -> '007433/2005'; vazio -> ''."""
    n, a = str(n).strip(), str(a).strip()
    if not n or not a:
        return ""
    try:
        return f"{int(n):06d}/{a}"
    except ValueError:
        return f"{n}/{a}"


def status_por_processo(df: pd.DataFrame) -> dict[str, str]:
    """Mapeia cada processo (origem e execução) -> pasta de status, priorizando
    dívida ativa > protesto > não enviados, a partir dos débitos do Nereu."""
    da = df["dívida ativa"].astype(str).str.strip() != "Sem envio à Dívida Ativa"
    pr = df["protesto"].astype(str).str.strip() != "Sem Protesto"

    acc: dict[str, dict[str, bool]] = {}
    for i in range(len(df)):
        r = df.iloc[i]
        for p in (_chave(r["nprocorig"], r["anoprocorig"]), _chave(r["nprocexe"], r["anoprocexe"])):
            if not p:
                continue
            s = acc.setdefault(p, {"da": False, "pr": False})
            s["da"] |= bool(da.iloc[i])
            s["pr"] |= bool(pr.iloc[i])
    return {
        p: "divida_ativa" if s["da"] else "protesto" if s["pr"] else "nao_enviados"
        for p, s in acc.items()
    }


def _moeda(v) -> str:
    """1234.5 -> 'R$ 1.234,50'."""
    return "R$ " + f"{float(v):,.2f}".replace(",", "\0").replace(".", ",").replace("\0", ".")


POSICAO = "02/07/2026"  # data da planilha debitos_nereu_02072026
EXTENSO = {1: "um", 2: "dois", 3: "três", 4: "quatro", 5: "cinco"}

SOBRESTADO_SIM = (
    "Registre-se, ainda, que o presente processo já havia sido sobrestado "
    "anteriormente, por determinação do Relator."
)
SOBRESTADO_NAO = (
    "Registre-se, ainda, que o presente processo não havia sido objeto de "
    "sobrestamento determinado pelo Relator."
)


def fetch_sobrestados() -> set[str]:
    """Processos da lista que têm (ou tiveram) marcador de sobrestamento."""
    placeholders = {f"p{i}": numero for i, numero in enumerate(PROCESSOS)}
    in_clause = ", ".join(f":{key}" for key in placeholders)
    sql = f"""
    SELECT DISTINCT
        CONCAT(RIGHT('000000' + CAST(mp.Numero_Processo AS varchar), 6), '/', mp.Ano_Processo) AS processo
    FROM dbo.Pro_MarcadorProcesso mp
    INNER JOIN dbo.Pro_Marcador m ON m.IdMarcador = mp.IdMarcador
    WHERE m.Descricao LIKE :sobrestado
      AND CONCAT(RIGHT('000000' + CAST(mp.Numero_Processo AS varchar), 6), '/', mp.Ano_Processo) IN ({in_clause})
    """
    df = run_query_df(sql, sobrestado="%sobrest%", **placeholders)
    return set(df["processo"]) if not df.empty else set()


def _linha_debito(r) -> dict[str, str]:
    """Uma linha da tabela de débitos do despacho."""
    return {
        "valor_original": _moeda(r["valor original"]),
        "valor_atualizado": _moeda(r["valor atualizado"]),
        "situacao": str(r["situação do débito"]).strip(),
        "desconto": str(r["desconto em folha"]).strip(),
        "divida_ativa": str(r["dívida ativa"]).strip(),
        "protesto": str(r["protesto"]).strip(),
    }


def debitos_por_processo(df: pd.DataFrame) -> dict[str, dict]:
    """Por processo: frase-resumo ('Ressalta-se que o presente processo ...')
    e linhas da tabela de débitos (mesma seleção do texto corrido anterior:
    débitos ativos; se só houver cancelados, mostra os cancelados)."""
    grupos: dict[str, dict[int, pd.Series]] = {}
    for i in range(len(df)):
        r = df.iloc[i]
        for p in (_chave(r["nprocorig"], r["anoprocorig"]), _chave(r["nprocexe"], r["anoprocexe"])):
            if p:
                grupos.setdefault(p, {})[int(r["id_debito"])] = r  # dedup por id_debito

    detalhes: dict[str, dict] = {}
    for p, debitos in grupos.items():
        ativos = [r for r in debitos.values()
                  if not str(r["situação do débito"]).strip().startswith("Cancelada")]
        if not ativos:
            n = len(debitos)
            resumo = (
                "possui apenas débito cancelado por erro de cadastro, sem valor "
                "exigível, conforme detalhado no quadro a seguir:"
                if n == 1
                else "possui apenas débitos cancelados por erro de cadastro, sem valor "
                "exigível, conforme detalhado no quadro a seguir:"
            )
            linhas = [_linha_debito(r) for r in debitos.values()]
        else:
            n = len(ativos)
            plural = "s" if n > 1 else ""
            resumo = (
                f"possui {n} ({EXTENSO[n]}) débito{plural} cadastrado{plural} em desfavor "
                "do responsável, conforme detalhado no quadro a seguir:"
            )
            linhas = [_linha_debito(r) for r in ativos]
        detalhes[p] = {"resumo": resumo, "linhas": linhas}
    return detalhes


def _estilizar_tabela(doc: DocxTemplate) -> None:
    """Linhas zebradas da tabela de débitos (identidade visual TCE/RN); o
    cabeçalho verde e as bordas já vêm prontos do modelo."""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    # doc.docx direto: get_docx() recarregaria o template, descartando o render
    for tabela in doc.docx.tables:
        for i, row in enumerate(tabela.rows[1:]):
            if i % 2 != 0:
                continue  # pares (0-based ímpares) ficam brancas
            for cell in row.cells:
                shd = OxmlElement("w:shd")
                shd.set(qn("w:val"), "clear")
                shd.set(qn("w:fill"), "F2F2F2")
                cell._tc.get_or_add_tcPr().append(shd)


def main() -> None:
    df = fetch_processos()

    encontrados = set(df["processo"]) if not df.empty else set()
    faltando = [p for p in PROCESSOS if p not in encontrados]
    if faltando:
        print(
            f"Aviso: {len(faltando)} processo(s) não encontrados no setor {SETOR}: "
            f"{', '.join(faltando)}"
        )

    if df.empty:
        print("Nenhum processo encontrado no setor CCD.")
        return

    debitos = build_enriched_df()
    status = status_por_processo(debitos)
    detalhes = debitos_por_processo(debitos)
    sobrestados = fetch_sobrestados()
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)  # recria a árvore <relator>/<status>/ do zero
    for row in df.itertuples():
        if row.processo not in detalhes:
            print(f"Aviso: {row.processo} sem débito na planilha do Nereu — pulado.")
            continue
        st = status.get(row.processo, "nao_enviados")
        out = OUT_DIR / _conselheiro(row.relator) / st
        out.mkdir(parents=True, exist_ok=True)
        doc = DocxTemplate(str(TEMPLATE_PATH))
        doc.render({
            "processo": row.processo,
            "relator": row.relator,
            "tratamento": _tratamento(row.relator),
            "resumo_debitos": detalhes[row.processo]["resumo"],
            "debitos": detalhes[row.processo]["linhas"],
            "posicao": POSICAO,
            "sobrestamento": SOBRESTADO_SIM if row.processo in sobrestados else SOBRESTADO_NAO,
        })
        _estilizar_tabela(doc)
        nome_arq = row.processo.replace("/", "_")
        doc_path = out / f"{nome_arq}.docx"
        doc.save(str(doc_path))
        docx_to_pdf(str(doc_path), str(out))
        pdf_path = out / f"{nome_arq}.pdf"
        merge_pdfs([pdf_path, ACORDAO_PDF], pdf_path)  # anexa o acórdão ao fim
        print(f"Gerado: {row.processo} -> {_conselheiro(row.relator)}/{st}")

    print(f"{len(df)} despacho(s) gerado(s) em {OUT_DIR}")


if __name__ == "__main__":
    main()
