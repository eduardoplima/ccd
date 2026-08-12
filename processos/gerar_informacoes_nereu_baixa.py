"""Informações de pagamento dos débitos de NEREU BATISTA LINHARES.

Dez processos de execução em que a multa foi paga por desconto em folha (2025) e a
transferência ao FRAP foi conciliada no histórico do débito. A informação comunica o
pagamento ao Conselheiro Relator e pede as providências do art. 26 da Resolução nº
013/2015-TCE (exclusão do Cadastro Informativo + arquivamento) quando não há saldo.

O parágrafo 2 refaz a conciliação: resposta da SEAD ao TCE (ofício autuado como processo
"RESPOSTA À COMUNICAÇÃO Nº ..." e apensado à execução, com o evento indicado nos autos),
competência do desconto, o par de processos que a mesma ordem bancária cobre e o item do
extrato do FRAP (nº da OB, data de emissão e data do crédito, de BdDIP.dbo.FRAPLancamento).

Levantamento em NEREU_PAGOS.md, revisto em 05/08/2026 contra a cadeia de débitos
(`IdDebitoAnterior` aponta para trás: a FOLHA é o débito vigente — ver
[[exe-debito-cadeia-folha-vigente]]). Dois quadros distintos:

- **Quitados**: 003269/2023 e 003661/2022 — pai "Pago Integralmente" e o saldo residual
  do filho cancelado por erro de cadastro. Cabe o art. 26 na íntegra.
- **Com saldo**: os outros oito — pai "Pago parcialmente" e filho(s) ainda "Em Aberto"
  (R$ 29,62 a R$ 158,58, atualização posterior ao desconto). O órgão pagador desconta e
  repassa o valor da notificação e não reprocessa a atualização perante o Tribunal, de
  modo que o resíduo não é imputável ao responsável; a conclusão sugere o cancelamento do
  valor residual, com quitação e arquivamento, e o encaminhamento traz o pedido subsidiário
  de arquivamento sem cancelamento (art. 159 da LC 464/2012 e art. 25, II e § 7º, da
  Res. 013/2015).

Base: processos/modelos/nereu_baixa.docx.
Rodar: .venv/Scripts/python.exe processos/gerar_informacoes_nereu_baixa.py
"""
import shutil
from datetime import datetime
from pathlib import Path

from docxtpl import DocxTemplate

from ccd.config import cpf
from ccd.db import run_query_df
from ccd.docs import docx_to_pdf

BASE = Path(__file__).parent
TEMPLATE = str(BASE / "modelos" / "nereu_baixa.docx")
DESTINO = BASE / "nereu_baixa"

RESPONSAVEL = "Nereu Batista Linhares"
_cpf = cpf("NEREU")
CPF = f"{_cpf[:3]}.{_cpf[3:6]}.{_cpf[6:9]}-{_cpf[9:]}"
DESTINATARIO = "ao Conselheiro Relator"  # Carlos Thompson Costa Fernandes em todos

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]
hoje = datetime.now()
DATA = f"Natal/RN, {hoje.day} de {MESES[hoje.month - 1]} de {hoje.year}."

# id_debito -> desconto, documento (ordem bancária) do extrato do FRAP, processo descontado em
# conjunto e a resposta do órgão nos autos. Os descontos foram feitos aos pares, com uma única
# ordem bancária cobrindo dois processos.
# `ev_notificacao`: evento da NOTIFICAÇÃO PARA DESCONTO EM FOLHA (28-30/10/2024).
# `oficio`/`apenso`/`ev_resposta`: a SEAD respondeu por ofício, autuado como processo
# "RESPOSTA À COMUNICAÇÃO Nº ..." e apensado à execução no evento indicado
# (conferido em 12/08/2026: Processos.IdProcessoApensador + Pro_ProcessoEvento). Os dados da OB
# (emissão, crédito, valor total) vêm ao vivo de BdDIP.dbo.FRAPLancamento pelo `doc`.
DEBITOS = [
    {"id": 22596, "mes": "janeiro/2025",   "doc": "202.501.310.027.938", "par": "003661/2022",
     "ev_notificacao": 91, "oficio": "10342/2024", "apenso": "300044/2025", "ev_resposta": 94},
    {"id": 22554, "mes": "janeiro/2025",   "doc": "202.501.310.027.938", "par": "003269/2023",
     "ev_notificacao": 85, "oficio": "10341/2024", "apenso": "300038/2025", "ev_resposta": 88},
    {"id": 22595, "mes": "fevereiro/2025", "doc": "202.502.280.064.161", "par": "001418/2023",
     "ev_notificacao": 85, "oficio": "10274/2024", "apenso": "300036/2025", "ev_resposta": 88},
    {"id": 23478, "mes": "fevereiro/2025", "doc": "202.502.280.064.161", "par": "001391/2023",
     "ev_notificacao": 79, "oficio": "10273/2024", "apenso": "300037/2025", "ev_resposta": 82},
    {"id": 22484, "mes": "março/2025",     "doc": "202.504.010.028.737", "par": "000099/2023",
     "ev_notificacao": 80, "oficio": "10275/2024", "apenso": "300033/2025", "ev_resposta": 83},
    {"id": 23057, "mes": "março/2025",     "doc": "202.504.010.028.737", "par": "003666/2022",
     "ev_notificacao": 84, "oficio": "10276/2024", "apenso": "300032/2025", "ev_resposta": 87},
    {"id": 23466, "mes": "abril/2025",     "doc": "202.505.060.035.364", "par": "001420/2023",
     "ev_notificacao": 74, "oficio": "10283/2024", "apenso": "300030/2025", "ev_resposta": 77},
    {"id": 22452, "mes": "abril/2025",     "doc": "202.505.060.035.364", "par": "001417/2023",
     "ev_notificacao": 79, "oficio": "10285/2024", "apenso": "300029/2025", "ev_resposta": 82},
    {"id": 23056, "mes": "maio/2025",      "doc": "202.506.040.011.394", "par": "000106/2023",
     "ev_notificacao": 84, "oficio": "10282/2024", "apenso": "300031/2025", "ev_resposta": 87},
    {"id": 22859, "mes": "maio/2025",      "doc": "202.506.040.011.394", "par": "000100/2023",
     "ev_notificacao": 90, "oficio": "10281/2024", "apenso": "300043/2025", "ev_resposta": 93},
]

DESCONTO = (
    "Notificado o órgão (Evento {ev_notificacao}), a Secretaria de Estado da Administração – SEAD "
    "respondeu por meio do Ofício nº {oficio}/SEAD (Evento {ev_resposta}), no qual informa a "
    "implantação do desconto no contracheque de {mes}, no valor de R$ {total}. Trata-se de "
    "R$ {valor} referente à multa imputada no âmbito do presente processo somada à multa objeto do "
    "processo nº {par} – TC, no valor de R$ {valor_par}. A conciliação consistiu no cotejo desse "
    "montante com o extrato da conta corrente nº {conta} do FRAP, onde se identificou a Ordem "
    "Bancária nº {doc}, emitida em {data_ob}, creditada em {data_extrato} no montante exato de "
    "R$ {total}, correspondente à transferência informada pelo órgão responsável."
)

CONCLUSAO_QUITADO = (
    "Comprovado o recolhimento do valor devido, impõe-se a exclusão do nome do responsável do "
    "Cadastro Informativo de Créditos não Quitados do Tribunal de Contas do Estado e o posterior "
    "arquivamento do processo de execução, na forma do art. 26 da Resolução nº 013/2015 – TCE/RN, "
    "devendo constar dos autos a certidão declaratória da quitação de que trata o seu parágrafo único."
)
CONCLUSAO_COM_SALDO = (
    "Verifica-se que o desconto consignado foi efetivado no valor fixado por este Tribunal no "
    "momento da notificação ao órgão. O saldo remanescente decorre da atualização incidente até o "
    "adimplemento da dívida (art. 119 da LC Estadual nº 464/2012). Trata-se de resíduo cuja "
    "cobrança custaria mais que o próprio valor a ser recuperado. Em face disso, sugere-se o "
    "cancelamento do valor residual, com expedição de quitação ao responsável e o consequente "
    "arquivamento do processo."
)

ENCAMINHAMENTO_QUITADO = (
    f"Ante o exposto, remetem-se os autos {DESTINATARIO}, com sugestão de arquivamento do processo."
)
ENCAMINHAMENTO_COM_SALDO = (
    "Ante o exposto, remetem-se os autos ao Exmo. Conselheiro Relator, com sugestão de arquivamento "
    "do processo e de cancelamento da dívida remanescente ou, subsidiariamente, de arquivamento sem "
    "cancelamento do débito — permanecendo o devedor obrigado ao pagamento do saldo —, nos termos do "
    "art. 159 da Lei Complementar Estadual nº 464/2012 e do art. 25, inciso II e § 7º, da Resolução "
    "nº 013/2015 – TCE/RN."
)


def brl(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")


def carregar() -> list[dict]:
    """Dados vivos de cada débito: processo/assunto da execução, valor recolhido, ordem
    bancária do extrato do FRAP e saldo remanescente (filhos da cadeia ainda em aberto)."""
    ids = ",".join(str(d["id"]) for d in DEBITOS)
    pais = run_query_df(f"""
        SELECT e.IdDebito, s.DescricaoStatusDivida situacao, e.ValorPago,
               RTRIM(pe.numero_processo) numero, RTRIM(pe.ano_processo) ano,
               RTRIM(pe.assunto) assunto, RTRIM(pe.setor_atual) setor, re.nome relator
        FROM Exe_Debito e
        LEFT JOIN Exe_StatusDivida s ON s.CodigoStatusDivida = e.CodigoStatusDivida
        LEFT JOIN Processos pe ON pe.IdProcesso = e.IdProcessoExecucao
        LEFT JOIN Relator re ON re.codigo = pe.codigo_relator
        WHERE e.IdDebito IN ({ids})""").set_index("IdDebito")
    saldos = run_query_df(f"""
        SELECT f.IdDebitoAnterior pai, f.IdDebito, f.valorOriginalDebito valor
        FROM Exe_Debito f
        LEFT JOIN Exe_StatusDivida s ON s.CodigoStatusDivida = f.CodigoStatusDivida
        WHERE f.IdDebitoAnterior IN ({ids}) AND s.DescricaoStatusDivida = 'Em Aberto'
        ORDER BY f.IdDebito""")
    docs = ",".join(f"'{d['doc']}'" for d in DEBITOS)
    obs = run_query_df(f"""
        SELECT l.Documento, l.DocData, l.DtMovimento, l.Valor, c.Conta
        FROM BdDIP.dbo.FRAPLancamento l
        JOIN BdDIP.dbo.FRAPConta c ON c.IdConta = l.IdConta
        WHERE l.Documento IN ({docs})""").set_index("Documento")

    itens = []
    for deb in DEBITOS:
        pai = pais.loc[deb["id"]]
        abertos = saldos[saldos.pai == deb["id"]]
        ob = obs.loc[deb["doc"]]
        pago = float(pai.ValorPago)
        item = {**deb, "numero": pai.numero, "ano": pai.ano, "assunto": pai.assunto,
                "relator": pai.relator, "setor": pai.setor, "situacao": pai.situacao,
                "pago": pago, "saldo": float(abertos.valor.sum()),
                "abertos": [(int(r.IdDebito), float(r.valor)) for r in abertos.itertuples()],
                "conta": ob.Conta.strip(), "total": float(ob.Valor),
                # a OB cobre os dois processos do par: o resto é a multa do outro
                "valor_par": round(float(ob.Valor) - pago, 2),
                "data_ob": ob.DocData.strftime("%d/%m/%Y"),
                "data_extrato": ob.DtMovimento.strftime("%d/%m/%Y")}
        itens.append(item)
    return itens


def status_debito(item: dict) -> str:
    if not item["abertos"]:
        return (f'O débito nº {item["id"]} consta como {item["situacao"]}, '
                f'não remanescendo saldo em aberto em nome do responsável.')
    valores = [f"R$ {brl(v)} (débito Id {i})" for i, v in item["abertos"]]
    detalhe = " e ".join([", ".join(valores[:-1]), valores[-1]] if len(valores) > 2 else valores)
    # com um único resíduo o total já está dito: nada de "o que perfaz"
    if len(valores) > 1:
        detalhe += f", o que perfaz R$ {brl(item['saldo'])}"
    return (f'O débito nº {item["id"]} consta como {item["situacao"]}, '
            f'remanescendo em aberto débitos derivados de {detalhe}.')


def contexto(item: dict) -> dict:
    quitado = not item["abertos"]
    # parágrafos numerados: o modelo não tem lista automática, o número vai no texto
    corpo = {
        "abertura": 1,
        "desconto": 2,
        "status": 3,
        "conclusao": 4,
        "encaminhamento": 5,
    }
    return {
        "processo": f'{item["numero"]}/{item["ano"]} - TC',
        "assunto": item["assunto"],
        "relator": item["relator"].title(),
        "responsavel": RESPONSAVEL,
        "cpf": CPF,
        "valor": brl(item["pago"]),
        "n_abertura": f'{corpo["abertura"]}. ',
        "n_desconto": f'{corpo["desconto"]}. ',
        "desconto": DESCONTO.format(**{**item, "valor": brl(item["pago"]),
                                       "valor_par": brl(item["valor_par"]),
                                       "total": brl(item["total"])}),
        "status": f'{corpo["status"]}. {status_debito(item)}',
        "conclusao": f'{corpo["conclusao"]}. ' + (
            CONCLUSAO_QUITADO if quitado else CONCLUSAO_COM_SALDO),
        "encaminhamento": f'{corpo["encaminhamento"]}. ' + (
            ENCAMINHAMENTO_QUITADO if quitado else ENCAMINHAMENTO_COM_SALDO),
        "destinatario": DESTINATARIO,
        "data": DATA,
    }


def gerar(item: dict) -> Path:
    pasta = DESTINO / f'{item["numero"]}_{item["ano"]}'
    pasta.mkdir(parents=True, exist_ok=True)
    out = pasta / f'informacao_{item["numero"]}_{item["ano"]}.docx'
    doc = DocxTemplate(TEMPLATE)
    doc.render(contexto(item))
    # preserva a versão anterior antes de sobrescrever (skill edicao-minima)
    if out.exists():
        bak = out.with_name(f"{out.stem}_{datetime.now():%Y%m%d_%H%M%S}{out.suffix}")
        shutil.copy2(out, bak)
        print(f"  versão anterior preservada em: {bak.name}")
    doc.save(str(out))
    docx_to_pdf(str(out), str(pasta))
    return out


if __name__ == "__main__":
    import docx  # noqa: E402

    itens = carregar()

    # check (ponytail): a OB de cada par cobre exatamente os dois processos
    por_processo = {f'{i["numero"]}/{i["ano"]}': i for i in itens}
    for i in itens:
        par = por_processo[i["par"]]
        assert par["doc"] == i["doc"], f'{i["numero"]}: par com outra ordem bancária'
        assert abs(par["pago"] - i["valor_par"]) < 0.01, (
            f'{i["numero"]}: {brl(i["pago"])} + {brl(par["pago"])} != {brl(i["total"])}')

    for item in itens:
        ctx = contexto(item)
        print(f'{item["numero"]}/{item["ano"]} (setor {item["setor"]}, débito {item["id"]}, '
              f'{item["situacao"]}, saldo R$ {brl(item["saldo"])}):')
        out = gerar(item)

        # check (ponytail): nada de placeholder solto e os campos foram para o lugar certo
        texto = "\n".join(p.text for p in docx.Document(str(out)).paragraphs)
        assert "{{" not in texto and "}}" not in texto, "placeholder não substituído"
        for trecho in (ctx["processo"], ctx["assunto"], RESPONSAVEL, CPF, item["doc"],
                       ctx["valor"], ctx["desconto"], ctx["status"], ctx["conclusao"],
                       ctx["encaminhamento"], DATA):
            assert trecho in texto, f'{item["numero"]}: faltou "{trecho[:40]}"'
        # a conciliação tem de vir rastreável: resposta do órgão, OB e as duas datas
        for trecho in (f'Evento {item["ev_notificacao"]}', f'Evento {item["ev_resposta"]}',
                       item["oficio"], item["doc"], item["data_ob"], item["data_extrato"],
                       item["par"], brl(item["total"]), brl(item["valor_par"])):
            assert trecho in ctx["desconto"], f'{item["numero"]}: faltou "{trecho}"'
        # os cinco parágrafos do corpo saem numerados
        for n in range(1, 6):
            assert f"\n{n}. " in "\n" + texto, f'{item["numero"]}: faltou o parágrafo {n}'
        # sem saldo, a conclusão é o art. 26 puro; havendo saldo, cancelamento do resíduo +
        # quitação + arquivamento, com o pedido subsidiário no encaminhamento
        if item["abertos"]:
            for trecho in ("cancelamento do valor residual", "expedição de quitação",
                           "arquivamento do processo"):
                assert trecho in ctx["conclusao"], f'{item["numero"]}: faltou "{trecho}"'
            for trecho in ("cancelamento da dívida remanescente", "subsidiariamente",
                           "art. 159"):
                assert trecho in ctx["encaminhamento"], f'{item["numero"]}: faltou "{trecho}"'
            # resíduo único: o total não se repete
            assert ("o que perfaz" in ctx["status"]) == (len(item["abertos"]) > 1)
        else:
            assert "art. 26" in ctx["conclusao"]
        assert out.with_suffix(".pdf").is_file(), "PDF não gerado"
        print(f"  salvo: {out.relative_to(BASE)} (+ .pdf)")
