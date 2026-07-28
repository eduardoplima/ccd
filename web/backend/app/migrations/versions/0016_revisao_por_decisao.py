"""Revisão por decisão (CGAD).

- `NERDecisao` ganha claim + estado de revisão: `ReservadoPor`, `DataReserva`,
  `RevisadoPor`, `DataRevisao`. Pendente = `RevisadoPor IS NULL` e >=1 filho NER.
- Novas tabelas de auditoria `MultaStaging` e `RessarcimentoStaging` — multa e
  ressarcimento não têm tabela final; a staging aponta direto para a linha NER
  (`IdNer* IS NULL` = entidade adicionada manualmente pelo revisor).

Tipos físicos espelham `ObrigacaoStaging` (Status varchar(8), descrições
varchar(max), JSON em nvarchar(max), datas em datetime).

Revision ID: 0016_revisao_por_decisao
Revises: 0015_email_opcional_deve_trocar_senha
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0016_revisao_por_decisao"
down_revision: str | Sequence[str] | None = "0015_email_opcional_deve_trocar_senha"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE dbo.NERDecisao ADD "
        "ReservadoPor varchar(255) NULL, "
        "DataReserva datetime NULL, "
        "RevisadoPor varchar(255) NULL, "
        "DataRevisao datetime NULL;"
    )

    op.execute(
        """
        CREATE TABLE dbo.MultaStaging (
            IdMultaStaging int IDENTITY(1,1) NOT NULL
                CONSTRAINT PK_MultaStaging PRIMARY KEY,
            IdNerMulta int NULL
                CONSTRAINT FK_MultaStaging_NERMulta
                REFERENCES dbo.NERMulta(IdNerMulta),
            IdProcesso int NOT NULL,
            IdComposicaoPauta int NOT NULL,
            IdVotoPauta int NOT NULL,
            DescricaoMulta varchar(max) NOT NULL,
            ValorFixo float NULL,
            Percentual float NULL,
            BaseCalculo float NULL,
            NomeResponsavel varchar(max) NULL,
            DocumentoResponsavel varchar(max) NULL,
            EMultaSolidaria bit NULL,
            Solidarios nvarchar(max) NULL,
            Status varchar(8) NOT NULL
                CONSTRAINT CK_MultaStaging_Status
                CHECK (Status IN ('pending', 'approved', 'rejected')),
            Revisor varchar(255) NULL,
            DataRevisao datetime NULL,
            PayloadOriginal nvarchar(max) NULL,
            ObservacoesRevisao varchar(max) NULL
        );
        """
    )
    op.execute("CREATE INDEX ix_multastaging_idnermulta ON dbo.MultaStaging(IdNerMulta);")
    op.execute("CREATE INDEX ix_multastaging_idprocesso ON dbo.MultaStaging(IdProcesso);")
    op.execute("CREATE INDEX ix_multastaging_status ON dbo.MultaStaging(Status);")
    op.execute(
        "CREATE UNIQUE INDEX ux_multastaging_idnermulta ON dbo.MultaStaging(IdNerMulta) "
        "WHERE IdNerMulta IS NOT NULL;"
    )

    op.execute(
        """
        CREATE TABLE dbo.RessarcimentoStaging (
            IdRessarcimentoStaging int IDENTITY(1,1) NOT NULL
                CONSTRAINT PK_RessarcimentoStaging PRIMARY KEY,
            IdNerRessarcimento int NULL
                CONSTRAINT FK_RessarcimentoStaging_NERRessarcimento
                REFERENCES dbo.NERRessarcimento(IdNerRessarcimento),
            IdProcesso int NOT NULL,
            IdComposicaoPauta int NOT NULL,
            IdVotoPauta int NOT NULL,
            DescricaoRessarcimento varchar(max) NOT NULL,
            ValorDano float NULL,
            PercentualImputado float NULL,
            ValorImputado float NULL,
            NomeResponsavel varchar(max) NULL,
            DocumentoResponsavel varchar(max) NULL,
            Status varchar(8) NOT NULL
                CONSTRAINT CK_RessarcimentoStaging_Status
                CHECK (Status IN ('pending', 'approved', 'rejected')),
            Revisor varchar(255) NULL,
            DataRevisao datetime NULL,
            PayloadOriginal nvarchar(max) NULL,
            ObservacoesRevisao varchar(max) NULL
        );
        """
    )
    op.execute(
        "CREATE INDEX ix_ressarcimentostaging_idnerressarcimento "
        "ON dbo.RessarcimentoStaging(IdNerRessarcimento);"
    )
    op.execute(
        "CREATE INDEX ix_ressarcimentostaging_idprocesso ON dbo.RessarcimentoStaging(IdProcesso);"
    )
    op.execute("CREATE INDEX ix_ressarcimentostaging_status ON dbo.RessarcimentoStaging(Status);")
    op.execute(
        "CREATE UNIQUE INDEX ux_ressarcimentostaging_idnerressarcimento "
        "ON dbo.RessarcimentoStaging(IdNerRessarcimento) "
        "WHERE IdNerRessarcimento IS NOT NULL;"
    )


def downgrade() -> None:
    op.execute("DROP TABLE dbo.RessarcimentoStaging;")
    op.execute("DROP TABLE dbo.MultaStaging;")
    op.execute(
        "ALTER TABLE dbo.NERDecisao DROP COLUMN "
        "ReservadoPor, DataReserva, RevisadoPor, DataRevisao;"
    )
