"""Benefícios: DataOcorrencia = data do acórdão (Exe_Debito.dataDecisao da raiz).

Cada multa/débito é ligado a um acórdão, e é ele o parâmetro temporal do
filtro por ano (decisão de 23/09/2026). Antes, DEBITO usava o trânsito e
BOLETO o 1º pagamento, o que espalhava a mesma multa por anos diferentes.
Alinha o estoque ativo de DEBITO e BOLETO ao que o job passou a gravar.

Revision ID: 0030_beneficio_data_acordao
Revises: 0029_beneficio_boleto_por_debito
Create Date: 2026-09-23
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0030_beneficio_data_acordao"
down_revision: str | Sequence[str] | None = "0029_beneficio_boleto_por_debito"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE b SET DataOcorrencia = CAST(r.dataDecisao AS DATE), DataAtualizacao = SYSDATETIME()
          FROM dbo.CCDBeneficio b
          JOIN processo.dbo.Exe_Debito r ON r.IdDebito = b.IdDebitoExecucao
         WHERE b.Ativo = 1 AND b.Origem IN ('DEBITO', 'BOLETO')
           AND (b.DataOcorrencia IS NULL OR b.DataOcorrencia <> CAST(r.dataDecisao AS DATE));
        """
    )


def downgrade() -> None:
    # ponytail: sem reconstrução (trânsito / 1º pagamento exigem a CTE da cadeia);
    # para voltar, retire o estoque (Ativo=0) e rode a detecção da revisão anterior.
    pass
