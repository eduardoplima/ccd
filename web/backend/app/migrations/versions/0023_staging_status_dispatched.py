"""Status 'dispatched' (Enviado) e DataEnvio nas quatro tabelas *Staging do CGAD.

O job de ETL que leva obrigações e recomendações aprovadas para Obg_Obrigacao
no banco `processo` marca as linhas com Status='dispatched' e DataEnvio. Os
CHECKs só aceitavam pending/approved/rejected e Status era varchar(8) — drop
do CHECK, alarga a coluna, cria DataEnvio, recria o CHECK. Os CHECKs de
ObrigacaoStaging/RecomendacaoStaging vieram sem nome (tabelas anteriores às
migrações), por isso o drop é por definição, não por nome.

`vwCCDDeterminacao` (0022) filtrava `Status = 'approved'`; recriada aceitando
'dispatched', já que enviado continua sendo determinação aprovada.

Revision ID: 0023_staging_status_dispatched
Revises: 0022_views_agente_ccd
Create Date: 2026-09-14
"""

from __future__ import annotations

import importlib.util
from collections.abc import Sequence
from pathlib import Path

from alembic import op

revision: str = "0023_staging_status_dispatched"
down_revision: str | Sequence[str] | None = "0022_views_agente_ccd"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TABELAS = ("MultaStaging", "ObrigacaoStaging", "RecomendacaoStaging", "RessarcimentoStaging")
_NOVOS = "'pending', 'approved', 'rejected', 'dispatched'"
_ANTIGOS = "'pending', 'approved', 'rejected'"


def _drop_check(tabela: str) -> None:
    op.execute(
        f"""
        DECLARE @nome sysname;
        SELECT @nome = name FROM sys.check_constraints
         WHERE parent_object_id = OBJECT_ID('dbo.{tabela}')
           AND definition LIKE '%Status%';
        IF @nome IS NOT NULL
            EXEC('ALTER TABLE dbo.{tabela} DROP CONSTRAINT [' + @nome + ']');
        """
    )


def _add_check(tabela: str, valores: str) -> None:
    op.execute(
        f"ALTER TABLE dbo.{tabela} ADD CONSTRAINT CK_{tabela}_Status CHECK (Status IN ({valores}));"
    )


def _view_determinacao() -> str:
    spec = importlib.util.spec_from_file_location(
        "mig_0022", Path(__file__).with_name("0022_views_agente_ccd.py")
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.VW_DETERMINACAO


def upgrade() -> None:
    for tabela in _TABELAS:
        _drop_check(tabela)
        op.execute(f"ALTER TABLE dbo.{tabela} ALTER COLUMN Status varchar(10) NOT NULL;")
        op.execute(
            f"IF COL_LENGTH('dbo.{tabela}', 'DataEnvio') IS NULL "
            f"ALTER TABLE dbo.{tabela} ADD DataEnvio datetime NULL;"
        )
        _add_check(tabela, _NOVOS)
    op.execute(
        _view_determinacao().replace("Status = 'approved'", "Status IN ('approved', 'dispatched')")
    )


def downgrade() -> None:
    op.execute(_view_determinacao())
    for tabela in _TABELAS:
        op.execute(f"UPDATE dbo.{tabela} SET Status = 'approved' WHERE Status = 'dispatched';")
        _drop_check(tabela)
        op.execute(
            f"IF COL_LENGTH('dbo.{tabela}', 'DataEnvio') IS NOT NULL "
            f"ALTER TABLE dbo.{tabela} DROP COLUMN DataEnvio;"
        )
        op.execute(f"ALTER TABLE dbo.{tabela} ALTER COLUMN Status varchar(8) NOT NULL;")
        _add_check(tabela, _ANTIGOS)
