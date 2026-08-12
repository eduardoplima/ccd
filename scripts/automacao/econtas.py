"""CLI da automação do e-Contas (classe em ccd.econtas) — sucessor da Área Restrita ASP.

Uso:
    python -m scripts.automacao.econtas certificar [--processo 12345/2024]
    python -m scripts.automacao.econtas consultar 12345/2024 [12346/2024 ...]
    python -m scripts.automacao.econtas tramitar 12345/2024 [--destino DIP] [--dry-run]
    python -m scripts.automacao.econtas informacao 12345/2024 --pdf caminho.pdf [--dry-run]
    python -m scripts.automacao.econtas informacao-lote --pasta saidas/automacao/x [--dry-run]

`certificar` é a bateria somente-leitura: login SSO, dados do operador, setores
e (com --processo) consulta + payloads que tramitar/informacao enviariam.
Assinatura continua em scripts/automacao/assinar_informacoes.py (Web PKI/A3).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

from ccd.econtas import EContas, parse_processo


def certificar(processo: str | None) -> int:
    print("1. login SSO (tceauth /v2/token + tceadmin2 informacoes/login)...")
    ec = EContas()
    op = ec.operador if isinstance(ec.operador, dict) else {}
    print(f"   OK: operador={op.get('nome') or op.get('nomeOperador') or list(op)[:8]}")
    print("2. setores do operador (GetAllSetorByToken)...")
    setores = ec.setores()
    print(f"   OK: {len(setores)} setor(es): {str(setores)[:300]}")
    if processo:
        numero, ano = parse_processo(processo)
        print(f"3. consulta /api/Processo {numero:06d}/{ano}...")
        proc = ec.consultar(numero, ano)
        print(f"   OK: idProcesso={proc.get('idProcesso')} setorAtual={proc.get('setorAtual')!r}")
        print("4. payloads (NADA será enviado):")
        ec.tramitar([(numero, ano)], destino="DIP", dry_run=True)
        ec.cadastrar_informacao_digitalizada(numero, ano, "exemplo.pdf", dry_run=True)
    print("certificação dry-run concluída.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Automação do e-Contas (processos.tce.rn.gov.br)")
    sub = parser.add_subparsers(dest="tarefa", required=True)

    p_cert = sub.add_parser("certificar", help="bateria dry-run: login, setores, consulta, payloads")
    p_cert.add_argument("--processo", help="numero/ano para testar consulta e payloads")

    p_cons = sub.add_parser("consultar", help="consultar processo(s) por número/ano")
    p_cons.add_argument("processos", nargs="+", help="numero/ano, ex.: 12345/2024")

    p_tram = sub.add_parser("tramitar", help="tramitar processo(s) ao setor destino")
    p_tram.add_argument("processos", nargs="+", help="numero/ano, ex.: 12345/2024")
    p_tram.add_argument("--destino", default="DIP", help="setor destino (default: DIP)")
    p_tram.add_argument("--dry-run", action="store_true", help="mostra o payload; não envia")

    p_info = sub.add_parser("informacao", help="cadastrar informação digitalizada (PDF)")
    p_info.add_argument("processos", nargs="+", help="numero/ano, ex.: 12345/2024")
    p_info.add_argument("--pdf", required=True, help="PDF da informação")
    p_info.add_argument("--dry-run", action="store_true", help="mostra o payload; não envia")

    p_lote = sub.add_parser("informacao-lote",
                            help="cadastra informação de cada PDF NNNNNN_YYYY.pdf de uma pasta")
    p_lote.add_argument("--pasta", required=True, help="pasta com PDFs NNNNNN_YYYY.pdf (recursivo)")
    p_lote.add_argument("--dry-run", action="store_true", help="mostra os payloads; não envia")

    args = parser.parse_args()

    if args.tarefa == "certificar":
        return certificar(args.processo)

    if args.tarefa == "informacao" and not os.path.isfile(args.pdf):
        print(f"PDF não encontrado: {args.pdf}")
        return 1

    if args.tarefa == "informacao-lote":
        pasta = Path(args.pasta)
        if not pasta.is_dir():
            print(f"pasta não encontrada: {pasta}")
            return 1
        alvos = []
        for pdf in sorted(pasta.rglob("*.pdf")):
            m = re.fullmatch(r"(\d{1,6})_(\d{4})", pdf.stem)
            if m:
                alvos.append((int(m.group(1)), int(m.group(2)), pdf))
            else:
                print(f"  ignorado (nome fora do padrão NNNNNN_YYYY): {pdf.name}")
        if not alvos:
            print(f"nenhum PDF NNNNNN_YYYY.pdf em {pasta}")
            return 1
        ec = EContas()
        falhas = 0
        for numero, ano, pdf in alvos:
            print(f"{numero:06d}/{ano}: ({pdf.relative_to(pasta)})")
            try:
                ec.cadastrar_informacao_digitalizada(numero, ano, str(pdf), dry_run=args.dry_run)
            except Exception as e:  # segue para o próximo do lote
                print(f"  ERRO: {e}")
                falhas += 1
        return 1 if falhas else 0

    try:
        procs = [parse_processo(p) for p in args.processos]
    except ValueError as e:
        print(e)
        return 1

    ec = EContas()
    if args.tarefa == "tramitar":
        try:
            ec.tramitar(procs, args.destino, dry_run=args.dry_run)
        except Exception as e:
            print(f"ERRO: {e}")
            return 1
        return 0

    falhas = 0
    for numero, ano in procs:
        print(f"{numero:06d}/{ano}:")
        try:
            if args.tarefa == "consultar":
                proc = ec.consultar(numero, ano)
                print(f"  {json.dumps(proc, ensure_ascii=False, default=str)[:400]}")
            else:  # informacao
                ec.cadastrar_informacao_digitalizada(numero, ano, args.pdf, dry_run=args.dry_run)
        except Exception as e:  # segue para o próximo do lote
            print(f"  ERRO: {e}")
            falhas += 1
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
