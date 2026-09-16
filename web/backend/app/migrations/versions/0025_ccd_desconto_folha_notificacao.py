"""Desconto em folha: tipo e evento da notificação e do recebimento.

A notificação ao órgão pode ser eletrônica (mandado da DE pelo e-TCE, Res.
025/2025) ou física (via postal); o recebimento, certidão de comunicação
eletrônica, recebimento tácito, AR dos Correios ou a certidão da DE que
atesta o início do prazo. As colunas antigas (NumeroNotificacao,
DataNotificacao, NumeroPostagemAr, DataAr) continuam; estas só qualificam
e apontam o evento (Pro_ProcessoEvento) para o link nos autos do e-Contas.

Revision ID: 0025_ccd_desconto_folha_notificacao
Revises: 0024_ccd_desconto_folha
Create Date: 2026-09-15
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0025_ccd_desconto_folha_notificacao"
down_revision: str | Sequence[str] | None = "0024_ccd_desconto_folha"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_COLUNAS = [
    ("TipoNotificacao", "CHAR(1) NULL"),  # E eletrônica / F física (postal)
    ("EventoNotificacao", "INT NULL"),
    ("IdEventoNotificacao", "INT NULL"),
    ("TipoRecebimento", "VARCHAR(2) NULL"),  # E certidão eletrônica / T tácito / AR / DE
    ("EventoRecebimento", "INT NULL"),
    ("IdEventoRecebimento", "INT NULL"),
]


def upgrade() -> None:
    for nome, tipo in _COLUNAS:
        op.execute(
            f"IF COL_LENGTH('dbo.CCDDescontoFolha', '{nome}') IS NULL "
            f"ALTER TABLE dbo.CCDDescontoFolha ADD {nome} {tipo};"
        )


def downgrade() -> None:
    for nome, _ in _COLUNAS:
        op.execute(
            f"IF COL_LENGTH('dbo.CCDDescontoFolha', '{nome}') IS NOT NULL "
            f"ALTER TABLE dbo.CCDDescontoFolha DROP COLUMN {nome};"
        )
