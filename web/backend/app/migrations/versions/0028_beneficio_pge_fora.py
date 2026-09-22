"""Benefícios: repasse da PGE sai da carteira da CCD.

A recuperação em dívida ativa (repasse PGE) é atribuição do MPC, não benefício
da CCD. O job de detecção deixou de gerar a origem 'PGE'; esta migração desativa
o estoque já detectado (3.951 linhas em 22/09/2026). O CHECK de Origem mantém o
valor por compatibilidade.

Revision ID: 0028_beneficio_pge_fora
Revises: 0027_usuario_permissoes_pode_ver
Create Date: 2026-09-22
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0028_beneficio_pge_fora"
down_revision: str | Sequence[str] | None = "0027_usuario_permissoes_pode_ver"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE dbo.CCDBeneficio SET Ativo = 0, DataAtualizacao = SYSDATETIME()
         WHERE Origem = 'PGE' AND Ativo = 1;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE dbo.CCDBeneficio SET Ativo = 1, DataAtualizacao = SYSDATETIME()
         WHERE Origem = 'PGE' AND Ativo = 0;
        """
    )
