"""Origem 'PROPOSTA' no CHECK de CCDBeneficio.

A CCD passa a importar as propostas de benefício das UTCEs já cadastradas no
BdBeneficio (Beneficio_PropostaBeneficio, IdStatusBeneficio=7 Aprovado) para
gerenciar o fluxo proposta -> potencial -> efetivo. O CHECK da 0020 não previa
o valor — drop + recreate.

Revision ID: 0021_origem_proposta
Revises: 0020_ccd_beneficio
Create Date: 2026-09-01
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0021_origem_proposta"
down_revision: str | Sequence[str] | None = "0020_ccd_beneficio"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_ORIGENS_NOVAS = "'MANUAL', 'DEBITO', 'BOLETO', 'PGE', 'FOLHA', 'DIVIDA_ATIVA', 'FRAP', 'PROPOSTA'"
_ORIGENS_ANTIGAS = "'MANUAL', 'DEBITO', 'BOLETO', 'PGE', 'FOLHA', 'DIVIDA_ATIVA', 'FRAP'"


def _recreate_check(origens: str) -> None:
    op.execute(
        f"""
        IF EXISTS (SELECT 1 FROM sys.check_constraints
                    WHERE name = 'CK_CCDBeneficio_Origem'
                      AND parent_object_id = OBJECT_ID('dbo.CCDBeneficio'))
            ALTER TABLE dbo.CCDBeneficio DROP CONSTRAINT CK_CCDBeneficio_Origem;

        ALTER TABLE dbo.CCDBeneficio ADD CONSTRAINT CK_CCDBeneficio_Origem
            CHECK (Origem IN ({origens}));
        """
    )


def upgrade() -> None:
    _recreate_check(_ORIGENS_NOVAS)


def downgrade() -> None:
    _recreate_check(_ORIGENS_ANTIGAS)
