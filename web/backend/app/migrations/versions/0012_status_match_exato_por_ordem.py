"""FRAPStatusMatch: novo código EXATO_POR_ORDEM no matcher 'OB'.

Reflete o desempate por ordem cronológica (`seq_bb` do extrato x
`NUORDEMBANCARIA` do SIGEF) implementado em `tools/frap/matching/ob.py`.
Sem o seed, INSERT em FRAPMatchOB falha quando o matcher emite o novo
status. MERGE idempotente.

Revision ID: 0012_status_match_exato_por_ordem
Revises: 0011_metrica_totais
Create Date: 2026-05-29
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0012_status_match_exato_por_ordem"
down_revision: str | Sequence[str] | None = "0011_metrica_totais"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        MERGE dbo.FRAPStatusMatch AS tgt
        USING (VALUES
            (CAST(15 AS TINYINT), 'EXATO_POR_ORDEM', 'OB',
             N'M:N na chave (DataPagamento, ValorOB) desempatado por ordem (seq_bb x NUORDEMBANCARIA)')
        ) AS src (IdStatusMatch, Codigo, Matcher, Descricao)
        ON tgt.IdStatusMatch = src.IdStatusMatch
        WHEN NOT MATCHED THEN
            INSERT (IdStatusMatch, Codigo, Matcher, Descricao)
            VALUES (src.IdStatusMatch, src.Codigo, src.Matcher, src.Descricao)
        WHEN MATCHED AND (
                tgt.Codigo  <> src.Codigo
             OR tgt.Matcher <> src.Matcher
             OR ISNULL(tgt.Descricao, N'') <> ISNULL(src.Descricao, N'')
        ) THEN
            UPDATE SET Codigo = src.Codigo, Matcher = src.Matcher, Descricao = src.Descricao;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM dbo.FRAPStatusMatch
         WHERE IdStatusMatch = 15
           AND Codigo  = 'EXATO_POR_ORDEM'
           AND Matcher = 'OB';
        """
    )
