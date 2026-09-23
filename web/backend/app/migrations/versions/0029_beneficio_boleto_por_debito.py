"""Benefícios: efetivo (BOLETO) passa ao grão débito.

Até aqui o job de detecção gerava 1 linha BOLETO por parcela paga
(ChaveOrigem 'BOLETO:<IdRetornoBoleto>'). A partir desta revisão o grão é o
débito (raiz da cadeia), 'BOLETO:DEBITO:<raiz>', com valor recalculado a cada
rodada — pagamentos da mesma multa não geram efetivo novo, e o potencial da
raiz é absorvido. Esta migração só retira (Ativo=0) o estoque no grão antigo;
a rodada seguinte do job recria no grão novo.

Revision ID: 0029_beneficio_boleto_por_debito
Revises: 0028_beneficio_pge_fora
Create Date: 2026-09-23
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0029_beneficio_boleto_por_debito"
down_revision: str | Sequence[str] | None = "0028_beneficio_pge_fora"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE dbo.CCDBeneficio SET Ativo = 0, DataAtualizacao = SYSDATETIME()
         WHERE Origem = 'BOLETO' AND Ativo = 1
           AND ChaveOrigem NOT LIKE 'BOLETO:DEBITO:%';
        """
    )


def downgrade() -> None:
    # Retira o grão novo; o job da revisão anterior reinsere o grão parcela.
    op.execute(
        """
        UPDATE dbo.CCDBeneficio SET Ativo = 0, DataAtualizacao = SYSDATETIME()
         WHERE Origem = 'BOLETO' AND Ativo = 1
           AND ChaveOrigem LIKE 'BOLETO:DEBITO:%';
        """
    )
