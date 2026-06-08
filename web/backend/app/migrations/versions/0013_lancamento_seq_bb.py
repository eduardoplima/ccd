"""FRAPLancamento.SeqBB: persiste 7 últimos dígitos do `Documento` (autenticação BB).

Reflete o campo `seq_bb` em `extratos/schemas.py:Lancamento`. Usado como
chave de desempate em `match_ob` quando há M:N na chave (DataPagamento,
ValorOB). Persistir evita ter que recalcular do `Documento` em consumidores
do banco. Backfill estraindo só os dígitos do `Documento` e pegando os
7 últimos (NULL quando há menos de 7).

Revision ID: 0013_lancamento_seq_bb
Revises: 0012_status_match_exato_por_ordem
Create Date: 2026-05-29
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0013_lancamento_seq_bb"
down_revision: str | Sequence[str] | None = "0012_status_match_exato_por_ordem"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPLancamento')
               AND name = 'SeqBB'
        )
            ALTER TABLE dbo.FRAPLancamento ADD SeqBB CHAR(7) NULL;
        """
    )
    # Backfill: extrai dígitos do Documento e pega os 7 últimos quando há ao
    # menos 7. O Documento neste domínio só tem dígitos + separadores
    # (. - / espaço parênteses), então REPLACE encadeado basta — evita TRANSLATE,
    # que só existe no SQL Server 2017+ (produção roda 2016).
    op.execute(
        """
        UPDATE dbo.FRAPLancamento
           SET SeqBB = RIGHT(digitos, 7)
          FROM dbo.FRAPLancamento
         CROSS APPLY (
            SELECT REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
                       ISNULL(Documento, ''),
                       '.', ''), '-', ''), '/', ''), ' ', ''), '(', ''), ')', '') AS digitos
         ) d
         WHERE SeqBB IS NULL AND LEN(digitos) >= 7;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        IF EXISTS (
            SELECT 1 FROM sys.columns
             WHERE object_id = OBJECT_ID('dbo.FRAPLancamento')
               AND name = 'SeqBB'
        )
            ALTER TABLE dbo.FRAPLancamento DROP COLUMN SeqBB;
        """
    )
