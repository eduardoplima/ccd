"""Desconto em folha finalizado — conferência e informação de arquivamento.

Universo: processos com marcador ativo 5907 "DESCONTO EM FOLHA - Finalizado" ou 6170
"DESCONTO EM FOLHA - Fim ago/set", cruzados com o cadastro do módulo web
(BdDIP.CCDDescontoFolha: responsável, débito, nº/evento da notificação). Para cada
processo confronta:
  - valor notificado: o mandado da DE não traz valor; vem do ato que ele encaminha —
    despacho da CCD ("Valor da multa: R$ …") ou determinação do gabinete ("valor de R$ …"),
    o último anterior ao evento da notificação (regex no PDF do share);
  - retenções: SIAI Pessoal (tabelas-base, última remessa por folha, competência da FOLHA,
    rubrica TCE/FRAP filtrada em Python — web/backend/app/ccd/siai_pessoal/service.py).
    Folha municipal fora do SIAI: parcelas informadas pelo órgão (CCDDescontoFolhaValor)
    ou, sem elas, as baixas lançadas pela CCD (Processo_Execucoes_Baixa_TCE);
  - crédito no FRAP de cada parcela: OB já conciliada no módulo; senão, crédito de valor
    idêntico (SIAI: de M a M+2; baixas: após a notificação), cada um usado uma vez;
  - baixas lançadas pela CCD ("procedi à baixa de R$ …").
Gera a informação (valor recolhido e baixado + arquivamento, art. 26 da Resolução
nº 013/2015-TCE) quando as retenções somam o valor notificado e todas têm crédito no FRAP;
o resto só entra no resumo.md, com o motivo.

Rodar: .venv/Scripts/python.exe processos/projetos/desconto_folha_finalizados/gerar_informacoes.py [proc ...]
"""
import re
import shutil
import sys
from copy import deepcopy
from datetime import datetime
from functools import cache
from pathlib import Path

import pandas as pd
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, RGBColor
from docxtpl import DocxTemplate

from ccd.config import REPO_ROOT, informacoes_dir
from ccd.db import get_connection, run_query_df
from ccd.docs import docx_to_pdf
from ccd.pdf import extract_text_from_pdf

TEMPLATE = str(REPO_ROOT / "scripts" / "automacao" / "templates" / "modelo_informacao.docx")
DESTINO = Path(__file__).parent
MARCADORES = {5907: "Finalizado", 6170: "Fim ago/set"}
# baixas lançadas pela CCD que o banco processo ainda não reflete (lag): processo -> valor.
# A baixa quita o débito (saldo zero), independentemente do saldo que o banco ainda mostre.
BAIXAS_INFORMADAS = {"001484/2025": 480.58}  # 13ª parcela (ago/2026), baixada em 14/10/2026
TOLERANCIA = 0.05  # arredondamento das parcelas (ex.: 4 × 1.313,21 = 5.252,84 vs 5.252,85)

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]
hoje = datetime.now()
DATA = f"Natal/RN, {hoje.day} de {MESES[hoje.month - 1]} de {hoje.year}."

SQL_UNIVERSO = """
SELECT mp.IdMarcador, p.IdProcesso, RTRIM(p.numero_processo) AS num, RTRIM(p.ano_processo) AS ano,
       RTRIM(p.assunto) AS assunto, RTRIM(r.nome) AS relator, RTRIM(p.setor_atual) AS setor
FROM dbo.Pro_MarcadorProcesso mp
JOIN dbo.Processos p ON p.IdProcesso = mp.IdProcesso
LEFT JOIN dbo.Relator r ON r.codigo = p.codigo_relator
WHERE mp.DataExclusao IS NULL AND mp.IdMarcador IN (5907, 6170)
"""

SQL_CADASTROS = """
SELECT c.IdCCDDescontoFolha AS id, c.NumeroProcesso AS num, c.AnoProcesso AS ano, c.IdDebito,
       RTRIM(c.NomePessoa) AS nome, RIGHT(REPLICATE('0', 11) + RTRIM(c.CpfCnpj), 11) AS cpf,
       RTRIM(c.NomeOrgao) AS orgao, c.NumeroNotificacao, c.DataNotificacao, c.IdEventoNotificacao
FROM dbo.CCDDescontoFolha c
WHERE c.Ativo = 1
"""

# parcelas informadas pelo órgão (extraídas da resposta) com a OB conciliada, se houver
SQL_PARCELAS = """
SELECT v.IdCCDDescontoFolha AS id, v.NumeroParcela, v.MesReferencia, v.AnoReferencia, v.Valor,
       L.IdLancamento, L.DtMovimento, L.Documento, L.Valor AS ValorOB
FROM dbo.CCDDescontoFolhaValor v
LEFT JOIN dbo.CCDDescontoFolhaMatch m ON m.IdCCDDescontoFolhaValor = v.IdCCDDescontoFolhaValor
LEFT JOIN dbo.FRAPLancamento L ON L.IdLancamento = m.IdLancamentoFRAP
"""

SQL_FRAP_CREDITOS = """
SELECT L.IdLancamento, L.DtMovimento, L.Documento, L.Valor
FROM dbo.FRAPLancamento L
WHERE L.ValorDC = 'C' AND L.IdCategoria IN (1, 3) AND L.DtMovimento >= :desde
"""
SQL_FRAP_FIM = "SELECT MAX(DtMovimento) AS fim FROM dbo.FRAPLancamento"

# vw_ata_informacao.IdProcesso é NULL — filtrar por numero/ano.
# Saldo vigente da cadeia do débito: sobe até a raiz e desce até as folhas (o débito vigente é a
# folha; cada baixa cria um filho com o remanescente). Só folhas em aberto (status 1).
SQL_SALDO = """
WITH up AS (SELECT IdDebito, IdDebitoAnterior FROM dbo.Exe_Debito WHERE IdDebito = :id
            UNION ALL
            SELECT d.IdDebito, d.IdDebitoAnterior FROM dbo.Exe_Debito d JOIN up ON d.IdDebito = up.IdDebitoAnterior),
dn AS (SELECT IdDebito FROM up WHERE IdDebitoAnterior IS NULL
       UNION ALL
       SELECT d.IdDebito FROM dbo.Exe_Debito d JOIN dn ON d.IdDebitoAnterior = dn.IdDebito)
SELECT e.IdDebito, CAST(e.valorOriginalDebito AS FLOAT) AS principal,
       CAST(dbo.fn_Exe_RetornaValorAtualizado(e.IdDebito) AS FLOAT) AS atualizado
FROM dn JOIN dbo.Exe_Debito e ON e.IdDebito = dn.IdDebito
WHERE e.CodigoStatusDivida = 1
  AND NOT EXISTS (SELECT 1 FROM dbo.Exe_Debito f WHERE f.IdDebitoAnterior = e.IdDebito)
"""

SQL_EVENTOS = """
SELECT ppe.IdProcessoEvento AS id_evento, ppe.SequencialProcessoEvento AS evento, inf.ordem,
       RTRIM(inf.setor) AS setor, RTRIM(inf.nome_informacao) AS nome, inf.data_resumo,
       CONCAT(RTRIM(inf.setor), '_', inf.numero_processo, '_', inf.ano_processo, '_',
              RIGHT(CONCAT('0000', inf.ordem), 4), '.pdf') AS arquivo
FROM dbo.vw_ata_informacao inf
JOIN dbo.Pro_ProcessoEvento ppe ON ppe.IdInformacao = inf.idInformacao
WHERE inf.numero_processo = :num AND inf.ano_processo = :ano
  AND COALESCE(inf.resumo, '') <> 'Evento do Processo Original' AND COALESCE(inf.Inativa, 0) = 0
ORDER BY inf.ordem
"""

# SIAI Pessoal pelas tabelas-base (web/backend/app/ccd/siai_pessoal/service.py): servidor
# ou pensionista; um contracheque por (ano, mês, órgão, tipo de folha), última remessa.
SQL_SIAI = """
WITH cc AS (
    SELECT CC.IdContraCheque, ER.IdOrgao, CC.Matricula,
           TRY_CAST(LTRIM(RTRIM(F.Ano)) AS INT) AS ano,
           TRY_CAST(LTRIM(RTRIM(F.Mes)) AS INT) AS mes,
           ROW_NUMBER() OVER (
               PARTITION BY TRY_CAST(LTRIM(RTRIM(F.Ano)) AS INT),
                            TRY_CAST(LTRIM(RTRIM(F.Mes)) AS INT),
                            ER.IdOrgao, F.IdTipoFolhaPagamento
               ORDER BY ER.IdEnvioRemessa DESC, CC.IdContraCheque DESC) AS rn
    FROM BDSiaiPessoal.dbo.Comum_Pessoa P
    CROSS APPLY (
        SELECT C.IdContraCheque, C.IdFolhaPagamento, FU.Matricula
        FROM BDSiaiPessoal.dbo.SiaiDp_Funcionario FU
        JOIN BDSiaiPessoal.dbo.SiaiDp_ContraCheque C ON C.IdFuncionario = FU.IdFuncionario
        WHERE FU.IdPessoa = P.IdPessoa
        UNION ALL
        SELECT C.IdContraCheque, C.IdFolhaPagamento, PE.Matricula
        FROM BDSiaiPessoal.dbo.SiaiDp_Pensionista PE
        JOIN BDSiaiPessoal.dbo.SiaiDp_ContraCheque C ON C.IdPensionista = PE.IdPensionista
        WHERE PE.IdPessoa = P.IdPessoa
    ) CC
    JOIN BDSiaiPessoal.dbo.SiaiDp_FolhaPagamento F ON F.IdFolhaPagamento = CC.IdFolhaPagamento
    JOIN BDSiaiPessoal.dbo.SiaiDp_RemessaFolhaPagamento RFP
      ON RFP.IdRemessaFolhaPagamento = F.IdRemessaFolhaPagamento
    JOIN BDSiaiPessoal.dbo.Envio_Remessa ER ON ER.IdEnvioRemessa = RFP.IdEnvioRemessa
    WHERE P.CPF = :cpf
      AND ER.IdTipoEnvioRemessa = 1
      AND ER.IdSituacaoRemessa IN (4, 7)
      AND ER.IdEnvioRemessaVinculada IS NOT NULL
      AND TRY_CAST(LTRIM(RTRIM(F.Ano)) AS INT) >= :ano_min
)
SELECT cc.ano, cc.mes, RTRIM(O.NomeOrgao) AS orgao, RTRIM(cc.Matricula) AS matricula,
       RTRIM(R.Codigo) AS codigo, RTRIM(R.Descricao) AS rubrica,
       CAST(CCI.Valor AS DECIMAL(18, 2)) AS valor
FROM cc
LEFT JOIN Bdc.dbo.vw_Gen_Orgao O ON O.IdOrgao = cc.IdOrgao
JOIN BDSiaiPessoal.dbo.SiaiDp_ContraChequeItem CCI ON CCI.IdContraCheque = cc.IdContraCheque
JOIN BDSiaiPessoal.dbo.SiaiDp_Rubrica R ON R.IdRubrica = CCI.IdRubrica
WHERE cc.rn = 1 AND R.Tipo = '2'
"""

VALOR = r"R\$\s*(?:R\$\s*)?([\d.]+,\d{2})"
RE_NOTIFICADO = re.compile(
    r"(?:valor(?:\(es\))?\s+da\(?s?\)?\s+multa\(?s?\)?\s*:|valor\s+de)\s*" + VALOR, re.I)
RE_BAIXA = re.compile(r"baixa\s+de\s+" + VALOR, re.I)

FUNDAMENTO_DESCONTO = "art. 25, inciso I, da Resolução nº 013/2015-TCE"
RE_ALINEA = re.compile(r"^[a-z]\) ")  # alíneas da sugestão: parágrafo recuado, sem número


def alineas_fecho(it: dict) -> list[str]:
    """Baixa do residual + quitação, exclusão do Cadastro Informativo e arquivamento."""
    baixa = (f"a baixa do saldo residual de R$ {brl(it['saldo_atualizado'])}, com a expedição "
             "de quitação ao responsável" if it.get("saldo_atualizado")
             else "a expedição de quitação ao responsável")
    return [f"{baixa};",
            "a exclusão do seu nome do Cadastro Informativo de Créditos não Quitados do "
            "Tribunal de Contas do Estado; e",
            "o arquivamento do processo de execução, na forma do art. 26 da Resolução "
            "nº 013/2015-TCE."]


RELATORAS = ("ANA PAULA", "MARIA ADÉLIA")  # início do nome em dbo.Relator


def intro_sugestao(it: dict) -> str:
    trat = ("Exma. Cons. Relatora" if (it["relator"] or "").upper().startswith(RELATORAS)
            else "Exmo. Cons. Relator")
    return ("Ante o exposto, comprovado o recolhimento do valor notificado, encaminham-se os "
            f"autos ao gabinete d{'a' if trat.startswith('Exma') else 'o'} {trat} com as "
            "seguintes sugestões:")


def sugestao(intro: str, alineas: list[str]) -> list[str]:
    return [intro] + [f"{chr(97 + i)}) {a}" for i, a in enumerate(alineas)]


def brl(v: float) -> str:
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def num(s: str) -> float:
    return float(s.replace(".", "").replace(",", "."))


def fmt_cpf(c: str) -> str:
    return f"{c[:3]}.{c[3:6]}.{c[6:9]}-{c[9:]}"


def nome_proprio(nome: str) -> str:
    return " ".join(w.lower() if w.lower() in ("de", "da", "do", "das", "dos", "e") else w.capitalize()
                    for w in nome.split())


SIGLAS_ORGAO = {
    "ALRN": "à Assembleia Legislativa do Estado do Rio Grande do Norte",
    "IPERN": "ao Instituto de Previdência dos Servidores do Estado do Rio Grande do Norte",
}


def orgao_txt(nome: str) -> str:
    """'à Prefeitura Municipal de Lajes' / 'ao Instituto …' (com o artigo contraído)."""
    nome = nome.strip()
    if nome.upper() in SIGLAS_ORGAO:
        return SIGLAS_ORGAO[nome.upper()]
    nome = nome_proprio(nome)
    fem = nome.split()[0] in ("Prefeitura", "Câmara", "Secretaria", "Assembleia", "Fundação")
    return f"{'à' if fem else 'ao'} {nome}"


def comp(ano: int, mes: int) -> str:
    return f"{MESES[mes - 1]}/{ano}"


def eventos_txt(evs: list[int]) -> str:
    evs = sorted(set(evs))
    if len(evs) == 1:
        return f"Evento {evs[0]}"
    return "Eventos " + ", ".join(map(str, evs[:-1])) + f" e {evs[-1]}"


# Rubrica de nome genérico conferida à mão (valor = parcela informada/baixada, mês a mês):
# o filtro por nome não a reconhece. Chave: (processo, código da rubrica).
RUBRICAS_CONFERIDAS = {
    ("000407/2025", "419"),  # Pref. Lajes — DESCONTO AUTORIZADO, 6 × 410,68
    ("003665/2025", "548"),  # Pref. Serra do Mel — DESCONTOS DIVERSOS, 4 × 1.313,21
}


def rubrica_tce(nome: str, processo: str, codigo: str = "") -> bool:
    """Cópia de web/.../siai_pessoal/service.py:rubrica_tce (tipo 2 já filtrado no SQL),
    + "TRIB. DE CONTAS" abreviado e as rubricas conferidas."""
    if (processo, str(codigo).strip()) in RUBRICAS_CONFERIDAS:
        return True
    n = str(nome or "").upper()
    numero, ano = processo.split("/")
    variantes = (processo, f"{numero.lstrip('0')}/{ano}")
    return "VANT" not in n and (
        any(k in n for k in ("TCE", "FRAP", "TRIBUNAL DE CONTAS"))
        or re.search(r"\bTRIB\.? DE CONTAS\b", n) is not None
        or re.search(r"\bTC\b", n) is not None or any(v in n for v in variantes))


@cache
def texto_pdf(setor: str, arquivo: str) -> str:
    try:
        return re.sub(r"\s+", " ", extract_text_from_pdf(str(informacoes_dir() / setor / arquivo)))
    except Exception as e:  # PDF ausente/corrompido: fica sem valor, cai no resumo
        print(f"  ! {arquivo}: {e}")
        return ""


def valor_notificado(eventos: pd.DataFrame, ordem_notif: int) -> tuple[float, int] | None:
    """Último valor notificado nos atos (CCD/gabinete) anteriores ao mandado."""
    ant = eventos[(eventos.ordem < ordem_notif) & ~eventos.setor.str.startswith("DE")
                  & ~eventos.nome.str.contains("Certid|Baixa|Capa|Protesto", case=False)]
    for r in ant.sort_values("ordem", ascending=False).itertuples():
        achados = RE_NOTIFICADO.findall(texto_pdf(r.setor, r.arquivo))
        if achados:
            return num(achados[-1]), int(r.evento)
    return None


class Creditos:
    """Créditos do FRAP (OB recebida/transferência), cada um casado uma única vez."""

    def __init__(self, df: pd.DataFrame, ja_usados: set[int]):
        self.df = df.assign(Valor=df.Valor.astype(float),
                            DtMovimento=pd.to_datetime(df.DtMovimento)).sort_values("DtMovimento")
        self.usados = set(ja_usados)

    def casar(self, valor: float, ini: pd.Timestamp, fim: pd.Timestamp | None = None):
        c = self.df[(self.df.DtMovimento >= ini) & ((self.df.Valor - valor).abs() < 0.005)
                    & ~self.df.IdLancamento.isin(self.usados)]
        if fim is not None:
            c = c[c.DtMovimento <= fim]
        if c.empty:
            return None
        ob = c.iloc[0]
        self.usados.add(int(ob.IdLancamento))
        return ob


def ressalva_creditos(obs: list[tuple[str, str]]) -> str | None:
    """Ressalva de que os créditos do quadro não são repetidos; obs = [(data, documento)]."""
    if not obs:
        return None
    mesma_data = len({d for d, _ in obs}) < len(obs)
    txt = ("Registra-se que os créditos constantes do Quadro 1 não são valores repetidos: cada "
           "parcela corresponde a um lançamento distinto no extrato bancário da conta do FRAP, "
           "e nenhum lançamento foi aproveitado para mais de uma parcela.")
    if mesma_data:
        txt += (" Os créditos de mesma data decorrem de o órgão ter repassado mais de uma parcela "
                "no mesmo dia.")
    return txt


def ob_txt(ob) -> str:
    return "não localizado" if ob is None else f"{ob.DtMovimento:%d/%m/%Y} – {ob.Documento}"


def retencoes(c, processo: str, parcelas: pd.DataFrame, baixas: list, cred: Creditos,
              engd) -> tuple[str, list[dict]]:
    """(fonte, linhas): SIAI Pessoal × parcelas informadas pelo órgão × crédito no FRAP.

    Linha = {ref, competencia, detalhe, siai, orgao, valor, ob}; siai/orgao = None quando a
    parcela não consta daquela fonte. Pareamento: pela competência quando o órgão a informou,
    senão pela ordem (competências do SIAI × NumeroParcela). valor = SIAI, ou o do órgão.
    """
    dt = pd.Timestamp(c.DataNotificacao)
    siai = run_query_df(SQL_SIAI, engd, cpf=c.cpf, ano_min=dt.year)
    eh_tce = pd.Series([rubrica_tce(n, processo, cod) for n, cod in zip(siai.rubrica, siai.codigo, strict=True)],
                       index=siai.index, dtype=bool)
    siai = siai[eh_tce &(siai.ano * 100 + siai.mes >= dt.year * 100 + dt.month)]
    siai = (siai.assign(valor=siai.valor.astype(float))
            .groupby(["ano", "mes", "orgao", "codigo", "rubrica"], as_index=False)
            .valor.sum().sort_values(["ano", "mes"]))
    org = list(parcelas.sort_values("NumeroParcela").itertuples())
    if siai.empty and not org:
        if baixas:
            linhas = [dict(ref=f"Evento {ev}", competencia=None, detalhe=f"baixa de {d:%d/%m/%Y}",
                           siai=None, orgao=None, valor=v, ob=cred.casar(v, dt.normalize()))
                      for ev, d, v in baixas]
            return "baixas", linhas
        return "nenhuma", []

    pares: list[tuple] = []  # (linha SIAI | None, parcela do órgão | None)
    if org and all(pd.notna(o.MesReferencia) for o in org):
        chave = {(int(o.AnoReferencia), int(o.MesReferencia)): o for o in org}
        for s in siai.itertuples():
            pares.append((s, chave.pop((int(s.ano), int(s.mes)), None)))
        pares += [(None, o) for o in chave.values()]
    else:  # ponytail: pareia pela ordem; contagens diferentes desalinham → divergência no resumo
        s_rows = list(siai.itertuples())
        pares = [(s_rows[i] if i < len(s_rows) else None, org[i] if i < len(org) else None)
                 for i in range(max(len(s_rows), len(org)))]

    linhas = []
    for i, (s, o) in enumerate(pares, 1):
        if s is not None:
            ano, mes = int(s.ano), int(s.mes)
        elif pd.notna(o.MesReferencia):
            ano, mes = int(o.AnoReferencia), int(o.MesReferencia)
        else:
            ano = mes = None
        valor = float(s.valor) if s is not None else float(o.Valor)
        # OB conciliada no módulo; senão, crédito idêntico (de M a M+2, ou após a notificação)
        if o is not None and pd.notna(o.IdLancamento):
            ob = pd.Series(dict(DtMovimento=pd.Timestamp(o.DtMovimento), Documento=o.Documento,
                                Valor=float(o.ValorOB)))
        elif ano is not None:
            ini = pd.Timestamp(ano, mes, 1)
            ob = cred.casar(valor, ini, ini + pd.offsets.MonthEnd(3))
        else:
            ob = cred.casar(valor, dt.normalize())
        competencia = comp(ano, mes) if ano is not None else None
        linhas.append(dict(
            ref=competencia or f"{i}ª parcela", competencia=competencia,
            detalhe=f"{s.codigo} – {s.rubrica}" if s is not None else None,
            siai=float(s.valor) if s is not None else None,
            orgao=float(o.Valor) if o is not None else None, valor=valor, ob=ob))
    fonte = "+".join(f for f, tem in (("siai", not siai.empty), ("orgao", bool(org))) if tem)
    return fonte, linhas


def carregar() -> list[dict]:
    engp, engd = get_connection("processo"), get_connection("BdDIP")
    uni = run_query_df(SQL_UNIVERSO, engp)
    cad = run_query_df(SQL_CADASTROS, engd)
    parcelas = run_query_df(SQL_PARCELAS, engd)
    desde = pd.Timestamp(cad.DataNotificacao.min()).normalize()
    cred = Creditos(run_query_df(SQL_FRAP_CREDITOS, engd, desde=desde),
                    set(parcelas.IdLancamento.dropna().astype(int)))
    frap_fim = pd.Timestamp(run_query_df(SQL_FRAP_FIM, engd).fim[0])

    itens = []
    for p in uni.sort_values(["ano", "num"]).itertuples():
        processo = f"{p.num}/{p.ano}"
        eventos = run_query_df(SQL_EVENTOS, engp, num=p.num, ano=p.ano)
        baixas = []
        for e in eventos[eventos.nome.str.contains("Execucoes_Baixa", case=False)].itertuples():
            v = RE_BAIXA.findall(texto_pdf(e.setor, e.arquivo))
            if v:
                baixas.append((int(e.evento), pd.Timestamp(e.data_resumo), num(v[0])))
        cads = cad[(cad.num == p.num) & (cad.ano == p.ano)]
        item = dict(processo=processo, marcador=MARCADORES[int(p.IdMarcador)], assunto=p.assunto,
                    relator=p.relator or "", setor=p.setor, baixas=baixas,
                    total_baixas=round(sum(v for *_, v in baixas), 2), frap_fim=frap_fim,
                    nome=None, notificado=None, retido=0.0, frap=0.0, fonte="—", linhas=[])
        itens.append(item)
        if len(cads) != 1:
            item["motivo"] = (f"{len(cads)} responsáveis/cadastros — análise manual" if len(cads)
                              else "sem cadastro no módulo Desconto em Folha")
            continue
        c = cads.iloc[0]
        ev_notif = eventos[eventos.id_evento == c.IdEventoNotificacao]
        notif = (valor_notificado(eventos, int(ev_notif.ordem.iloc[0]))
                 if not ev_notif.empty else None)
        fonte, linhas = retencoes(c, processo, parcelas[parcelas.id == c.id], baixas, cred, engd)
        saldo = run_query_df(SQL_SALDO, engp, id=int(c.IdDebito))
        item.update(
            saldo_principal=round(float(saldo.principal.sum()), 2),
            saldo_atualizado=round(float(saldo.atualizado.sum()), 2),
            nome=c.nome, cpf=c.cpf, orgao=c.orgao, id_debito=int(c.IdDebito),
            notificacao=c.NumeroNotificacao, data_notificacao=pd.Timestamp(c.DataNotificacao),
            evento_notificacao=int(ev_notif.evento.iloc[0]) if not ev_notif.empty else None,
            notificado=notif[0] if notif else None, evento_valor=notif[1] if notif else None,
            fonte=fonte, linhas=linhas,
            retido=round(sum(r["valor"] for r in linhas), 2),
            frap=round(sum(float(r["ob"].Valor) for r in linhas if r["ob"] is not None), 2),
        )
        if processo in BAIXAS_INFORMADAS:
            item["baixa_informada"] = BAIXAS_INFORMADAS[processo]
            item["total_baixas"] = round(item["total_baixas"] + item["baixa_informada"], 2)
            item["saldo_atualizado"] = 0.0
        if notif is None or item["evento_notificacao"] is None:
            item["motivo"] = "valor notificado não localizado nos atos anteriores ao mandado"
        elif not linhas:
            item["motivo"] = "nenhuma retenção localizada (SIAI, resposta do órgão ou baixas da CCD)"
        elif div := [r["ref"] for r in linhas if r["siai"] is not None
                     and r["orgao"] is not None and abs(r["siai"] - r["orgao"]) > 0.005]:
            item["motivo"] = f"SIAI × órgão divergem em {', '.join(div)}"
        elif (item["retido"] - item["notificado"] > TOLERANCIA
              and all(r["ob"] is not None for r in linhas)):
            # descontado além do notificado e tudo creditado → informação sugere restituir o excedente
            item["excesso"] = round(item["retido"] - item["notificado"], 2)
            item["motivo"] = None
        elif abs(item["retido"] - item["notificado"]) > TOLERANCIA:
            item["motivo"] = (f"retido R$ {brl(item['retido'])} diverge do notificado "
                              f"R$ {brl(item['notificado'])}")
        elif any(r["ob"] is None for r in linhas):
            falta = [r["ref"] for r in linhas if r["ob"] is None]
            item["motivo"] = (f"retido = notificado, mas sem crédito no FRAP para {', '.join(falta)} "
                              f"(extrato até {frap_fim:%d/%m/%Y})")
        else:
            item["motivo"] = None
    return itens


def paragrafo_excesso(it: dict) -> str:
    """Órgão descontou além do notificado: situação atípica, notificar para cessar os descontos."""
    acum, extras = 0.0, []
    for i, r in enumerate(it["linhas"], 1):
        if acum >= it["notificado"] - TOLERANCIA:
            extras.append(f"{i}ª parcela ({r['competencia']})" if r["competencia"] else f"{i}ª parcela")
        acum += r["valor"]
    lista = extras[0] if len(extras) == 1 else ", ".join(extras[:-1]) + f" e {extras[-1]}"
    return ("Registra-se que o órgão prosseguiu com o desconto após atingido o valor notificado, "
            f"retendo {'a' if len(extras) == 1 else 'as'} {lista}, de modo que o total descontado "
            f"superou em R$ {brl(it['excesso'])} o valor da notificação. " + (
            "O acréscimo corresponde à atualização monetária do débito no período do desconto: "
            "com a baixa dessa parcela, o débito foi integralmente quitado, sem saldo "
            "remanescente no sistema de execuções." if not it["saldo_atualizado"] else
            "Trata-se de situação "
            "atípica: a determinação limitava-se ao desconto do valor notificado (art. 25, § 1º, "
            "inciso I, da Resolução nº 013/2015-TCE), razão pela qual o órgão deve ser notificado "
            "para que cesse os descontos relativos a este processo."))


def montar_paragrafos(it: dict) -> tuple[list[str], list[tuple]]:
    pars = [
        f'Trata-se do Processo de Execução em que se executa multa imputada a '
        f'{nome_proprio(it["nome"])} (CPF nº {fmt_cpf(it["cpf"])}). Por determinação constante '
        f'do Evento {it["evento_valor"]}, foi expedida notificação {orgao_txt(it["orgao"])} para '
        f'o desconto em folha de pagamento do valor de R$ {brl(it["notificado"])}, nos termos '
        f'do {FUNDAMENTO_DESCONTO}.'
    ]
    n = len(it["linhas"])
    tem_siai, tem_orgao = "siai" in it["fonte"], "orgao" in it["fonte"]
    frap_txt = ("creditadas na conta do Fundo de Reaparelhamento e Aperfeiçoamento (FRAP), "
                "conforme o quadro a seguir:")
    excesso = it.get("excesso", 0.0)
    correspondencia = (f"superando em R$ {brl(excesso)} o valor notificado" if excesso
                       else "correspondentes ao valor notificado")
    parcelas_txt = (f"1 parcela que totaliza R$ {brl(it['retido'])}" if n == 1
                    else f"{n} parcelas que totalizam R$ {brl(it['retido'])}")
    if tem_siai:
        rubricas = sorted({r["detalhe"] for r in it["linhas"] if r["detalhe"]})
        txt = ("Consultadas as folhas de pagamento remetidas ao SIAI Pessoal, verificou-se a "
               f"retenção, na{'s' if len(rubricas) > 1 else ''} rubrica{'s' if len(rubricas) > 1 else ''} "
               f"{'; '.join(rubricas)}, de {parcelas_txt}, {correspondencia}")
        if tem_orgao:
            txt += (", em conformidade com as parcelas informadas pelo órgão em resposta à "
                    "notificação")
        pars.append(f"{txt}, todas {frap_txt}")
    else:
        origem = ("das parcelas informadas pelo órgão em resposta à notificação"
                  if tem_orgao else "das baixas lançadas por esta Coordenadoria")
        pars.append(
            f"Não se localizou o desconto nas folhas de pagamento remetidas ao SIAI Pessoal. "
            f"A partir {origem}, {'identificou-se' if n == 1 else 'identificaram-se'} "
            f"{parcelas_txt}, {correspondencia}, todas {frap_txt}")
    if tem_siai or tem_orgao:
        def v(x):
            return "—" if x is None else brl(x)
        cols = [("Parcela", lambda i, r: f"{i}ª", ""),
                ("Competência", lambda i, r: r["competencia"] or "—", "")]
        if tem_siai:
            cols.append(("SIAI Pessoal (R$)", lambda i, r: v(r["siai"]),
                         brl(sum(r["siai"] or 0 for r in it["linhas"]))))
        if tem_orgao:
            cols.append(("Informado pelo órgão (R$)", lambda i, r: v(r["orgao"]),
                         brl(sum(r["orgao"] or 0 for r in it["linhas"]))))
        cols.append(("Crédito no FRAP", lambda i, r: ob_txt(r["ob"]) + (
            f" (R$ {brl(float(r['ob'].Valor))})" if r["ob"] is not None else ""),
                     f"R$ {brl(it['frap'])}"))
        cab = [c[0] for c in cols]
        linhas = [[f(i, r) for _, f, _ in cols] for i, r in enumerate(it["linhas"], 1)]
        linhas.append(["Total"] + [t for *_, t in cols[1:]])
        titulo = "Retenções na folha, parcelas informadas pelo órgão e créditos na conta do FRAP"
        if not tem_orgao:
            titulo = "Retenções no SIAI Pessoal e créditos na conta do FRAP"
        elif not tem_siai:
            titulo = "Parcelas informadas pelo órgão e créditos na conta do FRAP"
    else:
        cab = ["Parcela", "Origem", "Valor (R$)", "Crédito no FRAP"]
        linhas = [[r["ref"], r["detalhe"], brl(r["valor"]), ob_txt(r["ob"])] for r in it["linhas"]]
        linhas.append(["Total", "", brl(it["retido"]), brl(it["frap"])])
        titulo = "Parcelas descontadas e créditos na conta do FRAP"
    quadros = [("conforme o quadro a seguir", f"Quadro 1 – {titulo}", cab, linhas)]
    if ressalva := ressalva_creditos([(f"{r['ob'].DtMovimento:%d/%m/%Y}", r["ob"].Documento)
                                      for r in it["linhas"] if r["ob"] is not None]):
        pars.append(ressalva)  # logo após o parágrafo do quadro → fica abaixo da tabela

    # o residual não "deve ser baixado" aqui: só se registra que não é culpa do responsável;
    # a baixa é sugerida na conclusão (alíneas)
    residual = (f"remanesce saldo atualizado de R$ {brl(it['saldo_atualizado'])}, decorrente da "
                "atualização monetária calculada pelo próprio sistema de execução de débitos do "
                "TCE/RN (art. 119 da LC Estadual nº 464/2012), resíduo que não foi causado pelo "
                "jurisdicionado.")
    adimpliu = ("Desse modo, conclui-se que o jurisdicionado adimpliu integralmente o valor que "
                "lhe foi notificado.")
    if it["baixas"]:  # redação do usuário (14/10/2026)
        um = len(it["baixas"]) == 1 and not it.get("baixa_informada")
        evs = sorted({ev for ev, *_ in it["baixas"]})
        ref = (f"Eventos {evs[0]} a {evs[-1]}" if len(evs) > 2 and evs[-1] - evs[0] == len(evs) - 1
               else eventos_txt(evs))
        if it.get("baixa_informada"):
            ref += f" e baixa de R$ {brl(it['baixa_informada'])} lançada nesta data"
        txt = ("Esta Coordenadoria procedeu à baixa, no sistema de execuções, "
               + (f"do valor recolhido, de R$ {brl(it['total_baixas'])} ({ref})." if um else
                  f"dos valores recolhidos, que totalizam R$ {brl(it['total_baixas'])} ({ref})."))
        if it["saldo_atualizado"]:
            txt += f" Após {'a baixa' if um else 'as baixas'}, {residual}"
        elif excesso:
            pass  # a quitação é explicada no parágrafo do excesso
        else:
            txt += " Não remanesce saldo no sistema de execuções."
        pars.append(f"{txt} {adimpliu}")
    else:
        pars.append(
            "O débito consta em aberto no sistema de execuções pelo valor atualizado de "
            f"R$ {brl(it['saldo_atualizado'])}, ainda sem baixa das parcelas recolhidas. "
            f"Procede-se à baixa do valor recolhido de R$ {brl(it['retido'])}. O saldo residual "
            "atualizado que remanescer não decorre de falha do jurisdicionado ou do responsável. "
            f"{adimpliu}")
    if excesso:
        pars.append(paragrafo_excesso(it))
    cessar = []
    if excesso:
        cessar = [f"a comunicação {orgao_txt(it['orgao'])} da quitação do débito, para que não "
                  "efetue novos descontos em folha relativos a este processo;"
                  if not it["saldo_atualizado"] else
                  f"a notificação {orgao_txt(it['orgao'])} para que cesse os descontos em folha "
                  "relativos a este processo;"]
    pars += sugestao(intro_sugestao(it), cessar + alineas_fecho(it))
    return pars, quadros


# --- identidade visual TCE/RN (ref. processos/utils/gerar_informacoes_nereu_resposta_sead.py) ---
TCE = {"verde_principal": "2E5B3C", "verde_escuro": "1A3D28",
       "cinza_claro": "F2F2F2", "cinza_borda": "CCCCCC", "cinza_texto": "333333"}


def _shade(cell, hex_cor: str) -> None:
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hex_cor)
    cell._tc.get_or_add_tcPr().append(shd)


def _tabela_apos(d, ancora_texto: str, legenda: str, cabecalho: list[str],
                 linhas: list[list[str]]) -> None:
    """Insere legenda "Quadro N – título" + tabela após o parágrafo-âncora."""
    ancora = next(p for p in d.paragraphs if ancora_texto in p.text)
    cap = d.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_cap = cap.add_run(legenda)
    run_cap.bold = True
    run_cap.font.color.rgb = RGBColor.from_string(TCE["verde_escuro"])
    ancora._p.addnext(cap._p)
    t = d.add_table(rows=0, cols=len(cabecalho))
    borders = OxmlElement("w:tblBorders")
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{lado}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"),
               TCE["cinza_borda"] if lado.startswith("inside") else TCE["verde_principal"])
        borders.append(el)
    t._tbl.tblPr.append(borders)
    for i, linha in enumerate([cabecalho] + linhas):
        total = linha[0].startswith("Total")
        cells = t.add_row().cells
        for cell, texto in zip(cells, linha, strict=True):
            if i == 0:
                _shade(cell, TCE["verde_principal"])
            elif total:
                _shade(cell, TCE["verde_escuro"])
            elif i % 2 == 1:
                _shade(cell, TCE["cinza_claro"])
            par = cell.paragraphs[0]
            par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = par.add_run(texto)
            run.bold = i == 0 or total
            run.font.color.rgb = RGBColor.from_string(
                "FFFFFF" if (i == 0 or total) else TCE["cinza_texto"])
    cap._p.addnext(t._tbl)


def gerar(it: dict) -> Path:
    numero, ano = it["processo"].split("/")
    pasta = DESTINO / f"{numero}_{ano}"
    pasta.mkdir(parents=True, exist_ok=True)
    out = pasta / f"informacao_{numero}_{ano}.docx"

    pars, quadros = montar_paragrafos(it)
    doc = DocxTemplate(TEMPLATE)
    doc.render({"processo": f'{it["processo"]} - TC', "assunto": it["assunto"],
                "relator": it["relator"], "parágrafos": pars})
    d = doc.docx  # pós-processamento (get_docx() descartaria o render)
    for ancora, legenda, cab, linhas in quadros:
        _tabela_apos(d, ancora, legenda, cab, linhas)
    for p in d.paragraphs:  # alíneas da sugestão: fora da numeração, recuadas
        if RE_ALINEA.match(p.text) and (num_pr := p._p.pPr.find(qn("w:numPr"))) is not None:
            p._p.pPr.remove(num_pr)
            p.paragraph_format.left_indent = Cm(1.5)

    # data antes do bloco de assinatura (o modelo não traz)
    assinado = next(p for p in d.paragraphs if "assinado digitalmente" in p.text)
    for texto in (DATA, ""):
        novo = deepcopy(assinado._p)
        for r in list(novo):
            if r.tag == qn("w:r"):
                novo.remove(r)
        assinado._p.addprevious(novo)
        if texto:
            r = deepcopy(assinado.runs[0]._r)
            novo.append(r)
            for t in r.findall(qn("w:t")):
                t.text = texto

    if out.exists():  # preserva a versão anterior (skill edicao-minima)
        bak = out.with_name(f"{out.stem}_{datetime.now():%Y%m%d_%H%M%S}{out.suffix}")
        shutil.copy2(out, bak)
        print(f"  versão anterior preservada em: {bak.name}")
    doc.save(str(out))
    docx_to_pdf(str(out), str(pasta))
    return out


def resumo(itens: list[dict]) -> str:
    out = [f"# Desconto em folha finalizados — conferência ({hoje:%d/%m/%Y})", "",
           "Marcadores 5907 (Finalizado) e 6170 (Fim ago/set). Retido = SIAI Pessoal pareado com as parcelas do órgão; folha fora "
           "do SIAI → parcelas informadas pelo órgão ou baixas da CCD. "
           f"Extrato do FRAP até {itens[0]['frap_fim']:%d/%m/%Y}." if itens else "", "",
           "| Processo | Marcador | Responsável | Notificação | Notificado (R$) | Retido (R$) "
           "| FRAP (R$) | Baixas CCD (R$) | Resultado |",
           "|---|---|---|---|---|---|---|---|---|"]
    for it in itens:
        res = "**informação gerada**" if it["motivo"] is None else it["motivo"]
        notif = (f"{brl(it['notificado'])} (Ev. {it['evento_valor']})"
                 if it["notificado"] else "—")
        nt = (f"{it['notificacao']} (Ev. {it['evento_notificacao']})"
              if it["nome"] else "—")
        out.append(
            f"| {it['processo']} | {it['marcador']} | {it['nome'] or '—'} | {nt} | {notif} "
            f"| {brl(it['retido'])} ({len(it['linhas'])}, {it['fonte']}) | {brl(it['frap'])} "
            f"| {brl(it['total_baixas'])} ({len(it['baixas'])}) | {res} |")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    import docx

    sys.stdout.reconfigure(encoding="utf-8")
    itens = carregar()
    (DESTINO / "resumo.md").write_text(resumo(itens), encoding="utf-8")  # sempre o universo todo
    print(resumo(itens))
    for it in itens:
        if it["motivo"] is not None or (sys.argv[1:] and it["processo"] not in sys.argv[1:]):
            continue
        out = gerar(it)
        d = docx.Document(str(out))
        texto = "\n".join([p.text for p in d.paragraphs]
                          + [c.text for t in d.tables for r in t.rows for c in r.cells])
        assert "{{" not in texto and "}}" not in texto, f'{it["processo"]}: placeholder solto'
        for s in (it["processo"], brl(it["notificado"]), DATA,
                  "Quadro 1 –", "art. 26 da Resolução"):
            assert s in texto, f'{it["processo"]}: falta "{s}"'
        assert "É a informação" not in texto and "deve ser baixado" not in texto
        assert all(p.paragraph_format.left_indent for p in d.paragraphs if RE_ALINEA.match(p.text))
        assert len(d.tables) == 1, f'{it["processo"]}: {len(d.tables)} quadros'
        assert out.with_suffix(".pdf").exists(), f"{out.name}: PDF não gerado"
        print(f'{it["processo"]}: {out.relative_to(DESTINO)} + PDF')
