"""Conjunto de dados anotado (CGAD) — múltiplos anotadores.

- `DatasetDocumento`: um texto de decisão a anotar. Origem `decicontas` são os
  861 documentos do corpus DeciContas.br importados do Label Studio; `ampliacao`
  são as decisões de 2024/2025 amostradas da view do banco `processo`.
- `DatasetAnotacao`: a anotação de UM anotador sobre UM documento. Os spans vão
  em JSON (`[{"start":int,"end":int,"label":str}]`), mesmo formato do campo
  `entities` do `decicontas.json` — o corpus inteiro tem 459 spans, uma tabela
  por span não se paga.

`CodigoTipoProcesso` é gravado em todo documento para que o filtro de atos de
pessoal (APO, APP, ASS, CEM, CTT, CVP, FCO, INC, INM, NCE, NOM, PDR, PEN, PEP,
RBN) seja um WHERE quando/se for reativado.

Revision ID: 0017_dataset_anotacao
Revises: 0016_revisao_por_decisao
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op


revision: str = "0017_dataset_anotacao"
down_revision: str | Sequence[str] | None = "0016_revisao_por_decisao"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE dbo.DatasetDocumento (
            IdDocumento int IDENTITY(1,1) NOT NULL
                CONSTRAINT PK_DatasetDocumento PRIMARY KEY,
            IdExterno int NULL,
            IdProcesso int NULL,
            IdComposicaoPauta int NULL,
            IdVotoPauta int NULL,
            Processo varchar(20) NULL,
            CodigoTipoProcesso char(3) NULL,
            DataSessao datetime NULL,
            Texto varchar(max) NOT NULL,
            Origem varchar(16) NOT NULL
                CONSTRAINT CK_DatasetDocumento_Origem
                CHECK (Origem IN ('decicontas', 'ampliacao')),
            DataInclusao datetime NOT NULL
                CONSTRAINT DF_DatasetDocumento_DataInclusao DEFAULT (GETDATE())
        );
        """
    )
    op.execute(
        "CREATE UNIQUE INDEX ux_datasetdocumento_idexterno "
        "ON dbo.DatasetDocumento(IdExterno) WHERE IdExterno IS NOT NULL;"
    )
    op.execute(
        "CREATE UNIQUE INDEX ux_datasetdocumento_decisao "
        "ON dbo.DatasetDocumento(IdComposicaoPauta, IdVotoPauta) "
        "WHERE IdComposicaoPauta IS NOT NULL AND IdVotoPauta IS NOT NULL;"
    )
    op.execute("CREATE INDEX ix_datasetdocumento_origem ON dbo.DatasetDocumento(Origem);")

    op.execute(
        """
        CREATE TABLE dbo.DatasetAnotacao (
            IdAnotacao int IDENTITY(1,1) NOT NULL
                CONSTRAINT PK_DatasetAnotacao PRIMARY KEY,
            IdDocumento int NOT NULL
                CONSTRAINT FK_DatasetAnotacao_DatasetDocumento
                REFERENCES dbo.DatasetDocumento(IdDocumento),
            Anotador varchar(150) NOT NULL,
            Status varchar(8) NOT NULL
                CONSTRAINT CK_DatasetAnotacao_Status
                CHECK (Status IN ('pending', 'done')),
            Spans nvarchar(max) NULL,
            DataInicio datetime NULL,
            DataConclusao datetime NULL,
            CONSTRAINT ux_datasetanotacao_documento_anotador
                UNIQUE (IdDocumento, Anotador)
        );
        """
    )
    op.execute("CREATE INDEX ix_datasetanotacao_anotador ON dbo.DatasetAnotacao(Anotador);")
    op.execute(
        "CREATE INDEX ix_datasetanotacao_anotador_status ON dbo.DatasetAnotacao(Anotador, Status);"
    )


def downgrade() -> None:
    op.execute("DROP TABLE dbo.DatasetAnotacao;")
    op.execute("DROP TABLE dbo.DatasetDocumento;")
