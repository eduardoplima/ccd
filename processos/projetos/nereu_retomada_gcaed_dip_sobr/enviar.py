"""Ciclo na Área Restrita do despacho que substitui a peça DIP_SOBR (envio à DAP) no lote GCAED (marcador 6139).

Etapas, nesta ordem (cada uma com --dry-run; sem processos = os 57 do lote):
    tramitar-ida    CCD -> DIP ("ENVIO PARA DIP_SOBR"; a DIP_SOBR recebe manualmente)
    cadastrar       na DIP_SOBR: distribuição própria + informação digitalizada (<numero_ano>/<numero_ano>.pdf)
    (assinar)       python -m scripts.automacao.assinar_informacoes <procs> --cert EDUARDO  (lotes de 20)
    substituir      peça DIP_SOBR antiga (Luzenildo, ordem do banco) -> despacho novo
    tramitar-volta  DIP_SOBR -> CCD

Rodar da raiz: .venv/Scripts/python.exe processos/projetos/nereu_retomada_gcaed_dip_sobr/enviar.py <etapa> [procs]
"""
import argparse
import sys
from pathlib import Path

from ccd.area_restrita import AreaRestrita, parse_processo
from ccd.db import run_query_df

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA.parents[1] / "utils"))
from gerar_despachos_nereu_dip_sobr import SQL_DIP_SOBR  # noqa: E402
from gerar_informacoes_nereu_retomada_gcaed import MARCADOR  # noqa: E402

SETOR = "DIP_SOBR"
AUTOR_ANTIGA = "Luzenildo"
PROV_IDA = "ENVIO PARA DIP_SOBR"  # CCD não tramita direto p/ DIP_SOBR; a DIP encaminha
PROV_VOLTA = "ANÁLISE DE FATO SUPERVENIENTE"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("etapa", choices=["tramitar-ida", "cadastrar", "substituir", "tramitar-volta"])
    ap.add_argument("processos", nargs="*", help="numero/ano; default: os 57 do lote")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    ordens = run_query_df(SQL_DIP_SOBR, marcador=MARCADOR).set_index("processo").ordem
    alvos = args.processos or sorted(ordens.index, key=lambda p: p[-4:] + p)
    fora = set(alvos) - set(ordens.index)
    assert not fora, f"fora do lote: {fora}"
    procs = [parse_processo(p) for p in alvos]

    if args.etapa == "tramitar-ida":
        AreaRestrita("CCD").tramitar(procs, "DIP", PROV_IDA, dry_run=args.dry_run)
        return 0
    if args.etapa == "tramitar-volta":
        AreaRestrita(SETOR).tramitar(procs, "CCD", PROV_VOLTA, dry_run=args.dry_run)
        return 0

    ar = AreaRestrita(SETOR)
    falhas = 0
    for p, (numero, ano) in zip(alvos, procs, strict=True):
        print(f"{p}:")
        try:
            if args.etapa == "cadastrar":
                pdf = PASTA / f"{numero:06d}_{ano}" / f"{numero:06d}_{ano}.pdf"
                assert pdf.is_file(), f"PDF não gerado: {pdf}"
                ar.distribuir_propria(numero, ano, dry_run=args.dry_run)
                ar.cadastrar_informacao_digitalizada(numero, ano, str(pdf), dry_run=args.dry_run)
            else:
                ar.substituir_informacao(numero, ano, AUTOR_ANTIGA, ordem_substituida=int(ordens[p]),
                                         dry_run=args.dry_run)
        except Exception as e:  # segue para o próximo do lote
            print(f"  ERRO: {e}")
            falhas += 1
    print(f"\n{len(alvos) - falhas}/{len(alvos)} ok")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
