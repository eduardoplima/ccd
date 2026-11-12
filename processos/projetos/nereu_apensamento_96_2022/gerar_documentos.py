"""Certidão (APR 003474/2021, item "b") e Informação Instrutiva (000096/2022, itens "c"/"d"/"e")
do Despacho do Evento 63 do 000096/2022. Lê levantamento.json (rodar levantamento.py antes).

Saídas (nada é cadastrado):
  apr_3474_2021/certidao_003474_2021.docx/.pdf + anexos/despacho_ev63_000096_2022.pdf
  apr_3474_2021/envio_apr.pdf (certidão + cópia do despacho)
  000096_2022/informacao_000096_2022.docx/.pdf (anexo: ../levantamento_96_2022.xlsx)
Modelo: scripts/automacao/templates/modelo_informacao.docx (numera os parágrafos); quadros no
padrão de processos/utils/gerar_informacoes_nereu_resposta_sead.py.

Rodar: .venv/Scripts/python.exe processos/projetos/nereu_apensamento_96_2022/gerar_documentos.py
"""
import json
import shutil
from copy import deepcopy
from datetime import datetime
from pathlib import Path

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor
from docxtpl import DocxTemplate

from ccd.config import REPO_ROOT
from ccd.docs import docx_to_pdf
from ccd.pdf import merge_pdfs
from ccd.processo import get_info_file_path

BASE = Path(__file__).resolve().parent
TEMPLATE = str(REPO_ROOT / "scripts" / "automacao" / "templates" / "modelo_informacao.docx")
RELATOR = "Antonio Ed Souza Santana"  # Conselheiro titular
DESPACHO_PDF = {"setor": "GCAED", "arquivo": "GCAED_000096_2022_0054.pdf"}  # Evento 63
ASSUNTO_96 = "EXECUÇÃO DA DECISÃO PROFERIDA NOS AUTOS DO PROCESSO Nº 019291/2017 - TC"
ASSUNTO_APR = ("APURAÇÃO DE RESPONSABILIDADE DANO ERÁRIO PERPETRADO PELO IPERN EM FACE DESCUMPRIMENTO "
               "REITERADO DECISÕES TCE/RN RELATIVAS A BENEFÍCIOS PREVID., CONFORME DETERMINADO NO "
               "ACÓRDÃO Nº 189/2021 (PROC: 102523/2018)")
TCE = {"verde_principal": "2E5B3C", "verde_escuro": "1A3D28",
       "cinza_claro": "F2F2F2", "cinza_borda": "CCCCCC", "cinza_texto": "333333"}
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]
hoje = datetime.now()
DATA = f"Natal/RN, {hoje.day} de {MESES[hoje.month - 1]} de {hoje.year}."
L = json.loads((BASE / "levantamento.json").read_text(encoding="utf-8"))
TC = "{}-TC".format


# ---------- docx helpers (padrão dos lotes nereu_*) ----------
def _xml_texto(el) -> str:
    return "".join(t.text or "" for t in el.findall(f".//{qn('w:t')}")).strip()


def _shade(cell, hex_cor: str) -> None:
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hex_cor)
    cell._tc.get_or_add_tcPr().append(shd)


def _tabela_apos(d, ancora_texto: str, legenda: str, cabecalho: list[str], linhas: list[list[str]]) -> None:
    """Insere legenda "Quadro N – título" + tabela após o parágrafo-âncora."""
    ancora = next(p for p in d.paragraphs if ancora_texto in p.text)
    cap = d.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.keep_with_next = True
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
        el.set(qn("w:color"), TCE["cinza_borda"] if lado.startswith("inside") else TCE["verde_principal"])
        borders.append(el)
    t._tbl.tblPr.append(borders)
    for i, linha in enumerate([cabecalho] + linhas):
        cells = t.add_row().cells
        for cell, texto in zip(cells, linha, strict=True):
            if i == 0:
                _shade(cell, TCE["verde_principal"])
            elif i % 2 == 1:
                _shade(cell, TCE["cinza_claro"])
            par = cell.paragraphs[0]
            par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = par.add_run(texto)
            run.bold = i == 0
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor.from_string("FFFFFF" if i == 0 else TCE["cinza_texto"])
    cap._p.addnext(t._tbl)


def montar(out: Path, processo: str, assunto: str, titulo: str, ps: list[str],
           quadros: list[tuple[str, str, list[str], list[list[str]]]]) -> None:
    doc = DocxTemplate(TEMPLATE)
    doc.render({"processo": f"{processo} - TC", "assunto": assunto, "relator": RELATOR, "parágrafos": ps})
    d = doc.docx  # pós-processamento (get_docx() descartaria o render)
    cab = next(p for p in d.paragraphs if p.text == "INFORMAÇÃO INSTRUTIVA")
    cab.runs[0].text = titulo
    for _ in range(2):  # o modelo deixa duas linhas em branco após o título
        nxt = cab._p.getnext()
        if _xml_texto(nxt):
            break
        nxt.getparent().remove(nxt)
    for q in quadros:
        _tabela_apos(d, *q)
    # data antes do bloco de assinatura (sem parágrafos vazios), assinatura presa à data
    assinado = next(p for p in d.paragraphs if "assinado digitalmente" in p.text)
    prev = assinado._p.getprevious()
    while prev is not None and not _xml_texto(prev):
        vazio, prev = prev, prev.getprevious()
        vazio.getparent().remove(vazio)
    novo = deepcopy(assinado._p)
    for r in list(novo):
        if r.tag == qn("w:r"):
            novo.remove(r)
    assinado._p.addprevious(novo)
    r = deepcopy(assinado.runs[0]._r)
    novo.append(r)
    for t in r.findall(qn("w:t")):
        t.text = DATA
    idx = next(i for i, p in enumerate(d.paragraphs) if p.text.startswith("Natal/RN"))
    for p in d.paragraphs[idx - 1:-1]:  # último parágrafo + data + assinatura ficam juntos
        p.paragraph_format.keep_with_next = True

    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():  # preserva a versão anterior (skill edicao-minima)
        shutil.copy2(out, out.with_name(f"{out.stem}_{datetime.now():%Y%m%d_%H%M%S}{out.suffix}"))
    doc.save(str(out))
    docx_to_pdf(str(out), str(out.parent))

    # check (ponytail): texto completo, legendas, sem placeholder, sem termo proibido
    dd = docx.Document(str(out))
    texto = "\n".join(p.text for p in dd.paragraphs)
    assert "{{" not in texto and "}}" not in texto, "placeholder não substituído"
    for trecho in (*ps, DATA, f"{processo} - TC", RELATOR, f"\n{titulo}\n", *(q[1] for q in quadros)):
        assert trecho in texto, f"faltou {trecho[:60]!r}"
    for proibido in ("É a informação.", "Substituto", "INFORMAÇÃO INSTRUTIVA" if titulo != "INFORMAÇÃO INSTRUTIVA" else "\x00"):
        assert proibido not in texto, f"termo proibido {proibido}"
    assert len(dd.tables) == len(quadros), "quadros não inseridos"
    assert out.with_suffix(".pdf").is_file(), "PDF não gerado"


# ---------- Certidão na APR (item "b") ----------
SITUACAO = {"000134/2022": "Desconto em folha implantado"}


def certidao() -> Path:
    tab2 = L["tabela2"]
    div2 = [(e, o) for t, e, o in L["divergencias"] if t == "2"]
    ps = [
        "Certifico, para os fins do item “b)” das determinações do Despacho proferido pelo Conselheiro Relator "
        "no Evento 63 do Processo nº 000096/2022-TC (Execução da Decisão nº 745/2020-TC), em 11/11/2026, cuja "
        "cópia acompanha esta certidão, que os processos originários relacionados no quadro a seguir — vinculados "
        "a execuções de multa em face do Sr. Nereu Batista Linhares nas quais já foram praticados atos efetivos de "
        "cobrança, a saber, desconto em folha de pagamento implantado ou remessa ao Ministério Público de Contas para "
        "inscrição do crédito em dívida ativa e cobrança judicial, nos termos do art. 118, incisos I e II, da Lei "
        "Complementar Estadual nº 464/2012 — deverão ser desconsiderados na contabilização da multa diária global "
        "cominada no Acórdão nº 162/2022-TC, por já terem sido objeto de cobrança individual, ponto a ser enfrentado "
        "por ocasião do julgamento de mérito desta Apuração de Responsabilidade.",

        "Certifico, ainda, conforme consignado no referido Despacho, que fica mantida nestes autos a apuração do "
        "dano ao erário relativo aos processos originários acima relacionados, prosseguindo as respectivas "
        "execuções em seu trâmite regular.",

        "Registro, por fim, para a devida apreciação pelo Relator, que os processos originários nº "
        + " e nº ".join(f"{TC(o)} (Processo de Execução nº {TC(e)})" for e, o in div2)
        + ", embora relacionados na Tabela 2 do Despacho, não foram localizados por esta Coordenadoria na planilha "
        "consolidada do Evento 103 destes autos.",
    ]
    linhas = [[str(i), TC(e), TC(o), SITUACAO.get(e, "Remetida ao MPC (dívida ativa – PGE/RN)")]
              for i, (e, o) in enumerate(tab2, 1)]
    out = BASE / "apr_3474_2021" / "certidao_003474_2021.docx"
    montar(out, "003474/2021", ASSUNTO_APR, "CERTIDÃO", ps, [(
        "cuja cópia acompanha esta certidão",
        "Quadro 1 – Processos originários a desconsiderar na contabilização da multa diária da APR (Tabela 2 do Despacho)",
        ["Nº", "Processo de Execução", "Processo Originário", "Situação da execução"], linhas)])
    anexos = out.parent / "anexos"
    anexos.mkdir(exist_ok=True)
    despacho = anexos / "despacho_ev63_000096_2022.pdf"
    shutil.copy2(get_info_file_path(DESPACHO_PDF), despacho)
    merge_pdfs([out.with_suffix(".pdf"), despacho], out.parent / "envio_apr.pdf")
    return out


# ---------- Informação no 000096/2022 (itens "c", "d", "e") ----------
def informacao() -> Path:
    rem = L["remanescentes_detalhe"]
    assert len(rem) == 1 and rem[0]["execucao"] == "003380/2024", rem  # texto escrito para esse cenário
    r = rem[0]
    valor = f"{float(r['valor']):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    n_t1, n_t2 = L["tabela1"].__len__(), L["tabela2"].__len__()
    ps = [
        "Trata-se de Processo de Execução da Decisão nº 745/2020-TC (Processo nº 019291/2017-TC) em face do Sr. "
        "Nereu Batista Linhares, Presidente do Instituto de Previdência dos Servidores do Estado do Rio Grande do "
        "Norte – IPERN, no qual esta Coordenadoria, por meio da Informação Instrutiva do Evento 60, propôs a reunião, "
        "mediante apensamento a estes autos, de todas as execuções de multa do referido responsável sob a relatoria "
        "do Conselheiro Antonio Ed Souza Santana, à exceção das abrangidas pela Apuração de Responsabilidade nº "
        "003474/2021-TC.",

        "Pelo Despacho do Evento 63, de 11/11/2026, o Conselheiro Relator acolheu parcialmente a proposta e "
        "determinou a reunião apenas das execuções cujos processos originários integram o escopo da APR nº "
        "003474/2021-TC — definido pela relação consolidada pela Diretoria de Atos de Pessoal no Evento 103 daquele "
        "feito, e não pela lista formal de apensados — e nas quais não tenham sido praticados atos efetivos de "
        "cobrança (desconto em folha de pagamento implantado ou remessa ao Ministério Público de Contas para "
        "inscrição em dívida ativa), por vislumbrar, em juízo preliminar, a incidência do non bis in idem entre a "
        "multa diária individual e a responsabilização concentrada na referida apuração, inclusive a multa diária "
        f"cominada no Acórdão nº 162/2022-TC. Coube à assessoria do Gabinete o apensamento das {n_t1} execuções da "
        "Tabela 1 (item “a”) e, a esta Diretoria: (b) viabilizar a juntada de cópia do Despacho à APR, certificando "
        f"que os {n_t2} processos originários da Tabela 2 deverão ser desconsiderados na contabilização da multa "
        "diária global; (c) revisar o levantamento anexo ao Evento 60 à luz do critério fixado e reunir eventuais "
        "execuções remanescentes; (d) manifestar-se sobre a possibilidade de arquivamento destes autos e dos "
        "apensados em situação idêntica; e (e) encaminhar o feito ao Ministério Público de Contas, sem retorno ao "
        "Gabinete.",

        "Em cumprimento ao item “c”, esta Coordenadoria refez o levantamento adotando como critério a relação de "
        f"processos originários do Evento 103 da APR nº 003474/2021-TC ({L['originarios_ev103']} processos "
        "identificados na planilha), cotejada com a totalidade das execuções de multa em face do Sr. Nereu Batista "
        f"Linhares registradas no sistema desta Corte ({L['execucoes_nereu']} execuções, das quais {L['gcaed']} sob a "
        "relatoria do Conselheiro Antonio Ed Souza Santana). O resultado completo consta da planilha anexa.",

        f"Identificaram-se {L['gcaed_na_apr']} execuções sob essa relatoria cujos processos originários integram o "
        f"escopo da APR. Dentre elas, as {n_t1} relacionadas na Tabela 1 do Despacho foram confirmadas: todas "
        "tramitam no Gabinete do Relator, têm o processo originário correspondente ao registrado no sistema e não "
        "registram desconto em folha implantado nem envio à Procuradoria-Geral do Estado, tendo a cobrança se "
        f"limitado ao protesto cartorial ({L['protestadas_t1']} com a dívida protestada); {L['suspensas_t1']} delas "
        "têm o débito atualmente na situação “suspenso”, em razão da liminar outrora deferida no Mandado de "
        f"Segurança nº 0807247-93.2025.8.20.0000. As {n_t2} execuções da Tabela 2 também foram confirmadas (17 em "
        "tramitação no Ministério Público de Contas, a de nº 000117/2022-TC já devolvida ao Gabinete e a de nº "
        "000134/2022-TC com desconto em folha em acompanhamento nesta Coordenadoria).",

        "Além das execuções já relacionadas no Despacho, o cotejo revelou uma única execução remanescente que "
        "preenche o critério fixado — processo originário constante do Evento 103 da APR, relatoria do Conselheiro "
        "Antonio Ed Souza Santana e ausência de atos efetivos de cobrança —, conforme o quadro a seguir:",

        f"O Processo nº {TC(r['execucao'])} encontra-se no Gabinete do Relator (última peça: Informação Instrutiva "
        "desta Coordenadoria de 29/10/2026, que sugeriu a retomada da marcha processual), razão pela qual não é "
        "possível a esta Diretoria promover o seu apensamento. Sugere-se, assim, que o Gabinete o inclua na reunião "
        "determinada no item “a”. Não foram identificadas execuções remanescentes com desconto em folha implantado "
        "ou remessa ao Ministério Público de Contas que devessem ser acrescidas à certidão do item “b”.",

        "Registra-se, para a devida apreciação pelo Relator, que três processos originários relacionados no "
        "Despacho não foram localizados por esta Coordenadoria na planilha do Evento 103 da APR, conforme o quadro "
        "seguinte, de modo que as execuções correspondentes talvez não devam integrar a reunião (Tabela 1) ou a "
        "certidão (Tabela 2):",

        f"As demais {L['gcaed_fora_apr']} execuções sob a mesma relatoria cujos processos originários não integram "
        f"a APR, bem como as {L['outros_relatores_na_apr']} execuções de outros relatores com processo originário no "
        "Evento 103, não foram alcançadas pelo Despacho e prosseguem em seu trâmite regular.",

        f"Quanto ao item “b”, esta Coordenadoria elaborou a certidão de que os {n_t2} processos originários "
        "relacionados na Tabela 2 do Despacho deverão ser desconsiderados na contabilização da multa diária global "
        "cominada no Acórdão nº 162/2022-TC, mantida a apuração do dano ao erário a eles relativo, a qual será "
        "juntada, acompanhada de cópia do Despacho do Evento 63, aos autos da APR nº 003474/2021-TC, que atualmente "
        "tramitam na Diretoria de Atos de Pessoal.",

        "No tocante ao item “d”, esta Coordenadoria manifesta-se favoravelmente ao arquivamento destes autos e das "
        "execuções a ele apensadas em situação idêntica. A multa diária prevista no art. 110 da Lei Complementar "
        "Estadual nº 464/2012 e no art. 34 da Resolução nº 028/2012-TCE tem natureza coercitiva, acessória à "
        "obrigação de fazer imposta nas decisões denegatórias de registro. Com a medida cautelar deferida no "
        "Acórdão nº 162/2022-TC, o Tribunal Pleno concentrou em um único comando a exigência de cumprimento de todas "
        "as decisões abrangidas pela apuração, inclusive as até então descumpridas, dotando-o de multa diária "
        "própria e da advertência de responsabilização solidária pelo dano, de sorte que a coerção individual "
        "exercida em cada execução perdeu a sua função instrumental.",

        "Verifica-se, ademais, a tríplice identidade apontada no Despacho — de sujeito (o mesmo responsável, "
        "pessoalmente citado na APR), de fato (a omissão continuada em adotar as medidas regularizadoras "
        "determinadas nas decisões denegatórias de registro) e de fundamento (arts. 101, parágrafo único, e 110 da "
        "Lei Complementar Estadual nº 464/2012) —, de modo que o prosseguimento da cobrança individual das multas "
        "diárias configuraria dupla sanção pela mesma conduta, vedada pelo princípio do non bis in idem, à luz da "
        "Súmula nº 19 do Supremo Tribunal Federal e do art. 22, § 3º, da Lei de Introdução às Normas do Direito "
        f"Brasileiro. Anota-se que em nenhuma das {n_t1 + 1} execuções houve satisfação, ainda que parcial, do "
        "crédito, e que a maior parte dos débitos se encontra com a exigibilidade suspensa no sistema.",

        "Acolhida a proposta pelo colegiado, caberá a esta Diretoria, após o trânsito em julgado da deliberação, "
        "promover o cancelamento dos débitos no sistema de execução e solicitar o cancelamento dos protestos "
        "lavrados, com a consequente exclusão dos registros no Cadastro Informativo de Créditos não Quitados, sem "
        "prejuízo da responsabilização do Sr. Nereu Batista Linhares no âmbito da APR nº 003474/2021-TC, na qual a "
        "mesma conduta continuará a ser apreciada de forma integral, inclusive quanto ao dano ao erário.",

        "Ante o exposto, em cumprimento ao item “e” do Despacho do Evento 63, encaminham-se os autos ao Ministério "
        "Público de Contas, para emissão de parecer conclusivo sobre o arquivamento proposto, sem necessidade de "
        "retorno ao Gabinete do Relator.",
    ]
    quadros = [
        ("preenche o critério fixado", "Quadro 1 – Execução remanescente a reunir a estes autos (item “c”)",
         ["Processo de Execução", "Processo Originário", "Setor atual", "Situação do débito", "Valor original (R$)"],
         [[TC(r["execucao"]), TC(r["origem"]), r["setor"], r["situacao"], valor]]),
        ("não foram localizados por esta Coordenadoria na planilha",
         "Quadro 2 – Processos originários do Despacho não localizados no Evento 103 da APR",
         ["Tabela do Despacho", "Processo de Execução", "Processo Originário"],
         [[f"Tabela {t}", TC(e), TC(o)] for t, e, o in L["divergencias"]]),
    ]
    out = BASE / "000096_2022" / "informacao_000096_2022.docx"
    montar(out, "000096/2022", ASSUNTO_96, "INFORMAÇÃO INSTRUTIVA", ps, quadros)
    return out


if __name__ == "__main__":
    print("certidão  ->", certidao())
    print("informação ->", informacao())
