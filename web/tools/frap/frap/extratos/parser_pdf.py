"""Parser dos extratos .pdf antigos do BB (conta atual).

Os extratos antigos (pré-2020) só existem em PDF, não nos .txt fixed-width que o
`parser.py` consome. Reusa o resto do pipeline: a saída tem as MESMAS colunas de
`parser.parse_extrato`, então `ingest._enriquece` + `persistencia.extrato.publica_extrato`
funcionam sem mudança.

Notas do formato (validadas em 46 meses):
- PDFs protegidos por senha (owner pw); `pypdf` lê com user-pw vazia.
- Lançamentos ocupam VÁRIAS páginas; páginas de continuação NÃO repetem o header
  "Dt. movimento" — por isso varremos todas as páginas e detectamos transações pela
  estrutura, não pelo header.
- `extraction_mode="layout"` é obrigatório: sem ele o pypdf cola "Documento" e "Valor".
- A página de "Investimentos Fundos" é a única com a palavra "cotas" — pulada (suas
  linhas com data senão entrariam como lançamento).
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

# Linha de transação: data_balancete [data_movimento] + ag(4) + lote(5) + cod(3) + resto.
# A 2ª data (movimento) só aparece em alguns meses; quando ausente, usa-se a 1ª p/ ambas.
# Tolerante a larguras 3-4/4-5/3 por segurança em meses não amostrados.
_FIELDS = re.compile(
    r"^(\d{2}/\d{2}/\d{4})(?:\s+(\d{2}/\d{2}/\d{4}))?\s+(\d{3,4})\s+(\d{4,5})\s+(\d{3})\s+(.*)$"
)
# Valor monetário com sufixo C/D. A 1ª ocorrência é o valor; a 2ª (se houver) é o saldo.
_VALOR = re.compile(r"([\d.]+,\d{2})\s+([CD])")
# Documento: blob numérico (com pontos/hífen) logo antes do valor.
_DOC = re.compile(r"\s(\d[\d.\-]*)$")
# Linhas de header/rodapé que se repetem nas páginas de continuação — NÃO são
# continuação de descrição (senão grudariam na última transação da página anterior).
_RUIDO = re.compile(
    r"Cliente|Ag[êe]ncia|Conta corrente|Per[íi]odo do extrato|Lan[çc]amentos"
    r"|Transa[çc][ãa]o efetuada|Servi[çc]o de Atendimento|Ouvidoria|deficientes"
    r"|Dt\. balancete|SAC 0800|^A33|^G\d{3}",
    re.IGNORECASE,
)

# Meses PT (abreviado e completo) → MM. Cobre os nomes variados dos arquivos.
_MESES = {
    "jan": "01", "fev": "02", "mar": "03", "abr": "04", "mai": "05", "jun": "06",
    "jul": "07", "ago": "08", "set": "09", "out": "10", "nov": "11", "dez": "12",
}


def _normaliza(s: str) -> str:
    n = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return n.lower().strip()


def periodo_do_nome(nome_arquivo: str, ano: str) -> str | None:
    """Deriva MMAAAA do nome do arquivo (1ª palavra = mês) + ano da pasta.

    Aceita 'Jan Extrato BB.pdf', 'Março Extrato BB.pdf', 'Agosto Extrato_700000-6.pdf'.
    """
    primeira = _normaliza(nome_arquivo).split()[0] if nome_arquivo.strip() else ""
    mm = _MESES.get(primeira[:3])
    return f"{mm}{ano}" if mm else None


def _parse_valor(s: str) -> float:
    return float(s.replace(".", "").replace(",", "."))


def parse_extrato_pdf(filepath: str | Path) -> pd.DataFrame:
    """Lê os lançamentos da página 1 do extrato PDF do BB.

    Colunas iguais às de `parser.parse_extrato`: ordem_no_arquivo, dt_movimento,
    dt_balancete, ag_origem, lote, historico, documento, valor, valor_dc,
    descricao. Linhas sem data são continuação da `descricao` da transação
    anterior (nome/CPF do depositante) — TODAS são concatenadas, nada se perde.
    """
    reader = PdfReader(str(filepath))
    records: list[dict] = []
    for page in reader.pages:
        texto = page.extract_text(extraction_mode="layout") or ""
        linhas = texto.splitlines()
        # Página de lançamentos = tem ≥1 linha-transação. Investimentos/rodapé não
        # têm (suas linhas começam com data mas seguem "APLICAÇÃO"/"SALDO ANTERIOR",
        # sem ag/lote/cod) — descartadas (mais robusto que procurar "cotas").
        if not any(_FIELDS.match(ln.strip()) for ln in linhas):
            continue
        stopped = False
        for line in linhas:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("---") or "OBSERVA" in stripped.upper():
                stopped = True  # fim dos lançamentos desta página
                continue
            if stopped:
                continue
            m = _FIELDS.match(stripped)
            if m:
                records.append({"line": m, "descricao": []})
            elif records and not _RUIDO.search(stripped):
                records[-1]["descricao"].append(stripped)

    parsed: list[dict] = []
    for ordem, rec in enumerate(records, start=1):
        balancete, movimento, ag, lote, _cod, resto = rec["line"].groups()
        dt_balancete = balancete
        dt_movimento = movimento or balancete

        valor: float | None = None
        valor_dc = ""
        documento = ""
        historico = resto.strip()

        vm = _VALOR.search(resto)
        if vm:
            valor = _parse_valor(vm.group(1))
            valor_dc = vm.group(2)
            head = resto[: vm.start()].strip()
            dm = _DOC.search(head)
            if dm:
                documento = dm.group(1)
                historico = head[: dm.start()]
            else:
                historico = head
        historico = re.sub(r"\s+", " ", historico).strip()

        parsed.append({
            "ordem_no_arquivo": ordem,
            "dt_movimento": dt_movimento,
            "dt_balancete": dt_balancete,
            "ag_origem": ag,
            "lote": lote,
            "historico": historico,
            "documento": documento,
            "valor": valor,
            "valor_dc": valor_dc,
            "descricao": " ".join(rec["descricao"]),
        })

    return pd.DataFrame(parsed)


def saldo_reconcilia(df: pd.DataFrame) -> tuple[float, float]:
    """(saldo_anterior, saldo_fim) do mês, p/ checar a cadeia entre meses.

    saldo_fim = saldo_anterior + Σ(valor·sinal) sobre transações, excluindo as
    linhas marcadoras `SALDO`. Invariante: saldo_fim[m] == saldo_anterior[m+1].
    """
    def _is_saldo(h: str) -> bool:
        h = h.lower()
        return "saldo" in h or "s a l d o" in h

    def _signed(v, dc):
        v = v or 0.0
        return v if dc == "C" else -v

    sal = df[df["historico"].apply(_is_saldo)]
    ant = _signed(sal.iloc[0]["valor"], sal.iloc[0]["valor_dc"]) if len(sal) else 0.0
    mov = sum(
        _signed(r.valor, r.valor_dc)
        for r in df.itertuples()
        if not _is_saldo(r.historico)
    )
    return round(ant, 2), round(ant + mov, 2)


if __name__ == "__main__":  # smoke check: python -m frap.extratos.parser_pdf <pdf>
    import sys

    df = parse_extrato_pdf(sys.argv[1])
    ant, fim = saldo_reconcilia(df)
    print(f"{len(df)} lançamentos | saldo_anterior={ant} saldo_fim={fim}")
    assert not df.empty, "0 lançamentos — PDF ilegível ou layout inesperado"
    assert df["valor"].notna().all(), "linha sem valor — parser falhou"
