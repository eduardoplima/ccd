"""Gera o script T-SQL de INSERT das multas da CCD em BdBeneficio.dbo.Beneficio_PropostaBeneficio.

Lê o staging dbo.CCDBeneficio (BdDIP) — tipo 1 (Sanção/Multa), origens DEBITO
(potencial) e BOLETO (efetivo) — com DataOcorrencia nos anos pedidos, aplicando
o mesmo filtro de validade da folha da cadeia de web/backend/app/ccd/beneficios/tasks.py
(débito cancelado/suspenso fica fora). O efetivo é vinculado ao potencial do
mesmo débito (raiz da cadeia) via IdBeneficioAnterior, resolvido no próprio
script com MERGE ... OUTPUT. NADA é executado aqui: só gera o .sql.

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
SELECT b.IdCCDBeneficio, b.Origem, nr.id_raiz, b.DescricaoPropostaBeneficio, b.ValorQuantidade,
       b.IdBeneficioSituacaoEfetivacao, b.IdBeneficioSituacao, b.IdAreaTematica,
       b.IdCaracterizacaoBeneficio, b.IdTipoBeneficio, b.IdSubTipoBeneficio,
       b.NumeroProcessoDecisao, b.AnoProcessoDecisao, b.DataOcorrencia
FROM dbo.CCDBeneficio b
JOIN cadeia nr ON nr.id_no = b.IdDebitoExecucao
JOIN folhas f ON f.id_raiz = nr.id_raiz AND f.rn = 1
WHERE b.Ativo = 1 AND b.IdTipoBeneficio = 1 AND b.Origem IN ('DEBITO', 'BOLETO')
  AND YEAR(b.DataOcorrencia) IN ({anos})
  AND (b.Origem = 'BOLETO' OR (
        f.DataCancelamento IS NULL AND f.CodigoStatusDivida <> 20
        AND NOT EXISTS (SELECT 1 FROM processo.dbo.Exe_StatusDivida sd
                         WHERE sd.CodigoStatusDivida = f.CodigoStatusDivida AND sd.StatusCancelamento = 1)))
ORDER BY b.IdBeneficioSituacaoEfetivacao DESC, b.DataOcorrencia, b.IdCCDBeneficio
OPTION (MAXRECURSION 100)
"""

_COLS_LOTE = (
    "IdInterno, IdInternoAnterior, DescricaoPropostaBeneficio, ValorQuantidade, "
    "IdBeneficioSituacaoEfetivacao, IdBeneficioSituacao, IdAreaTematica, IdCaracterizacaoBeneficio, "
    "IdTipoBeneficio, IdSubTipoBeneficio, NumeroProcessoDecisao, AnoProcessoDecisao, DataOcorrencia"
)
_COLS_DESTINO = (
    "DescricaoPropostaBeneficio, ValorQuantidade, ValorQuantidadeOriginal, "
    "IdBeneficioSituacaoEfetivacao, IdBeneficioSituacao, IdAreaTematica, IdCaracterizacaoBeneficio, "
    "IdTipoBeneficio, IdSubTipoBeneficio, NumeroProcessoDecisao, AnoProcessoDecisao, "
    "IdStatusBeneficio, IdSetorUsuarioCadastro, DataInclusao, IdSessao, IdBeneficioAnterior"
)
_VALS_DESTINO = (
    "s.DescricaoPropostaBeneficio, s.ValorQuantidade, s.ValorQuantidade, "
    "s.IdBeneficioSituacaoEfetivacao, s.IdBeneficioSituacao, s.IdAreaTematica, s.IdCaracterizacaoBeneficio, "
    "s.IdTipoBeneficio, s.IdSubTipoBeneficio, s.NumeroProcessoDecisao, s.AnoProcessoDecisao, "
    "1, @IdSetor, GETDATE(), @IdSessao, s.IdBeneficioAnterior"
)


def _lit(v: object) -> str:
    if v is None:
        return "NULL"
    if isinstance(v, str):
        return "N'" + v.replace("'", "''") + "'"
    if isinstance(v, date):
        return f"'{v.isoformat()}'"
    if isinstance(v, Decimal):
        return f"{v:.2f}"
    return str(v)


def gerar(anos: list[int], id_setor: int) -> tuple[str, dict[str, int]]:
    sql = _SQL.format(anos=", ".join(str(int(a)) for a in anos))
    with get_connection("BdDIP").connect() as c:
        rows = [dict(r) for r in c.execute(text(sql)).mappings()]

    potencial_por_raiz = {
        r["id_raiz"]: r["IdCCDBeneficio"] for r in rows if r["Origem"] == "DEBITO"
    }
    valores = []
    n_vinc = 0
    for r in rows:
        anterior = potencial_por_raiz.get(r["id_raiz"]) if r["Origem"] == "BOLETO" else None
        n_vinc += anterior is not None
        valores.append(
            "("
            + ", ".join(
                _lit(v)
                for v in (
                    r["IdCCDBeneficio"],
                    anterior,
                    r["DescricaoPropostaBeneficio"],
                    r["ValorQuantidade"],
                    r["IdBeneficioSituacaoEfetivacao"],
                    r["IdBeneficioSituacao"],
                    r["IdAreaTematica"],
                    r["IdCaracterizacaoBeneficio"],
                    r["IdTipoBeneficio"],
                    r["IdSubTipoBeneficio"],
                    r["NumeroProcessoDecisao"],
                    r["AnoProcessoDecisao"],
                    r["DataOcorrencia"],
                )
            )
            + ")"
        )

    n_pot = len(potencial_por_raiz)
    n_efe = len(rows) - n_pot
    resumo = {"potenciais": n_pot, "efetivos": n_efe, "efetivos_vinculados": n_vinc}

    partes = [
        f"""-- Multas da CCD ({", ".join(map(str, anos))}) para o SisBenefícios — gerado por
-- scripts/automacao/beneficios_insert_multas.py em {date.today().isoformat()} a partir do staging
-- BdDIP.dbo.CCDBeneficio (origens DEBITO=potencial e BOLETO=efetivo, tipo 1 Sanção/subtipo 1 Multa,
-- só débitos válidos pela folha da cadeia). {n_pot} potenciais + {n_efe} efetivos
-- ({resumo["efetivos_vinculados"]} efetivos vinculados ao potencial do mesmo débito).
--
-- Antes de rodar: preencher @IdSessao (sessão de auditoria do SisBenefícios) e conferir @IdSetor.
-- O script termina em ROLLBACK; troque por COMMIT para gravar.
USE BdBeneficio;
SET NOCOUNT ON; SET XACT_ABORT ON;
DECLARE @IdSessao int = NULL;  -- OBRIGATÓRIO (coluna NOT NULL)
DECLARE @IdSetor  int = {id_setor};  -- processo.dbo.Setor: COORDENADORIA DE CONTROLE DE DECISÕES
IF @IdSessao IS NULL THROW 50000, 'Preencha @IdSessao.', 1;

CREATE TABLE #lote (
    IdInterno int PRIMARY KEY, IdInternoAnterior int NULL,
    DescricaoPropostaBeneficio varchar(500) NOT NULL, ValorQuantidade decimal(14,2) NULL,
    IdBeneficioSituacaoEfetivacao smallint, IdBeneficioSituacao smallint, IdAreaTematica smallint,
    IdCaracterizacaoBeneficio tinyint, IdTipoBeneficio int, IdSubTipoBeneficio int,
    NumeroProcessoDecisao varchar(6) NULL, AnoProcessoDecisao smallint NULL, DataOcorrencia date NULL
);
CREATE TABLE #map (IdInterno int PRIMARY KEY, IdPropostaBeneficio int NOT NULL);
"""
    ]
    for i in range(0, len(valores), 1000):
        partes.append(
            f"INSERT INTO #lote ({_COLS_LOTE}) VALUES\n" + ",\n".join(valores[i : i + 1000]) + ";\n"
        )
    partes.append(
        f"""
BEGIN TRAN;

-- 1) potenciais (IdBeneficioSituacaoEfetivacao = 2): OUTPUT devolve o id gerado por IdInterno
MERGE dbo.Beneficio_PropostaBeneficio AS t
USING (SELECT l.*, CAST(NULL AS int) AS IdBeneficioAnterior
         FROM #lote l WHERE l.IdBeneficioSituacaoEfetivacao = 2) AS s
   ON 1 = 0
WHEN NOT MATCHED THEN INSERT ({_COLS_DESTINO})
     VALUES ({_VALS_DESTINO})
OUTPUT s.IdInterno, inserted.IdPropostaBeneficio INTO #map (IdInterno, IdPropostaBeneficio);

-- 2) efetivos (= 1), vinculados ao potencial do mesmo débito quando ele está no lote
MERGE dbo.Beneficio_PropostaBeneficio AS t
USING (SELECT l.*, m.IdPropostaBeneficio AS IdBeneficioAnterior
         FROM #lote l LEFT JOIN #map m ON m.IdInterno = l.IdInternoAnterior
        WHERE l.IdBeneficioSituacaoEfetivacao = 1) AS s
   ON 1 = 0
WHEN NOT MATCHED THEN INSERT ({_COLS_DESTINO})
     VALUES ({_VALS_DESTINO})
OUTPUT s.IdInterno, inserted.IdPropostaBeneficio INTO #map (IdInterno, IdPropostaBeneficio);

SELECT l.IdBeneficioSituacaoEfetivacao AS efetivacao, COUNT(*) AS inseridos,
       SUM(l.ValorQuantidade) AS valor,
       SUM(CASE WHEN l.IdInternoAnterior IS NOT NULL THEN 1 ELSE 0 END) AS vinculados
  FROM #lote l JOIN #map m ON m.IdInterno = l.IdInterno
 GROUP BY l.IdBeneficioSituacaoEfetivacao;

ROLLBACK TRAN;  -- troque por COMMIT TRAN para gravar
DROP TABLE #map; DROP TABLE #lote;
"""
    )
    return "".join(partes), resumo


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--anos", nargs="+", type=int, default=[2025, 2026])
    ap.add_argument("--setor", type=int, default=ID_SETOR_CCD)
    args = ap.parse_args()
    script, resumo = gerar(args.anos, args.setor)
    out = REPO_ROOT / "saidas" / "automacao" / "beneficios"
    out.mkdir(parents=True, exist_ok=True)
    destino = out / f"insert_multas_{'_'.join(map(str, args.anos))}.sql"
    destino.write_text(script, encoding="utf-8")
    print(f"{destino}: {resumo}")


if __name__ == "__main__":
    main()
