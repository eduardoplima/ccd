"""Ingestão de pasta MMYYYY.txt → DataFrame canônico."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from frap.extratos import classifica as _classifica
from frap.extratos import extrator_pessoa, parser, parser_pdf

_PERIODO_PATTERN = re.compile(r"^(\d{6})\.txt$")


class ExtratoInvalido(ValueError):
    """Arquivo de extrato reprovado nas validações de ingestão."""


def _valida_conta(df: pd.DataFrame, conta: str) -> None:
    for periodo, grupo in df.groupby("periodo"):
        _valida_periodo(grupo, str(periodo), conta)
        _valida_saldo(grupo, str(periodo), conta)


def _valida_periodo(grupo: pd.DataFrame, periodo: str, conta: str) -> None:
    """Movimentos devem cair no MM/AAAA do nome do arquivo.

    A exportação do BB às vezes devolve outro período com o nome pedido (visto em
    4 arquivos reais), e o cabeçalho "Período do extrato" do arquivo também mente —
    por isso a checagem é pelas datas dos movimentos.
    """
    mov = grupo[grupo["valor"].notna() & (grupo["categoria"] != _classifica.Categoria.SALDO.value)]
    datas = mov["dt_movimento"].dropna()
    if datas.empty:
        return
    fora = float((datas.dt.strftime("%m%Y") != periodo).mean())
    if fora > 0.5:
        raise ExtratoInvalido(
            f"{conta}/{periodo}: {fora:.0%} dos movimentos fora do período do nome do arquivo "
            f"(conteúdo {datas.min():%d/%m/%Y}..{datas.max():%d/%m/%Y}) — exportação errada do BB?"
        )


def _valida_saldo(grupo: pd.DataFrame, periodo: str, conta: str) -> None:
    """saldo anterior + Σ(movimentos assinados) deve bater com a linha final de saldo.

    Detecta linhas duplicadas/perdidas dentro do arquivo. Nos .txt o saldo anterior
    vem da coluna Saldo (`saldo`); nos .pdf, do `valor` da linha "SALDO ANTERIOR".
    Sem as duas linhas marcadoras, a checagem é pulada.
    """
    def _sig(v: float, dc: str) -> float:
        return v if (dc or "C") == "C" else -v

    g = grupo.sort_values("ordem_no_arquivo")
    marcas = g[g["categoria"] == _classifica.Categoria.SALDO.value]
    ant = marcas[marcas["historico"].str.lower().str.contains("anterior")]
    fim = marcas[~marcas.index.isin(ant.index) & marcas["valor"].notna()]
    if ant.empty or fim.empty:
        return
    r_ant = ant.iloc[0]
    if "saldo" in g.columns and pd.notna(r_ant.get("saldo")):
        saldo_ant = _sig(float(r_ant["saldo"]), r_ant.get("saldo_dc"))
    elif pd.notna(r_ant["valor"]):
        saldo_ant = _sig(float(r_ant["valor"]), r_ant["valor_dc"])
    else:
        return
    r_fim = fim.iloc[-1]
    saldo_fim = _sig(float(r_fim["valor"]), r_fim["valor_dc"])

    mov = g[g["valor"].notna() & (g["categoria"] != _classifica.Categoria.SALDO.value)]
    total = sum(_sig(float(r.valor), r.valor_dc) for r in mov.itertuples())
    if abs(saldo_ant + total - saldo_fim) > 0.01:
        raise ExtratoInvalido(
            f"{conta}/{periodo}: saldo não fecha (anterior {saldo_ant:.2f} + movimentos {total:.2f} "
            f"= {saldo_ant + total:.2f} ≠ saldo final {saldo_fim:.2f}) — "
            f"possíveis linhas duplicadas/faltantes no arquivo"
        )


def _enriquece(df: pd.DataFrame, conta: str) -> pd.DataFrame:
    """Deriva as colunas canônicas (datas, doc_data, seq_bb, categoria, cpfcnpj).

    Compartilhado por `ingest_conta` (.txt) e `ingest_pdf_conta` (.pdf) — ambos
    produzem as mesmas colunas brutas, só muda o parser de origem.
    """
    df = df.copy()
    df["conta"] = conta
    df["dt_movimento"] = pd.to_datetime(df["dt_movimento"], errors="coerce", dayfirst=True)
    df["dt_balancete"] = pd.to_datetime(df["dt_balancete"], errors="coerce", dayfirst=True)
    df["doc_data"] = df["documento"].apply(_extrai_doc_data)
    df["seq_bb"] = df["documento"].apply(_extrai_seq_bb)
    df["categoria"] = df["historico"].apply(lambda h: _classifica.classifica(h).value)

    extracoes = df["descricao"].apply(extrator_pessoa.extrai_cpfcnpj)
    df["cpfcnpj_depositante"] = extracoes.apply(lambda t: t[0])
    df["cpfcnpj_ambiguo"] = extracoes.apply(lambda t: t[1])
    return df


def ingest_conta(pasta_conta: Path, conta: str) -> pd.DataFrame:
    """Lê todos os MMYYYY.txt de uma pasta-conta e devolve DataFrame canônico."""
    parts: list[pd.DataFrame] = []
    for arquivo in sorted(pasta_conta.glob("*.txt")):
        m = _PERIODO_PATTERN.match(arquivo.name)
        if not m:
            continue
        df = parser.parse_extrato(arquivo)
        if df.empty:
            continue
        df["periodo"] = m.group(1)
        parts.append(df)
    if not parts:
        return pd.DataFrame()

    df = _enriquece(pd.concat(parts, ignore_index=True), conta)
    _valida_conta(df, conta)
    return df


def ingest_pdf_conta(pasta: Path, conta: str = "700000-6") -> pd.DataFrame:
    """Lê os extratos .pdf antigos (subpastas `<ano>/`, 1 PDF por mês) → canônico.

    O período (MMAAAA) vem do nome do arquivo (mês) + nome da subpasta (ano).
    PDFs ilegíveis (ex.: abril/2020 — fonte sem ToUnicode) devolvem 0 linhas e são
    pulados; trate-os à parte. Mesmas colunas de `ingest_conta`.
    """
    parts: list[pd.DataFrame] = []
    for ano_dir in sorted(p for p in pasta.iterdir() if p.is_dir()):
        for arquivo in sorted(ano_dir.glob("*.pdf")):
            periodo = parser_pdf.periodo_do_nome(arquivo.name, ano_dir.name)
            if periodo is None:
                continue
            df = parser_pdf.parse_extrato_pdf(arquivo)
            if df.empty:
                continue
            df["periodo"] = periodo
            parts.append(df)
    if not parts:
        return pd.DataFrame()

    df = _enriquece(pd.concat(parts, ignore_index=True), conta)
    _valida_conta(df, conta)
    return df


def ingest_pasta(base: Path) -> pd.DataFrame:
    """Itera as subpastas-conta de `base` e devolve um DataFrame canônico consolidado."""
    parts: list[pd.DataFrame] = []
    for conta_dir in sorted(p for p in base.iterdir() if p.is_dir()):
        df = ingest_conta(conta_dir, conta_dir.name)
        if not df.empty:
            parts.append(df)
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts, ignore_index=True)


def _extrai_doc_data(documento: str) -> pd.Timestamp | None:
    """Os 8 primeiros dígitos do `documento` (sem pontos) são YYYYMMDD."""
    if not documento:
        return None
    digitos = "".join(c for c in documento if c.isdigit())
    if len(digitos) < 8:
        return None
    return pd.to_datetime(digitos[:8], format="%Y%m%d", errors="coerce")


def _extrai_seq_bb(documento: str) -> str | None:
    """Últimos 7 dígitos do `documento` BB — autenticação sequencial do dia.
    Usado como chave de desempate quando há M OBs com mesma (data, valor)."""
    if not documento:
        return None
    digitos = "".join(c for c in documento if c.isdigit())
    if len(digitos) < 7:
        return None
    return digitos[-7:]
