from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth.models import Usuario
from app.config import get_settings
from app.deps import get_current_user
from app.wiki.schemas import WikiPage, WikiPageMeta, WikiPageUpdate, WikiSearchHit

router = APIRouter(prefix="/api/v1/wiki", tags=["wiki"])

# Páginas versionadas no repo (entram na imagem via COPY backend/).
WIKI_ROOT = Path(__file__).resolve().parents[2] / "wiki"

_SLUG_RE = re.compile(r"[\w-]+(/[\w-]+)*")


def _edits_dir() -> Path | None:
    """Overlay de edições feitas pela UI. Vazio em dev = escreve direto no repo."""
    d = get_settings().wiki_edits_dir
    return Path(d) if d else None


def _page_file(root: Path, slug: str) -> Path:
    if not _SLUG_RE.fullmatch(slug):
        raise HTTPException(status_code=404, detail="page not found")
    f = (root / f"{slug}.md").resolve()
    if not f.is_relative_to(root.resolve()):
        raise HTTPException(status_code=404, detail="page not found")
    return f


def _resolve(slug: str) -> tuple[Path, bool]:
    """Arquivo efetivo da página: override (se houver) senão o do repo."""
    edits = _edits_dir()
    if edits is not None:
        f = _page_file(edits, slug)
        if f.is_file():
            return f, True
    f = _page_file(WIKI_ROOT, slug)
    if f.is_file():
        return f, False
    raise HTTPException(status_code=404, detail="page not found")


def _title(content: str, slug: str) -> str:
    for line in content.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return slug


def _all_slugs() -> dict[str, bool]:
    """slug -> tem override."""
    slugs: dict[str, bool] = {}
    for f in sorted(WIKI_ROOT.rglob("*.md")):
        slugs[f.relative_to(WIKI_ROOT).with_suffix("").as_posix()] = False
    edits = _edits_dir()
    if edits is not None and edits.is_dir():
        for f in sorted(edits.rglob("*.md")):
            slugs[f.relative_to(edits).with_suffix("").as_posix()] = True
    return slugs


def _norm(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s.casefold()) if not unicodedata.combining(c)
    )


@router.get("/pages", response_model=list[WikiPageMeta])
def listar_paginas(_: Usuario = Depends(get_current_user)) -> list[WikiPageMeta]:
    out = []
    for slug, editado in sorted(_all_slugs().items()):
        content = _resolve(slug)[0].read_text(encoding="utf-8")
        out.append(WikiPageMeta(slug=slug, title=_title(content, slug), editado=editado))
    return out


@router.get("/search", response_model=list[WikiSearchHit])
def buscar(
    q: str = Query(min_length=2, max_length=200),
    _: Usuario = Depends(get_current_user),
) -> list[WikiSearchHit]:
    needle = _norm(q)
    hits = []
    for slug in sorted(_all_slugs()):
        content = _resolve(slug)[0].read_text(encoding="utf-8")
        pos = _norm(content).find(needle)
        if pos < 0:
            continue
        # _norm preserva o comprimento (só remove combinantes de NFD sobre o casefold),
        # então pos é aproximado no texto original; bom o suficiente para snippet.
        start, end = max(0, pos - 60), pos + len(needle) + 60
        snippet = " ".join(content[start:end].split())
        hits.append(WikiSearchHit(slug=slug, title=_title(content, slug), snippet=snippet))
    return hits


@router.get("/pages/{slug:path}", response_model=WikiPage)
def obter_pagina(slug: str, _: Usuario = Depends(get_current_user)) -> WikiPage:
    f, editado = _resolve(slug)
    content = f.read_text(encoding="utf-8")
    return WikiPage(slug=slug, title=_title(content, slug), content=content, editado=editado)


@router.put("/pages/{slug:path}", response_model=WikiPage)
def salvar_pagina(
    slug: str,
    body: WikiPageUpdate,
    _: Usuario = Depends(get_current_user),
) -> WikiPage:
    root = _edits_dir() or WIKI_ROOT
    f = _page_file(root, slug)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(body.content, encoding="utf-8")
    return obter_pagina(slug, _)


@router.delete("/pages/{slug:path}/override", status_code=204)
def descartar_override(slug: str, _: Usuario = Depends(get_current_user)) -> None:
    edits = _edits_dir()
    if edits is None:
        raise HTTPException(status_code=404, detail="override not found")
    f = _page_file(edits, slug)
    if not f.is_file():
        raise HTTPException(status_code=404, detail="override not found")
    f.unlink()
