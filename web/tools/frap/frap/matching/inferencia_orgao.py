"""Inferência de órgão pagador a partir de texto livre do extrato.

Quando o `CpfCnpjDepositante` do `FRAPLancamento` não basta (ex: pagamento
centralizado pelo Estado em nome de um órgão subordinado, ou prefeitura
pagando servidor mas com depositante intermediário), o `Historico` e a
`Descricao` do extrato costumam citar o órgão pagador real:

    "PREF MUN ALTO RODRIGUES"             → Prefeitura de Alto do Rodrigues
    "ESTADO DO RIO GRANDE D"              → Estado RN (libera órgãos com
                                            IdOrgaoSuperior = 272)
    "INSTITUTO DE PREVIDENCIA SOC..."     → instituto previdenciário da cidade

A inferência roda 1× por lançamento e devolve um `set[int]` de IdOrgao
candidatos. O matcher usa esse set para liberar match Nível B' por
correspondência direta com o `IdOrgaoNotificado` da parcela.

Não é busca exaustiva: cobre os padrões mais comuns vistos na planilha de
monitoramento. Cresce conforme novos padrões aparecem.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import Engine, text

# Marcador especial: lançamento veio do Estado RN (libera todos os órgãos
# com IdOrgaoSuperior = 272). Sentinela negativo p/ não colidir com IdOrgao.
ESTADO_RN_SENTINELA = -1

_RE_ESTADO_RN = re.compile(r"\bESTADO\s+DO\s+RIO\s+GRANDE\b", re.I)
# "PREF", "PREF.", "PREFEITURA", "PREFEITURA MUNICIPAL", "PMUN", "P. MUN"
_RE_PREFEITURA = re.compile(
    r"\b(?:P(?:REF)?\.?\s*MUN\.?|PREFEITURA(?:\s+MUNICIPAL)?|MUNICIPIO)\s+(?:DE\s+|DO\s+|DA\s+)?(.+?)(?:\s+CNPJ\b|\s+CPF\b|$)",
    re.I,
)
# "INST PREV", "INSTITUTO DE PREVIDENCIA", "INST. PREV. SOC."
_RE_INST_PREV = re.compile(
    r"\bINST(?:ITUTO)?\.?\s+(?:DE\s+)?PREV(?:IDENCIA)?\.?\s*(?:SOC(?:IAL)?\.?\s+)?(?:DOS?\s+SERV(?:IDORES)?)?(?:\s+(?:DE|DO|DA)\s+)?(.+?)(?:\s+CNPJ\b|\s+CPF\b|$)",
    re.I,
)
# "SECRETARIA MUNICIPAL DE X DE Y" — captura a cidade no final (Y)
_RE_SEC_MUNICIPAL = re.compile(
    r"\bSEC(?:RETARIA)?\.?\s+MUN(?:ICIPAL)?\.?(?:\s+DE\s+\S+)?\s+(?:DE\s+|DO\s+|DA\s+)?(.+?)(?:\s+CNPJ\b|\s+CPF\b|$)",
    re.I,
)
# Abreviação curta "P M X" / "PM X" / "P.M. X" — vista em extratos do BB
# ("P M PASSA E FICA FEB"). Não tem MUN, então _RE_PREFEITURA não pega.
# Para com sufixo de mês para não contaminar tokens da cidade.
_MESES_SUFIXO = "JAN|FEV|FEB|MAR|ABR|APR|MAI|MAY|JUN|JUL|AGO|AUG|SET|SEP|OUT|OCT|NOV|DEZ|DEC"
_RE_PREF_ABREV = re.compile(
    rf"\bP\.?\s*M\.?\s+(?:DE\s+|DO\s+|DA\s+)?(.+?)"
    rf"(?:\s+CNPJ\b|\s+CPF\b|\s+(?:{_MESES_SUFIXO})\b|$)",
    re.I,
)

# Aliases manuais — siglas que aparecem nos extratos mas faltam em
# vw_Gen_Orgao.SiglaOrgao (ou estão lá com outra grafia). Chave = sigla
# normalizada (UPPER, sem acento, alfanumérico+espaço). Valor = IdOrgao destino.
#
# Cresce conforme novos casos aparecem nas amostras sem-match do CLI
# `frap inferir-orgaos-lancamentos`. Os IdOrgao reais devem ser preenchidos
# após consulta ao Bdc.dbo.vw_Gen_Orgao.
_SIGLA_ALIAS: dict[str, int] = {
    # "ALRN": <IdOrgao da Assembleia Legislativa do Estado do RN>,
}

_STOPWORDS = {
    "DE",
    "DO",
    "DA",
    "DOS",
    "DAS",
    "E",
    "EM",
    "MUN",
    "MUNICIPAL",
    "PREF",
    "PREFEITURA",
    "INST",
    "INSTITUTO",
    "PREV",
    "PREVIDENCIA",
    "PREVIDENCIARIO",
    "SOCIAL",
    "SERV",
    "SERVIDORES",
    "SERVIDOR",
    "SEC",
    "SECRETARIA",
    "CNPJ",
    "CPF",
    "FRAP",
    "TCE",
}


@dataclass(frozen=True)
class OrgaoIndex:
    id_orgao: int
    nome: str
    nome_normalizado: str
    sigla: str | None  # "IPERN", "PGE/RN", etc — direto da view
    sigla_normalizada: str | None
    cnpj: str | None  # 14 dígitos só-números, sem máscara
    id_orgao_superior: int | None
    eh_prefeitura: bool
    eh_inst_prev: bool


def _normaliza(s: str) -> str:
    """Remove acentos, uppercase, normaliza espaços/pontuação."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    # troca pontuação por espaço, mantém letras+digitos+espaço
    s = re.sub(r"[^A-Za-z0-9]+", " ", s)
    return " ".join(s.upper().split())


def _so_digitos(s: str | None) -> str | None:
    if not s:
        return None
    out = "".join(c for c in str(s) if c.isdigit())
    return out or None


def _tokens_cidade(s: str) -> list[str]:
    return [t for t in _normaliza(s).split() if len(t) >= 3 and t not in _STOPWORDS]


def carregar_indice_orgaos(engine: Engine) -> list[OrgaoIndex]:
    """Lê `Bdc.dbo.vw_Gen_Orgao` (NomeOrgao + SiglaOrgao + CNPJ + IdOrgaoSuperior)."""
    sql = text(
        """
        SELECT IdOrgao,
               LTRIM(RTRIM(NomeOrgao))                       AS NomeOrgao,
               LTRIM(RTRIM(ISNULL(SiglaOrgao, '')))          AS SiglaOrgao,
               LTRIM(RTRIM(ISNULL(CNPJ, '')))                AS CNPJ,
               IdOrgaoSuperior
        FROM Bdc.dbo.vw_Gen_Orgao
        WHERE NomeOrgao IS NOT NULL
        """
    )
    out: list[OrgaoIndex] = []
    with engine.connect() as conn:
        for r in conn.execute(sql).fetchall():
            id_org = int(r[0])
            nome = str(r[1])
            sigla_raw = str(r[2]) or None
            cnpj_raw = _so_digitos(r[3])
            id_sup = int(r[4]) if r[4] is not None else None
            nome_norm = _normaliza(nome)
            sigla_norm = _normaliza(sigla_raw) if sigla_raw else None
            cnpj14 = cnpj_raw.zfill(14) if cnpj_raw and len(cnpj_raw) <= 14 else cnpj_raw
            eh_pref = "PREFEITURA" in nome_norm or " MUNICIPIO" in f" {nome_norm}"
            eh_iprev = "PREVIDENCIA" in nome_norm and (
                "INSTITUTO" in nome_norm or "IPSS" in nome_norm or "FUND" in nome_norm
            )
            out.append(
                OrgaoIndex(
                    id_orgao=id_org,
                    nome=nome,
                    nome_normalizado=nome_norm,
                    sigla=sigla_raw if sigla_raw else None,
                    sigla_normalizada=sigla_norm if sigla_norm else None,
                    cnpj=cnpj14 if cnpj14 and len(cnpj14) == 14 else None,
                    id_orgao_superior=id_sup,
                    eh_prefeitura=eh_pref,
                    eh_inst_prev=eh_iprev,
                )
            )
    return out


def buscar_orgao_por_sigla(sigla: str, indice: list[OrgaoIndex]) -> OrgaoIndex | None:
    """Match exato (case/diacrítico-insensível) na coluna SiglaOrgao da view."""
    if not sigla:
        return None
    alvo = _normaliza(sigla)
    for org in indice:
        if org.sigla_normalizada and org.sigla_normalizada == alvo:
            return org
    return None


def buscar_orgao_por_cnpj(cnpj: str, indice: list[OrgaoIndex]) -> OrgaoIndex | None:
    """Match exato pelo CNPJ (14 dígitos, sem máscara)."""
    digits = _so_digitos(cnpj)
    if not digits:
        return None
    alvo = digits.zfill(14)
    for org in indice:
        if org.cnpj == alvo:
            return org
    return None


def inferir_orgaos_lancamento(
    historico: str | None,
    descricao: str | None,
    indice: list[OrgaoIndex],
    cpfcnpj_depositante: str | None = None,
) -> set[int]:
    """Retorna IdOrgaos candidatos a partir do lançamento.

    Ordem de evidência:
      1. CNPJ depositante (14 dígitos exatos) bate com `vw_Gen_Orgao.CNPJ` →
         candidato direto e mais confiável.
      2. CNPJ encontrado dentro do `Historico`/`Descricao` (qualquer sequência
         de 14 dígitos) → match em `vw_Gen_Orgao.CNPJ`.
      3. Sigla isolada no texto (`IPERN`, `PGE`, `SESAP`...) bate com `SiglaOrgao`.
      4. Padrões textuais: `ESTADO DO RIO GRANDE` → `ESTADO_RN_SENTINELA`;
         `PREF MUN X` → prefeitura por tokens; `INST PREV X` → idem.
    """
    candidatos: set[int] = set()

    # (1) CNPJ direto do depositante
    if cpfcnpj_depositante:
        digits = _so_digitos(cpfcnpj_depositante) or ""
        if len(digits) == 14:
            org = buscar_orgao_por_cnpj(digits, indice)
            if org is not None:
                candidatos.add(org.id_orgao)

    texto = f"{historico or ''} {descricao or ''}".strip()
    if not texto:
        return candidatos

    # (2) CNPJ embutido no texto livre (padrão "XX.XXX.XXX/XXXX-XX" ou 14 dígitos)
    for m in re.finditer(r"\d[\d./\-\s]{16,21}\d", texto):
        d = _so_digitos(m.group(0)) or ""
        if len(d) == 14:
            org = buscar_orgao_por_cnpj(d, indice)
            if org is not None:
                candidatos.add(org.id_orgao)

    # (3) Sigla canônica (case-insensível, com word boundary)
    texto_norm = _normaliza(texto)
    for org in indice:
        if not org.sigla_normalizada or len(org.sigla_normalizada) < 3:
            continue
        # palavra inteira (boundaries de não-alfanumérico)
        padrao = re.escape(org.sigla_normalizada)
        if re.search(rf"(?:^|[^A-Z0-9]){padrao}(?:$|[^A-Z0-9])", texto_norm):
            candidatos.add(org.id_orgao)

    # (3b) Alias manual — siglas ausentes em vw_Gen_Orgao.SiglaOrgao
    for alias, id_orgao in _SIGLA_ALIAS.items():
        if re.search(rf"(?:^|[^A-Z0-9]){re.escape(alias)}(?:$|[^A-Z0-9])", texto_norm):
            candidatos.add(id_orgao)

    # (4) Padrões textuais
    if _RE_ESTADO_RN.search(texto):
        candidatos.add(ESTADO_RN_SENTINELA)

    # Prefeitura municipal
    for m in _RE_PREFEITURA.finditer(texto):
        cidade_tokens = _tokens_cidade(m.group(1))
        if not cidade_tokens:
            continue
        candidatos.update(_match_orgao_por_tokens(cidade_tokens, indice, "prefeitura"))

    # Prefeitura abreviada (P M / PM / P.M.) — só roda se _RE_PREFEITURA não pegou
    for m in _RE_PREF_ABREV.finditer(texto):
        cidade_tokens = _tokens_cidade(m.group(1))
        if not cidade_tokens:
            continue
        candidatos.update(_match_orgao_por_tokens(cidade_tokens, indice, "prefeitura"))

    # Instituto de previdência
    for m in _RE_INST_PREV.finditer(texto):
        cidade_tokens = _tokens_cidade(m.group(1))
        if not cidade_tokens:
            continue
        candidatos.update(_match_orgao_por_tokens(cidade_tokens, indice, "inst_prev"))

    # Secretaria municipal (mais ambíguo, só roda se nada de prefeitura/inst matchou)
    if not any(c != ESTADO_RN_SENTINELA for c in candidatos):
        for m in _RE_SEC_MUNICIPAL.finditer(texto):
            cidade_tokens = _tokens_cidade(m.group(1))
            if not cidade_tokens:
                continue
            candidatos.update(_match_orgao_por_tokens(cidade_tokens, indice, "prefeitura"))

    return candidatos


def _match_orgao_por_tokens(
    cidade_tokens: list[str],
    indice: list[OrgaoIndex],
    tipo: str,  # "prefeitura" | "inst_prev"
) -> set[int]:
    """Retorna IdOrgaos do índice cujo nome normalizado contém TODOS os tokens.

    Comparação tolerante a espaços: o token pode estar com ou sem espaço interno
    (ex: "DAGUA" no extrato vs "D AGUA" no nome do órgão).

    Empate-quebrado por menor nome (mais específico). Se >5 candidatos, descarta
    (provavelmente token muito genérico).
    """
    matches: list[OrgaoIndex] = []
    for org in indice:
        if tipo == "prefeitura" and not org.eh_prefeitura:
            continue
        if tipo == "inst_prev" and not org.eh_inst_prev:
            continue
        nome_compact = org.nome_normalizado.replace(" ", "")
        if all((t in org.nome_normalizado) or (t in nome_compact) for t in cidade_tokens):
            matches.append(org)
    if not matches or len(matches) > 5:
        return set()
    matches.sort(key=lambda o: len(o.nome_normalizado))
    return {matches[0].id_orgao}


def construir_mapa_lancamentos(
    lancamentos: Iterable[dict],
    indice: list[OrgaoIndex],
) -> dict[int, set[int]]:
    """Aplica `inferir_orgaos_lancamento` a cada lançamento, retorna mapa
    `IdLancamento -> set[IdOrgao]` (inclui `ESTADO_RN_SENTINELA` quando aplicável).
    """
    out: dict[int, set[int]] = {}
    for L in lancamentos:
        cand = inferir_orgaos_lancamento(
            L.get("Historico"),
            L.get("Descricao"),
            indice,
            cpfcnpj_depositante=L.get("CpfCnpjDepositante"),
        )
        if cand:
            out[int(L["IdLancamento"])] = cand
    return out


def expandir_estado_rn(
    mapa: dict[int, set[int]],
    indice: list[OrgaoIndex],
    id_orgao_superior_alvo: int,
) -> dict[int, set[int]]:
    """Substitui `ESTADO_RN_SENTINELA` pelo set de IdOrgao subordinados ao alvo.

    O sentinela é abstrato; expandir aqui evita carregar a hierarquia no matcher.
    """
    subordinados = {o.id_orgao for o in indice if o.id_orgao_superior == id_orgao_superior_alvo}
    out: dict[int, set[int]] = {}
    for id_lanc, cand in mapa.items():
        if ESTADO_RN_SENTINELA in cand:
            expandido = {x for x in cand if x != ESTADO_RN_SENTINELA}
            expandido |= subordinados
            out[id_lanc] = expandido
        else:
            out[id_lanc] = set(cand)
    return out
