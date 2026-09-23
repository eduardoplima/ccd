"""Gera o script T-SQL de INSERT das multas e ressarcimentos da CCD em BdBeneficio.dbo.Beneficio_PropostaBeneficio.

Lê o staging dbo.CCDBeneficio (BdDIP) — tipos 1 (Sanção/Multa) e 2 (Restituição/
Débito imputado), origens DEBITO (potencial) e BOLETO (efetivo) — com DataOcorrencia
nos anos pedidos, aplicando o mesmo filtro de validade da folha da cadeia de
web/backend/app/ccd/beneficios/tasks.py (débito cancelado/suspenso fica fora).

Consolidação (decisão de 23/09/2026): o staging BOLETO tem 1 linha por PARCELA paga;
aqui o grão é o DÉBITO (raiz da cadeia) — valor = soma das parcelas do período,
situação Efetivado Total se a folha tem dataBaixa, senão Parcial. Retorno bancário
importado em dobro (mesmo IdBoleto + NumeroAutenticacao) conta uma vez. Débito que
tem efetivo no período não sai também como potencial.

Saída: um INSERT por linha. NADA é executado aqui: só gera o .sql.

Uso: python -m scripts.automacao.beneficios_insert_multas [--anos 2025 2026] [--setor 762]
     python -m scripts.automacao.beneficios_insert_multas --self-check
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import text

from ccd.config import REPO_ROOT
from ccd.db import get_connection

ID_SETOR_CCD = 762  # processo.dbo.Setor: COORDENADORIA DE CONTROLE DE DECISÕES

# Espelho de tasks._CTE_CADEIA + tasks._FOLHA_VALIDA (não importável fora do venv do web/).
_SQL = """
WITH cadeia AS (
    SELECT r.IdDebito AS id_raiz, r.IdDebito AS id_no, 0 AS nivel
      FROM processo.dbo.Exe_Debito r WHERE r.IdDebitoAnterior IS NULL
    UNION ALL
    SELECT c.id_raiz, f.IdDebito, c.nivel + 1
      FROM cadeia c JOIN processo.dbo.Exe_Debito f ON f.IdDebitoAnterior = c.id_no
),
folhas AS (
    SELECT c.id_raiz, e.CodigoStatusDivida, e.DataCancelamento, e.dataBaixa,
           ROW_NUMBER() OVER (PARTITION BY c.id_raiz
                              ORDER BY c.nivel DESC, e.datainclusao DESC, e.IdDebito DESC) AS rn
      FROM cadeia c JOIN processo.dbo.Exe_Debito e ON e.IdDebito = c.id_no
     WHERE NOT EXISTS (SELECT 1 FROM processo.dbo.Exe_Debito g WHERE g.IdDebitoAnterior = e.IdDebito)
)
SELECT b.Origem, b.IdCCDBeneficio, nr.id_raiz, f.dataBaixa, rb.IdBoleto, rb.NumeroAutenticacao,
       b.DescricaoPropostaBeneficio, b.ValorQuantidade, b.IdBeneficioSituacaoEfetivacao,
       b.IdBeneficioSituacao, b.IdAreaTematica, b.IdCaracterizacaoBeneficio, b.IdTipoBeneficio,
       b.IdSubTipoBeneficio, b.NumeroProcessoDecisao, b.AnoProcessoDecisao
FROM dbo.CCDBeneficio b
JOIN cadeia nr ON nr.id_no = b.IdDebitoExecucao
JOIN folhas f ON f.id_raiz = nr.id_raiz AND f.rn = 1
LEFT JOIN processo.dbo.Exe_Retorno_Boleto rb ON CONCAT('BOLETO:', rb.IdRetornoBoleto) = b.ChaveOrigem
WHERE b.Ativo = 1 AND b.IdTipoBeneficio IN (1, 2) AND b.Origem IN ('DEBITO', 'BOLETO')
  AND YEAR(b.DataOcorrencia) IN ({anos})
  AND (b.Origem = 'BOLETO' OR (
        f.DataCancelamento IS NULL AND f.CodigoStatusDivida <> 20
        AND NOT EXISTS (SELECT 1 FROM processo.dbo.Exe_StatusDivida sd
                         WHERE sd.CodigoStatusDivida = f.CodigoStatusDivida AND sd.StatusCancelamento = 1)))
ORDER BY b.Origem, b.IdCCDBeneficio
OPTION (MAXRECURSION 100)
"""

_COLUNAS = (
    "DescricaoPropostaBeneficio, ValorQuantidade, ValorQuantidadeOriginal, "
    "IdBeneficioSituacaoEfetivacao, IdBeneficioSituacao, IdAreaTematica, IdCaracterizacaoBeneficio, "
    "IdTipoBeneficio, IdSubTipoBeneficio, NumeroProcessoDecisao, AnoProcessoDecisao, "
    "IdStatusBeneficio, IdSetorUsuarioCadastro, DataInclusao, IdSessao"
)


def _lit(v: object) -> str:
    if v is None:
        return "NULL"
    if isinstance(v, str):
        return "N'" + v.replace("'", "''") + "'"
    if isinstance(v, Decimal):
        return f"{v:.2f}"
    return str(v)


def consolidar(rows: list[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Staging (1 linha por parcela/potencial) -> 1 linha por débito (raiz da cadeia)."""
    vistos: set[tuple[Any, Any]] = set()
    efetivos: dict[Any, dict[str, Any]] = {}
    dup = 0
    for r in sorted(rows, key=lambda r: r["IdCCDBeneficio"]):
        if r["Origem"] != "BOLETO":
            continue
        chave = (r["IdBoleto"], r["NumeroAutenticacao"])
        if chave in vistos:
            dup += 1
            continue
        vistos.add(chave)
        e = efetivos.get(r["id_raiz"])
        if e is None:
            e = efetivos[r["id_raiz"]] = dict(r, parcelas=0, ValorQuantidade=Decimal(0))
            e["IdBeneficioSituacaoEfetivacao"] = 1  # Efetivo
            e["IdBeneficioSituacao"] = 3 if r["dataBaixa"] is not None else 2  # Total / Parcial
        e["parcelas"] += 1
        e["ValorQuantidade"] += Decimal(r["ValorQuantidade"])
    for e in efetivos.values():
        if e["parcelas"] > 1:
            e["DescricaoPropostaBeneficio"] += f" ({e['parcelas']} parcelas)"
    potenciais = [dict(r) for r in rows if r["Origem"] == "DEBITO"]
    absorvidos = sum(1 for p in potenciais if p["id_raiz"] in efetivos)
    saida = [p for p in potenciais if p["id_raiz"] not in efetivos] + list(efetivos.values())
    resumo = {
        "potenciais": len(potenciais) - absorvidos,
        "efetivos": len(efetivos),
        "parcelas": sum(e["parcelas"] for e in efetivos.values()),
        "retornos_em_dobro": dup,
        "potenciais_absorvidos": absorvidos,
    }
    return saida, resumo


def gerar(anos: list[int], id_setor: int) -> tuple[str, dict[str, int]]:
    sql = _SQL.format(anos=", ".join(str(int(a)) for a in anos))
    with get_connection("BdDIP").connect() as c:
        rows = c.execute(text(sql)).mappings().all()
    linhas, resumo = consolidar(list(rows))

    inserts = [
        f"INSERT INTO dbo.Beneficio_PropostaBeneficio ({_COLUNAS}) VALUES ("
        + ", ".join(
            [
                _lit(r["DescricaoPropostaBeneficio"]),
                _lit(r["ValorQuantidade"]),
                _lit(r["ValorQuantidade"]),
                _lit(r["IdBeneficioSituacaoEfetivacao"]),
                _lit(r["IdBeneficioSituacao"]),
                _lit(r["IdAreaTematica"]),
                _lit(r["IdCaracterizacaoBeneficio"]),
                _lit(r["IdTipoBeneficio"]),
                _lit(r["IdSubTipoBeneficio"]),
                _lit(r["NumeroProcessoDecisao"]),
                _lit(r["AnoProcessoDecisao"]),
                "1",  # IdStatusBeneficio: Cadastrado
                str(id_setor),
                "GETDATE()",
                "@IdSessao",
            ]
        )
        + ");"
        for r in linhas
    ]
    cabecalho = (
        f"-- Multas e ressarcimentos da CCD ({', '.join(map(str, anos))}) para o SisBenefícios — gerado por\n"
        f"-- scripts/automacao/beneficios_insert_multas.py em {date.today().isoformat()} a partir de\n"
        "-- BdDIP.dbo.CCDBeneficio (DEBITO=potencial, BOLETO=efetivo; tipo 1 Multa e tipo 2 Débito imputado;\n"
        "-- só débitos válidos pela folha da cadeia). Grão = débito: efetivo soma as parcelas do período\n"
        "-- (Total se baixado, senão Parcial); débito com efetivo não sai também como potencial.\n"
        f"-- {resumo['potenciais']} potenciais + {resumo['efetivos']} efetivos "
        f"({resumo['parcelas']} parcelas somadas, {resumo['retornos_em_dobro']} retornos em dobro descartados, "
        f"{resumo['potenciais_absorvidos']} potenciais absorvidos pelo efetivo).\n"
        "USE BdBeneficio;\n"
        "DECLARE @IdSessao int = NULL;  -- OBRIGATÓRIO: sessão de auditoria do SisBenefícios\n"
        f"-- IdSetorUsuarioCadastro = {id_setor} (processo.dbo.Setor: COORDENADORIA DE CONTROLE DE DECISÕES)\n\n"
    )
    return cabecalho + "\n".join(inserts) + "\n", resumo


def _self_check() -> None:
    def linha(id_, origem, raiz, valor, boleto=None, aut=None, baixa=None):
        return {
            "IdCCDBeneficio": id_, "Origem": origem, "id_raiz": raiz, "dataBaixa": baixa,
            "IdBoleto": boleto, "NumeroAutenticacao": aut, "DescricaoPropostaBeneficio": f"d{raiz}",
            "ValorQuantidade": Decimal(valor), "IdBeneficioSituacaoEfetivacao": 2 if origem == "DEBITO" else 1,
            "IdBeneficioSituacao": 1, "IdAreaTematica": 13, "IdCaracterizacaoBeneficio": 2,
            "IdTipoBeneficio": 1, "IdSubTipoBeneficio": 1, "NumeroProcessoDecisao": "1", "AnoProcessoDecisao": 2025,
        }  # fmt: skip

    rows = [
        linha(1, "DEBITO", 10, "300"),  # potencial absorvido (tem efetivo)
        linha(2, "DEBITO", 20, "500"),  # potencial que fica
        linha(3, "BOLETO", 10, "100", 1, "A", baixa=date(2026, 1, 1)),
        linha(4, "BOLETO", 10, "100", 1, "A", baixa=date(2026, 1, 1)),  # retorno em dobro
        linha(5, "BOLETO", 10, "100", 2, "B", baixa=date(2026, 1, 1)),
        linha(6, "BOLETO", 30, "50", 3, "C"),  # 1 parcela, débito aberto
    ]
    saida, resumo = consolidar(rows)
    assert [(r["Origem"], r["id_raiz"]) for r in saida] == [
        ("DEBITO", 20),
        ("BOLETO", 10),
        ("BOLETO", 30),
    ]
    e10, e30 = saida[1], saida[2]
    assert e10["ValorQuantidade"] == Decimal(200) and e10["IdBeneficioSituacao"] == 3
    assert (
        e10["DescricaoPropostaBeneficio"] == "d10 (2 parcelas)"
        and e10["IdBeneficioSituacaoEfetivacao"] == 1
    )
    assert e30["IdBeneficioSituacao"] == 2 and e30["DescricaoPropostaBeneficio"] == "d30"
    assert resumo == {
        "potenciais": 1, "efetivos": 2, "parcelas": 3, "retornos_em_dobro": 1, "potenciais_absorvidos": 1,
    }  # fmt: skip
    print("self-check OK")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--anos", nargs="+", type=int, default=[2025, 2026])
    ap.add_argument("--setor", type=int, default=ID_SETOR_CCD)
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()
    if args.self_check:
        _self_check()
        return
    script, resumo = gerar(args.anos, args.setor)
    out = REPO_ROOT / "saidas" / "automacao" / "beneficios"
    out.mkdir(parents=True, exist_ok=True)
    destino = out / f"insert_multas_ressarcimentos_{'_'.join(map(str, args.anos))}.sql"
    destino.write_text(script, encoding="utf-8")
    print(f"{destino}: {resumo}")


if __name__ == "__main__":
    main()
