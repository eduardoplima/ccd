"""Gera o script T-SQL de INSERT das multas e ressarcimentos da CCD em BdBeneficio.dbo.Beneficio_PropostaBeneficio.

Lê o staging dbo.CCDBeneficio (BdDIP) — tipos 1 (Sanção/Multa) e 2 (Restituição/
Débito imputado), origens DEBITO (potencial) e BOLETO (efetivo) — com DataOcorrencia
nos anos pedidos, aplicando o mesmo filtro de validade da folha da cadeia de
web/backend/app/ccd/beneficios/tasks.py (débito cancelado/suspenso fica fora).

O grão já vem consolidado do staging (decisão de 23/09/2026, migração 0029): 1 linha
por DÉBITO (raiz da cadeia). O efetivo soma as parcelas pagas (MemoriaCalculo traz o
nº de parcelas e o período), situação Efetivado Total se a folha tem dataBaixa, senão
Parcial; retorno bancário em dobro conta uma vez; débito com efetivo não sai também
como potencial (absorvido pela detecção). DataOcorrencia = data do ACÓRDÃO da raiz
(Exe_Debito.dataDecisao) nas duas origens — cada multa é ligada a um acórdão e é ele o
parâmetro temporal de --anos (migração 0030).

Saída: um INSERT por linha. NADA é executado aqui: só gera o .sql.

Uso: python -m scripts.automacao.beneficios_insert_multas [--anos 2025 2026] [--setor 762]
"""

from __future__ import annotations

import argparse
from datetime import date
from decimal import Decimal

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
    SELECT c.id_raiz, e.CodigoStatusDivida, e.DataCancelamento,
           ROW_NUMBER() OVER (PARTITION BY c.id_raiz
                              ORDER BY c.nivel DESC, e.datainclusao DESC, e.IdDebito DESC) AS rn
      FROM cadeia c JOIN processo.dbo.Exe_Debito e ON e.IdDebito = c.id_no
     WHERE NOT EXISTS (SELECT 1 FROM processo.dbo.Exe_Debito g WHERE g.IdDebitoAnterior = e.IdDebito)
)
SELECT b.DescricaoPropostaBeneficio, b.MemoriaCalculoPropostaBeneficio, b.ValorQuantidade,
       b.IdBeneficioSituacaoEfetivacao, b.IdBeneficioSituacao, b.IdAreaTematica,
       b.IdCaracterizacaoBeneficio, b.IdTipoBeneficio, b.IdSubTipoBeneficio,
       b.NumeroProcessoDecisao, b.AnoProcessoDecisao
FROM dbo.CCDBeneficio b
JOIN folhas f ON f.id_raiz = b.IdDebitoExecucao AND f.rn = 1
WHERE b.Ativo = 1 AND b.IdTipoBeneficio IN (1, 2) AND b.Origem IN ('DEBITO', 'BOLETO')
  AND YEAR(b.DataOcorrencia) IN ({anos})
  AND (b.Origem = 'BOLETO' OR (
        f.DataCancelamento IS NULL AND f.CodigoStatusDivida <> 20
        AND NOT EXISTS (SELECT 1 FROM processo.dbo.Exe_StatusDivida sd
                         WHERE sd.CodigoStatusDivida = f.CodigoStatusDivida AND sd.StatusCancelamento = 1)))
ORDER BY b.IdBeneficioSituacaoEfetivacao DESC, b.IdDebitoExecucao
OPTION (MAXRECURSION 100)
"""

_COLUNAS = (
    "DescricaoPropostaBeneficio, MemoriaCalculoPropostaBeneficio, ValorQuantidade, "
    "ValorQuantidadeOriginal, IdBeneficioSituacaoEfetivacao, IdBeneficioSituacao, IdAreaTematica, "
    "IdCaracterizacaoBeneficio, IdTipoBeneficio, IdSubTipoBeneficio, NumeroProcessoDecisao, "
    "AnoProcessoDecisao, IdStatusBeneficio, IdSetorUsuarioCadastro, DataInclusao, IdSessao"
)


def _lit(v: object) -> str:
    if v is None:
        return "NULL"
    if isinstance(v, str):
        return "N'" + v.replace("'", "''") + "'"
    if isinstance(v, Decimal):
        return f"{v:.2f}"
    return str(v)


def gerar(anos: list[int], id_setor: int) -> tuple[str, dict[str, int]]:
    sql = _SQL.format(anos=", ".join(str(int(a)) for a in anos))
    with get_connection("BdDIP").connect() as c:
        rows = c.execute(text(sql)).mappings().all()

    inserts = [
        f"INSERT INTO dbo.Beneficio_PropostaBeneficio ({_COLUNAS}) VALUES ("
        + ", ".join(
            [
                _lit(r["DescricaoPropostaBeneficio"]),
                _lit(r["MemoriaCalculoPropostaBeneficio"]),
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
        for r in rows
    ]
    n_pot = sum(1 for r in rows if r["IdBeneficioSituacaoEfetivacao"] == 2)
    resumo = {"potenciais": n_pot, "efetivos": len(rows) - n_pot}
    cabecalho = (
        f"-- Multas e ressarcimentos da CCD com acórdão em {', '.join(map(str, anos))} para o SisBenefícios — gerado por\n"
        f"-- scripts/automacao/beneficios_insert_multas.py em {date.today().isoformat()} a partir de\n"
        "-- BdDIP.dbo.CCDBeneficio (DEBITO=potencial, BOLETO=efetivo; tipo 1 Multa e tipo 2 Débito imputado;\n"
        "-- só débitos válidos pela folha da cadeia). Grão = débito: o efetivo soma as parcelas pagas\n"
        "-- (Total se baixado, senão Parcial) e absorve o potencial da mesma multa.\n"
        f"-- {n_pot} potenciais + {len(rows) - n_pot} efetivos.\n"
        "USE BdBeneficio;\n"
        "DECLARE @IdSessao int = NULL;  -- OBRIGATÓRIO: sessão de auditoria do SisBenefícios\n"
        f"-- IdSetorUsuarioCadastro = {id_setor} (processo.dbo.Setor: COORDENADORIA DE CONTROLE DE DECISÕES)\n\n"
    )
    return cabecalho + "\n".join(inserts) + "\n", resumo


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--anos", nargs="+", type=int, default=[2025, 2026])
    ap.add_argument("--setor", type=int, default=ID_SETOR_CCD)
    args = ap.parse_args()
    script, resumo = gerar(args.anos, args.setor)
    out = REPO_ROOT / "saidas" / "automacao" / "beneficios"
    out.mkdir(parents=True, exist_ok=True)
    destino = out / f"insert_multas_ressarcimentos_{'_'.join(map(str, args.anos))}.sql"
    destino.write_text(script, encoding="utf-8")
    print(f"{destino}: {resumo}")


if __name__ == "__main__":
    main()
