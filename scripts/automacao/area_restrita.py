"""CLI da automação da Área Restrita do TCE (classe em ccd.area_restrita).

Uso:
    python -m scripts.automacao.area_restrita distribuir 12345/2024 [12346/2024 ...] [--dry-run]
    python -m scripts.automacao.area_restrita informacao 12345/2024 --pdf caminho.pdf [--dry-run]
    python -m scripts.automacao.area_restrita informacao-lote --pasta saidas/x [--dry-run]
    python -m scripts.automacao.area_restrita substituir 12345/2024 [--autor Luzenildo] [--dry-run]
    python -m scripts.automacao.area_restrita tramitar 12345/2024 [--destino DIP] --relator ana [--dry-run]
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

from ccd.area_restrita import GABINETES, AreaRestrita, parse_processo


def main() -> int:
    parser = argparse.ArgumentParser(description="Automação da Área Restrita do TCE")
    sub = parser.add_subparsers(dest="tarefa", required=True)

    p_dist = sub.add_parser("distribuir", help="distribuição própria + iniciar análise")
    p_dist.add_argument("processos", nargs="+", help="numero/ano, ex.: 12345/2024")
    p_dist.add_argument("--dry-run", action="store_true", help="só consulta; não distribui")

    p_info = sub.add_parser("informacao", help="cadastrar informação digitalizada (InformacaoInstrutiva)")
    p_info.add_argument("processos", nargs="+", help="numero/ano, ex.: 12345/2024")
    p_info.add_argument("--pdf", required=True, help="PDF a subir como arquivo digitalizado 1")
    p_info.add_argument("--dry-run", action="store_true", help="só consulta; não sobe nem inclui")

    p_lote = sub.add_parser(
        "informacao-lote",
        help="cadastra informação digitalizada de cada PDF NNNNNN_YYYY.pdf de uma pasta",
    )
    p_lote.add_argument("--pasta", required=True, help="pasta com PDFs NNNNNN_YYYY.pdf (recursivo)")
    p_lote.add_argument("--dry-run", action="store_true", help="só consulta; não sobe nem inclui")

    p_subst = sub.add_parser(
        "substituir",
        help='substituir a informação de um autor pela "Informação instrutiva" mais recente',
    )
    p_subst.add_argument("processos", nargs="+", help="numero/ano, ex.: 12345/2024")
    p_subst.add_argument("--autor", default="Luzenildo",
                         help="autor da informação a substituir (default: Luzenildo)")
    p_subst.add_argument("--data", default=None,
                         help="data de digitação da informação a substituir (ex.: 08/07/2026); "
                              "sem ela, vale a mais recente do autor")
    p_subst.add_argument("--dry-run", action="store_true", help="só mostra o par; não substitui")

    p_tram = sub.add_parser("tramitar", help="tramitar processos EM LOTE do setor atual para o destino")
    p_tram.add_argument("processos", nargs="+", help="numero/ano, ex.: 12345/2024")
    p_tram.add_argument("--destino", default="DIP", help="setor destino (default: DIP)")
    p_tram.add_argument("--relator", choices=sorted(GABINETES),
                        help='usa providência "ENVIO A <gabinete do relator>"')
    p_tram.add_argument("--providencia", help='providência explícita, ex.: "ENVIO A GAANA"')
    p_tram.add_argument("--dry-run", action="store_true", help="vai até o form; não confirma")

    args = parser.parse_args()

    if args.tarefa == "substituir":
        ar = AreaRestrita()
        falhas = 0
        for proc in args.processos:
            try:
                numero, ano = parse_processo(proc)
            except ValueError as e:
                print(e)
                falhas += 1
                continue
            print(f"{numero:06d}/{ano}:")
            try:
                ar.substituir_informacao(numero, ano, args.autor,
                                         data_substituida=args.data, dry_run=args.dry_run)
            except Exception as e:  # segue para o próximo do lote
                print(f"  ERRO: {e}")
                falhas += 1
        return 1 if falhas else 0

    if args.tarefa == "tramitar":
        providencia = args.providencia or (
            args.relator and f"ENVIO A {GABINETES[args.relator]}"
        )
        if not providencia:
            print("informe --relator ou --providencia")
            return 1
        try:
            procs = [parse_processo(proc) for proc in args.processos]
        except ValueError as e:
            print(e)
            return 1
        ar = AreaRestrita()
        try:
            ar.tramitar(procs, args.destino, providencia, dry_run=args.dry_run)
        except Exception as e:
            print(f"ERRO: {e}")
            return 1
        return 0

    if args.tarefa == "informacao-lote":
        pasta = Path(args.pasta)
        if not pasta.is_dir():
            print(f"pasta não encontrada: {pasta}")
            return 1
        alvos: list[tuple[int, int, Path]] = []
        for pdf in sorted(pasta.rglob("*.pdf")):
            m = re.fullmatch(r"(\d{1,6})_(\d{4})", pdf.stem)
            if not m:
                print(f"  ignorado (nome fora do padrão NNNNNN_YYYY): {pdf.name}")
                continue
            alvos.append((int(m.group(1)), int(m.group(2)), pdf))
        if not alvos:
            print(f"nenhum PDF NNNNNN_YYYY.pdf em {pasta}")
            return 1
        ar = AreaRestrita()
        falhas = 0
        for numero, ano, pdf in alvos:
            print(f"{numero:06d}/{ano}: ({pdf.relative_to(pasta)})")
            try:
                ar.cadastrar_informacao_digitalizada(numero, ano, str(pdf), dry_run=args.dry_run)
            except Exception as e:  # segue para o próximo do lote
                print(f"  ERRO: {e}")
                falhas += 1
        return 1 if falhas else 0

    if args.tarefa == "informacao" and not os.path.isfile(args.pdf):
        print(f"PDF não encontrado: {args.pdf}")
        return 1

    ar = AreaRestrita()
    falhas = 0
    for proc in args.processos:
        try:
            numero, ano = parse_processo(proc)
        except ValueError as e:
            print(e)
            falhas += 1
            continue
        print(f"{numero:06d}/{ano}:")
        try:
            if args.tarefa == "distribuir":
                ar.distribuir_propria(numero, ano, dry_run=args.dry_run)
            else:
                ar.cadastrar_informacao_digitalizada(numero, ano, args.pdf, dry_run=args.dry_run)
        except Exception as e:  # segue para o próximo processo do lote
            print(f"  ERRO: {e}")
            falhas += 1
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
