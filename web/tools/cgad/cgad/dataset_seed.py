"""Popula o conjunto de dados anotado (CGAD) — roda uma vez, da máquina de dev.

Duas fontes:

1. **Legado** — os 861 documentos do corpus DeciContas.br (`decicontas.json`),
   inteiros, atribuídos ao **eduardo** como anotação já concluída. O JSON só tem
   texto, então os metadados (processo, tipo, data da sessão) são recuperados
   casando o texto **normalizado** contra `all_decisions.csv` (casamento exato sem
   normalizar pega só 438 de 861) e daí para `vw_ia_votos_acordaos_decisoes`.
2. **Ampliação** — decisões de 2024 e 2025 que não são de atos de pessoal,
   deduplicadas e amostradas até o conjunto fechar `ALVO_TOTAL`. A dedup importa: o
   pool bruto tem 16% de textos idênticos e grupos de até 96 cópias literais do
   mesmo acórdão.

Depois cria a fila: `antonietta` e `isabella` reanotam tudo às cegas; `eduardo`
recebe só a ampliação, já que o legado é dele.

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

import numpy as np
import pandas as pd
from rapidfuzz import fuzz, process
from sqlalchemy import delete, select, text
from sqlalchemy.orm import Session

from cgad.models import DatasetAnotacaoORM, DatasetDocumentoORM
from cgad.utils import DB_DECISOES, DB_PROCESSOS, get_connection, get_session

ANOTADORES = ["eduardo", "antonietta", "isabella"]
ANOS_AMPLIACAO = [2024, 2025]
ALVO_TOTAL = 1200  # legado (861) + ampliação
SIMILARIDADE_MAXIMA = 95  # acima disso, dois acórdãos são a mesma peça
SEED = 20260811  # amostra reprodutível
TAMANHO_MINIMO = 200

# repo root: cgad-pkg -> tools/cgad -> tools -> web -> <repo>
REPO_ROOT = Path(__file__).resolve().parents[4]
CORPUS_JSON = REPO_ROOT / "decicontas" / "decicontas.json"
ALL_DECISIONS_CSV = REPO_ROOT / "repos" / "decicontas.app" / "dataset" / "all_decisions.csv"

# Códigos de atos de pessoal, apurados em processo.dbo.Tipo.
CODIGOS_ATOS_PESSOAL = [
    "APO",
    "APP",
    "ASS",
    "CEM",
    "CTT",
    "CVP",
    "FCO",
    "INC",
    "INM",
    "NCE",
    "NOM",
    "PDR",
    "PEN",
    "PEP",
    "RBN",
]


def normalizar(texto: str) -> str:
    """Chave de casamento entre o corpus e o CSV de decisões, e de dedup exata."""
    sem_acento = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", sem_acento).strip().lower()


def esqueleto(texto: str) -> str:
    """Chave de dedup que ignora números: colapsa o mesmo acórdão emitido com
    número de processo, data ou valor diferentes."""
    return re.sub(r"[^a-z# ]", "", re.sub(r"[0-9]+", "#", normalizar(texto)))


def dedup_fuzzy(textos: list[str], limite: int = SIMILARIDADE_MAXIMA) -> np.ndarray:
    """Máscara booleana mantendo o primeiro representante de cada grupo de textos
    com similaridade >= `limite`. O(n²) em C++ — ~1 min para n≈2.000, e este
    script roda uma vez."""
    if not textos:
        return np.zeros(0, bool)
    m = process.cdist(textos, textos, scorer=fuzz.ratio, workers=-1, score_cutoff=limite)
    np.fill_diagonal(m, 0)
    manter = np.ones(len(textos), bool)
    indices = np.arange(len(textos))
    for i in range(len(textos)):
        if manter[i]:
            manter[(m[i] >= limite) & (indices > i)] = False
    return manter


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


# ----- fonte 1: corpus legado -------------------------------------------------


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
    # (IdComposicaoPauta, IdVotoPauta) rejeitaria a repetida — deduplicar aqui, e
    # não no INSERT, para o alvo de ALVO_TOTAL fechar. Fica quem tem mais spans.
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


# ----- fonte 2: ampliação 2024/2025 ------------------------------------------


def carregar_ampliacao(legado: list[Documento]) -> list[Documento]:
    """Decisões de 2024/2025 fora de atos de pessoal, deduplicadas e amostradas.

    O alvo é o que falta para o conjunto fechar `ALVO_TOTAL` junto com o legado.
    A cascata é impressa etapa a etapa porque esses números vão para o *dataset
    paper* — a proveniência do corpus precisa ser auditável.
    """
    alvo = max(0, ALVO_TOTAL - len(legado))
    codigos = ",".join(f"'{c}'" for c in CODIGOS_ATOS_PESSOAL)
    sql = f"""
        SELECT DISTINCT
               v.IdProcesso AS id_processo,
               v.IdComposicaoPauta AS icp,
               v.idVotoPauta AS ivp,
               CONCAT(v.NumeroProcesso, '/', v.AnoProcesso) AS processo,
               v.codigo_tipo_processo AS cod,
               v.DataSessao AS data_sessao,
               v.texto_acordao AS texto
        FROM {DB_PROCESSOS}.dbo.vw_ia_votos_acordaos_decisoes v
        WHERE YEAR(v.DataSessao) IN ({",".join(str(a) for a in ANOS_AMPLIACAO)})
          AND v.texto_acordao IS NOT NULL
          AND LEN(v.texto_acordao) > {TAMANHO_MINIMO}
          AND COALESCE(v.codigo_tipo_processo, '') NOT IN ({codigos})
    """
    df = pd.read_sql(sql, get_connection(DB_PROCESSOS))
    print(f"  {len(df)} decisões (2024/2025, fora de atos de pessoal)")

    df["norm"] = df.texto.map(normalizar)
    df["esq"] = df.norm.map(esqueleto)
    df = df.drop_duplicates("norm").drop_duplicates("esq").reset_index(drop=True)
    print(f"  {len(df)} após dedup exata e por esqueleto")

    df = df[dedup_fuzzy(df.norm.tolist())].reset_index(drop=True)
    print(f"  {len(df)} após dedup fuzzy >= {SIMILARIDADE_MAXIMA}%")

    # Não faz sentido mandar anotar de novo algo que já está no corpus legado.
    # Por decisão (o índice único barraria no INSERT) e por texto parecido.
    decisoes_legado = {(d.id_composicao_pauta, d.id_voto_pauta) for d in legado}
    df = df[[(r.icp, r.ivp) not in decisoes_legado for r in df.itertuples()]].reset_index(drop=True)

    textos_legado = [normalizar(d.texto) for d in legado]
    colisao = process.cdist(
        df.norm.tolist(),
        textos_legado,
        scorer=fuzz.ratio,
        workers=-1,
        score_cutoff=SIMILARIDADE_MAXIMA,
    ).max(axis=1)
    df = df[colisao < SIMILARIDADE_MAXIMA].reset_index(drop=True)
    print(f"  {len(df)} após remover o que já existe no legado")

    df["ano"] = pd.to_datetime(df.data_sessao).dt.year
    amostra = amostrar(df, alvo)
    print(
        f"  {len(amostra)} amostradas (alvo {alvo}) "
        f"{amostra.ano.value_counts().sort_index().to_dict()}"
    )

    return [
        Documento(
            texto=r["texto"],
            origem="ampliacao",
            id_processo=int(r["id_processo"]),
            id_composicao_pauta=int(r["icp"]),
            id_voto_pauta=int(r["ivp"]),
            processo=r["processo"],
            codigo_tipo_processo=r["cod"],
            data_sessao=pd.to_datetime(r["data_sessao"]).to_pydatetime(),
        )
        for _, r in amostra.iterrows()
    ]


def amostrar(df: pd.DataFrame, n: int) -> pd.DataFrame:
    """Amostra ~n linhas preservando a proporção de `(ano, cod)` do pool.

    Arredondar para cima por estrato passa de n; o corte final volta ao alvo.
    """
    if len(df) <= n:
        return df
    fracao = n / len(df)
    estratos = [
        grupo.sample(n=max(1, round(len(grupo) * fracao)), random_state=SEED)
        for _, grupo in df.groupby(["ano", "cod"])
    ]
    return pd.concat(estratos).sample(frac=1, random_state=SEED).head(n)


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

    As anotações do eduardo são regeneradas do JSON, mas as dos outros seriam
    trabalho humano perdido — daí a guarda.
    """
    humanas = session.scalar(
        select(DatasetAnotacaoORM.Anotador)
        .where(
            DatasetAnotacaoORM.Status == "done",
            DatasetAnotacaoORM.Anotador != "eduardo",
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

    print("Corpus legado:")
    legado = carregar_legado()
    print(f"  {sum(len(d.spans or []) for d in legado)} spans preservados")

    print(f"Ampliação {ANOS_AMPLIACAO}:")
    ampliacao = carregar_ampliacao(legado)

    total_docs = len(legado) + len(ampliacao)
    # eduardo só entra na fila da ampliação; o legado já é dele.
    pendentes = len(legado) * 2 + len(ampliacao) * 3
    print(f"\nTotal: {total_docs} documentos, {pendentes} anotações pendentes")

    if args.dry_run:
        print("(dry-run — nada gravado)")
        return

    session = get_session(DB_DECISOES)
    try:
        if args.reconstruir:
            limpar(session)
            print("Conjunto anterior apagado.")
        novos = gravar(session, legado + ampliacao)
        criadas = montar_fila(session)
        print(f"Gravados {novos} documentos novos e {criadas} anotações pendentes.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
