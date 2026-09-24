"""Informações de pagamento dos débitos de NEREU BATISTA LINHARES.

Dez processos de execução em que a multa foi paga por desconto em folha (2025) e a
transferência ao FRAP foi conciliada no histórico do débito. A informação comunica o
pagamento ao Conselheiro Relator e pede as providências do art. 26 da Resolução nº
013/2015-TCE (exclusão do Cadastro Informativo + arquivamento) quando não há saldo.

O parágrafo 2 refaz a conciliação: resposta da SEAD ao TCE (ofício autuado como processo
"RESPOSTA À COMUNICAÇÃO Nº ..." e apensado à execução, com o evento indicado nos autos),
competência do desconto, o par de processos que a mesma ordem bancária cobre e o item do
extrato do FRAP (nº da OB, data de emissão e data do crédito, de BdDIP.dbo.FRAPLancamento).

Levantamento em docs/notas/NEREU_PAGOS.md, revisto em 05/08/2026 contra a cadeia de débitos
(`IdDebitoAnterior` aponta para trás: a FOLHA é o débito vigente — ver
[[exe-debito-cadeia-folha-vigente]]). Dois quadros distintos:

- **Quitados**: 003269/2023 e 003661/2022 — pai "Pago Integralmente" e o saldo residual
  do filho cancelado por erro de cadastro. Não havendo o que cancelar, o parágrafo 5 toma a
  conciliação como comprovação do recolhimento e pede o arquivamento pelo art. 26.
- **Com saldo**: os outros oito — pai "Pago parcialmente" e filho(s) ainda "Em Aberto"
  (R$ 29,62 a R$ 158,58, atualização posterior ao desconto). O órgão pagador desconta e
  repassa o valor da notificação e não reprocessa a atualização perante o Tribunal, de
  modo que o resíduo não é imputável ao responsável; a conclusão sugere o cancelamento do
  valor residual, com quitação e arquivamento, e o encaminhamento traz o pedido subsidiário
  de arquivamento sem cancelamento (art. 159 da LC 464/2012 e art. 25, II e § 7º, da
  Res. 013/2015). É esse resíduo — dívida ainda formalmente em aberto — que impediu o
  arquivamento imediato após a baixa (parágrafo 3).

O parágrafo 4 é comum aos dez e remete aos dois eventos do sobrestamento, buscados ao vivo por
`eventos_sobrestamento`: a última informação da CCD anterior à decisão e a decisão do Relator.
Em nove deles a informação é a instrutiva que noticiou o acórdão do Pleno do TJRN no Mandado de
Segurança nº 0807247-93.2025.8.20.0000 (29/06/2026), e o mandado é citado. Em 003269/2023 não há
instrutiva: a última informação da CCD (Evento 118) é o despacho sobre o próprio pagamento, e o
parágrafo sai sem citar o mandado.

Base: processos/modelos/nereu_baixa.docx.
Rodar: .venv/Scripts/python.exe processos/utils/gerar_informacoes_nereu_baixa.py
"""
import shutil
from datetime import datetime
from pathlib import Path

from docxtpl import DocxTemplate

from ccd.config import cpf
from ccd.db import run_query_df
from ccd.docs import docx_to_pdf

BASE = Path(__file__).resolve().parents[1]  # processos/
TEMPLATE = str(BASE / "modelos" / "nereu_baixa.docx")
DESTINO = BASE / "projetos" / "nereu_baixa"

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

# o acórdão do Pleno do TJRN (29/06/2026) no MS anulou as multas ligadas às vantagens
# transitórias dos servidores da saúde; foi o que a CCD noticiou nos autos (Evento `ev_judicial`)
# e o que levou o Relator a manter o sobrestamento (Evento `ev_decisao`)
MANDADO = "Mandado de Segurança Cível nº 0807247-93.2025.8.20.0000"
TITULO_DECISAO = "CCD - mantem sobrestamento"  # informação do gabinete (GCCTH)
TITULO_INSTRUTIVA = "InformacaoInstrutiva"  # informações da CCD sobre o acórdão do MS

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
    "A conciliação realizada comprova o recolhimento do valor devido, portanto, impõe-se a "
    "exclusão do nome do responsável do Cadastro Informativo de Créditos não Quitados do "
    "Tribunal de Contas do Estado e o posterior arquivamento do processo de execução, na forma "
    "do art. 26 da Resolução nº 013/2015 – TCE/RN."
)
CONCLUSAO_COM_SALDO = (
    "Verifica-se que o desconto consignado foi efetivado no valor fixado por este Tribunal no "
    "momento da notificação ao órgão. O saldo remanescente decorre da atualização incidente até o "
    "adimplemento da dívida (art. 119 da LC Estadual nº 464/2012). Trata-se de resíduo cuja "
    "cobrança custaria mais que o próprio valor a ser recuperado. Em face disso, sugere-se o "
    "cancelamento do valor residual, com expedição de quitação ao responsável e o consequente "
    "arquivamento do processo."
)

SOBRESTAMENTO = (
    "{inicio} os fatos {referentes}relatados no Evento {ev_judicial} e a determinação do Exmo. "
    "Conselheiro Relator exarada no Evento {ev_decisao}."
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


def eventos_sobrestamento(ev) -> tuple[int | None, str, int | None]:
    """(evento da informação da CCD, título dela, evento da decisão do Relator) do processo.

    A decisão é a última do gabinete; a informação que a motivou é a última da CCD antes dela
    (das instrutivas sobre o acórdão do MS, as anteriores são versões substituídas da mesma
    matéria). O título importa: só a instrutiva trata do MS — em 003269/2023 a última é um
    despacho sobre o próprio pagamento, e aí o parágrafo 4 sai sem citar o mandado."""
    decisao = ev[ev.titulo.str.startswith(TITULO_DECISAO)].evento
    if decisao.empty:
        return None, "", None
    y = int(decisao.max())
    antes = ev[(ev.setor == "CCD") & (ev.evento < y)].sort_values("evento")
    if antes.empty:
        return None, "", y
    return int(antes.iloc[-1].evento), antes.iloc[-1].titulo, y


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
    # eventos citados no parágrafo 3. `vw_ata_informacao.IdProcesso` vem NULL: filtrar por
    # numero/ano. "Evento" na tela é o SequencialProcessoEvento (ver [[evento-e-sequencialprocessoevento]])
    chaves = {f"p{n}": f'{r.numero}/{r.ano}' for n, r in enumerate(pais.itertuples())}
    eventos = run_query_df(f"""
        SELECT RTRIM(v.numero_processo)+'/'+RTRIM(v.ano_processo) processo, RTRIM(v.setor) setor,
               RTRIM(v.Titulo_Modelo_informacao) titulo, ev.SequencialProcessoEvento evento
        FROM vw_ata_informacao v
        JOIN Pro_ProcessoEvento ev ON ev.idInformacao = v.idInformacao
        WHERE RTRIM(v.numero_processo)+'/'+RTRIM(v.ano_processo)
              IN ({",".join(f":{k}" for k in chaves)})""", **chaves)
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
        ev_judicial, titulo_judicial, ev_decisao = eventos_sobrestamento(
            eventos[eventos.processo == f"{pai.numero}/{pai.ano}"])
        item = {**deb, "ev_judicial": ev_judicial, "titulo_judicial": titulo_judicial,
                "ev_decisao": ev_decisao,
                "numero": pai.numero, "ano": pai.ano, "assunto": pai.assunto,
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
    plural = len(valores) > 1
    return (f'O débito nº {item["id"]} consta como {item["situacao"]}, remanescendo em aberto '
            f'{"os valores" if plural else "o valor"} de {detalhe}. '
            f'{"Estes constituem" if plural else "Este constitui"} dívida em nome do responsável, '
            f'o que obstou o arquivamento imediato dos autos por ocasião da baixa do pagamento.')


def contexto(item: dict) -> dict:
    quitado = not item["abertos"]
    # parágrafos numerados: o modelo não tem lista automática, o número vai no texto
    corpo = {
        "abertura": 1,
        "desconto": 2,
        "status": 3,
        "sobrestamento": 4,
        "conclusao": 5,
        "encaminhamento": 6,
    }
    # só a informação instrutiva noticia o acórdão do MS; a do 003269/2023 trata do pagamento
    referentes = f"referentes ao {MANDADO} " if item["titulo_judicial"] == TITULO_INSTRUTIVA else ""
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
        # sem resíduo o parágrafo 3 não termina no arquivamento obstado: nada a que dar seguimento
        "sobrestamento": f'{corpo["sobrestamento"]}. ' + SOBRESTAMENTO.format(
            inicio="Sobrevieram" if quitado else "Em seguida, sobrevieram",
            referentes=referentes, **item),
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
                       ctx["valor"], ctx["desconto"], ctx["status"], ctx["sobrestamento"],
                       ctx["conclusao"], ctx["encaminhamento"], DATA):
            assert trecho in texto, f'{item["numero"]}: faltou "{trecho[:40]}"'
        # a conciliação tem de vir rastreável: resposta do órgão, OB e as duas datas
        for trecho in (f'Evento {item["ev_notificacao"]}', f'Evento {item["ev_resposta"]}',
                       item["oficio"], item["doc"], item["data_ob"], item["data_extrato"],
                       item["par"], brl(item["total"]), brl(item["valor_par"])):
            assert trecho in ctx["desconto"], f'{item["numero"]}: faltou "{trecho}"'
        # os seis parágrafos do corpo saem numerados (o 4 é o do sobrestamento)
        for n in range(1, 7):
            assert f"\n{n}. " in "\n" + texto, f'{item["numero"]}: faltou o parágrafo {n}'
        assert "\n7. " not in "\n" + texto, f'{item["numero"]}: parágrafo a mais'
        # os eventos citados têm de existir: sem eles o parágrafo 4 sai com "None". o mandado
        # só é citado quando a informação da CCD é a instrutiva que noticiou o acórdão
        assert item["ev_judicial"] and item["ev_decisao"], (
            f'{item["numero"]}: eventos do sobrestamento não localizados')
        for trecho in (f'Evento {item["ev_judicial"]}', f'Evento {item["ev_decisao"]}'):
            assert trecho in ctx["sobrestamento"], f'{item["numero"]}: faltou "{trecho}"'
        assert (MANDADO in ctx["sobrestamento"]) == (item["titulo_judicial"] == TITULO_INSTRUTIVA), (
            f'{item["numero"]}: menção ao mandado não confere com o Evento {item["ev_judicial"]} '
            f'({item["titulo_judicial"]})')
        # sem saldo, atesta-se o pagamento e aplica-se o art. 26; havendo saldo, a conclusão pede
        # cancelamento do resíduo + quitação + arquivamento, com o pedido subsidiário no encaminhamento
        if item["abertos"]:
            assert ("Estes constituem" in ctx["status"]) == (len(item["abertos"]) > 1)
            for trecho in ("cancelamento do valor residual", "expedição de quitação",
                           "arquivamento do processo"):
                assert trecho in ctx["conclusao"], f'{item["numero"]}: faltou "{trecho}"'
            for trecho in ("cancelamento da dívida remanescente", "subsidiariamente",
                           "art. 159"):
                assert trecho in ctx["encaminhamento"], f'{item["numero"]}: faltou "{trecho}"'
            # resíduo único: o total não se repete
            assert ("o que perfaz" in ctx["status"]) == (len(item["abertos"]) > 1)
        else:
            for trecho in ("A conciliação realizada", "recolhimento do valor devido", "art. 26"):
                assert trecho in ctx["conclusao"], f'{item["numero"]}: faltou "{trecho}"'
        assert out.with_suffix(".pdf").is_file(), "PDF não gerado"
        print(f"  salvo: {out.relative_to(BASE)} (+ .pdf)")
