"""Pré-triagem do conjunto de dados anotado (CGAD) — roda uma vez, da máquina de dev.

A maior parte dos documentos não tem entidade nenhuma, e o anotador só descobre
isso depois de ler o acórdão inteiro. Este script passa o DeepSeek em cada
documento e grava o resultado como se fosse um quarto anotador
(``Anotador='deepseek'``), o que dá à interface um filtro de "tem entidade" sem
tabela nem coluna nova.

Os spans do modelo **não** são mostrados a quem anota: a interface só usa a
presença deles para filtrar a lista, e a reanotação segue cega.

Idempotente — só marca documento que ainda não tem a linha do deepseek, então
uma execução interrompida retoma de onde parou.

    python -m cgad.dataset_pretag --limite 20   # amostra para conferir
    python -m cgad.dataset_pretag               # o conjunto inteiro
"""

from __future__ import annotations

import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from cgad.etl.text_alignment import find_span_offsets
from cgad.models import DatasetAnotacaoORM, DatasetDocumentoORM
from cgad.prompt import generate_few_shot_ner_prompts
from cgad.schema import NERDecisao
from cgad.utils import DB_DECISOES, get_session

ANOTADOR = "deepseek"
MODELO = os.getenv("AZURE_OPENAI_DEPLOYMENT") or "DeepSeek-V4-Flash"
# ponytail: 4 threads só para as chamadas ao modelo; sobe se o Azure aguentar.
THREADS = 4

# Campo do NERDecisao -> (rótulo do conjunto, atributo com o trecho).
LABELS = {
    "multas": ("MULTA", "descricao_multa"),
    "obrigacoes": ("OBRIGACAO", "descricao_obrigacao"),
    "ressarcimentos": ("RESSARCIMENTO", "descricao_ressarcimento"),
    "recomendacoes": ("RECOMENDACAO", "descricao_recomendacao"),
}


def extrator():
    """Cliente do DeepSeek no Foundry do SERPRO (ver ``frap.llm``)."""
    from frap.llm import structured

    extr = structured(NERDecisao, model=MODELO)
    if extr is None:
        raise SystemExit(
            "configure AZURE_OPENAI_ENDPOINT e AZURE_OPENAI_API_KEY no web/.env "
            "(base /openai/v1 do Foundry do SERPRO)"
        )
    return extr


def spans_do(ner: NERDecisao, texto: str) -> tuple[list[dict], int]:
    """Converte as descrições do modelo em spans de caractere.

    Devolve os spans na ordem do texto e quantas descrições não foram
    localizadas. Spans sobrepostos são descartados: o ``AnotacaoPayload`` do
    backend rejeita sobreposição e o primeiro já cobre o trecho.
    """
    achados: list[dict] = []
    perdidos = 0
    for campo, (label, atributo) in LABELS.items():
        for item in getattr(ner, campo) or []:
            start, end, _ = find_span_offsets(getattr(item, atributo, "") or "", texto)
            if start is None or end is None:
                perdidos += 1
                continue
            achados.append({"start": start, "end": end, "label": label})

    spans: list[dict] = []
    for span in sorted(achados, key=lambda s: (s["start"], s["end"])):
        if spans and span["start"] < spans[-1]["end"]:
            continue
        spans.append(span)
    return spans, perdidos


def pendentes(session: Session, limite: Optional[int], anotador: str) -> list[tuple[int, str]]:
    ja_marcados = select(DatasetAnotacaoORM.IdDocumento).where(
        DatasetAnotacaoORM.Anotador == anotador
    )
    consulta = (
        select(DatasetDocumentoORM.IdDocumento, DatasetDocumentoORM.Texto)
        .where(DatasetDocumentoORM.IdDocumento.not_in(ja_marcados))
        .order_by(DatasetDocumentoORM.IdDocumento)
    )
    if limite:
        consulta = consulta.limit(limite)
    return [(id_doc, texto) for id_doc, texto in session.execute(consulta)]


def marcar(
    session: Session, docs: list[tuple[int, str]], llm, anotador: str
) -> tuple[int, int, int]:
    def extrair(doc: tuple[int, str]):
        id_doc, texto = doc
        try:
            return id_doc, llm.invoke(generate_few_shot_ner_prompts(texto)), texto
        except Exception as erro:  # Azure/rede instáveis — reexecutar retoma
            print(f"  erro no documento {id_doc}: {erro}")
            return id_doc, None, texto

    marcados = com_entidade = perdidos = 0
    with ThreadPoolExecutor(THREADS) as pool:
        for id_doc, ner, texto in pool.map(extrair, docs):
            if ner is None:
                continue
            spans, nao_achados = spans_do(ner, texto)
            perdidos += nao_achados
            session.add(
                DatasetAnotacaoORM(
                    IdDocumento=id_doc,
                    Anotador=anotador,
                    Status="done",
                    Spans=json.dumps(spans, ensure_ascii=False),
                    DataConclusao=datetime.now(),
                )
            )
            session.commit()  # por documento: interrupção não perde o que já rodou
            marcados += 1
            com_entidade += 1 if spans else 0
    return marcados, com_entidade, perdidos


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limite", type=int, help="marca só os N primeiros ainda não marcados")
    parser.add_argument("--dry-run", action="store_true", help="não chama o modelo nem grava")
    parser.add_argument(
        "--anotador",
        default=ANOTADOR,
        help=f"nome sob o qual gravar (default {ANOTADOR}); use outro para comparar modelos",
    )
    args = parser.parse_args()

    session = get_session(DB_DECISOES)
    try:
        docs = pendentes(session, args.limite, args.anotador)
        print(f"{len(docs)} documentos a marcar com {MODELO} como '{args.anotador}'.")
        if args.dry_run or not docs:
            return

        marcados, com_entidade, perdidos = marcar(session, docs, extrator(), args.anotador)
        print(
            f"Marcados {marcados}: {com_entidade} com entidade, {marcados - com_entidade} vazios."
        )
        if perdidos:
            print(f"aviso: {perdidos} descrições do modelo não foram localizadas no texto")
    finally:
        session.close()


if __name__ == "__main__":
    main()
