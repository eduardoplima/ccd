"""Monitoramento das obrigações e recomendações curadas pela revisão do CGAD.

Primeira ação de monitoramento da CCD sobre o acervo curado (as linhas
`approved` de `BdDIP.dbo.ObrigacaoStaging` / `RecomendacaoStaging`). Três
camadas, na ordem:

1. **Triagem** — determinística, em SQL + função pura. Diz, para cada item
   curado, se o prazo já corre, se venceu, ou se não dá para saber.
2. **Varredura** — LLM (DeepSeek do Foundry do SERPRO) lendo as peças
   posteriores à decisão, à procura de prova de cumprimento. É insumo de
   trabalho, não juízo de cumprimento: quem atesta é o Relator
   (Res. 028/2012, art. 31).
3. **Ficha** — um `.md` por processo, para o auditor abrir e começar o caso.

Base normativa: NBASP 100 (ISSAI 100), "Monitoramento", nos princípios
relacionados ao processo de auditoria; NBASP 300 (ISSAI 300), item 42. O
TCE/RN aderiu às NBASP pela Res. 010/2020-TCE. No plano interno: Regimento
Interno, arts. 288, 299 e 431, IV, "c" (CGR); Res. 028/2012, arts. 27 a 35 e
45; Res. 042/2024 (SECEX), art. 32, I e II. Ver POP-CCD-013 na wiki.

Uso:
    python scripts/analise/monitoramento_obrigacoes.py --sem-llm
    python scripts/analise/monitoramento_obrigacoes.py --limite 20
    python scripts/analise/monitoramento_obrigacoes.py --processos 000068/2024
    python scripts/analise/monitoramento_obrigacoes.py --demo
"""
from __future__ import annotations

import argparse
import json
import re
import traceback
import unicodedata
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from ccd.config import read_sql
from ccd.db import get_connection, run_query_df
from ccd.llm import structured as _structured
from ccd.pdf import extract_text_from_pdf
from ccd.processo import get_info_file_path

# --------------------------------------------------------------------------
# Triagem — sem LLM
# --------------------------------------------------------------------------

Situacao = Literal["SEM_TRANSITO", "PRAZO_EM_CURSO", "PRAZO_VENCIDO", "PRAZO_INDETERMINADO"]
Ancora = Literal["transito", "cientificacao", "publicacao", "absoluta"]

SITUACOES: tuple[str, ...] = (
    "SEM_TRANSITO",
    "PRAZO_EM_CURSO",
    "PRAZO_VENCIDO",
    "PRAZO_INDETERMINADO",
)

# O campo `Prazo` é texto livre escrito pelo revisor. A amostra real é muito
# regular ("60 dias úteis após o trânsito em julgado"), mas tem quatro
# variantes que um regex ingênuo perde: inglês ("25 days", vindo do LLM),
# horas ("72h"), número puro ("180") e data absoluta ("2026-06-19").
_RE_ISO = re.compile(r"^\s*(\d{4})-(\d{2})-(\d{2})\s*$")
_RE_HORAS = re.compile(r"(\d+)\s*(?:h\b|horas?\b)", re.IGNORECASE)
_RE_DIAS = re.compile(r"(\d+)\s*(?:\([^)]*\)\s*)?(?:dias?|days?)\b", re.IGNORECASE)
_RE_MESES = re.compile(r"(\d+)\s*(?:\([^)]*\)\s*)?(?:m[eê]s(?:es)?|months?)\b", re.IGNORECASE)
_RE_NUMERO = re.compile(r"^\s*(\d+)\s*$")


@dataclass(frozen=True)
class Prazo:
    """Prazo interpretado a partir do texto livre. `dias=None` = não interpretado."""

    dias: int | None
    uteis: bool
    ancora: Ancora
    data_absoluta: date | None = None


def _ancora_de(texto: str) -> Ancora:
    t = texto.lower()
    if "nsito" in t:  # trânsito / transito, com ou sem acento
        return "transito"
    if "cientific" in t or "intima" in t or "cita" in t:
        return "cientificacao"
    if "public" in t:
        return "publicacao"
    # Sem âncora explícita, o prazo de obrigação de fazer corre do trânsito:
    # a execução se dá em decisão definitiva (Res. 028/2012, art. 27).
    return "transito"


def parse_prazo(texto: str | None) -> Prazo | None:
    """Interpreta o texto livre do prazo. Devolve None quando não dá para ler.

    Nunca inventa prazo: o que não for reconhecido cai em PRAZO_INDETERMINADO
    e vai para leitura humana.
    """
    if texto is None or (isinstance(texto, float) and pd.isna(texto)):
        return None
    t = str(texto).strip()
    if not t:
        return None

    iso = _RE_ISO.match(t)
    if iso:
        ano, mes, dia = (int(g) for g in iso.groups())
        try:
            return Prazo(dias=None, uteis=False, ancora="absoluta", data_absoluta=date(ano, mes, dia))
        except ValueError:
            return None

    # "úteis" aparece com e sem acento; "teis" pega os dois sem normalizar.
    uteis = "teis" in t.lower()
    ancora = _ancora_de(t)

    m = _RE_DIAS.search(t)
    if m:
        return Prazo(dias=int(m.group(1)), uteis=uteis, ancora=ancora)

    m = _RE_MESES.search(t)
    if m:
        # ponytail: mês = 30 dias corridos. Se a diferença importar num caso
        # concreto, trocar por dateutil.relativedelta.
        return Prazo(dias=int(m.group(1)) * 30, uteis=False, ancora=ancora)

    m = _RE_HORAS.search(t)
    if m:
        horas = int(m.group(1))
        return Prazo(dias=max(1, horas // 24), uteis=False, ancora=ancora)

    m = _RE_NUMERO.match(t)
    if m:
        return Prazo(dias=int(m.group(1)), uteis=uteis, ancora=ancora)

    return None


def vencimento(prazo: Prazo | None, data_transito: date | None) -> date | None:
    """Data de vencimento, ou None quando falta a data da âncora."""
    if prazo is None:
        return None
    if prazo.ancora == "absoluta":
        return prazo.data_absoluta
    if prazo.ancora != "transito":
        # Prazo contado da cientificação ou da publicação: o script não tem
        # essa data. Vira PRAZO_INDETERMINADO em vez de um palpite.
        return None
    if data_transito is None or prazo.dias is None:
        return None
    if prazo.uteis:
        # ponytail: busday_offset ignora feriados. Se a diferença importar num
        # caso concreto, plugar o calendário de feriados do TCE.
        alvo = np.busday_offset(np.datetime64(data_transito, "D"), prazo.dias, roll="forward")
        return alvo.astype("datetime64[D]").astype(date)
    return data_transito + timedelta(days=prazo.dias)


def triar(data_transito: date | None, prazo: Prazo | None, hoje: date) -> Situacao:
    """Classifica o item curado. Os quatro ramos cobrem todas as linhas."""
    venc = vencimento(prazo, data_transito)
    if venc is not None:
        return "PRAZO_VENCIDO" if venc < hoje else "PRAZO_EM_CURSO"
    if data_transito is None:
        return "SEM_TRANSITO"
    return "PRAZO_INDETERMINADO"


def _como_data(valor: Any) -> date | None:
    if valor is None or pd.isna(valor):
        return None
    return pd.Timestamp(valor).date()


def carregar_curadas(engine: Any, status: str = "approved") -> pd.DataFrame:
    """Lê o acervo curado com o contexto processual e aplica a triagem."""
    df = run_query_df(read_sql("obrigacoes_curadas.sql"), engine, status=status)
    hoje = date.today()

    prazos = list(df["prazo_texto"].apply(parse_prazo))
    transitos = list(df["data_transito"].apply(_como_data))

    df["prazo_dias"] = [p.dias if p else None for p in prazos]
    df["prazo_uteis"] = [bool(p.uteis) if p else False for p in prazos]
    df["prazo_ancora"] = [p.ancora if p else "" for p in prazos]
    df["data_vencimento"] = [vencimento(p, t) for p, t in zip(prazos, transitos, strict=True)]
    df["situacao"] = [triar(t, p, hoje) for p, t in zip(prazos, transitos, strict=True)]
    df["arquivado"] = df["setor_atual"].fillna("").str.upper().eq("ARQUI")
    df["sem_cgr"] = df["tem_cgr"].fillna(0).astype(int).eq(0)
    return df


def ordem_de_prioridade(df: pd.DataFrame) -> list[str]:
    """Processos ordenados pela urgência do monitoramento.

    Prazo vencido antes de tudo; dentro dele, os arquivados primeiro (ninguém
    está olhando) e os que não têm registro no CGR na frente dos que têm.
    """
    peso = pd.DataFrame({
        "processo": df["processo"],
        "vencido": df["situacao"].eq("PRAZO_VENCIDO").astype(int),
        "arquivado": df["arquivado"].astype(int),
        "sem_cgr": df["sem_cgr"].astype(int),
    })
    agg = peso.groupby("processo").max().sort_values(
        ["vencido", "arquivado", "sem_cgr"], ascending=False
    )
    return list(agg.index)


# --------------------------------------------------------------------------
# Varredura — LLM
# --------------------------------------------------------------------------

SYSTEM_PROMPT = """Você examina as peças de um processo do TCE/RN para dizer se há, nos autos, PROVA de cumprimento das obrigações e recomendações fixadas na decisão.

# Sua tarefa
Para CADA item listado (cada um tem um `id_staging`), diga o que as peças mostram:
- CUMPRIDA — há nos autos documento que comprova o cumprimento.
- NAO_CUMPRIDA — há nos autos manifestação expressa de descumprimento, ou certidão/parecer que o afirme.
- SEM_ELEMENTOS — as peças apresentadas não permitem concluir.

# Regra central de honestidade
SEM_ELEMENTOS é o padrão. Ausência de prova nos autos NÃO é prova de descumprimento — só use NAO_CUMPRIDA quando alguma peça afirmar o descumprimento, nunca por silêncio dos autos.

# Demais regras
- Cite literalmente o trecho que fundamenta a resposta, e em `fonte` informe o nome do arquivo de origem (o material vem com marcadores `=== Arquivo: <nome>.pdf (setor: <setor>) ===` antes de cada peça).
- Trecho que você não encontrar literalmente no material: deixe `trecho` vazio e responda SEM_ELEMENTOS. Não parafraseie como se fosse citação.
- Use confiança BAIXA quando a resposta depender de inferência ampla.
- `proximo_ato`: uma frase curta com a providência que a CCD deveria adotar (ex.: "cobrar comprovação do item 3", "certificar cumprimento e arquivar", "instaurar processo de monitoramento").
- Devolva exatamente um item para cada `id_staging` recebido, sem inventar outros.
- Responda em pt-BR.
"""


class AvaliacaoItem(BaseModel):
    id_staging: int = Field(description="O id_staging do item avaliado, copiado da lista recebida.")
    situacao_cumprimento: Literal["CUMPRIDA", "NAO_CUMPRIDA", "SEM_ELEMENTOS"]
    trecho: str = Field(default="", description="Citação literal da peça que fundamenta a resposta.")
    fonte: str = Field(default="", description="Nome do arquivo PDF que contém o trecho.")
    confianca: Literal["ALTA", "MEDIA", "BAIXA"]
    proximo_ato: str = Field(default="", description="Providência sugerida à CCD, em uma frase.")
    # Preenchido pelo script, não pelo modelo (ver conferir_trechos).
    trecho_conferido: bool = True


class RelatorioMonitoramento(BaseModel):
    processo: str
    avaliacoes: list[AvaliacaoItem] = Field(default_factory=list)
    pecas_lidas: int = 0
    pecas_disponiveis: int = 0
    truncado: bool = False
    observacao: str = ""


# Peças que nunca provam cumprimento — ruído puro no orçamento de contexto.
_RUIDO = (
    "apensamento",
    "ar_digitalizado",
    "termoadvogado",
    "._pautar",
    "mandado_",
)
# Vocabulário que sinaliza peça de cumprimento; entra na frente no orçamento.
_SINAL_CUMPRIMENTO = (
    "comprova",
    "cumprimento",
    "atendimento",
    "peticao",
    "petição",
    "defesa",
    "oficio",
    "ofício",
    "documento",
    "certid",
    "parecer",
    "informa",
)

_SQL_PECAS = """
SELECT concat(rtrim(inf.setor),'_',inf.numero_processo,'_',inf.ano_processo,
              '_',RIGHT(concat('0000',inf.ordem),4),'.pdf') AS arquivo,
       inf.setor, inf.numero_processo, inf.ano_processo, inf.ordem,
       inf.nome_informacao, inf.resumo, inf.DataInclusao
FROM processo.dbo.vw_ata_informacao inf
WHERE CONCAT(inf.numero_processo, '/', inf.ano_processo) = :processo
  AND (inf.Inativa IS NULL OR inf.Inativa = 0)
  AND (:desde IS NULL OR inf.DataInclusao >= :desde)
ORDER BY inf.DataInclusao DESC
"""


def _norm(texto: str) -> str:
    """Minúsculas, sem acento, espaços colapsados — para comparar com PDF extraído."""
    t = unicodedata.normalize("NFKD", texto or "")
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", t).strip().lower()


# Quanto do trecho citado precisa aparecer no material para a citação valer.
_PREFIXO_CONFERENCIA = 60


def conferir_trechos(relatorio: RelatorioMonitoramento, material: str) -> int:
    """Rebaixa a avaliação cujo trecho citado não existe no material lido.

    O modelo às vezes devolve CUMPRIDA com confiança ALTA citando um trecho que
    não está em peça nenhuma — aconteceu no processo 000926/2022 na primeira
    rodada, apesar de o prompt proibir. Instrução não segura isso; conferência
    determinística segura. Uma citação que não bate vira SEM_ELEMENTOS, porque
    um falso "cumprida" faz a CCD arquivar caso vivo.
    """
    alvo = _norm(material)
    rebaixadas = 0
    for av in relatorio.avaliacoes:
        trecho = _norm(av.trecho)
        if not trecho or trecho[:_PREFIXO_CONFERENCIA] in alvo:
            continue
        av.trecho_conferido = False
        rebaixadas += 1
        if av.situacao_cumprimento != "SEM_ELEMENTOS":
            av.situacao_cumprimento = "SEM_ELEMENTOS"
            av.confianca = "BAIXA"
    return rebaixadas


def _pontua_peca(nome: str) -> int:
    n = (nome or "").lower()
    if any(r in n for r in _RUIDO):
        return -1
    return 1 if any(s in n for s in _SINAL_CUMPRIMENTO) else 0


def selecionar_pecas(
    processo: str,
    engine: Any,
    desde: date | None,
    orcamento: int,
) -> tuple[str, int, int, bool]:
    """Texto das peças posteriores à decisão, dentro de um orçamento de caracteres.

    Devolve (material, pecas_lidas, pecas_disponiveis, truncado). As peças são
    ordenadas por sinal de cumprimento e depois por recência — um processo pode
    ter mais de cem peças, e ler todas não cabe numa chamada.
    """
    df = run_query_df(_SQL_PECAS, engine, processo=processo, desde=desde)
    disponiveis = len(df)
    if disponiveis == 0:
        return "", 0, 0, False

    df["pontos"] = df["nome_informacao"].apply(_pontua_peca)
    df = df[df["pontos"] >= 0].sort_values(["pontos", "DataInclusao"], ascending=False)

    blocos: list[str] = []
    usados = 0
    lidas = 0
    truncado = False
    for _, row in df.iterrows():
        caminho = get_info_file_path(row)
        try:
            texto = extract_text_from_pdf(caminho) or ""
        except Exception:  # PDF ausente no share, corrompido ou protegido
            continue
        if not texto.strip():
            continue
        setor = str(row["setor"]).strip()
        cabecalho = f"\n\n=== Arquivo: {row['arquivo']} (setor: {setor}) ===\n\n"
        if usados + len(texto) > orcamento:
            truncado = True
            break
        blocos.append(cabecalho + texto)
        usados += len(texto)
        lidas += 1

    return "".join(blocos).strip(), lidas, disponiveis, truncado


def varrer_processo(
    processo: str,
    itens: pd.DataFrame,
    engine: Any,
    llm: Any,
    orcamento: int = 60_000,
) -> RelatorioMonitoramento:
    """Procura prova de cumprimento nas peças posteriores à decisão."""
    desde = _como_data(itens["data_sessao"].max())
    material, lidas, disponiveis, truncado = selecionar_pecas(processo, engine, desde, orcamento)

    if not material:
        return RelatorioMonitoramento(
            processo=processo,
            pecas_disponiveis=disponiveis,
            observacao="Nenhuma peça legível posterior à decisão.",
        )

    linhas = [
        f"- id_staging={row.id_staging} ({row.tipo}) — órgão: "
        f"{row.orgao_responsavel or 'não informado'} — prazo: "
        f"{row.prazo_texto or 'não informado'}\n  {row.descricao}"
        for row in itens.itertuples()
    ]
    cabecalho = itens.iloc[0]
    user_message = (
        f"Processo: {processo}\n"
        f"Acórdão: {cabecalho.get('acordao') or 'não informado'}\n"
        f"Data da sessão: {desde or 'não informada'}\n"
        f"Interessado: {cabecalho.get('interessado') or 'não informado'}\n\n"
        "Itens fixados na decisão (avalie cada um):\n" + "\n".join(linhas) + "\n\n"
        f"Peças do processo posteriores à decisão:\n\n{material}"
    )

    chain = _structured(RelatorioMonitoramento, llm)
    relatorio: RelatorioMonitoramento = chain.invoke(
        [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_message)]
    )
    relatorio.processo = processo
    relatorio.pecas_lidas = lidas
    relatorio.pecas_disponiveis = disponiveis
    relatorio.truncado = truncado

    rebaixadas = conferir_trechos(relatorio, material)
    if rebaixadas:
        relatorio.observacao = (
            f"{relatorio.observacao} {rebaixadas} avaliação(ões) rebaixada(s) a "
            "SEM_ELEMENTOS: o trecho citado não foi encontrado nas peças lidas."
        ).strip()

    if truncado:
        relatorio.observacao = (
            f"{relatorio.observacao} Varredura parcial: {lidas} de {disponiveis} peças "
            "couberam no orçamento de contexto."
        ).strip()
    return relatorio


# --------------------------------------------------------------------------
# Saídas
# --------------------------------------------------------------------------

def _safe_name(processo: str) -> str:
    return processo.replace("/", "_")


def salvar_json(relatorio: RelatorioMonitoramento, out_dir: Path) -> Path:
    destino = out_dir / "varredura"
    destino.mkdir(parents=True, exist_ok=True)
    path = destino / f"{_safe_name(relatorio.processo)}.json"
    path.write_text(
        json.dumps(json.loads(relatorio.model_dump_json()), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def carregar_varreduras(out_dir: Path) -> dict[int, AvaliacaoItem]:
    """Todas as avaliações já gravadas em disco, por id_staging."""
    destino = out_dir / "varredura"
    achados: dict[int, AvaliacaoItem] = {}
    for path in sorted(destino.glob("*.json")) if destino.exists() else []:
        try:
            rel = RelatorioMonitoramento.model_validate_json(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for av in rel.avaliacoes:
            achados[av.id_staging] = av
    return achados


def _fmt_data(valor: Any) -> str:
    d = _como_data(valor)
    return d.strftime("%d/%m/%Y") if d else "—"


def escrever_ficha(
    processo: str,
    itens: pd.DataFrame,
    avaliacoes: dict[int, AvaliacaoItem],
    out_dir: Path,
) -> Path:
    """A ficha de monitoramento — o quickstart do auditor para um processo."""
    destino = out_dir / "fichas"
    destino.mkdir(parents=True, exist_ok=True)
    cab = itens.iloc[0]

    linhas: list[str] = [
        f"# Ficha de monitoramento — processo {processo}",
        "",
        "| Campo | Valor |",
        "|---|---|",
        f"| Acórdão | {cab.get('acordao') or '—'} |",
        f"| Data da sessão | {_fmt_data(cab.get('data_sessao'))} |",
        f"| Trânsito em julgado | {_fmt_data(cab.get('data_transito'))} |",
        f"| Relator | {cab.get('relator') or '—'} |",
        f"| Interessado | {cab.get('interessado') or '—'} |",
        f"| Setor atual | {cab.get('setor_atual') or '—'} |",
        f"| Registro no CGR | {'sim' if int(cab.get('tem_cgr') or 0) else 'NÃO'} |",
        f"| Itens curados | {len(itens)} |",
        "",
    ]

    if not int(cab.get("tem_cgr") or 0):
        linhas += [
            "> **Sem registro no Cadastro Geral de Recomendações.** O Regimento Interno "
            'manda acompanhar por ali (art. 299 e art. 431, IV, "c"). Avaliar o cadastro '
            "antes de qualquer outra providência.",
            "",
        ]

    for i, row in enumerate(itens.itertuples(), start=1):
        av = avaliacoes.get(int(row.id_staging))
        linhas += [
            f"## {i}. {str(row.tipo).capitalize()} (id_staging {row.id_staging})",
            "",
            f"> {row.descricao}",
            "",
            "| Campo | Valor |",
            "|---|---|",
            f"| Órgão responsável | {row.orgao_responsavel or '—'} |",
            f"| Responsável nomeado | {row.nome_responsavel or '—'} |",
            f"| Prazo (como está na decisão) | {row.prazo_texto or '—'} |",
            f"| Âncora do prazo | {row.prazo_ancora or '—'} |",
            f"| Vencimento calculado | {_fmt_data(row.data_vencimento)} |",
            f"| Situação (triagem) | **{row.situacao}** |",
            f"| Multa cominatória | {'sim' if row.tem_multa_cominatoria else 'não'} |",
            f"| Revisão | {row.revisor or '—'} em {_fmt_data(row.data_revisao)} |",
            "",
        ]
        if av is None:
            linhas += ["_Varredura das peças não executada para este item._", ""]
        else:
            linhas += [
                f"**Varredura das peças:** {av.situacao_cumprimento} "
                f"(confiança {av.confianca})",
                "",
            ]
            if av.trecho and av.trecho_conferido:
                linhas += [f"> {av.trecho}", "", f"Fonte: `{av.fonte or '—'}`", ""]
            elif av.trecho:
                linhas += [
                    "> **Citação descartada.** O modelo apresentou um trecho que não foi "
                    f"encontrado nas peças lidas (alegou vir de `{av.fonte or '—'}`). "
                    "A avaliação foi rebaixada a SEM_ELEMENTOS — leia as peças.",
                    "",
                ]
            if av.proximo_ato:
                linhas += [f"**Próximo ato sugerido:** {av.proximo_ato}", ""]

    linhas += [
        "---",
        "",
        "A varredura das peças é **insumo de trabalho, não juízo de cumprimento**: quem "
        "atesta o cumprimento é o Relator, mediante prova apresentada pelo responsável e "
        "após pronunciamento do corpo técnico (Res. 028/2012, art. 31).",
        "",
        'Base normativa: NBASP 100 (ISSAI 100), "Monitoramento"; NBASP 300 (ISSAI 300), '
        "item 42; Res. 010/2020-TCE (adesão às NBASP); Regimento Interno, arts. 288, 299 e "
        '431, IV, "c"; Res. 028/2012, arts. 27 a 35; Res. 042/2024, art. 32, I e II. '
        "Procedimento: POP-CCD-013.",
        "",
        f"Ficha gerada em {date.today().strftime('%d/%m/%Y')} por "
        "`scripts/analise/monitoramento_obrigacoes.py`.",
        "",
    ]

    path = destino / f"ficha_{_safe_name(processo)}.md"
    path.write_text("\n".join(linhas), encoding="utf-8")
    return path


def consolidar_xlsx(df: pd.DataFrame, avaliacoes: dict[int, AvaliacaoItem], out_dir: Path) -> Path:
    saida = df.copy()
    campos = {
        "cumprimento": lambda a: a.situacao_cumprimento,
        "cumprimento_confianca": lambda a: a.confianca,
        "cumprimento_trecho": lambda a: a.trecho,
        "cumprimento_fonte": lambda a: a.fonte,
        "cumprimento_trecho_conferido": lambda a: a.trecho_conferido,
        "proximo_ato": lambda a: a.proximo_ato,
    }
    for coluna, extrair in campos.items():
        saida[coluna] = saida["id_staging"].map(
            lambda i, f=extrair: f(avaliacoes[i]) if i in avaliacoes else ""
        )
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "monitoramento.xlsx"
    saida.to_excel(path, index=False)
    return path


def resumo(df: pd.DataFrame) -> str:
    linhas = [
        f"Itens curados: {len(df)} em {df['processo'].nunique()} processos "
        f"({df['tipo'].value_counts().to_dict()})",
        f"Sem registro no CGR: {int(df['sem_cgr'].sum())} | "
        f"em processo arquivado: {int(df['arquivado'].sum())}",
        "Triagem: " + ", ".join(
            f"{s}={int((df['situacao'] == s).sum())}" for s in SITUACOES
        ),
    ]
    return "\n".join(linhas)


# --------------------------------------------------------------------------

def main(
    out_dir: Path,
    processos_filtro: list[str] | None,
    limite: int | None,
    sem_llm: bool,
    orcamento: int,
) -> None:
    engine = get_connection("BdDIP")
    df = carregar_curadas(engine)
    if df.empty:
        print("Nenhum item curado encontrado.")
        return

    print(resumo(df))

    alvo = ordem_de_prioridade(df)
    if processos_filtro:
        wanted = set(processos_filtro)
        faltando = wanted - set(alvo)
        if faltando:
            print(f"Aviso: fora do acervo curado, ignorados: {sorted(faltando)}")
        alvo = [p for p in alvo if p in wanted]

    if not sem_llm:
        from ccd.llm import get_llm

        llm = get_llm()
        pendentes = [
            p for p in alvo
            if not (out_dir / "varredura" / f"{_safe_name(p)}.json").exists()
        ]
        if limite:
            pendentes = pendentes[:limite]
        for processo in pendentes:
            itens = df[df["processo"] == processo]
            print(f"[{processo}] varrendo {len(itens)} item(ns)...")
            try:
                rel = varrer_processo(processo, itens, engine, llm, orcamento=orcamento)
            except Exception as exc:
                print(f"[{processo}] FALHOU: {exc}")
                traceback.print_exc()
                rel = RelatorioMonitoramento(
                    processo=processo, observacao=f"Erro durante a varredura: {exc!r}"
                )
            salvar_json(rel, out_dir)
            print(f"[{processo}] {len(rel.avaliacoes)} avaliação(ões), "
                  f"{rel.pecas_lidas}/{rel.pecas_disponiveis} peças lidas")

    # Fichas e planilha são reconstruídas a partir de TUDO que está em disco,
    # para que uma rodada parcial (--limite/--processos) não apague o já feito.
    avaliacoes = carregar_varreduras(out_dir)
    for processo in alvo:
        escrever_ficha(processo, df[df["processo"] == processo], avaliacoes, out_dir)
    path = consolidar_xlsx(df, avaliacoes, out_dir)
    print(f"{len(alvo)} ficha(s) em {out_dir / 'fichas'}")
    print(f"Planilha ({len(df)} itens, {len(avaliacoes)} avaliados) -> {path}")


def demo() -> None:
    """Check embutido: os ramos de parse_prazo, vencimento e triar."""
    # parse_prazo — as formas que aparecem no acervo real
    p = parse_prazo("60 dias úteis após o trânsito em julgado")
    assert p is not None and p.dias == 60 and p.uteis and p.ancora == "transito"
    p = parse_prazo("90 dias")
    assert p is not None and p.dias == 90 and not p.uteis and p.ancora == "transito"
    p = parse_prazo("25 days")
    assert p is not None and p.dias == 25, "o revisor às vezes grava em inglês"
    p = parse_prazo("72h a contar de sua cientificação")
    assert p is not None and p.dias == 3 and p.ancora == "cientificacao"
    p = parse_prazo("180")
    assert p is not None and p.dias == 180
    p = parse_prazo("2026-06-19")
    assert p is not None and p.ancora == "absoluta" and p.data_absoluta == date(2026, 6, 19)
    assert parse_prazo("6 meses") is not None
    for vazio in (None, "", "   ", "assim que possível", float("nan")):
        assert parse_prazo(vazio) is None, f"não deveria interpretar {vazio!r}"

    # vencimento
    base = date(2026, 1, 5)  # segunda-feira
    assert vencimento(Prazo(10, False, "transito"), base) == date(2026, 1, 15)
    assert vencimento(Prazo(10, True, "transito"), base) == date(2026, 1, 19), "10 dias úteis"
    assert vencimento(Prazo(10, False, "transito"), None) is None
    assert vencimento(Prazo(10, False, "cientificacao"), base) is None, "âncora sem data"
    assert vencimento(Prazo(None, False, "absoluta", date(2026, 3, 1)), None) == date(2026, 3, 1)
    assert vencimento(None, base) is None

    # triar — os quatro ramos
    hoje = date(2026, 6, 1)
    assert triar(None, parse_prazo("30 dias"), hoje) == "SEM_TRANSITO"
    assert triar(date(2026, 5, 20), parse_prazo("30 dias"), hoje) == "PRAZO_EM_CURSO"
    assert triar(date(2026, 1, 10), parse_prazo("30 dias"), hoje) == "PRAZO_VENCIDO"
    assert triar(date(2026, 1, 10), None, hoje) == "PRAZO_INDETERMINADO"
    assert triar(date(2026, 1, 10), parse_prazo("30 dias após a publicação"), hoje) == \
        "PRAZO_INDETERMINADO", "prazo da publicação não é calculável aqui"
    assert triar(None, parse_prazo("2026-01-02"), hoje) == "PRAZO_VENCIDO", "data absoluta basta"

    # conferência de citações — a guarda contra trecho inventado
    material = "=== Arquivo: X.pdf ===\n\nApós análise da  documentação apresentada, houve o CUMPRIMENTO da obrigação de fazer determinada no acórdão."
    rel = RelatorioMonitoramento(
        processo="000001/2026",
        avaliacoes=[
            # cita literalmente (com acento e espaçamento diferentes) -> mantém
            AvaliacaoItem(
                id_staging=1, situacao_cumprimento="CUMPRIDA", confianca="ALTA",
                trecho="apos analise da documentacao apresentada, houve o cumprimento da obrigacao de fazer",
            ),
            # inventou o trecho -> rebaixa
            AvaliacaoItem(
                id_staging=2, situacao_cumprimento="CUMPRIDA", confianca="ALTA",
                trecho="O gestor comprovou a publicação do edital retificado no diário oficial do estado.",
            ),
            # sem trecho -> não mexe
            AvaliacaoItem(id_staging=3, situacao_cumprimento="SEM_ELEMENTOS", confianca="BAIXA"),
        ],
    )
    assert conferir_trechos(rel, material) == 1
    assert rel.avaliacoes[0].situacao_cumprimento == "CUMPRIDA"
    assert rel.avaliacoes[0].trecho_conferido
    assert rel.avaliacoes[1].situacao_cumprimento == "SEM_ELEMENTOS", "citação inventada rebaixa"
    assert rel.avaliacoes[1].confianca == "BAIXA"
    assert not rel.avaliacoes[1].trecho_conferido
    assert rel.avaliacoes[2].trecho_conferido, "sem trecho não é trecho reprovado"

    # seleção de peças — ruído fora, sinal na frente
    assert _pontua_peca("Processo_apensamento_TCE.doc") == -1
    assert _pontua_peca("Despacho._pautar.doc") == -1
    assert _pontua_peca("Comprovante_de_publicacao.pdf") == 1
    assert _pontua_peca("Voto.doc") == 0

    print("demo: OK")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="monitoramento_obrigacoes", description=__doc__)
    parser.add_argument("--out-dir", default="saidas/analise/monitoramento_obrigacoes")
    parser.add_argument("--processos", nargs="+", help="Subset de processos (ex.: 000068/2024).")
    parser.add_argument("--limite", type=int, help="Máximo de processos a varrer nesta rodada.")
    parser.add_argument("--sem-llm", action="store_true", help="Só triagem, planilha e fichas.")
    parser.add_argument("--orcamento", type=int, default=60_000,
                        help="Orçamento de caracteres de peças por processo.")
    parser.add_argument("--demo", action="store_true", help="Roda o check embutido e sai.")
    args = parser.parse_args()

    if args.demo:
        demo()
    else:
        main(Path(args.out_dir), args.processos, args.limite, args.sem_llm, args.orcamento)
