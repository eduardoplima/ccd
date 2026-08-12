"""Insere 2 recomendações manuais para 8389/2014 (IdProcesso 358457),
ancoradas na decisão mais recente 70/2026 (comp=124771, voto=46662).
Idempotente: pula se já existir mesma (processo, comp, voto, descricao)."""
import os
from pathlib import Path

for line in Path(r"C:\Users\05911205424\Dev\ccd\web\.env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k, v)

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from cgad.utils import DB_DECISOES, get_connection
from cgad.models import RecomendacaoORM

ID_PROCESSO = 358457
ID_COMP = 124771
ID_VOTO = 46662
ID_ORGAO = 115
ORGAO = "CÂMARA MUNICIPAL DE PASSAGEM"
NOME_RESP = "Atual gestor da Câmara Municipal de Passagem"

RECS = [
    "Recomendar ao atual gestor da Câmara Municipal de Passagem (CMPASSAGEM) que observe o teor da "
    "Súmula nº 28 – TCE, especialmente em relação às atividades habituais de natureza contábil, que "
    "não devem ser objeto de terceirização.",
    "Recomendar ao atual gestor da Câmara Municipal de Passagem (CMPASSAGEM) que as pesquisas de preços "
    "(que antecedem licitações ou que instruem compras diretas) sejam realizadas com pessoas físicas "
    "e/ou jurídicas não detentoras de vínculo entre si, devendo ser consultado, no mínimo, o quadro "
    "societário das entidades.",
]

Session = sessionmaker(bind=get_connection(DB_DECISOES))
s = Session()
try:
    for desc in RECS:
        exists = s.execute(
            select(RecomendacaoORM.IdRecomendacao).where(
                RecomendacaoORM.IdProcesso == ID_PROCESSO,
                RecomendacaoORM.IdComposicaoPauta == ID_COMP,
                RecomendacaoORM.IdVotoPauta == ID_VOTO,
                RecomendacaoORM.DescricaoRecomendacao == desc,
            )
        ).first()
        if exists:
            print(f"SKIP (já existe IdRecomendacao={exists[0]}): {desc[:60]}...")
            continue
        row = RecomendacaoORM(
            IdProcesso=ID_PROCESSO,
            IdComposicaoPauta=ID_COMP,
            IdVotoPauta=ID_VOTO,
            DescricaoRecomendacao=desc,
            PrazoCumprimentoRecomendacao=None,
            DataCumprimentoRecomendacao=None,
            NomeResponsavel=NOME_RESP,
            IdPessoaResponsavel=None,
            OrgaoResponsavel=ORGAO,
            IdOrgaoResponsavel=ID_ORGAO,
            Cancelado=False,
        )
        s.add(row)
        s.flush()
        print(f"INSERIDO IdRecomendacao={row.IdRecomendacao}: {desc[:60]}...")
    s.commit()
finally:
    s.close()

# verificação
eng = get_connection("processo")
import pandas as pd
print("\n--- Recomendacoes do 358457 agora ---")
print(pd.read_sql_query(
    "SELECT IdRecomendacao, IdComposicaoPauta, IdVotoPauta, IdOrgaoResponsavel, "
    "LEFT(DescricaoRecomendacao,70) d FROM BdDIP.dbo.Recomendacao WHERE IdProcesso=358457",
    eng).to_string(index=False))
