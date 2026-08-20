"""Popula o conjunto de dados anotado (CGAD) — roda uma vez, da máquina de dev.

Fonte única: os 861 documentos do corpus DeciContas.br (`decicontas.json`),
inteiros, atribuídos ao **eduardo** como anotação já concluída. O JSON só tem
texto, então os metadados (processo, tipo, data da sessão) são recuperados
casando o texto **normalizado** contra `all_decisions.csv` (casamento exato sem
normalizar pega só 438 de 861) e daí para `vw_ia_votos_acordaos_decisoes`.

Depois cria a fila: `antonietta` e `isabella` reanotam tudo às cegas; o eduardo
fica de fora, já que o corpus é a anotação dele.

Idempotente — reexecutar não duplica nada. Para refazer do zero, `--reconstruir`.

    python -m cgad.dataset_seed --dry-run
    python -m cgad.dataset_seed --reconstruir
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
from sqlalchemy import delete, select, text
from sqlalchemy.orm import Session

from cgad.models import DatasetAnotacaoORM, DatasetDocumentoORM
from cgad.utils import DB_DECISOES, DB_PROCESSOS, get_connection, get_session

ANOTADORES = ["eduardo", "antonietta", "isabella"]

# repo root: cgad-pkg -> tools/cgad -> tools -> web -> <repo>
REPO_ROOT = Path(__file__).resolve().parents[4]
CORPUS_JSON = REPO_ROOT / "decicontas" / "decicontas.json"
ALL_DECISIONS_CSV = REPO_ROOT / "repos" / "decicontas.app" / "dataset" / "all_decisions.csv"


def normalizar(texto: str) -> str:
    """Chave de casamento entre o corpus e o CSV de decisões, e de dedup exata."""
    sem_acento = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", sem_acento).strip().lower()


@dataclass
class Documento:
    texto: str
    origem: str
    id_externo: Optional[int] = None
    id_processo: Optional[int] = None
    id_composicao_pauta: Optional[int] = None
    id_voto_pauta: Optional[int] = None
    processo: Optional[str] = None
    codigo_tipo_processo: Optional[str] = None
    data_sessao: Optional[datetime] = None
    spans: Optional[list[dict]] = None  # anotação do eduardo (só no legado)


# ----- corpus -------------------------------------------------


def carregar_legado() -> list[Documento]:
    corpus = json.loads(CORPUS_JSON.read_text(encoding="utf-8"))
    csv = pd.read_csv(ALL_DECISIONS_CSV)
    csv["chave"] = csv["texto_acordao"].map(normalizar)
    por_chave = csv.drop_duplicates("chave").set_index("chave")

    docs: list[Documento] = []
    sem_casar = 0
    for item in corpus:
        chave = normalizar(item["text"])
        doc = Documento(
            texto=item["text"],
            origem="decicontas",
            id_externo=item["id"],
            spans=item.get("entities") or [],
        )
        if chave in por_chave.index:
            linha = por_chave.loc[chave]
            doc.id_composicao_pauta = int(linha["idcomposicaopauta"])
            doc.id_voto_pauta = int(linha["idvotopauta"])
            doc.data_sessao = pd.to_datetime(linha["datasessao"]).to_pydatetime()
        else:
            sem_casar += 1
        docs.append(doc)

    if sem_casar:
        print(f"  aviso: {sem_casar} documentos do corpus não casaram com o CSV")

    enriquecer(docs)

    # O corpus traz a mesma decisão duas vezes em alguns casos, e o índice único
    # (IdComposicaoPauta, IdVotoPauta) rejeitaria a repetida — deduplicar aqui.
    # Fica quem tem mais spans.
    melhor: dict[tuple, Documento] = {}
    for d in docs:
        chave = (
            (d.id_composicao_pauta, d.id_voto_pauta)
            if d.id_composicao_pauta is not None
            else ("ext", d.id_externo)
        )
        atual = melhor.get(chave)
        if atual is None or len(d.spans or []) > len(atual.spans or []):
            melhor[chave] = d  # dict mantém a posição da primeira inserção
    unicos = list(melhor.values())
    print(f"  {len(corpus)} -> {len(unicos)} ({len(corpus) - len(unicos)} decisões repetidas)")
    return unicos


def enriquecer(docs: list[Documento]) -> None:
    """Preenche IdProcesso/processo/codigo_tipo_processo pela view, em lote."""
    pares = [
        (d.id_composicao_pauta, d.id_voto_pauta) for d in docs if d.id_composicao_pauta is not None
    ]
    if not pares:
        return

    valores = ",".join(f"({a},{b})" for a, b in pares)
    sql = f"""
        SELECT v.IdComposicaoPauta AS icp,
               v.idVotoPauta AS ivp,
               MIN(v.IdProcesso) AS id_processo,
               MIN(v.codigo_tipo_processo) AS cod,
               MIN(CONCAT(v.NumeroProcesso, '/', v.AnoProcesso)) AS processo
        FROM {DB_PROCESSOS}.dbo.vw_ia_votos_acordaos_decisoes v
        JOIN (VALUES {valores}) t(a, b)
          ON t.a = v.IdComposicaoPauta AND t.b = v.idVotoPauta
        GROUP BY v.IdComposicaoPauta, v.idVotoPauta
    """
    with get_connection(DB_PROCESSOS).connect() as conn:
        meta = {(r.icp, r.ivp): (r.id_processo, r.cod, r.processo) for r in conn.execute(text(sql))}

    faltando = 0
    for d in docs:
        chave = (d.id_composicao_pauta, d.id_voto_pauta)
        if chave in meta:
            d.id_processo, d.codigo_tipo_processo, d.processo = meta[chave]
        elif d.id_composicao_pauta is not None:
            faltando += 1
    if faltando:
        print(f"  aviso: {faltando} documentos sem correspondência na view (metadados nulos)")


# ----- gravação --------------------------------------------------------------


def existentes(session: Session) -> tuple[set[int], set[tuple[int, int]]]:
    ids_externos = set(
        session.scalars(
            select(DatasetDocumentoORM.IdExterno).where(DatasetDocumentoORM.IdExterno.is_not(None))
        )
    )
    decisoes = set(
        session.execute(
            select(
                DatasetDocumentoORM.IdComposicaoPauta,
                DatasetDocumentoORM.IdVotoPauta,
            ).where(DatasetDocumentoORM.IdComposicaoPauta.is_not(None))
        ).all()
    )
    return ids_externos, decisoes


def gravar(session: Session, docs: list[Documento]) -> int:
    ids_externos, decisoes = existentes(session)
    novos = 0
    for d in docs:
        if d.id_externo is not None and d.id_externo in ids_externos:
            continue
        if d.id_composicao_pauta is not None:
            if (d.id_composicao_pauta, d.id_voto_pauta) in decisoes:
                continue
            decisoes.add((d.id_composicao_pauta, d.id_voto_pauta))

        linha = DatasetDocumentoORM(
            IdExterno=d.id_externo,
            IdProcesso=d.id_processo,
            IdComposicaoPauta=d.id_composicao_pauta,
            IdVotoPauta=d.id_voto_pauta,
            Processo=d.processo,
            CodigoTipoProcesso=d.codigo_tipo_processo,
            DataSessao=d.data_sessao,
            Texto=d.texto,
            Origem=d.origem,
        )
        session.add(linha)
        session.flush()
        novos += 1

        # A anotação do eduardo no legado já nasce concluída.
        if d.origem == "decicontas":
            session.add(
                DatasetAnotacaoORM(
                    IdDocumento=linha.IdDocumento,
                    Anotador="eduardo",
                    Status="done",
                    Spans=json.dumps(d.spans or [], ensure_ascii=False),
                    DataConclusao=datetime.now(),
                )
            )
    session.commit()
    return novos


def montar_fila(session: Session) -> int:
    """Uma linha `pending` por (documento, anotador) que ainda não exista.

    O eduardo cai fora do legado sozinho: `gravar` já criou a linha `done` dele
    lá, então o par (documento, eduardo) aparece em `ja_existe`.
    """
    documentos = session.scalars(select(DatasetDocumentoORM.IdDocumento)).all()
    ja_existe = set(
        session.execute(select(DatasetAnotacaoORM.IdDocumento, DatasetAnotacaoORM.Anotador)).all()
    )

    criadas = 0
    for id_doc in documentos:
        for anotador in ANOTADORES:
            if (id_doc, anotador) in ja_existe:
                continue
            session.add(DatasetAnotacaoORM(IdDocumento=id_doc, Anotador=anotador, Status="pending"))
            criadas += 1
    session.commit()
    return criadas


def limpar(session: Session) -> None:
    """Apaga tudo para semear do zero.

    As anotações do eduardo são regeneradas do JSON e as do deepseek pelo
    ``dataset_pretag``, mas as dos outros seriam trabalho humano perdido — daí a
    guarda.
    """
    humanas = session.scalar(
        select(DatasetAnotacaoORM.Anotador)
        .where(
            DatasetAnotacaoORM.Status == "done",
            DatasetAnotacaoORM.Anotador.not_in(["eduardo", "deepseek"]),
        )
        .limit(1)
    )
    if humanas is not None:
        raise SystemExit(
            f"abortado: já existe anotação concluída de '{humanas}'. "
            "Reconstruir apagaria trabalho humano."
        )
    session.execute(delete(DatasetAnotacaoORM))
    session.execute(delete(DatasetDocumentoORM))
    session.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="não grava nada")
    parser.add_argument(
        "--reconstruir",
        action="store_true",
        help="apaga o conjunto existente antes de semear",
    )
    args = parser.parse_args()

    print("Corpus DeciContas.br:")
    legado = carregar_legado()
    print(f"  {sum(len(d.spans or []) for d in legado)} spans preservados")

    # eduardo não entra na fila: o corpus já é a anotação dele.
    print(f"\nTotal: {len(legado)} documentos, {len(legado) * 2} anotações pendentes")

    if args.dry_run:
        print("(dry-run — nada gravado)")
        return

    session = get_session(DB_DECISOES)
    try:
        if args.reconstruir:
            limpar(session)
            print("Conjunto anterior apagado.")
        novos = gravar(session, legado)
        criadas = montar_fila(session)
        print(f"Gravados {novos} documentos novos e {criadas} anotações pendentes.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
