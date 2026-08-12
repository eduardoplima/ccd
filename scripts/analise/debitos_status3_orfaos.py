"""Débitos órfãos em status 3 ("Pago parcialmente") sem ValorPago.

Conferência do chamado da SETIC (ver `ANALISE_CHAMADO_DEBITOS_STATUS3.md`). Lista
os débitos que são **folha** da cadeia `IdDebitoAnterior`, estão em
`CodigoStatusDivida = 3` e não têm `ValorPago` nem boleto — combinação impossível
pela regra de negócio: a folha de uma cadeia com saldo devia estar em status 1
("Em Aberto").

Cada um desses órfãos nasceu de um pagamento registrado num débito que já tinha
filho, gerando um irmão paralelo. A coluna `irmao_que_seguiu` aponta o irmão que
de fato deu continuidade à cadeia.

Uso:
    python -m scripts.analise.debitos_status3_orfaos

Sai com código 1 enquanto houver órfão (hoje: 13). Depois de a SETIC executar os
cancelamentos, deve listar zero e sair com 0. Não grava nada no banco.
"""
from __future__ import annotations

import sys

import pandas as pd

from ccd.db import run_query_df

SQL = """
SELECT d.IdDebito                                      AS id_debito,
       d.IdDebitoAnterior                              AS id_pai,
       d.valorOriginalDebito                           AS valor_original,
       d.datainclusao                                  AS data_inclusao,
       d.usuarioinclusao                               AS usuario,
       CONCAT(po.numero_processo, '/', po.ano_processo) AS processo_origem,
       (SELECT g.Nome
          FROM processo.dbo.Exe_DebitoPessoa dp
          JOIN processo.dbo.GenPessoa g ON g.IdPessoa = dp.IDPessoa
         WHERE dp.IDDebito = d.IdDebito)               AS pessoa,
       (SELECT COUNT(*)
          FROM processo.dbo.Exe_Debito s
         WHERE s.IdDebitoAnterior = d.IdDebitoAnterior
           AND s.IdDebito <> d.IdDebito)               AS qtd_irmaos,
       (SELECT MIN(s.IdDebito)
          FROM processo.dbo.Exe_Debito s
         WHERE s.IdDebitoAnterior = d.IdDebitoAnterior
           AND s.IdDebito <> d.IdDebito
           AND EXISTS (SELECT 1 FROM processo.dbo.Exe_Debito n
                        WHERE n.IdDebitoAnterior = s.IdDebito)) AS irmao_que_seguiu,
       (SELECT COUNT(*)
          FROM processo.dbo.Exe_HistoricoDebito h
         WHERE h.IdDebito = d.IdDebitoAnterior)        AS ops_no_pai
  FROM processo.dbo.Exe_Debito d
  LEFT JOIN processo.dbo.Processos po ON po.IdProcesso = d.IdProcessoOrigem
 WHERE d.CodigoStatusDivida = :status_pago_parcial
   AND d.ValorPago IS NULL
   AND NOT EXISTS (SELECT 1 FROM processo.dbo.Exe_Debito f
                    WHERE f.IdDebitoAnterior = d.IdDebito)
   AND NOT EXISTS (SELECT 1 FROM processo.dbo.Exe_DebitoBoleto b
                    WHERE b.IdDebito = d.IdDebito)
 ORDER BY d.IdDebito
"""

STATUS_PAGO_PARCIAL = 3


def main() -> int:
    df = run_query_df(SQL, status_pago_parcial=STATUS_PAGO_PARCIAL)
    pd.set_option("display.width", 220)
    pd.set_option("display.max_rows", 200)
    if df.empty:
        print("OK: nenhum débito órfão — nada a corrigir.")
        return 0
    print(df.to_string(index=False))
    print(f"\n{len(df)} débito(s) órfão(s) — valor original somado: "
          f"R$ {df.valor_original.sum():,.2f}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
