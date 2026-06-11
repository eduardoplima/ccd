"""Match de desconto em folha — script autocontido para portar a outro sistema.

Concilia parcelas esperadas de desconto em folha contra (A) o contracheque do
servidor e (B) o crédito bancário FRAP, com um nível (B') opcional de inferência
de órgão pagador a partir do texto livre do extrato.

Entradas (carregadas dos mesmos bancos SQL Server do FRAP):
  - parcelas       ← BdDIP.dbo.FRAPDescontoFolhaParcela + FRAPDescontoFolha
  - contracheques  ← BdSIAIPessoal (itens com rubrica TCE/FRAP)
  - lançamentos    ← BdDIP.dbo.FRAPLancamento (categoria OB_RECEBIDA/TRANSFERENCIA)
  - índice órgãos  ← Bdc.dbo.vw_Gen_Orgao (cross-DB, para o Nível B')

Status de saída (1 linha por parcela):
  - OK_TUDO                — Nível A casa + Nível B casa
  - DESCONTADA_SEM_REPASSE — Nível A casa, Nível B falha
  - REPASSADA_SEM_DESCONTO — Nível A falha, mas há FRAPLancamento candidato
  - REPASSE_VIA_ORGAO      — Nível B': parcela sem contracheque casada via órgão depositante
  - PARCELA_AGUARDANDO     — vencimento futuro (DataVencimento > hoje)
  - NAO_DESCONTADA         — passou o mês, sem item no contracheque
  - BAIXADA_SEM_RASTRO     — baixa manual (TipoDeBaixa=2) sem item nem crédito

Responsável × Interessado (importante para contar/atribuir corretamente):
  O desconto em folha recai sobre o RESPONSÁVEL do débito — a pessoa que é parte
  do débito (`processo.dbo.Exe_DebitoPessoa`), que é quem `FRAPDescontoFolha.CpfCnpj`
  guarda. NÃO confundir com o INTERESSADO do processo (`processo.dbo.Processos.
  interessado`), que é o beneficiário do ato julgado (ex.: o pensionista) e NÃO
  sofre o desconto. Um único responsável (gestor) pode responder por N processos,
  cada um com um interessado diferente. A "camada de responsável + citação" abaixo
  resolve o responsável real e confirma-o pela CITAÇÃO DE 5 DIAS (tipo C05/I05/N05/
  P05 em `Cit_Citacoes`, emitida no processo de ORIGEM) — camada extra de certeza.

Variáveis de ambiente exigidas:
  SQL_SERVER_USER, SQL_SERVER_PASS, SQL_SERVER_HOST, SQL_SERVER_PORT
  SQL_SERVER_DRIVER  (opcional; default "ODBC Driver 18 for SQL Server")
  CNPJS_ESTADO_RN    (opcional; CSV de CNPJs do Estado-RN p/ regra Estado→órgão)

Dependências: pandas, sqlalchemy, pyodbc (+ driver ODBC SQL Server no SO).
python-dotenv é opcional (se ausente, lê variáveis direto do ambiente).

Uso:
  python match_desconto_folha_standalone.py --ano 2026 --mes 4
  python match_desconto_folha_standalone.py --ano 2026 --mes 4 --out match.csv
"""

from __future__ import annotations

import argparse
import os
import re
import unicodedata
import urllib.parse
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from enum import StrEnum

import pandas as pd
from sqlalchemy import Engine, bindparam, create_engine, text


# ============================================================================
# Config + engine
# ============================================================================

BANCO_DIP = "BdDIP"  # tabelas FRAP*
BANCO_SIAIPESSOAL = "BdSIAIPessoal"  # folha de pagamento (contracheques)
BANCO_BDC = "Bdc"  # vw_Gen_Orgao
BANCO_PROCESSO = "processo"  # Exe_Debito, Exe_DebitoPessoa, GenPessoa, Cit_Citacoes

# 272 = Governo do Estado RN. Quando IdOrgaoSuperior do órgão notificado é 272,
# o pagamento pode vir centralizado pelo Estado.
ID_ORGAO_SUPERIOR_ESTADO = 272


def _load_dotenv_opcional() -> None:
    """Carrega `.env` se python-dotenv existir; senão segue só com o ambiente."""
    try:
        from dotenv import load_dotenv

        load_dotenv(override=False)
    except ImportError:
        pass


def cnpjs_estado_rn() -> tuple[str, ...]:
    """Lista CSV (env CNPJS_ESTADO_RN) de CNPJs do Estado-RN normalizados a 14 dígitos.

    Vazia por padrão — neste caso a regra "Estado→órgão" do matcher fica desligada.
    """
    raw = os.environ.get("CNPJS_ESTADO_RN", "")
    out: list[str] = []
    for item in raw.split(","):
        digits = "".join(c for c in item if c.isdigit())
        if len(digits) == 14:
            out.append(digits)
    return tuple(out)


def _odbc_connect_string(database: str) -> str:
    user = os.environ["SQL_SERVER_USER"]
    pwd = os.environ["SQL_SERVER_PASS"]
    host = os.environ["SQL_SERVER_HOST"]
    port = os.environ["SQL_SERVER_PORT"]
    driver = os.environ.get("SQL_SERVER_DRIVER", "ODBC Driver 18 for SQL Server")
    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={host},{port};"
        f"DATABASE={database};"
        f"UID={user};PWD={pwd};"
        f"TrustServerCertificate=yes;Encrypt=no;"
    )


def build_engine(database: str) -> Engine:
    """SQLAlchemy Engine para o banco SQL Server pedido.

    Requer SQL_SERVER_USER/PASS/HOST/PORT no ambiente.
    """
    _load_dotenv_opcional()
    odbc = _odbc_connect_string(database)
    url = "mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(odbc)
    return create_engine(url, future=True)


# ============================================================================
# Inferência de órgão pagador (Nível B')
# ============================================================================

# Marcador especial: lançamento veio do Estado RN (libera todos os órgãos com
# IdOrgaoSuperior = 272). Sentinela negativo p/ não colidir com IdOrgao.
ESTADO_RN_SENTINELA = -1

_RE_ESTADO_RN = re.compile(r"\bESTADO\s+DO\s+RIO\s+GRANDE\b", re.I)
_RE_PREFEITURA = re.compile(
    r"\b(?:P(?:REF)?\.?\s*MUN\.?|PREFEITURA(?:\s+MUNICIPAL)?|MUNICIPIO)\s+(?:DE\s+|DO\s+|DA\s+)?(.+?)(?:\s+CNPJ\b|\s+CPF\b|$)",
    re.I,
)
_RE_INST_PREV = re.compile(
    r"\bINST(?:ITUTO)?\.?\s+(?:DE\s+)?PREV(?:IDENCIA)?\.?\s*(?:SOC(?:IAL)?\.?\s+)?(?:DOS?\s+SERV(?:IDORES)?)?(?:\s+(?:DE|DO|DA)\s+)?(.+?)(?:\s+CNPJ\b|\s+CPF\b|$)",
    re.I,
)
_RE_SEC_MUNICIPAL = re.compile(
    r"\bSEC(?:RETARIA)?\.?\s+MUN(?:ICIPAL)?\.?(?:\s+DE\s+\S+)?\s+(?:DE\s+|DO\s+|DA\s+)?(.+?)(?:\s+CNPJ\b|\s+CPF\b|$)",
    re.I,
)
_MESES_SUFIXO = "JAN|FEV|FEB|MAR|ABR|APR|MAI|MAY|JUN|JUL|AGO|AUG|SET|SEP|OUT|OCT|NOV|DEZ|DEC"
_RE_PREF_ABREV = re.compile(
    rf"\bP\.?\s*M\.?\s+(?:DE\s+|DO\s+|DA\s+)?(.+?)"
    rf"(?:\s+CNPJ\b|\s+CPF\b|\s+(?:{_MESES_SUFIXO})\b|$)",
    re.I,
)

# Aliases manuais — siglas que aparecem nos extratos mas faltam em
# vw_Gen_Orgao.SiglaOrgao. Chave = sigla normalizada; valor = IdOrgao destino.
_SIGLA_ALIAS: dict[str, int] = {
    # "ALRN": <IdOrgao da Assembleia Legislativa do Estado do RN>,
}

_STOPWORDS = {
    "DE", "DO", "DA", "DOS", "DAS", "E", "EM",
    "MUN", "MUNICIPAL", "PREF", "PREFEITURA",
    "INST", "INSTITUTO", "PREV", "PREVIDENCIA", "PREVIDENCIARIO", "SOCIAL",
    "SERV", "SERVIDORES", "SERVIDOR",
    "SEC", "SECRETARIA", "CNPJ", "CPF", "FRAP", "TCE",
}


@dataclass(frozen=True)
class OrgaoIndex:
    id_orgao: int
    nome: str
    nome_normalizado: str
    sigla: str | None
    sigla_normalizada: str | None
    cnpj: str | None  # 14 dígitos só-números
    id_orgao_superior: int | None
    eh_prefeitura: bool
    eh_inst_prev: bool


def _normaliza(s: str) -> str:
    """Remove acentos, uppercase, normaliza espaços/pontuação."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
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
    """Lê Bdc.dbo.vw_Gen_Orgao (NomeOrgao + SiglaOrgao + CNPJ + IdOrgaoSuperior)."""
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

    Ordem de evidência: CNPJ depositante → CNPJ no texto → sigla → padrões
    textuais (ESTADO DO RIO GRANDE / PREF MUN / INST PREV / SEC MUNICIPAL).
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

    # (2) CNPJ embutido no texto livre
    for m in re.finditer(r"\d[\d./\-\s]{16,21}\d", texto):
        d = _so_digitos(m.group(0)) or ""
        if len(d) == 14:
            org = buscar_orgao_por_cnpj(d, indice)
            if org is not None:
                candidatos.add(org.id_orgao)

    # (3) Sigla canônica
    texto_norm = _normaliza(texto)
    for org in indice:
        if not org.sigla_normalizada or len(org.sigla_normalizada) < 3:
            continue
        padrao = re.escape(org.sigla_normalizada)
        if re.search(rf"(?:^|[^A-Z0-9]){padrao}(?:$|[^A-Z0-9])", texto_norm):
            candidatos.add(org.id_orgao)

    # (3b) Alias manual
    for alias, id_orgao in _SIGLA_ALIAS.items():
        if re.search(rf"(?:^|[^A-Z0-9]){re.escape(alias)}(?:$|[^A-Z0-9])", texto_norm):
            candidatos.add(id_orgao)

    # (4) Padrões textuais
    if _RE_ESTADO_RN.search(texto):
        candidatos.add(ESTADO_RN_SENTINELA)

    for m in _RE_PREFEITURA.finditer(texto):
        cidade_tokens = _tokens_cidade(m.group(1))
        if not cidade_tokens:
            continue
        candidatos.update(_match_orgao_por_tokens(cidade_tokens, indice, "prefeitura"))

    for m in _RE_PREF_ABREV.finditer(texto):
        cidade_tokens = _tokens_cidade(m.group(1))
        if not cidade_tokens:
            continue
        candidatos.update(_match_orgao_por_tokens(cidade_tokens, indice, "prefeitura"))

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
    """IdOrgaos cujo nome normalizado contém TODOS os tokens. Empate → menor nome.

    Se >5 candidatos, descarta (token genérico demais).
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
    """Mapa IdLancamento -> set[IdOrgao] (inclui ESTADO_RN_SENTINELA quando aplicável)."""
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
    """Substitui ESTADO_RN_SENTINELA pelo set de IdOrgao subordinados ao alvo."""
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


def montar_orgaos_por_lancamento(
    eng_dip: Engine, lanc_df: pd.DataFrame
) -> dict[int, set[int]]:
    """Combina inferência por texto + regra Estado-RN em IdLancamento -> set[IdOrgao]."""
    if lanc_df.empty:
        return {}
    indice = carregar_indice_orgaos(eng_dip)
    mapa = construir_mapa_lancamentos(lanc_df.to_dict(orient="records"), indice)
    mapa = expandir_estado_rn(mapa, indice, ID_ORGAO_SUPERIOR_ESTADO)
    cnpjs_estado = set(cnpjs_estado_rn())
    if cnpjs_estado:
        subordinados = {
            o.id_orgao for o in indice if o.id_orgao_superior == ID_ORGAO_SUPERIOR_ESTADO
        }
        for r in lanc_df.itertuples():
            cnpj_dep = str(getattr(r, "CpfCnpjDepositante", "") or "")
            if cnpj_dep in cnpjs_estado:
                mapa.setdefault(int(r.IdLancamento), set()).update(subordinados)
    return mapa


# ============================================================================
# Carregadores SQL
# ============================================================================

_SQL_PARCELAS = text(
    """
    SELECT
        P.IdFRAPDescontoFolhaParcela, P.MesReferencia, P.AnoReferencia,
        P.ValorEsperado, P.DataVencimento AS DataVencimentoParcela,
        P.SituacaoParcela, P.TipoDeBaixa, P.DataPagamentoParcela,
        DF.CpfCnpj, DF.IdOrgaoNotificado
    FROM dbo.FRAPDescontoFolhaParcela P
    JOIN dbo.FRAPDescontoFolha DF ON DF.IdFRAPDescontoFolha = P.IdFRAPDescontoFolha
    WHERE P.MesReferencia = :mes AND P.AnoReferencia = :ano
      AND DF.Ativo = 1
    """
)

_SQL_CONTRACHEQUE_DESCONTOS_TCE = """
SELECT
    CCI.IdContraChequeItem,
    CCI.IdContraCheque,
    CCI.IdRubrica,
    R.Codigo                             AS RubricaCodigo,
    LTRIM(RTRIM(R.Descricao))            AS RubricaDescricao,
    CAST(LTRIM(RTRIM(CCI.MesReferencia)) AS INT)   AS MesReferencia,
    CAST(LTRIM(RTRIM(CCI.AnoReferencia)) AS INT)   AS AnoReferencia,
    CCI.Valor,
    F.IdFolhaPagamento,
    CC.IdFuncionario,
    P.IdPessoa,
    P.CPF,
    LTRIM(RTRIM(P.Nome))                 AS NomePessoa
FROM dbo.SiaiDp_ContraChequeItem CCI
JOIN dbo.SiaiDp_Rubrica          R   ON R.IdRubrica       = CCI.IdRubrica
JOIN dbo.SiaiDp_ContraCheque     CC  ON CC.IdContraCheque = CCI.IdContraCheque
JOIN dbo.SiaiDp_FolhaPagamento   F   ON F.IdFolhaPagamento = CC.IdFolhaPagamento
LEFT JOIN dbo.SiaiDp_Funcionario FU  ON FU.IdFuncionario  = CC.IdFuncionario
LEFT JOIN dbo.Comum_Pessoa       P   ON P.IdPessoa        = FU.IdPessoa
WHERE
    R.Tipo = '2'
    AND (UPPER(R.Descricao) LIKE '%TCE%'
         OR UPPER(R.Descricao) LIKE '%TRIBUNAL DE CONTAS%'
         OR UPPER(R.Descricao) LIKE '%FRAP%')
    AND CAST(LTRIM(RTRIM(CCI.AnoReferencia)) AS INT) = :ano
    AND CAST(LTRIM(RTRIM(CCI.MesReferencia)) AS INT) = :mes
    AND P.CPF IN :cpfs
"""

_SQL_LANCAMENTOS_FRAP = text(
    """
    SELECT L.IdLancamento, L.DtMovimento, L.Valor,
           cat.Codigo AS Categoria, L.CpfCnpjDepositante,
           L.Historico, L.Descricao
    FROM dbo.FRAPLancamento L
    JOIN dbo.FRAPCategoria cat ON cat.IdCategoria = L.IdCategoria
    WHERE cat.Codigo IN ('OB_RECEBIDA', 'TRANSFERENCIA')
      AND L.ValorDC = 'C'
      AND L.DtMovimento BETWEEN
          DATEFROMPARTS(:ano, :mes, 1) AND DATEADD(DAY, 45, EOMONTH(DATEFROMPARTS(:ano, :mes, 1)))
    """
)


def carregar_parcelas(eng_dip: Engine, ano: int, mes: int) -> pd.DataFrame:
    """Parcelas ativas do mês/ano em BdDIP.FRAPDescontoFolhaParcela."""
    with eng_dip.connect() as c:
        return pd.read_sql(_SQL_PARCELAS, c, params={"mes": mes, "ano": ano})


def carregar_contracheques(
    eng_sip: Engine, cpfs: Iterable[str], mes: int, ano: int
) -> pd.DataFrame:
    """Itens de contracheque com rubrica TCE/FRAP no mês/ano para a lista de CPFs."""
    docs = tuple({c for c in cpfs if c})
    if not docs:
        return pd.DataFrame()
    stmt = text(_SQL_CONTRACHEQUE_DESCONTOS_TCE).bindparams(
        bindparam("cpfs", expanding=True)
    )
    with eng_sip.connect() as conn:
        return pd.read_sql(stmt, conn, params={"cpfs": docs, "mes": mes, "ano": ano})


def carregar_lancamentos_frap(eng_dip: Engine, ano: int, mes: int) -> pd.DataFrame:
    """Créditos FRAP (OB_RECEBIDA/TRANSFERENCIA) na janela do mês até D+45."""
    with eng_dip.connect() as c:
        return pd.read_sql(_SQL_LANCAMENTOS_FRAP, c, params={"mes": mes, "ano": ano})


# ============================================================================
# Matcher (Níveis A / B / B')
# ============================================================================


class StatusDescontoFolha(StrEnum):
    OK_TUDO = "OK_TUDO"
    DESCONTADA_SEM_REPASSE = "DESCONTADA_SEM_REPASSE"
    REPASSADA_SEM_DESCONTO = "REPASSADA_SEM_DESCONTO"
    REPASSE_VIA_ORGAO = "REPASSE_VIA_ORGAO"
    PARCELA_AGUARDANDO = "PARCELA_AGUARDANDO"
    NAO_DESCONTADA = "NAO_DESCONTADA"
    BAIXADA_SEM_RASTRO = "BAIXADA_SEM_RASTRO"


_TOL = 0.005


def match_desconto_folha(
    parcelas_df: pd.DataFrame,
    contracheques_df: pd.DataFrame,
    lancamentos_frap_df: pd.DataFrame,
    janela_dias: int = 31,
    hoje: date | None = None,
    *,
    orgaos_por_lancamento: dict[int, set[int]] | None = None,
) -> pd.DataFrame:
    """Concilia parcelas com contracheque (Nível A) e crédito FRAP (Nível B/B').

    `parcelas_df`: CpfCnpj, MesReferencia, AnoReferencia, ValorEsperado,
                   DataVencimentoParcela, SituacaoParcela, TipoDeBaixa,
                   DataPagamentoParcela, IdFRAPDescontoFolhaParcela (chave),
                   IdOrgaoNotificado (opcional, p/ Nível B').
    `contracheques_df`: CPF, MesReferencia, AnoReferencia, Valor,
                        IdContraChequeItem, IdRubrica.
    `lancamentos_frap_df`: IdLancamento, DtMovimento, Valor, Categoria.

    Nível B' (opcional): `orgaos_por_lancamento` mapeia IdLancamento -> set[IdOrgao]
    com os órgãos que podem ser pagadores reais (CNPJ depositante / inferência de
    texto). Parcelas NAO_DESCONTADA ou DESCONTADA_SEM_REPASSE cujo IdOrgaoNotificado
    aparece no set tentam match individual por valor exato + janela.

    Retorna 1 linha por parcela: IdFRAPDescontoFolhaParcela, IdContraChequeItem,
    IdRubrica, ValorContracheque, IdLancamentoFRAP, status_match.
    """
    hoje = hoje or date.today()
    parcelas = parcelas_df.copy()
    if parcelas.empty:
        return pd.DataFrame(
            columns=[
                "IdFRAPDescontoFolhaParcela",
                "IdContraChequeItem",
                "IdRubrica",
                "ValorContracheque",
                "IdLancamentoFRAP",
                "status_match",
            ]
        )

    # ---------- Nível A: parcela × contracheque ----------
    contra = contracheques_df.copy()
    if not contra.empty:
        contra["CPF"] = contra["CPF"].astype(str).str.zfill(11)
        contra["valor_cent"] = (contra["Valor"].astype(float) * 100).round().astype("Int64")
        # Deduplicar (servidor pode ter o mesmo item em folhas distintas no mesmo mês —
        # complementar/13º/extra). Fica com o IdContraChequeItem de menor id.
        contra = contra.sort_values("IdContraChequeItem").drop_duplicates(
            subset=["CPF", "MesReferencia", "AnoReferencia", "valor_cent"], keep="first"
        )

    parcelas["CpfCnpj"] = parcelas["CpfCnpj"].astype(str).str.zfill(11)
    parcelas["valor_cent"] = (parcelas["ValorEsperado"].astype(float) * 100).round().astype("Int64")

    if not contra.empty:
        merged_a = parcelas.merge(
            contra[
                [
                    "CPF",
                    "MesReferencia",
                    "AnoReferencia",
                    "valor_cent",
                    "IdContraChequeItem",
                    "IdRubrica",
                    "Valor",
                ]
            ].rename(columns={"Valor": "ValorContracheque"}),
            how="left",
            left_on=["CpfCnpj", "MesReferencia", "AnoReferencia", "valor_cent"],
            right_on=["CPF", "MesReferencia", "AnoReferencia", "valor_cent"],
        )
        merged_a = merged_a.drop(columns=["CPF"], errors="ignore")
    else:
        merged_a = parcelas.copy()
        merged_a["IdContraChequeItem"] = pd.NA
        merged_a["IdRubrica"] = pd.NA
        merged_a["ValorContracheque"] = pd.NA

    merged_a["__casou_contracheque"] = merged_a["IdContraChequeItem"].notna()

    # ---------- Nível B: lote (mes, ano) × FRAPLancamento ----------
    fr = lancamentos_frap_df.copy() if lancamentos_frap_df is not None else pd.DataFrame()
    if not fr.empty:
        cat_col = (
            "Categoria"
            if "Categoria" in fr.columns
            else ("categoria" if "categoria" in fr.columns else None)
        )
        if cat_col is not None:
            fr = fr[fr[cat_col].astype(str).isin(("OB_RECEBIDA", "TRANSFERENCIA"))].copy()
        dt_col = "DtMovimento" if "DtMovimento" in fr.columns else "dt_movimento"
        fr["DtMovimento"] = pd.to_datetime(fr[dt_col]).dt.normalize()
        valor_col = "Valor" if "Valor" in fr.columns else "valor"
        fr["Valor"] = pd.to_numeric(fr[valor_col], errors="coerce")

    confirmadas = merged_a[merged_a["__casou_contracheque"]].copy()
    lote_para_lanc: dict[tuple[int, int], int | None] = {}
    if not confirmadas.empty and not fr.empty:
        somas = confirmadas.groupby(["MesReferencia", "AnoReferencia"])["ValorContracheque"].sum()
        lanc_consumido: set = set()
        for (mes, ano), soma in somas.items():
            soma = float(soma)
            primeiro_dia = pd.Timestamp(date(int(ano), int(mes), 1))
            ultimo_dia = primeiro_dia + pd.offsets.MonthEnd(0)
            limite = ultimo_dia + pd.Timedelta(days=janela_dias)
            cand = fr[
                (fr["DtMovimento"] >= primeiro_dia)
                & (fr["DtMovimento"] <= limite)
                & ((fr["Valor"] - soma).abs() < _TOL)
                & (~fr["IdLancamento"].isin(lanc_consumido))
            ].sort_values("DtMovimento")
            escolhido = int(cand.iloc[0]["IdLancamento"]) if not cand.empty else None
            if escolhido is not None:
                lanc_consumido.add(escolhido)
            lote_para_lanc[(int(mes), int(ano))] = escolhido

    def _lanc_para_parcela(row):
        if not row["__casou_contracheque"]:
            return None
        return lote_para_lanc.get((int(row["MesReferencia"]), int(row["AnoReferencia"])))

    merged_a["IdLancamentoFRAP"] = merged_a.apply(_lanc_para_parcela, axis=1)

    # ---------- Status final ----------
    def _status(row) -> str:
        casou_cc = bool(row["__casou_contracheque"])
        casou_fr = pd.notna(row["IdLancamentoFRAP"])
        venc = pd.to_datetime(row.get("DataVencimentoParcela"), errors="coerce")
        sit = str(row.get("SituacaoParcela") or "").strip()
        tipo_baixa = row.get("TipoDeBaixa")

        if casou_cc and casou_fr:
            return StatusDescontoFolha.OK_TUDO.value
        if casou_cc and not casou_fr:
            return StatusDescontoFolha.DESCONTADA_SEM_REPASSE.value
        if not casou_cc and casou_fr:
            return StatusDescontoFolha.REPASSADA_SEM_DESCONTO.value
        # nenhum dos dois casou
        if pd.notna(venc) and venc.date() > hoje:
            return StatusDescontoFolha.PARCELA_AGUARDANDO.value
        if sit == "2" and pd.notna(row.get("DataPagamentoParcela")) and tipo_baixa == 2:
            return StatusDescontoFolha.BAIXADA_SEM_RASTRO.value
        return StatusDescontoFolha.NAO_DESCONTADA.value

    merged_a["status_match"] = merged_a.apply(_status, axis=1)

    # ---------- Nível B' (opcional, aditivo) ----------
    # Cobre dois cenários onde o Nível B (soma do lote) falha mas existe crédito
    # individual por órgão: NAO_DESCONTADA (prefeitura pagou direto) e
    # DESCONTADA_SEM_REPASSE (várias prefeituras repassam separadamente).
    if (
        orgaos_por_lancamento
        and "IdOrgaoNotificado" in merged_a.columns
        and not fr.empty
        and "IdLancamentoFRAP" in merged_a.columns
    ):
        fr_b_linha = fr.copy()
        fr_b_linha["valor_cent"] = (fr_b_linha["Valor"].astype(float) * 100).round().astype("Int64")
        fr_b_linha["__orgaos_inf"] = fr_b_linha["IdLancamento"].map(
            lambda i: orgaos_por_lancamento.get(int(i), set())
        )
        fr_b_linha = fr_b_linha[fr_b_linha["__orgaos_inf"].map(bool)].copy()
        if not fr_b_linha.empty:
            consumidos: set[int] = {
                int(v) for v in merged_a["IdLancamentoFRAP"].dropna().tolist()
            }
            alvos = (
                StatusDescontoFolha.NAO_DESCONTADA.value,
                StatusDescontoFolha.DESCONTADA_SEM_REPASSE.value,
            )
            for idx, row in merged_a.iterrows():
                status_atual = str(row["status_match"])
                if status_atual not in alvos:
                    continue
                id_org = row.get("IdOrgaoNotificado")
                if id_org is None or pd.isna(id_org):
                    continue
                id_org_int = int(id_org)
                mes_p = int(row["MesReferencia"])
                ano_p = int(row["AnoReferencia"])
                primeiro_dia = pd.Timestamp(date(ano_p, mes_p, 1))
                ultimo_dia = primeiro_dia + pd.offsets.MonthEnd(0)
                limite = ultimo_dia + pd.Timedelta(days=janela_dias)
                valor_cent = int(row["valor_cent"])
                cand = fr_b_linha[
                    (fr_b_linha["DtMovimento"] >= primeiro_dia)
                    & (fr_b_linha["DtMovimento"] <= limite)
                    & (fr_b_linha["valor_cent"] == valor_cent)
                    & (~fr_b_linha["IdLancamento"].isin(consumidos))
                    & (fr_b_linha["__orgaos_inf"].map(lambda s: id_org_int in s))
                ].sort_values("DtMovimento")
                if cand.empty:
                    continue
                escolhido = int(cand.iloc[0]["IdLancamento"])
                consumidos.add(escolhido)
                merged_a.at[idx, "IdLancamentoFRAP"] = escolhido
                if status_atual == StatusDescontoFolha.DESCONTADA_SEM_REPASSE.value:
                    merged_a.at[idx, "status_match"] = StatusDescontoFolha.OK_TUDO.value
                else:
                    merged_a.at[idx, "status_match"] = StatusDescontoFolha.REPASSE_VIA_ORGAO.value

    cols = [
        "IdFRAPDescontoFolhaParcela",
        "IdContraChequeItem",
        "IdRubrica",
        "ValorContracheque",
        "IdLancamentoFRAP",
        "status_match",
    ]
    return merged_a[cols].copy()


# ============================================================================
# Camada de responsável + citação (certeza)
# ============================================================================
#
# O matcher acima chaveia pelo RESPONSÁVEL (FRAPDescontoFolha.CpfCnpj). Estas
# funções, opcionais, resolvem o responsável diretamente do `processo` e o
# confirmam pela citação de 5 dias. Úteis na app de destino para validar/atribuir
# o desconto à pessoa certa (não ao interessado). Não alteram a saída do matcher.


def carregar_responsavel_debito(
    engine: Engine, ids_debito: Iterable[int]
) -> dict[int, dict]:
    """Responsável (parte) de cada débito: `Exe_DebitoPessoa` → `GenPessoa`.

    `GenPessoa` não tem coluna `CPF`; o documento fica em `Documento`.
    Retorna `{IdDebito: {"documento": str|None, "nome": str|None}}`.
    """
    ids = tuple({int(i) for i in ids_debito if i is not None})
    if not ids:
        return {}
    sql = text(
        """
        SELECT dp.IDDebito AS IdDebito,
               LTRIM(RTRIM(gp.Documento)) AS Documento,
               LTRIM(RTRIM(gp.Nome))      AS Nome
        FROM processo.dbo.Exe_DebitoPessoa dp
        JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = dp.IDPessoa
        WHERE dp.IDDebito IN :ids
        """
    ).bindparams(bindparam("ids", expanding=True))
    out: dict[int, dict] = {}
    with engine.connect() as conn:
        for r in conn.execute(sql, {"ids": ids}).fetchall():
            # Um débito pode ter >1 pessoa (solidariedade); mantém a primeira vista.
            out.setdefault(int(r[0]), {"documento": r[1] or None, "nome": r[2] or None})
    return out


def carregar_processo_origem(engine: Engine, ids_debito: Iterable[int]) -> dict[int, int]:
    """Mapa `IdDebito -> IdProcessoOrigem` (a citação de 5 dias fica na origem)."""
    ids = tuple({int(i) for i in ids_debito if i is not None})
    if not ids:
        return {}
    sql = text(
        """
        SELECT IdDebito, IdProcessoOrigem
        FROM processo.dbo.Exe_Debito
        WHERE IdDebito IN :ids AND IdProcessoOrigem IS NOT NULL
        """
    ).bindparams(bindparam("ids", expanding=True))
    with engine.connect() as conn:
        rows = conn.execute(sql, {"ids": ids}).fetchall()
    return {int(r[0]): int(r[1]) for r in rows}


def carregar_citados_5dias(
    engine: Engine, ids_processo: Iterable[int]
) -> dict[int, set[str]]:
    """Documentos citados com prazo de 5 dias, por processo.

    Filtra pelo TIPO da citação (`Cit_Tipo_Citacao.Prazo = 5`, cobre C05/I05/N05/
    P05) — não pela coluna `Cit_Citacoes.Prazo`, que costuma vir NULL. `ids_processo`
    deve conter os IdProcesso de ORIGEM (ver `carregar_processo_origem`).
    Retorna `{IdProcesso: {documentos (só dígitos)}}`.
    """
    ids = tuple({int(i) for i in ids_processo if i is not None})
    if not ids:
        return {}
    sql = text(
        """
        SELECT cc.IdProcesso, LTRIM(RTRIM(gp.Documento)) AS Documento
        FROM processo.dbo.Cit_Citacoes cc
        JOIN processo.dbo.Cit_Tipo_Citacao tc ON tc.Codigo = cc.Tipo AND tc.Prazo = 5
        JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = cc.IdPessoa
        WHERE cc.IdProcesso IN :ids
        """
    ).bindparams(bindparam("ids", expanding=True))
    out: dict[int, set[str]] = {}
    with engine.connect() as conn:
        for r in conn.execute(sql, {"ids": ids}).fetchall():
            d = _so_digitos(r[1])
            if d:
                out.setdefault(int(r[0]), set()).add(d)
    return out


def responsavel_confirmado_por_citacao(
    doc_responsavel: str | None, docs_citados: Iterable[str]
) -> bool:
    """True se o documento do responsável aparece entre os citados em 5 dias.

    Compara só os dígitos (tolerante a máscara/zfill de CPF 11 / CNPJ 14).
    """
    alvo = _so_digitos(doc_responsavel)
    if not alvo:
        return False
    alvos = {alvo, alvo.zfill(11), alvo.zfill(14)}
    for c in docs_citados:
        cd = _so_digitos(c) or ""
        if cd in alvos or cd.zfill(11) == alvo.zfill(11) or cd.zfill(14) == alvo.zfill(14):
            return True
    return False


# ============================================================================
# Orquestração / CLI
# ============================================================================


def conciliar(ano: int, mes: int) -> pd.DataFrame:
    """Carrega as três fontes, monta o Nível B' e roda o matcher."""
    eng_dip = build_engine(BANCO_DIP)

    parcelas = carregar_parcelas(eng_dip, ano, mes)
    if parcelas.empty:
        print(f"Sem parcelas em {ano}-{mes:02d} no FRAPDescontoFolhaParcela.")
        return parcelas

    cpfs = parcelas["CpfCnpj"].dropna().astype(str).str.zfill(11).unique().tolist()
    eng_sip = build_engine(BANCO_SIAIPESSOAL)
    contra = carregar_contracheques(eng_sip, cpfs, mes, ano)

    lanc = carregar_lancamentos_frap(eng_dip, ano, mes)
    orgaos_por_lancamento = montar_orgaos_por_lancamento(eng_dip, lanc)

    return match_desconto_folha(
        parcelas,
        contra,
        lanc,
        orgaos_por_lancamento=orgaos_por_lancamento,
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Match de desconto em folha (FRAP).")
    ap.add_argument("--ano", type=int, required=True)
    ap.add_argument("--mes", type=int, required=True, choices=range(1, 13))
    ap.add_argument("--out", type=str, default=None, help="CSV de saída (opcional)")
    args = ap.parse_args()

    resultado = conciliar(args.ano, args.mes)
    if resultado.empty:
        return

    print(f"{len(resultado)} parcelas")
    print(resultado["status_match"].value_counts().to_string())

    if args.out:
        resultado.to_csv(args.out, index=False, encoding="utf-8-sig")
        print(f"-> {args.out}")


if __name__ == "__main__":
    main()
