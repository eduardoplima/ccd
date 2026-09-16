"""Localiza a notificação ao órgão e o seu recebimento no processo de execução.

Três gerações de fluxo convivem nos cadastros (levantamento de 15/09/2026):
- 2017–2018: DE_MANDA/DAE_MANDA "NOTIFICAÇÃO PARA DESCONTO EM FOLHA", via postal,
  AR digitalizado depois (AR_Digitalizado_Retorno / retornoAR.doc).
- 2023–2025: "MANDADO_NOTIFICAÇÃO_*_VIA POSTAL", idem.
- 2026 (Res. 025/2025): DE "(NOVO) 8_Mandado_Notificação" eletrônico; recebimento
  pela "CERTIDÃO DE RECEBIMENTO DE COMUNICAÇÃO ELETRÔNICA" ou "RECEBIMENTO TÁCITO".

O número da notificação só existe no PDF (Cit_Citacoes não registra
notificações nesses processos); o fallback é Cit_Certidao Classe 'NOT'.
Sem o share de PDFs (backend fora do worker) tudo continua funcionando, só
sem número/tipo-por-texto/data-do-PDF.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ccd.desconto_folha import processo_lookup

_NUMERO_RE = re.compile(
    r"(?:MANDADO\s+DE\s+)?NOTIFICA[ÇC][ÃA]O\s*(?:N\s*[º°o.]*\s*)?(\d{6})\s*/?\s*(\d{4})",
    re.IGNORECASE,
)
_DATA_RECEBIMENTO_RE = re.compile(
    r"(?:recebid[ao]\s+pelo\s+destinat[áa]rio|t[áa]cito.{0,80}?)\s+em\s+(\d{2}/\d{2}/\d{4})",
    re.IGNORECASE | re.DOTALL,
)
_INICIO_PRAZO_RE = re.compile(r"In[ií]cio\s+do\s+prazo\s+(\d{2}/\d{2}/\d{4})", re.IGNORECASE)
_COPIA_DA_ORIGEM = "evento do processo original"
_AR_NOMES = {"ar_digitalizado_retorno", "retornoar.doc"}
_CERTIDAO_DE_NOMES = {"certidão", "certidao", "processo_certidaodiretoriaexpediente_tce.doc"}


# ----- funções puras --------------------------------------------------------


def numero_da_notificacao(texto: str) -> Optional[str]:
    """'MANDADO DE NOTIFICAÇÃO 000933/2026 - DE' / 'NOTIFICAÇÃO Nº 001904 / 2025' -> '000933/2026'."""
    m = _NUMERO_RE.search(texto or "")
    return f"{m.group(1)}/{m.group(2)}" if m else None


def tipo_da_notificacao(nome: str, texto: str = "") -> str:
    """E (eletrônica, e-TCE) ou F (física, via postal)."""
    n, t = (nome or "").upper(), (texto or "").lower()
    if "(NOVO)" in n or "e-tce" in t or "eletrônic" in t or "eletronic" in t:
        return "E"
    return "F"


def data_recebimento(texto: str) -> Optional[datetime]:
    m = _DATA_RECEBIMENTO_RE.search(texto or "")
    return datetime.strptime(m.group(1), "%d/%m/%Y") if m else None


def data_inicio_prazo(texto: str) -> Optional[datetime]:
    m = _INICIO_PRAZO_RE.search(texto or "")
    return datetime.strptime(m.group(1), "%d/%m/%Y") if m else None


def classificar_recebimento(nome: str) -> Optional[str]:
    """E certidão eletrônica / T tácito / AR aviso de recebimento / None."""
    n = (nome or "").strip().lower()
    if n in _AR_NOMES:
        return "AR"
    if "recebimento" in n and "eletr" in n:
        return "T" if "tácito" in n or "tacito" in n else "E"
    return None


def eh_notificacao(info: dict[str, Any]) -> bool:
    nome = str(info.get("nome_informacao") or "").upper()
    if "NOTIFICA" not in nome or str(info.get("setor") or "").upper() == "CCD":
        return False
    return not nome.startswith(("VOLUME_DIGITALIZADO", "AR_"))


def _nativa(info: dict[str, Any]) -> bool:
    """Descarta cópias da origem ('Evento do Processo Original') e informações inativas."""
    if str(info.get("resumo") or "").strip().lower() == _COPIA_DA_ORIGEM:
        return False
    return not info.get("Inativa")


# ----- PDF ------------------------------------------------------------------


def _texto(info: dict[str, Any]) -> str:
    """Texto do PDF no share; '' se o arquivo não existir (backend sem o share) ou falhar."""
    try:
        from frap.ccd.pdf import extract_text_from_pdf, informacoes_dir

        caminho: Path = informacoes_dir() / str(info["setor"]) / str(info["arquivo"])
        if not caminho.exists():
            return ""
        return extract_text_from_pdf(caminho) or ""
    except Exception:
        return ""


# ----- localização ----------------------------------------------------------


def _vazio() -> dict[str, Any]:
    return {
        "NumeroNotificacao": None,
        "DataNotificacao": None,
        "TipoNotificacao": None,
        "EventoNotificacao": None,
        "IdEventoNotificacao": None,
        "NumeroPostagemAr": None,
        "DataAr": None,
        "TipoRecebimento": None,
        "EventoRecebimento": None,
        "IdEventoRecebimento": None,
    }


def _certidao_not(session: Session, numero: str, ano: str) -> Optional[tuple[str, datetime]]:
    row = session.execute(
        text(
            """
            SELECT TOP 1 NumeroCitacao, AnoCitacao, DataInclusao FROM dbo.Cit_Certidao
            WHERE Numero_processo = :numero AND Ano_processo = :ano AND Classe = 'NOT'
              AND inativo IS NULL AND NumeroCitacao IS NOT NULL
            ORDER BY DataInclusao DESC
            """
        ),
        {"numero": numero, "ano": ano},
    ).first()
    if not row:
        return None
    return f"{str(row[0]).strip()}/{str(row[1]).strip()}", row[2]


def localizar(
    session: Session, *, id_processo: int, numero: str, ano: str, id_origem: int | None
) -> dict[str, Any]:
    """Notificação (última do processo) e o recebimento que a segue.

    Sobrepõe-se ao `processo_lookup.notificacao/ar` antigo, que fica como fallback.
    """
    out = _vazio()
    infos = [i for i in processo_lookup.informacoes(session, numero, ano) if _nativa(i)]
    infos.sort(key=lambda i: (i.get("data_resumo") or datetime.min, int(i.get("ordem") or 0)))

    notif = next((i for i in reversed(infos) if eh_notificacao(i)), None)
    if notif is not None:
        texto = _texto(notif)
        out.update(
            NumeroNotificacao=numero_da_notificacao(texto),
            DataNotificacao=notif.get("data_resumo"),
            TipoNotificacao=tipo_da_notificacao(str(notif.get("nome_informacao") or ""), texto),
            EventoNotificacao=int(notif["evento"]) if notif.get("evento") is not None else None,
            IdEventoNotificacao=int(notif["id_evento"]) if notif.get("id_evento") else None,
        )
    if not out["NumeroNotificacao"]:
        cert = _certidao_not(session, numero, ano)
        if cert:
            out["NumeroNotificacao"] = cert[0]
            out["DataNotificacao"] = out["DataNotificacao"] or cert[1]
    antigo = processo_lookup.notificacao(
        session, numero=numero, ano=ano, id_processo=id_processo, id_origem=id_origem
    )
    if notif is None:
        out["NumeroNotificacao"] = out["NumeroNotificacao"] or antigo["numero"]
        out["DataNotificacao"] = out["DataNotificacao"] or antigo["data"]

    # recebimento: primeira informação depois da notificação
    marco = (notif or {}).get("data_resumo") or datetime.min
    depois = [i for i in infos if notif is None or (i.get("data_resumo") or datetime.min) > marco]
    receb = next((i for i in depois if classificar_recebimento(i.get("nome_informacao"))), None)
    if receb is not None:
        texto = _texto(receb)
        out.update(
            TipoRecebimento=classificar_recebimento(receb.get("nome_informacao")),
            DataAr=data_recebimento(texto) or receb.get("data_resumo"),
            EventoRecebimento=int(receb["evento"]) if receb.get("evento") is not None else None,
            IdEventoRecebimento=int(receb["id_evento"]) if receb.get("id_evento") else None,
        )
    else:
        for cert_de in depois:
            if str(cert_de.get("setor") or "").upper() != "DE_EXP":
                continue
            if str(cert_de.get("nome_informacao") or "").strip().lower() not in _CERTIDAO_DE_NOMES:
                continue
            inicio = data_inicio_prazo(_texto(cert_de))
            if inicio:
                out.update(
                    TipoRecebimento="DE",
                    DataAr=inicio,
                    EventoRecebimento=int(cert_de["evento"])
                    if cert_de.get("evento") is not None
                    else None,
                    IdEventoRecebimento=int(cert_de["id_evento"])
                    if cert_de.get("id_evento")
                    else None,
                )
                break
    # postagem/entrega do AR pelas tabelas Cit_* (raro nas notificações, mas grátis)
    ar = processo_lookup.ar(
        session,
        id_informacao=antigo["id_informacao"],
        id_citacao=antigo["id_citacao"],
        numero_postagem=antigo["numero_postagem"],
    )
    out["NumeroPostagemAr"] = ar["numero_postagem"]
    if out["DataAr"] is None and ar["data"] is not None:
        out["DataAr"], out["TipoRecebimento"] = ar["data"], "AR"
    return out
