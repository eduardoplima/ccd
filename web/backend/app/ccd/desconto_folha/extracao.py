"""Extração do valor da resposta do órgão (roda no worker ARQ).

Lê os PDFs dos apensados do processo (ou das respostas digitalizadas no
próprio principal) no share, pergunta ao DeepSeek (Foundry
do SERPRO, via `frap.llm`) o valor total e as parcelas, confere que o trecho
citado existe no texto (a LLM inventa citação com confiança) e grava o
resultado no cadastro. Depois tenta o match automático no FRAP.
"""

from __future__ import annotations

import difflib
import re
import unicodedata
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.ccd.desconto_folha import match, processo_lookup
from app.config import get_settings

_MAX_CHARS = 60_000


class ParcelaExtraida(BaseModel):
    numero: int = Field(description="Número sequencial da parcela, começando em 1")
    mes: Optional[int] = Field(None, description="Mês de competência (1-12), se informado")
    ano: Optional[int] = Field(None, description="Ano de competência, se informado")
    valor: Optional[float] = Field(None, description="Valor da parcela em reais")


class RespostaDescontoFolha(BaseModel):
    encontrou: bool = Field(
        description="True só se o texto informa o valor efetivamente descontado/implantado em folha"
    )
    valor_total: Optional[float] = Field(
        None, description="Valor total descontado ou a descontar, em reais (ex.: 2477.35)"
    )
    parcelado: bool = Field(False, description="True se o desconto é em parcelas mensais")
    parcelas: list[ParcelaExtraida] = Field(
        default_factory=list, description="Parcelas, quando parcelado; vazio quando valor único"
    )
    trecho: str = Field(
        "", description="Cópia literal do trecho do texto que informa o valor (uma frase)"
    )


_PROMPT = """Você lê a resposta de um órgão público a uma notificação do TCE/RN para desconto em folha
de pagamento de uma multa ou débito. Extraia SOMENTE o que o texto afirma sobre o valor do desconto:
- valor total descontado/implantado (ou a implantar) em folha;
- se é parcelado, cada parcela com competência (mês/ano) quando o texto informar;
- o trecho literal (uma frase, copiada exatamente) de onde tirou o valor.
Não invente valores nem competências. Se o texto não informa o valor do desconto em folha
(ex.: só acusa recebimento, ou nega vínculo), responda encontrou=false e deixe o resto vazio.
Valores em reais no formato numérico (R$2.477,35 → 2477.35).

Texto:
\"\"\"{texto}\"\"\"
"""


def _normalizar(texto: str) -> str:
    t = texto.replace("ﬁ", "fi").replace("ﬂ", "fl")
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", t).lower().strip()


def trecho_confere(trecho: str, texto: str, minimo: int = 15, tolerancia: float = 0.8) -> bool:
    """O trecho citado tem que aparecer no texto normalizado.

    Literal primeiro; senão, ao menos `tolerancia` do trecho casa em blocos de
    10+ caracteres. ponytail: cobre PDFs que perdem ligaduras ("ins tuida") e
    tabelas quebradas; medido no lote de 09/2026: reais >= 0,93, inventado <= 0,49.
    """
    t = _normalizar(trecho)[:120]
    if len(t) < minimo:
        return False
    n = _normalizar(texto)
    if t[:60] in n:
        return True
    blocos = difflib.SequenceMatcher(None, t, n, autojunk=False).get_matching_blocks()
    return sum(b.size for b in blocos if b.size >= 10) / len(t) >= tolerancia


def _session_factory() -> sessionmaker[Session]:
    engine = create_engine(get_settings().database_url, future=True, pool_pre_ping=True)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def _llm_chain() -> Any:
    from langchain_core.prompts import PromptTemplate

    from frap.llm import get_llm_client, structured

    llm = get_llm_client()
    if llm is None:
        raise RuntimeError(
            "LLM não configurado: defina AZURE_OPENAI_API_KEY e AZURE_OPENAI_ENDPOINT "
            "(Foundry do SERPRO) para extrair a resposta."
        )
    return PromptTemplate.from_template(_PROMPT) | structured(RespostaDescontoFolha, llm)


def _texto_dos_pdfs(infos: list[dict[str, Any]]) -> tuple[str, list[str]]:
    from frap.ccd.pdf import extract_text_from_pdf, informacoes_dir

    base = informacoes_dir()
    partes: list[str] = []
    arquivos: list[str] = []
    for i in infos:
        caminho = base / i["setor"] / i["arquivo"]
        texto = extract_text_from_pdf(caminho)
        if texto.strip():
            partes.append(f"=== {i['arquivo']} (evento {i['evento']})\n{texto}")
            arquivos.append(i["arquivo"])
    return "\n\n".join(partes)[:_MAX_CHARS], arquivos


def competencias_em_sequencia(
    linhas: list[tuple[int, int | None, int | None, float]],
) -> list[tuple[int, int | None, int | None, float]]:
    """Preenche mês/ano das parcelas seguintes a partir da primeira informada.

    O ofício diz "a partir do contracheque de fevereiro/2026" e a LLM só marca a
    primeira; parcelas mensais seguem em sequência. Só preenche buracos.
    """
    out: list[tuple[int, int | None, int | None, float]] = []
    mes = ano = None
    for numero, m, a, valor in linhas:
        if m and a:
            mes, ano = int(m), int(a)
        elif mes and ano:
            mes += 1
            if mes > 12:
                mes, ano = 1, ano + 1
            m, a = mes, ano
        out.append((numero, m, a, valor))
    return out


def _gravar(
    session: Session,
    *,
    id_cadastro: int,
    status: str,
    apensado: dict[str, Any] | None,
    evento: int | None,
    arquivos: list[str],
    resposta: RespostaDescontoFolha | None,
) -> None:
    agora = datetime.utcnow().replace(microsecond=0)
    params: dict[str, Any] = {
        "c": id_cadastro,
        "status": status,
        "agora": agora,
        "idp": apensado["id_processo"] if apensado else None,
        "num": apensado["numero"] if apensado else None,
        "ano": apensado["ano"] if apensado else None,
        "ev": evento,
        "dr": apensado["data_registro"] if apensado else None,
        "arq": ", ".join(arquivos)[:400] or None,
        "trecho": resposta.trecho if resposta else None,
        "total": resposta.valor_total if resposta else None,
        "parc": 1 if resposta and resposta.parcelado else 0,
    }
    session.execute(
        text(
            """
            UPDATE CCDDescontoFolha SET
                StatusExtracao = :status, DataExtracao = :agora, DataAtualizacao = :agora,
                IdProcessoResposta = COALESCE(:idp, IdProcessoResposta),
                NumeroProcessoResposta = COALESCE(:num, NumeroProcessoResposta),
                AnoProcessoResposta = COALESCE(:ano, AnoProcessoResposta),
                EventoResposta = COALESCE(:ev, EventoResposta),
                DataResposta = COALESCE(:dr, DataResposta),
                ArquivoResposta = :arq, TrechoResposta = :trecho,
                ValorTotal = :total, Parcelado = :parc
            WHERE IdCCDDescontoFolha = :c
            """
        ),
        params,
    )
    # Só os valores da LLM são substituídos; os manuais ficam.
    session.execute(
        text(
            "DELETE FROM CCDDescontoFolhaMatch WHERE IdCCDDescontoFolhaValor IN "
            "(SELECT IdCCDDescontoFolhaValor FROM CCDDescontoFolhaValor "
            " WHERE IdCCDDescontoFolha = :c AND Origem = 'L')"
        ),
        {"c": id_cadastro},
    )
    session.execute(
        text("DELETE FROM CCDDescontoFolhaValor WHERE IdCCDDescontoFolha = :c AND Origem = 'L'"),
        {"c": id_cadastro},
    )
    if resposta and resposta.encontrou:
        linhas = (
            competencias_em_sequencia(
                [
                    (p.numero, p.mes, p.ano, p.valor)
                    for p in resposta.parcelas
                    if p.valor and p.valor > 0
                ]
            )
            if resposta.parcelado and resposta.parcelas
            else ([(1, None, None, resposta.valor_total)] if resposta.valor_total else [])
        )
        for numero, mes, ano, valor in linhas:
            session.execute(
                text(
                    "INSERT INTO CCDDescontoFolhaValor "
                    "(IdCCDDescontoFolha, NumeroParcela, MesReferencia, AnoReferencia, Valor, Origem) "
                    "VALUES (:c, :n, :m, :a, :v, 'L')"
                ),
                {"c": id_cadastro, "n": numero, "m": mes, "a": ano, "v": round(float(valor), 2)},
            )
    session.commit()


def extrair_resposta(id_cadastro: int) -> str:
    """Pipeline completo para um cadastro. Devolve um resumo legível para o job."""
    from app.db import get_processo_engine

    factory = _session_factory()
    with factory() as s:
        cad = (
            s.execute(
                text(
                    "SELECT IdProcesso, RTRIM(NumeroProcesso) AS numero, RTRIM(AnoProcesso) AS ano, "
                    "NumeroNotificacao, DataNotificacao "
                    "FROM CCDDescontoFolha WHERE IdCCDDescontoFolha = :c AND Ativo = 1"
                ),
                {"c": id_cadastro},
            )
            .mappings()
            .first()
        )
    if cad is None:
        raise ValueError(f"cadastro {id_cadastro} não encontrado")

    with Session(get_processo_engine()) as sp:
        apensos = processo_lookup.apensados(sp, int(cad["IdProcesso"]))
        infos_principal = processo_lookup.informacoes(sp, cad["numero"], cad["ano"])
        # Fontes: apensados (resposta autuada à parte) e, sem apensado ou além dele,
        # respostas digitalizadas no próprio principal (caso IPERN/ALRN/prefeituras).
        fontes = apensos + processo_lookup.respostas_no_principal(
            infos_principal,
            id_processo=int(cad["IdProcesso"]),
            numero=cad["numero"],
            ano=cad["ano"],
            numero_notificacao=cad["NumeroNotificacao"],
            data_notificacao=cad["DataNotificacao"],
        )
        textos = [
            (
                f,
                *_texto_dos_pdfs(
                    f["infos"]
                    if "infos" in f
                    else processo_lookup.informacoes(sp, f["numero"], f["ano"])
                ),
            )
            for f in fontes
        ]

    if not fontes:
        with factory() as s:
            _gravar(
                s,
                id_cadastro=id_cadastro,
                status="SEM_RESPOSTA",
                apensado=None,
                evento=None,
                arquivos=[],
                resposta=None,
            )
        return "sem apensado nem resposta no principal"

    chain = _llm_chain()
    ultimo_erro: str | None = None
    for ap, texto_ap, arquivos in textos:
        if not texto_ap:
            continue
        resposta: RespostaDescontoFolha = chain.invoke({"texto": texto_ap})
        evento = (
            int(ap["evento"])
            if "evento" in ap
            else processo_lookup.evento_apensamento(infos_principal, ap["data_registro"])
        )
        if not resposta.encontrou:
            continue
        if not trecho_confere(resposta.trecho, texto_ap):
            ultimo_erro = f"trecho citado não encontrado em {ap['numero']}/{ap['ano']}"
            with factory() as s:
                _gravar(
                    s,
                    id_cadastro=id_cadastro,
                    status="ERRO",
                    apensado=ap,
                    evento=evento,
                    arquivos=arquivos,
                    resposta=None,
                )
            continue
        with factory() as s:
            _gravar(
                s,
                id_cadastro=id_cadastro,
                status="OK",
                apensado=ap,
                evento=evento,
                arquivos=arquivos,
                resposta=resposta,
            )
            n = match.match_automatico(s, id_cadastro=id_cadastro)
        return (
            f"resposta em {ap['numero']}/{ap['ano']} (evento {evento}): "
            f"R$ {resposta.valor_total or 0:,.2f}, {len(resposta.parcelas) or 1} valor(es), "
            f"{n} match(es) automático(s)"
        )

    if ultimo_erro:
        return ultimo_erro
    ap = fontes[0]
    with factory() as s:
        _gravar(
            s,
            id_cadastro=id_cadastro,
            status="SEM_RESPOSTA",
            apensado=ap,
            evento=(
                int(ap["evento"])
                if "evento" in ap
                else processo_lookup.evento_apensamento(infos_principal, ap["data_registro"])
            ),
            arquivos=[],
            resposta=None,
        )
    return "nenhuma resposta informa o valor do desconto"
