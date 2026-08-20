"""Exporta um JSONL por anotador humano do dataset de anotação NER.

Uma linha por documento: texto + spans de caractere ({start, end, label}),
mesmo formato do campo ``entities`` do decicontas.json. O pseudo-anotador
``deepseek`` (pré-tag LLM) fica de fora. ``spans: null`` = pendente nunca
tocado; ``spans: []`` = concluído sem entidade.

Uso: python -m cgad.dataset_export [--out DIR]
"""

import argparse
import json
from pathlib import Path

from cgad.models import DatasetAnotacaoORM, DatasetDocumentoORM
from cgad.utils import DB_DECISOES, get_session

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_OUT = REPO_ROOT / "saidas" / "analise" / "dataset_anotadores"


def exportar(out_dir: Path) -> dict[str, tuple[int, int]]:
    """Escreve dataset_<anotador>.jsonl e retorna {anotador: (docs, spans)}."""
    out_dir.mkdir(parents=True, exist_ok=True)
    session = get_session(DB_DECISOES)
    try:
        rows = (
            session.query(DatasetAnotacaoORM, DatasetDocumentoORM)
            .join(DatasetDocumentoORM)
            .filter(DatasetAnotacaoORM.Anotador != "deepseek")
            .order_by(DatasetAnotacaoORM.Anotador, DatasetDocumentoORM.IdDocumento)
            .all()
        )
    finally:
        session.close()

    contagens: dict[str, tuple[int, int]] = {}
    arquivos: dict[str, object] = {}
    try:
        for anot, doc in rows:
            spans = json.loads(anot.Spans) if anot.Spans is not None else None
            linha = {
                "id": doc.IdExterno if doc.IdExterno is not None else doc.IdDocumento,
                "processo": doc.Processo,
                "data_sessao": doc.DataSessao.isoformat() if doc.DataSessao else None,
                "origem": doc.Origem,
                "text": doc.Texto,
                "status": anot.Status,
                "data_conclusao": anot.DataConclusao.isoformat() if anot.DataConclusao else None,
                "spans": spans,
            }
            if anot.Anotador not in arquivos:
                arquivos[anot.Anotador] = (out_dir / f"dataset_{anot.Anotador}.jsonl").open(
                    "w", encoding="utf-8"
                )
            arquivos[anot.Anotador].write(json.dumps(linha, ensure_ascii=False) + "\n")
            docs, n_spans = contagens.get(anot.Anotador, (0, 0))
            contagens[anot.Anotador] = (docs + 1, n_spans + len(spans or []))
    finally:
        for f in arquivos.values():
            f.close()
    return contagens


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="diretório de saída")
    args = parser.parse_args()
    contagens = exportar(args.out)
    for anotador, (docs, spans) in sorted(contagens.items()):
        print(f"{anotador}: {docs} documentos, {spans} spans -> dataset_{anotador}.jsonl")
    print(f"Saída em {args.out}")


if __name__ == "__main__":
    main()
