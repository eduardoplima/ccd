"""Cruzamento parcela x contracheque x extrato FRAP dos processos finalizados com desconto em folha.

Uma aba por processo (002013/2025, 003045/2025, 000407/2025, 003665/2025), com o plano de
parcelamento (extraido dos documentos dos autos), o desconto na folha (BdSIAIPessoal, rubrica
TCE/FRAP) e o item de extrato correspondente (BdDIP.FRAPLancamento).

Rodar (da raiz do repo):
  .venv/Scripts/python.exe scripts/analise/cruzamento_desconto_folha_frap.py
"""

from __future__ import annotations

import pandas as pd

from ccd.config import REPO_ROOT, cpf, load_env
from ccd.db import get_connection, run_query_df

load_env()

OUT = REPO_ROOT / "saidas" / "analise" / "desconto_folha_cruzamento_frap.xlsx"

# ponytail: o plano de parcelas nao esta no banco (so nos oficios/despachos dos autos),
# entao fica aqui como literal, com a fonte documental na propria aba.
PROCESSOS = [
    dict(
        aba="002013_2025",
        processo="002013/2025",
        nome="SERGIO EDUARDO BEZERRA TEODORO",
        cpf=cpf("SERGIO_TEODORO"),
        orgao="SECRETARIA DE ESTADO DA EDUCACAO (SEEC)",
        debito=21712,
        origem="001151/2021",
        plano="12 parcelas de R$ 997,41 (multa atualizada R$ 11.968,94)",
        fonte="Informacao instrutiva CCD de 13/11/2025 (evento 204) + folha SIAIDP; SEEC nao respondeu formalmente",
        parcelas=[(i + 1, m, a, 997.41) for i, (m, a) in enumerate(
            [(6, 2025), (7, 2025), (8, 2025), (9, 2025), (10, 2025), (11, 2025), (12, 2025),
             (1, 2026), (2, 2026), (3, 2026), (4, 2026), (5, 2026)])],
        lancamentos=[2429, 2995, 2997, 3003, 3007],
    ),
    dict(
        aba="003045_2025",
        processo="003045/2025",
        nome="ROSALBA CIARLINI ROSADO",
        cpf=cpf("ROSALBA_ROSADO"),
        orgao="INSTITUTO DE PREVIDENCIA DOS SERVIDORES DO RN (IPERN)",
        debito=20625,
        origem="005528/2020",
        plano="3 parcelas de R$ 1.800,00 + 1 de R$ 1.080,51 (multa R$ 6.480,51)",
        fonte="Oficio 026/2026-IPERN/PR de 06/03/2026 (evento 147 / informacao 144)",
        parcelas=[(1, 2, 2026, 1800.00), (2, 3, 2026, 1800.00),
                  (3, 4, 2026, 1800.00), (4, 5, 2026, 1080.51)],
        lancamentos=[14050, 14096, 14151, 13884],
    ),
    dict(
        aba="000407_2025",
        processo="000407/2025",
        nome="FELIPE FERREIRA MENEZES ARAUJO",
        cpf=cpf("FELIPE_ARAUJO"),
        orgao="PREFEITURA MUNICIPAL DE LAJES",
        debito=27512,
        origem="200042/2023",
        plano="6 parcelas de R$ 410,68 (multa R$ 2.464,08)",
        fonte="Oficio 0001/2026-CGM de Lajes, 28/01/2026 (apenso 300132/2026)",
        # folha municipal: sem competencia declarada e sem rastro no SIAIDP
        parcelas=[(i, None, None, 410.68) for i in range(1, 7)],
        lancamentos=[14139, 14140, 14141, 14142],
    ),
    dict(
        aba="003665_2025",
        processo="003665/2025",
        nome="FABIO BEZERRA DE OLIVEIRA",
        cpf=cpf("FABIO_OLIVEIRA"),
        orgao="PREFEITURA MUNICIPAL DE SERRA DO MEL",
        debito=28314,
        origem="007603/2019",
        plano="4 parcelas de R$ 1.313,21 (multa R$ 5.252,85)",
        fonte="Manifestacao do Municipio de 31/03/2026 + comprovante de deposito (informacoes 44 e 45)",
        parcelas=[(i, None, None, 1313.21) for i in range(1, 5)],
        lancamentos=[14061, 14082, 14135, 14183],
    ),
]

_HIST = {  # pymssql devolve o varchar latin1 com replacement char
    "Ordem Banc�ria": "Ordem Bancaria",
    "632 Ordem Banc�ria": "632 Ordem Bancaria",
    "870 Transfer�ncia recebida": "870 Transferencia recebida",
    "Transfer�ncia recebida": "Transferencia recebida",
}


def _txt(s: object) -> str:
    s = "" if s is None else str(s)
    return _HIST.get(s, s.replace("�", "?"))


eng = get_connection("processo")
engp = get_connection("BdSIAIPessoal")
cpfs = ",".join(f"'{p['cpf']}'" for p in PROCESSOS)
ids_lanc = ",".join(str(i) for p in PROCESSOS for i in p["lancamentos"])

# --- descontos na folha (rubrica TCE/FRAP), deduplicados por competencia+valor -----------
cc = run_query_df(f"""
 SELECT P.CPF, CAST(LTRIM(RTRIM(CCI.MesReferencia)) AS INT) AS Mes,
        CAST(LTRIM(RTRIM(CCI.AnoReferencia)) AS INT) AS Ano, CCI.Valor,
        MIN(CCI.IdContraChequeItem) AS IdContraChequeItem, COUNT(*) AS folhas,
        MIN(R.Codigo) AS RubricaCodigo
 FROM dbo.SiaiDp_ContraChequeItem CCI
 JOIN dbo.SiaiDp_Rubrica R ON R.IdRubrica = CCI.IdRubrica
 JOIN dbo.SiaiDp_ContraCheque CC ON CC.IdContraCheque = CCI.IdContraCheque
 LEFT JOIN dbo.SiaiDp_Funcionario FU ON FU.IdFuncionario = CC.IdFuncionario
 LEFT JOIN dbo.Comum_Pessoa P ON P.IdPessoa = FU.IdPessoa
 WHERE P.CPF IN ({cpfs}) AND R.Tipo = '2'
   AND (UPPER(R.Descricao) LIKE '%TCE%' OR UPPER(R.Descricao) LIKE '%TRIBUNAL DE CONTAS%'
        OR UPPER(R.Descricao) LIKE '%FRAP%')
   AND CAST(LTRIM(RTRIM(CCI.AnoReferencia)) AS INT) >= 2025
 GROUP BY P.CPF, CAST(LTRIM(RTRIM(CCI.MesReferencia)) AS INT),
          CAST(LTRIM(RTRIM(CCI.AnoReferencia)) AS INT), CCI.Valor
""", engp)

# --- itens de extrato -------------------------------------------------------------------
lanc = run_query_df(f"""
 SELECT l.IdLancamento, l.IdConta, c.Conta, l.DtMovimento, l.Valor, l.Historico, l.Documento,
        CAST(l.Descricao AS varchar(300)) AS Descricao, cat.Codigo AS Categoria
 FROM BdDIP.dbo.FRAPLancamento l
 JOIN BdDIP.dbo.FRAPConta c ON c.IdConta = l.IdConta
 LEFT JOIN BdDIP.dbo.FRAPCategoria cat ON cat.IdCategoria = l.IdCategoria
 WHERE l.IdLancamento IN ({ids_lanc})
""", eng).set_index("IdLancamento")

# --- debitos ----------------------------------------------------------------------------
deb = run_query_df(f"""
 SELECT d.IdDebito, d.valorOriginalDebito, s.DescricaoStatusDivida AS status,
        processo.dbo.fn_Exe_RetornaValorAtualizado(d.IdDebito) AS valor_atual
 FROM Exe_Debito d LEFT JOIN Exe_StatusDivida s ON s.CodigoStatusDivida = d.CodigoStatusDivida
 WHERE d.IdDebito IN ({",".join(str(p["debito"]) for p in PROCESSOS)})
""", eng).set_index("IdDebito")

MESES = "jan fev mar abr mai jun jul ago set out nov dez".split()

with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
    for p in PROCESSOS:
        d = deb.loc[p["debito"]]
        cab = pd.DataFrame({
            "Campo": ["Processo de execucao", "Processo de origem", "Responsavel", "CPF",
                      "Orgao notificado", "IdDebito", "Valor original do debito",
                      "Valor atualizado hoje", "Situacao do debito no banco",
                      "Plano de parcelamento", "Fonte do plano", "Nota"],
            "Valor": [p["processo"], p["origem"], p["nome"], p["cpf"], p["orgao"], p["debito"],
                      float(d["valorOriginalDebito"]), round(float(d["valor_atual"]), 2),
                      _txt(d["status"]), p["plano"], p["fonte"],
                      "O credito no extrato nao identifica a competencia; a associacao "
                      "parcela x lancamento segue a ordem cronologica dos repasses."],
        })

        # repasses em ordem cronologica, atribuidos as parcelas na ordem (FIFO)
        repasses = lanc.loc[p["lancamentos"]].sort_values("DtMovimento").reset_index()
        cc_pessoa = cc[cc.CPF == p["cpf"]]

        linhas = []
        for i, (num, mes, ano, valor) in enumerate(p["parcelas"]):
            comp = f"{MESES[mes - 1]}/{ano}" if mes else ""
            item = cc_pessoa[(cc_pessoa.Mes == mes) & (cc_pessoa.Ano == ano)] if mes else cc_pessoa.iloc[0:0]
            r = repasses.iloc[i] if i < len(repasses) else None
            linhas.append({
                "Parcela": num,
                "Competencia": comp,
                "Valor previsto": valor,
                # o item da rubrica 644 e a soma de todos os descontos TCE do mes: em
                # 02-05/2026 o de Sergio traz 997,41 desta multa + 1.316,88 de outro debito
                "Item da folha (total da rubrica no mes)": float(item.Valor.iloc[0]) if len(item) else None,
                "IdContraChequeItem": int(item.IdContraChequeItem.iloc[0]) if len(item) else None,
                "Rubrica": _txt(item.RubricaCodigo.iloc[0]) if len(item) else "",
                "IdLancamento (extrato)": int(r.IdLancamento) if r is not None else None,
                "Data do credito": r.DtMovimento if r is not None else None,
                "Valor do credito": float(r.Valor) if r is not None else None,
                "Conta FRAP": r.Conta if r is not None else "",
                "Historico": _txt(r.Historico) if r is not None else "",
                "Documento (ag/cc remetente)": r.Documento if r is not None else "",
                "Descricao do extrato": _txt(r.Descricao) if r is not None else "",
                "Status": ("REPASSADA" if r is not None
                           else ("DESCONTADA SEM REPASSE" if len(item) else "SEM DESCONTO / A VENCER")),
            })
        tab = pd.DataFrame(linhas)

        total = pd.DataFrame({
            "Campo": ["Total previsto no plano", "Total descontado na folha",
                      "Total repassado (extrato)", "Diferenca (previsto - repassado)"],
            "Valor": [round(tab["Valor previsto"].sum(), 2),
                      round(tab.loc[tab["IdContraChequeItem"].notna(), "Valor previsto"].sum(), 2),
                      round(tab["Valor do credito"].fillna(0).sum(), 2),
                      round(tab["Valor previsto"].sum() - tab["Valor do credito"].fillna(0).sum(), 2)],
        })

        cab.to_excel(writer, sheet_name=p["aba"], index=False, startrow=0)
        tab.to_excel(writer, sheet_name=p["aba"], index=False, startrow=len(cab) + 3)
        total.to_excel(writer, sheet_name=p["aba"], index=False,
                       startrow=len(cab) + len(tab) + 6)

        ws = writer.sheets[p["aba"]]
        for col, w in zip("ABCDEFGHIJKLMN", (34, 30, 16, 30, 20, 10, 20, 16, 16, 12, 26, 28, 40, 24)):
            ws.column_dimensions[col].width = w
        print(f"{p['processo']}: {len(tab)} parcelas | repassado "
              f"{tab['Valor do credito'].fillna(0).sum():.2f} de {tab['Valor previsto'].sum():.2f}")

print(f"\nSalvo: {OUT}")
