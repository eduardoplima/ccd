"""Informações de anotação cadastral no CGAD (mesmo procedimento do 003594/2025).

Seis processos vieram à DIP/CCD para o Cadastro Geral de Acompanhamento de
Decisões determinado nos respectivos acórdãos (art. 431, IV, do Regimento
Interno c/c a Resolução nº 042/2024-TCE).

Base: processos/modelos/modelo_cadastro.doc — o texto corrido é o do modelo; só
mudam os trechos marcados ({{processo}}, {{assunto}}, {{relator}},
{{descricao}}, {{destinatario}}, {{data}}). O .docx ao lado é a conversão do
.doc usada como template do docxtpl, com três correções pontuais do modelo:
o campo "Assunto" trazia {{processo}}; o parágrafo final repetia "Ante o
exposto, esta Unidade de Controle Externo remete os autos ao"; e o destinatário
vinha fixo no feminino ("à Conselheira Relatora"), o que não serve aos dois
processos relatados pelo Conselheiro Gilberto Jales.

Rodar: .venv/Scripts/python.exe processos/gerar_informacoes_anotacao.py
"""
import shutil
from datetime import datetime
from pathlib import Path

from docxtpl import DocxTemplate

from ccd.db import run_query_df

BASE = Path(__file__).parent
TEMPLATE = str(BASE / "modelos" / "modelo_cadastro.docx")

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]
hoje = datetime.now()
DATA = f"Natal/RN, {hoje.day} de {MESES[hoje.month - 1]} de {hoje.year}."

CONSELHEIRO = "ao Conselheiro Relator"
CONSELHEIRA = "à Conselheira Relatora"

# `recomendacoes` são os IdRecomendacao do CGAD (BdDIP.dbo.Recomendacao)
# conferidos em 03/08/2026; a asserção em gerar() trava o documento caso o
# cadastro mude. Os números não vão no texto.
PROCESSOS = [
    {
        "processo": "302014/2021",
        "id_processo": 550197,
        "assunto": "DENÚNCIA",
        "relator": "Antonio Gilberto de Oliveira Jales",
        "destinatario": CONSELHEIRO,
        "recomendacoes": [928],
        "descricao":
            "de denúncia ofertada pelo Partido da Social Democracia Brasileira (PSDB) – "
            "Diretório Municipal de Goianinha/RN em face da Prefeitura Municipal de "
            "Goianinha, na qual foi proferido o Acórdão nº 51/2026-TC, pela 2ª Câmara deste "
            "Tribunal, em Sessão Virtual nº 0004vª, de 16 de março de 2026",
    },
    {
        "processo": "302645/2021",
        "id_processo": 553208,
        "assunto": "REPRESENTAÇÃO",
        "relator": "Antonio Gilberto de Oliveira Jales",
        "destinatario": CONSELHEIRO,
        "recomendacoes": [986],
        "descricao":
            "de representação relativa a certame licitatório da Prefeitura Municipal de São "
            "Gonçalo do Amarante, na qual foi proferido o Acórdão nº 90/2026-TC, pela 2ª "
            "Câmara deste Tribunal, em Sessão Virtual nº 0006vª, de 13 de abril de 2026",
    },
    {
        "processo": "003325/2024",
        "id_processo": 602108,
        "assunto": "CONTAS DO CHEFE DO PODER EXECUTIVO DA PREFEITURA MUNICIPAL DE SÍTIO "
                   "NOVO, REFERENTE AOS EXERCÍCIOS DE 2018, 2019 E 2020",
        "relator": "Ana Paula de Oliveira Gomes",
        "destinatario": CONSELHEIRA,
        "recomendacoes": [957],
        "descricao":
            "das contas do Chefe do Poder Executivo da Prefeitura Municipal de Sítio Novo, "
            "referentes aos exercícios de 2018, 2019 e 2020, nas quais foi proferido o "
            "Acórdão nº 143/2026-TC, pela 2ª Câmara deste Tribunal, em Sessão Virtual nº "
            "0008vª, de 11 de maio de 2026, sob a relatoria do Conselheiro Substituto Marco "
            "Antônio de Moraes Rêgo Montenegro, em substituição legal",
    },
    {
        "processo": "005202/2020",
        "id_processo": 540767,
        "assunto": "ACUMULAÇÃO DE CARGOS PÚBLICOS (ID15 - PFA 20/21)",
        "relator": "Ana Paula de Oliveira Gomes",
        "destinatario": CONSELHEIRA,
        "recomendacoes": [984],
        "descricao":
            "de processo relativo à acumulação de cargos públicos na Prefeitura Municipal "
            "de Nísia Floresta, no qual foi proferido o Acórdão nº 73/2025-TC, pela 2ª "
            "Câmara deste Tribunal, em Sessão Ordinária nº 00006ª, de 29 de abril de 2025",
    },
    {
        "processo": "302904/2023",
        "id_processo": 587005,
        "assunto": "REPRESENTAÇÃO",
        "relator": "Ana Paula de Oliveira Gomes",
        "destinatario": CONSELHEIRA,
        "recomendacoes": [708],
        "descricao":
            "de representação relativa ao Edital de Chamamento Público nº 009/2023 da "
            "Prefeitura Municipal de Parnamirim, na qual foi proferido o Acórdão nº "
            "214/2025-TC, pela 2ª Câmara deste Tribunal, em Sessão Ordinária nº 00016ª, de "
            "14 de outubro de 2025",
    },
    {
        "processo": "008389/2014",
        "id_processo": 358457,
        "assunto": "PLANO DE FISCALIZAÇÃO ANUAL REFERENTE AO EXERCÍCIO DE 2014/2015 "
                   "(06 volumes)",
        "relator": "Ana Paula de Oliveira Gomes",
        "destinatario": CONSELHEIRA,
        "recomendacoes": [989, 990],
        "descricao":
            "de auditoria realizada na Câmara Municipal de Passagem, no âmbito do Plano de "
            "Fiscalização Anual dos exercícios de 2014/2015, na qual foi proferido o "
            "Acórdão nº 25/2019-TC, pela 1ª Câmara deste Tribunal, em Sessão Ordinária nº "
            "00004ª, de 14 de fevereiro de 2019, mantido, no ponto, pelos Acórdãos nº "
            "258/2023-TC e nº 70/2026-TC, que apreciaram, respectivamente, o pedido de "
            "reconsideração e os embargos de declaração",
    },
]


def gerar(item: dict) -> Path:
    numero, ano = item["processo"].split("/")
    pasta = BASE / f"{numero}_{ano}"
    pasta.mkdir(exist_ok=True)
    out = pasta / f"informacao_{numero}_{ano}.docx"

    # trava o documento contra mudança no CGAD
    rec = run_query_df(
        "SELECT IdRecomendacao FROM BdDIP.dbo.Recomendacao "
        "WHERE IdProcesso = :i AND (Cancelado IS NULL OR Cancelado = 0) "
        "ORDER BY IdRecomendacao", i=item["id_processo"])
    assert sorted(rec.IdRecomendacao) == item["recomendacoes"], (
        f'{item["processo"]}: cadastro mudou (ids {sorted(rec.IdRecomendacao)}) — conferir')

    doc = DocxTemplate(TEMPLATE)
    doc.render({
        "processo": f'{item["processo"]} - TC',
        "assunto": item["assunto"],
        "relator": item["relator"],
        "descricao": item["descricao"],
        "destinatario": item["destinatario"],
        "data": DATA,
    })

    # preserva a versão anterior antes de sobrescrever (skill edicao-minima)
    if out.exists():
        bak = out.with_name(f"{out.stem}_{datetime.now():%Y%m%d_%H%M%S}{out.suffix}")
        shutil.copy2(out, bak)
        print(f"  versão anterior preservada em: {bak.name}")
    doc.save(str(out))
    return out


if __name__ == "__main__":
    import docx  # noqa: E402

    for item in PROCESSOS:
        print(f'{item["processo"]}:')
        out = gerar(item)

        # check (ponytail): nada de placeholder solto e os campos foram para o lugar certo
        salvo = docx.Document(str(out))
        texto = "\n".join(p.text for p in salvo.paragraphs)
        assert "{{" not in texto and "}}" not in texto, "placeholder não substituído"
        for trecho in (item["processo"], item["assunto"], item["relator"],
                       item["descricao"], item["destinatario"], DATA,
                       "Cadastro Geral de Acompanhamento de Decisões"):
            assert trecho in texto, f'{item["processo"]}: faltou "{trecho}"'
        assert texto.count("Ante o exposto") == 1, "parágrafo final duplicado"
        print(f"  salvo: {out}")
