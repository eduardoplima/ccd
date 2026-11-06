"""OCR com autocorreção para PDFs escaneados do share de informações.

Por página: usa a camada de texto nativa se for plausível; senão roda o
Tesseract (por) numa escada de pré-processamentos, mede a qualidade
(confiança ponderada × fração de tokens plausíveis) e para na primeira
variante que passa do limiar. Nenhuma passou → fica a melhor e a página é
marcada de baixa confiança. Porte de `scripts/analise/ocr_processo.py` da
raiz do repo, sem mudar a lógica.

Exige `tesseract` no PATH com o pacote de idioma `por` (Dockerfile.base).
"""

from __future__ import annotations

import io
import re
import subprocess
from collections.abc import Callable
from pathlib import Path

LIMIAR = 80.0  # calibrado: página impressa limpa (014904/2017 p.11) dá ~82
DPI_ALVO = 300
A4_LARGURA_POL = 8.27

_PLAUSIVEL = re.compile(
    r"^[\(\"“]?([A-Za-zÀ-ÿ]*[aeiouáéíóúâêôãõàAEIOUÁÉÍÓÚÂÊÔÃÕ][A-Za-zÀ-ÿ\-]*"
    r"|[A-Za-zÀ-ÿ]{1,3}|[\d.,/\-ºª°%]+|[§º°ª–\-])[\)\"”.,;:!?º°ª]*$"
)


def plausibilidade(texto: str) -> float:
    toks = texto.split()
    return sum(bool(_PLAUSIVEL.match(t)) for t in toks) / len(toks) if toks else 0.0


def score(palavras: list[tuple[str, float]]) -> float:
    """Confiança média ponderada pelo tamanho da palavra × fração de tokens plausíveis."""
    if not palavras:
        return 0.0
    peso = sum(len(w) for w, _ in palavras)
    conf = sum(len(w) * c for w, c in palavras) / peso
    return conf * plausibilidade(" ".join(w for w, _ in palavras))


def tesseract(img, psm: int) -> tuple[str, float]:
    """Roda o Tesseract (TSV) e devolve (texto por linha, score)."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    out = subprocess.run(
        ["tesseract", "stdin", "stdout", "-l", "por", "--psm", str(psm), "tsv"],
        input=buf.getvalue(),
        capture_output=True,
        check=True,
    ).stdout.decode("utf-8", "replace")
    palavras: list[tuple[str, float]] = []
    linhas: dict[tuple[str, str, str], list[str]] = {}
    for row in out.splitlines()[1:]:
        c = row.split("\t")
        if len(c) < 12 or float(c[10]) < 0 or not c[11].strip():
            continue
        palavras.append((c[11], float(c[10])))
        linhas.setdefault((c[2], c[3], c[4]), []).append(c[11])
    texto, bloco_ant = [], None
    for (bloco, _, _), ws in linhas.items():
        if bloco_ant is not None and bloco != bloco_ant:
            texto.append("")
        texto.append(" ".join(ws))
        bloco_ant = bloco
    return "\n".join(texto), score(palavras)


def rotacao_osd(img) -> int:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    r = subprocess.run(
        ["tesseract", "stdin", "stdout", "--psm", "0"], input=buf.getvalue(), capture_output=True
    )
    m = re.search(rb"Rotate: (\d+)", r.stdout)
    return int(m.group(1)) if m else 0


def _cinza(img):
    import numpy as np
    from PIL import Image, ImageOps

    # max dos canais: texto escuro em papel colorido (capas azuis) vira fundo claro
    if img.mode != "L":
        img = Image.fromarray(np.asarray(img.convert("RGB")).max(axis=2))
    return ImageOps.autocontrast(img, cutoff=1)


def _otsu(img):
    import numpy as np
    from PIL import Image

    a = np.asarray(img)
    hist = np.bincount(a.ravel(), minlength=256).astype(float)
    w = hist.cumsum()
    mu = (hist * np.arange(256)).cumsum()
    with np.errstate(divide="ignore", invalid="ignore"):
        var = (mu[-1] * w / w[-1] - mu) ** 2 / (w * (w[-1] - w))
    t = int(np.nanargmax(var))
    return Image.fromarray(((a > t) * 255).astype(np.uint8))


def _escala(img, fator: float):
    from PIL import Image

    return img.resize(
        (round(img.width * fator), round(img.height * fator)), Image.Resampling.LANCZOS
    )


def escada(fator: float) -> list[tuple[str, Callable, int]]:
    from PIL import ImageFilter

    f2 = fator * 4 / 3
    return [
        (f"x{fator:.1f} cinza psm6", lambda i: _cinza(_escala(i, fator)), 6),
        (
            f"x{fator:.1f} otsu+sharpen psm6",
            lambda i: _otsu(_cinza(_escala(i, fator)).filter(ImageFilter.SHARPEN)),
            6,
        ),
        (f"x{f2:.1f} cinza psm4", lambda i: _cinza(_escala(i, f2)), 4),
        (f"x{f2:.1f} cinza psm3", lambda i: _cinza(_escala(i, f2)), 3),
        # desfoque leve funde retícula/pontilhado (telas impressas, fundo cinza) antes do OCR
        (
            f"x{fator:.1f} desfoque psm4",
            lambda i: _cinza(_escala(i, fator)).filter(ImageFilter.GaussianBlur(1)),
            4,
        ),
        (
            f"x{fator:.1f} desfoque+otsu psm4",
            lambda i: _otsu(_cinza(_escala(i, fator)).filter(ImageFilter.GaussianBlur(1))),
            4,
        ),
    ]


def imagem_da_pagina(doc, page):
    import pymupdf as fitz
    from PIL import Image

    imgs = page.get_images()
    if len(imgs) == 1:  # página escaneada: pega a imagem original, sem reamostrar
        pix = fitz.Pixmap(doc, imgs[0][0])
        if pix.n - pix.alpha > 3:
            pix = fitz.Pixmap(fitz.csRGB, pix)
        return Image.open(io.BytesIO(pix.tobytes("png")))
    return Image.open(io.BytesIO(page.get_pixmap(dpi=DPI_ALVO).tobytes("png")))


def ocr_pagina(img) -> tuple[str, float, str]:
    dpi = img.width / A4_LARGURA_POL
    fator = min(max(DPI_ALVO / dpi, 1.0), 4.0)
    melhor = ("", -1.0, "")
    passos = escada(fator)
    for nome, prep, psm in passos:
        texto, s = tesseract(prep(img), psm)
        if s > melhor[1]:
            melhor = (texto, s, nome)
        if s >= LIMIAR:
            return melhor
    rot = rotacao_osd(_cinza(_escala(img, fator)))
    if rot:
        img = img.rotate(-rot, expand=True)
        for nome, prep, psm in passos[:2]:
            texto, s = tesseract(prep(img), psm)
            if s > melhor[1]:
                melhor = (texto, s, f"rot{rot} {nome}")
            if s >= LIMIAR:
                break
    return melhor


def texto_pdf(path: Path) -> tuple[str, list[float]]:
    """Texto de todas as páginas: camada nativa se plausível, senão OCR.

    Devolve (texto com separadores '--- página N ---', score por página;
    100 = texto nativo). Página abaixo de `LIMIAR` merece conferência.
    """
    import pymupdf as fitz

    doc = fitz.open(path)
    partes: list[str] = []
    scores: list[float] = []
    for n, page in enumerate(doc, 1):
        nativo = page.get_text().strip()
        if len(nativo) >= 200 and plausibilidade(nativo) >= 0.9:
            texto, s = nativo, 100.0
        else:
            texto, s, _ = ocr_pagina(imagem_da_pagina(doc, page))
        partes.append(f"--- página {n} ---\n{texto}")
        scores.append(s)
    return "\n\n".join(partes), scores
