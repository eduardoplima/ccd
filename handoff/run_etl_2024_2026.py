"""ETL CGAD com deepseek-v4-flash para as decisões restantes de 2024-2026.
Stage-1 (NER) + Stage-2 (obrigação/recomendação), overwrite=False (idempotente,
re-startável). Escreve em produção (BdDIP).
"""
import os
import sys
import time
from datetime import date
from pathlib import Path

for line in Path(r"C:\Users\05911205424\Dev\ccd\web\.env").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k, v)

from langchain_openai import AzureChatOpenAI
from sqlalchemy.orm import sessionmaker

from cgad.utils import (
    DB_DECISOES, get_connection, get_decisions_by_dates, process_decision_row, safe_int,
)
from cgad.etl.pipeline import (
    ExtractionFilters,
    enqueue_obrigacao_extraction,
    enqueue_recomendacao_extraction,
)
from cgad.schema import (
    NERDecisao, Obrigacao, Recomendacao, ResponsibleChoice, CitationChoice,
)

DEP = "deepseek-v4-flash"
START, END = date(2024, 1, 1), date(2026, 12, 31)
RUN_ID = "deepseek-2024_2026"


def structured(cls):
    llm = AzureChatOpenAI(deployment_name=DEP, model_name=DEP)
    return llm.with_structured_output(cls, include_raw=False, method="function_calling")


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


Session = sessionmaker(bind=get_connection(DB_DECISOES))

# ---- Stage 1: NER ----
log(f"Stage-1: carregando decisões {START}..{END}")
df = get_decisions_by_dates(START, END)
log(f"Stage-1: {len(df)} linhas driver (decisões x responsáveis)")

ner = structured(NERDecisao)
s1 = Session()
done = bad_id = errors = 0
seen = set()
try:
    for i, (_, row) in enumerate(df.iterrows(), 1):
        ids = (safe_int(row.get("id_processo")), safe_int(row.get("id_composicao_pauta")),
               safe_int(row.get("id_voto_pauta")))
        if any(v is None for v in ids):
            bad_id += 1
            continue
        triple = ids
        if triple in seen:
            continue
        seen.add(triple)
        try:
            process_decision_row(
                session=s1, row=row, extractor=ner,
                model_name=DEP, prompt_version="v1", run_id=RUN_ID, overwrite=False,
            )
            done += 1
        except Exception as e:
            errors += 1
            log(f"  NER ERRO {row.get('processo')} {triple}: {type(e).__name__} {str(e)[:160]}")
            # recupera a sessão: rollback da transação envenenada; se a conexão
            # caiu (08S01), descarta para forçar reconexão na próxima linha.
            try:
                s1.rollback()
            except Exception:
                try:
                    s1.close()
                except Exception:
                    pass
                s1 = Session()
        if done % 50 == 0 and done:
            log(f"  ...NER {done} decisões distintas processadas (linha {i}/{len(df)}), erros={errors}, ids_nulos={bad_id}")
finally:
    s1.close()
log(f"Stage-1 FIM: distintas={len(seen)} processadas={done} erros={errors} ids_nulos={bad_id}")

if os.environ.get("STAGE1_ONLY"):
    log("STAGE1_ONLY: parando antes do stage-2 (obrigações/recomendações).")
    sys.exit(0)

# ---- Stage 2: Obrigação + Recomendação ----
filters = ExtractionFilters(start_date=START, end_date=END, overwrite=False)
ob_c = {"e": 0, "f": 0, "s": 0}
rc_c = {"e": 0, "f": 0, "s": 0}


def mk_cb(counter):
    def cb(kind, payload):
        counter["e" if kind == "extracted" else "f" if kind == "failed" else "s"] += 1
        tot = sum(counter.values())
        if tot % 25 == 0:
            log(f"    stage2 progress: extracted={counter['e']} failed={counter['f']} skipped={counter['s']}")
    return cb


# ponytail: retry inteiro da chamada (idempotente via bridge Processed*); blip de
# rede derruba LLM e MSSQL de uma vez, então sessão nova a cada tentativa.
def run_stage2(label, fn, draft_cls, counter):
    for attempt in range(1, 11):
        s = Session()
        try:
            res = fn(
                filters, extractor=structured(draft_cls),
                responsible_extractor=structured(ResponsibleChoice),
                citation_extractor=structured(CitationChoice),
                session=s, on_item=mk_cb(counter),
            )
            log(f"{label}: scanned={res.scanned} enqueued={res.enqueued} skipped={res.skipped} failed={res.failed}")
            return
        except Exception as e:
            log(f"{label} ERRO (tentativa {attempt}/10): {type(e).__name__} {str(e)[:160]}")
            time.sleep(60)
        finally:
            s.close()
    raise SystemExit(f"{label}: desistindo após 10 tentativas")


log("Stage-2a: obrigações")
run_stage2("Obrigações", enqueue_obrigacao_extraction, Obrigacao, ob_c)

log("Stage-2b: recomendações")
run_stage2("Recomendações", enqueue_recomendacao_extraction, Recomendacao, rc_c)

log("DONE")
