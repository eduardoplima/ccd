"""Extrai os votos (PDF -> .md) dos processos com decisão desde 01/01/2024.

Corte: acórdãos e decisões monocráticas em vw_ia_votos_acordaos_decisoes,
excluindo atos de pessoal (APO/APP/PEN/ASS/NCE/CTT/CEM/FCO). O voto é o
evento imediatamente anterior ao evento "ACÓRDÃO PADRÃO"/"DECISÃO PADRÃO".

Saída: votos/<codigo_tipo_processo>/<numero>_<ano>_<evento>.md. Resumível:
arquivos já existentes são pulados.

Uso: python scripts/analise/extrair_votos.py [--limit N] [--data-corte 2024-01-01]
"""
from __future__ import annotations

import argparse

from ccd.config import REPO_ROOT
from ccd.db import get_connection, run_query_df
from ccd.pdf import extract_text_from_pdf
from ccd.processo import get_info_file_path

TIPOS_ATOS_PESSOAL = ("APO", "APP", "PEN", "ASS", "NCE", "CTT", "CEM", "FCO")

# lista constante (não é input de usuário) — inline porque text() não expande IN
SQL_CORTE = f"""
SELECT DISTINCT d.NumeroProcesso AS numero, d.AnoProcesso AS ano,
       d.codigo_tipo_processo AS tipo
FROM processo.dbo.vw_ia_votos_acordaos_decisoes d
WHERE d.DataSessao >= :data_corte
  AND d.resultadoTipo IN ('A', 'D')
  AND d.codigo_tipo_processo NOT IN {TIPOS_ATOS_PESSOAL!r}
ORDER BY d.AnoProcesso, d.NumeroProcesso
"""

SQL_EVENTOS = """
SELECT concat(rtrim(inf.setor),'_',inf.numero_processo,'_',inf.ano_processo,'_',RIGHT(concat('0000',inf.ordem),4),'.pdf') as arquivo,
       ppe.SequencialProcessoEvento as evento,
       inf.setor, inf.Titulo_Modelo_informacao as titulo
FROM processo.dbo.vw_ata_informacao inf
INNER JOIN processo.dbo.Pro_ProcessoEvento ppe
    ON inf.idinformacao = ppe.idinformacao
WHERE inf.numero_processo = :numero AND inf.ano_processo = :ano
ORDER BY ppe.SequencialProcessoEvento
"""


def extrair_voto(engine, numero: str, ano: str, tipo: str, out_dir) -> str:
    """Extrai o voto de um processo; retorna 'ok', 'pulado' ou motivo de falha."""
    eventos = run_query_df(SQL_EVENTOS, conn=engine, numero=numero, ano=ano)
    eh_decisao = eventos["titulo"].str.upper().str.contains(
        r"AC.RD.O PADR.O|DECIS.O PADR.O", regex=True, na=False
    )
    if not eh_decisao.any():
        return "sem evento de decisão"
    idx_decisao = eventos.index[eh_decisao][-1]
    if idx_decisao == 0:
        return "decisão é o primeiro evento (sem voto anterior)"
    voto = eventos.loc[idx_decisao - 1]

    destino = out_dir / tipo / f"{numero}_{ano}_{voto['evento']}.md"
    if destino.exists():
        return "pulado"

    if "VOTO" not in str(voto["titulo"]).upper():
        print(f"  aviso {numero}/{ano}: evento anterior não parece voto ({voto['titulo']!r})")

    caminho = get_info_file_path({"setor": voto["setor"], "arquivo": voto["arquivo"]})
    if not caminho.exists():
        return f"PDF ausente no share: {caminho.name}"
    texto = extract_text_from_pdf(caminho)
    if not texto.strip():
        return "PDF sem texto extraível"

    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8")
    return "ok"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None, help="processar só os N primeiros")
    parser.add_argument("--data-corte", default="2024-01-01")
    args = parser.parse_args()

    out_dir = REPO_ROOT / "votos"
    engine = get_connection()
    corte = run_query_df(SQL_CORTE, conn=engine, data_corte=args.data_corte)
    if args.limit:
        corte = corte.head(args.limit)
    print(f"{len(corte)} processos no corte (decisões >= {args.data_corte})")

    contagem: dict[str, int] = {"ok": 0, "pulado": 0, "falha": 0}
    falhas: list[str] = []
    for i, row in enumerate(corte.itertuples(), 1):
        try:
            resultado = extrair_voto(engine, row.numero, row.ano, row.tipo.strip(), out_dir)
        except Exception as exc:  # ponytail: loga e segue; corpus parcial > abortar no meio
            resultado = f"erro: {exc}"
        if resultado in ("ok", "pulado"):
            contagem[resultado] += 1
        else:
            contagem["falha"] += 1
            falhas.append(f"{row.numero}/{row.ano} ({row.tipo.strip()}): {resultado}")
        if i % 100 == 0:
            print(f"  {i}/{len(corte)}...")

    print(f"\nok: {contagem['ok']}  pulados: {contagem['pulado']}  falhas: {contagem['falha']}")
    if falhas:
        log = out_dir / "falhas.log"
        log.write_text("\n".join(falhas), encoding="utf-8")
        print(f"falhas em {log}")


if __name__ == "__main__":
    main()
