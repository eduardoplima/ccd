"""Junta despacho + decisão do STF (SS 5.749) + certidão de trânsito em envio/NNNNNN_YYYY.pdf.

Mesmos anexos do lote GCREN (processos/projetos/nereu_retomada/anexos/). O texto do despacho cita "documento
anexo" e "anexa certidão"; o cadastro na Área Restrita sobe um único PDF, então o `informacao-lote`
deve apontar para a pasta envio/.
Rodar: .venv/Scripts/python.exe processos/projetos/nereu_retomada_gcaed/montar_envio.py
"""
from pathlib import Path

from ccd.pdf import extract_text_from_pdf, merge_pdfs

BASE = Path(__file__).parent
ANEXOS_DIR = BASE.parent / "nereu_retomada" / "anexos"
ANEXOS = [ANEXOS_DIR / "decisao_STF_SS5749_28072026.pdf",
          ANEXOS_DIR / "certidao_transito_SS5749_27082026.pdf"]
ENVIO = BASE / "envio"
ENVIO.mkdir(exist_ok=True)

for pasta in sorted(p for p in BASE.iterdir() if p.is_dir() and p.name[0].isdigit()):
    despacho = pasta / f"{pasta.name}.pdf"
    out = ENVIO / despacho.name
    merge_pdfs([str(despacho), *map(str, ANEXOS)], str(out))
    texto = extract_text_from_pdf(str(out))
    assert f"Processo nº {pasta.name}-TC" in texto, pasta.name
    assert "DEFIRO O PEDIDO E SUSPENDO OS EFEITOS" in texto and "CERTIDÃO DE TRÂNSITO" in texto, pasta.name
    print(f"{out.relative_to(BASE)}: {out.stat().st_size // 1024} KB")
