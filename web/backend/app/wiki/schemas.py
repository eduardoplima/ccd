from __future__ import annotations

from pydantic import BaseModel, Field


class WikiPageMeta(BaseModel):
    slug: str
    title: str
    editado: bool


class WikiPage(WikiPageMeta):
    content: str


class WikiPageUpdate(BaseModel):
    content: str = Field(max_length=500_000)


class WikiSearchHit(BaseModel):
    slug: str
    title: str
    snippet: str
