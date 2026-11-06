"""Extração de um TAG a partir do PDF de um evento (roda no worker ARQ).

Localiza a peça no banco `processo`, lê o PDF do share (OCR quando é
escaneado, via `frap.ccd.ocr`), pede ao DeepSeek (Foundry do SERPRO, via
`frap.llm`) a estrutura do termo e grava o rascunho em CCDTAG/CCDTAGObrigacao
para revisão humana (`Revisado = 0`). A citação do LLM tem que ser conferida:
o texto integral vai junto (`TextoOCR`) e a tela mostra os dois lado a lado.
"""

from __future__ import annotations

import asyncio
import re
from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ccd.tags import service

_MAX_CHARS = 80_000

_SQL_PECA = """
SELECT p.IdProcesso, p.numero_processo AS numero, p.ano_processo AS ano,
       ppe.IdProcessoEvento AS id_evento, inf.idInformacao AS id_informacao,
       RTRIM(inf.setor) AS setor,
       CONCAT(RTRIM(inf.setor), '_', inf.numero_processo, '_', inf.ano_processo, '_',
              RIGHT(CONCAT('0000', inf.ordem), 4), '.pdf') AS arquivo
FROM dbo.Processos p
JOIN dbo.Pro_ProcessoEvento ppe ON ppe.IdProcesso = p.IdProcesso
JOIN dbo.vw_ata_informacao inf ON inf.idInformacao = ppe.IdInformacao
WHERE p.numero_processo = :numero AND p.ano_processo = :ano
  AND ppe.SequencialProcessoEvento = :evento
"""


class ObrigacaoExtraida(BaseModel):
    clausula: str = Field(
        description="Onde está no termo, ex.: 'Cláusula Segunda, caput', 'Cláusula Segunda, §1º'"
    )
    descricao: str = Field(description="A obrigação, em uma ou duas frases, como o termo a enuncia")
    prazo_texto: Optional[str] = Field(
        None, description="Prazo como escrito, ex.: '120 dias a partir de 1º de agosto de 2025'"
    )
    data_limite: Optional[str] = Field(
        None, description="Data-limite dd/mm/aaaa, se o termo informa ou tem quadro de datas"
    )


class TagExtraido(BaseModel):
    numero: Optional[str] = Field(None, description="Número do termo, ex.: '001/2025-PROC-GRC'")
    orgao: Optional[str] = Field(
        None, description="Órgão/entidade compromitente (quem assume as obrigações)"
    )
    responsavel: Optional[str] = Field(
        None, description="Nome da autoridade que assina pelo compromitente"
    )
    cargo_responsavel: Optional[str] = Field(None, description="Cargo dessa autoridade")
    compromissario: Optional[str] = Field(
        None, description="Quem propõe o termo (ex.: Procurador do Ministério Público de Contas)"
    )
    data_celebracao: Optional[str] = Field(None, description="Data de assinatura dd/mm/aaaa")
    prazo_final: Optional[str] = Field(
        None, description="Última data-limite do termo dd/mm/aaaa (fim da vigência/cumprimento)"
    )
    valor_multa_descumprimento: Optional[float] = Field(
        None, description="Multa por obrigação descumprida, em reais (R$15.000,00 → 15000.0)"
    )
    obrigacoes: list[ObrigacaoExtraida] = Field(default_factory=list)


_PROMPT = """Você lê um Termo de Ajustamento de Gestão (TAG) celebrado entre o Ministério Público de
Contas do RN e um jurisdicionado, para cadastro no CGTAG do TCE/RN (Regimento Interno, art. 351 §3º:
obrigação, autoridade responsável, prazo e sanção). O texto vem de OCR e pode ter erros de leitura.
Extraia:
- numero do termo, orgao compromitente, responsavel (quem assina pelo compromitente) e seu cargo,
  compromissario, data de celebração, valor da multa por descumprimento;
- obrigacoes: UMA entrada por obrigação da cláusula de compromisso (normalmente a Cláusula Segunda):
  o caput é uma obrigação (as alíneas que o detalham entram na descrição dela, resumidas), cada
  parágrafo com dever próprio é outra obrigação. Inclua também as obrigações de comprovar/informar
  o cumprimento quando tiverem data própria (quadro de datas da cláusula de comunicação).
- data_limite de cada obrigação: use o quadro de datas quando existir; senão, calcule só se o termo
  der dia inicial e prazo em dias; senão deixe null. prazo_final = a maior data_limite.
Não invente número, data, valor ou obrigação: o que não estiver no texto fica null.
Datas sempre dd/mm/aaaa.

Texto do termo:
\"\"\"{texto}\"\"\"
"""

_DATA = re.compile(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})")


def parse_data(texto: str | None) -> date | None:
    m = _DATA.search(texto or "")
    if not m:
        return None
    try:
        return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    except ValueError:
        return None


def _llm_chain() -> Any:
    from langchain_core.prompts import PromptTemplate

    from frap.llm import get_llm_client, structured

    llm = get_llm_client(timeout=120)
    if llm is None:
        raise RuntimeError(
            "LLM não configurado: defina AZURE_OPENAI_API_KEY e AZURE_OPENAI_ENDPOINT "
            "(Foundry do SERPRO) para extrair o TAG."
        )
    return PromptTemplate.from_template(_PROMPT) | structured(TagExtraido, llm)


def montar_registro(
    peca: dict[str, Any], evento: int, texto: str, extraido: TagExtraido
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Converte a saída do LLM nas linhas de CCDTAG / CCDTAGObrigacao."""
    obrigacoes = [
        {
            "Clausula": (o.clausula or "não localizada").strip(),
            "Descricao": o.descricao.strip(),
            "PrazoTexto": o.prazo_texto,
            "DataLimite": parse_data(o.data_limite),
        }
        for o in extraido.obrigacoes
        if o.descricao and o.descricao.strip()
    ]
    datas = [o["DataLimite"] for o in obrigacoes if o["DataLimite"]]
    cabecalho = {
        "IdProcesso": int(peca["IdProcesso"]),
        "NumeroProcesso": str(peca["numero"]).strip(),
        "AnoProcesso": int(peca["ano"]),
        "Evento": evento,
        "IdEvento": peca.get("id_evento"),
        "IdInformacao": peca.get("id_informacao"),
        "Numero": (extraido.numero or "não localizado")[:40],
        "Orgao": (extraido.orgao or "não localizado")[:255],
        "Responsavel": (extraido.responsavel or "não localizado")[:255],
        "CargoResponsavel": (extraido.cargo_responsavel or None)
        and extraido.cargo_responsavel[:255],
        "Compromissario": (extraido.compromissario or None) and extraido.compromissario[:255],
        "DataCelebracao": parse_data(extraido.data_celebracao),
        "Prazo": parse_data(extraido.prazo_final) or (max(datas) if datas else None),
        "ValorMultaDescumprimento": extraido.valor_multa_descumprimento,
        "TextoOCR": texto,
        "PayloadLLM": extraido.model_dump_json(),
    }
    return cabecalho, obrigacoes


def extrair_tag(processo: str, evento: int, id_usuario: int | None) -> str:
    from frap.ccd.ocr import LIMIAR, texto_pdf
    from frap.ccd.pdf import informacoes_dir

    from app.db import get_processo_engine
    from app.jobs.tasks import _session_factory

    numero, ano = service.parse_processo(processo)
    with Session(get_processo_engine()) as sp:
        peca = (
            sp.execute(text(_SQL_PECA), {"numero": numero, "ano": ano, "evento": evento})
            .mappings()
            .first()
        )
    if peca is None:
        raise RuntimeError(f"evento {evento} do processo {processo} sem peça no banco processo")
    peca = dict(peca)
    caminho = informacoes_dir() / peca["setor"] / peca["arquivo"]
    if not caminho.exists():
        raise RuntimeError(f"PDF não encontrado no share: {caminho}")
    texto, scores = texto_pdf(caminho)
    texto = texto[:_MAX_CHARS]
    if not texto.strip():
        raise RuntimeError("PDF sem texto legível, nem por OCR")
    extraido: TagExtraido = _llm_chain().invoke({"texto": texto})
    cabecalho, obrigacoes = montar_registro(peca, evento, texto, extraido)
    with _session_factory()() as s:
        if service.existe_ativo(s, cabecalho["IdProcesso"], evento):
            raise RuntimeError("já existe TAG ativo para este processo/evento")
        novo = service.criar(s, cabecalho=cabecalho, obrigacoes=obrigacoes, id_usuario=id_usuario)
    fracas = sum(1 for sc in scores if sc < LIMIAR)
    return (
        f"TAG {cabecalho['Numero']}: {len(obrigacoes)} obrigação(ões) gravadas (id {novo}); "
        f"{len(scores)} página(s), {fracas} com OCR fraco"
    )


async def task_extrair_tag(
    ctx: dict[str, Any], id_frap_job: int, processo: str, evento: int, id_usuario: int | None
) -> str:
    from app.jobs.tasks import _session_factory, _set_done, _set_failed, _set_running

    factory = _session_factory()
    _set_running(factory, id_frap_job)
    try:
        resultado = await asyncio.to_thread(extrair_tag, processo, int(evento), id_usuario)
        _set_done(factory, id_frap_job, resultado)
        return resultado
    except Exception as exc:
        _set_failed(factory, id_frap_job, repr(exc))
        raise
