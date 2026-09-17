"""Roda extrações CGAD mensais em sequência, pelo mesmo caminho do worker ARQ.

Executado DENTRO do container frap-worker (env já injetado pelo compose):
    python run_extracoes.py 2023          # dez/2023 -> jan/2023
    python run_extracoes.py 2023 9 8 3    # só esses meses, nessa ordem (re-rodar)

Cria a linha em Extracao (aparece na timeline de /cgad/etl) e chama
run_full_extraction in-process. Idempotente: NER existente não chama o LLM e
o stage-2 pula o que já está no bridge *Processada.
"""

import asyncio
import calendar
import logging
import sys
from datetime import UTC, date, datetime

from app.cgad.tasks import run_full_extraction
from cgad.models import ExtracaoORM
from cgad.utils import DB_DECISOES, get_connection
from sqlalchemy.orm import sessionmaker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("cgad.utils").setLevel(logging.WARNING)  # ruído dos skips


def janelas(ano: int, meses: list[int]) -> list[tuple[date, date]]:
    meses = meses or list(range(12, 0, -1))  # default decrescente: dez -> jan
    return [(date(ano, m, 1), date(ano, m, calendar.monthrange(ano, m)[1])) for m in meses]


async def main() -> None:
    ano = int(sys.argv[1])
    meses = [int(m) for m in sys.argv[2:]]
    Session = sessionmaker(bind=get_connection(DB_DECISOES))
    for inicio, fim in janelas(ano, meses):
        s = Session()
        row = ExtracaoORM(
            DataInicio=inicio,
            DataFim=fim,
            DataExecucao=datetime.now(UTC).replace(tzinfo=None),  # coluna é naive UTC
            Status="queued",
            EtapaAtual="queued",
        )
        s.add(row)
        s.commit()
        s.refresh(row)
        extracao_id = row.IdExtracao
        s.close()
        print(f"\n=== Extracao {extracao_id}: {inicio} .. {fim} ===", flush=True)
        try:
            res = await run_full_extraction(
                {"job_id": f"local-{extracao_id}"},
                {"start_date": inicio.isoformat(), "end_date": fim.isoformat()},
                extracao_id,
            )
            print(f"=== Extracao {extracao_id} concluida: {res}", flush=True)
        except Exception as e:  # a task já marcou Status=error; segue para o mês anterior
            print(f"=== Extracao {extracao_id} FALHOU: {type(e).__name__}: {e}", flush=True)


if __name__ == "__main__":
    assert janelas(2023, [])[0] == (date(2023, 12, 1), date(2023, 12, 31))
    assert janelas(2024, [2]) == [(date(2024, 2, 1), date(2024, 2, 29))]
    asyncio.run(main())
