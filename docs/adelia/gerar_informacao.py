"""Informação à Diretoria de Inovação Tecnológica: migração das automações de
desconto em folha e antecedentes para o Adelia.

Rodar da raiz:  .venv/Scripts/python.exe docs/adelia/gerar_informacao.py
Saída: docs/adelia/informacao_migracao_adelia.docx/.pdf (versão anterior preservada).
"""

import importlib.util
import shutil
from datetime import datetime
from pathlib import Path

from docxtpl import DocxTemplate

from ccd.config import REPO_ROOT
from ccd.docs import docx_to_pdf

PASTA = Path(__file__).resolve().parent
TEMPLATE = PASTA / "desconto_folha" / "templates" / "modelo_informacao.docx"
OUT = PASTA / "informacao_migracao_adelia.docx"

# reaproveita a tabela com identidade TCE e a data por extenso do gerador de desconto em folha
_spec = importlib.util.spec_from_file_location(
    "gi", REPO_ROOT / "processos" / "projetos" / "desconto_folha_finalizados" / "gerar_informacoes.py")
gi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gi)

PARAGRAFOS = [
    "Para viabilizar a reconstrução no ADELIA de fluxos de trabalho da CCD foram separados os "
    "artefatos que concentram as regras de negócio da produção de informações de antecedentes e "
    "desconto em folha: as consultas SQL aos bancos do Tribunal, os modelos de documento (.docx) e "
    "os prompts enviados ao modelo de linguagem, com os respectivos esquemas de saída e validações. "
    "Os arquivos estão organizados conforme o quadro a seguir.",

    "A automação de antecedentes segue quatro passos: (1) localiza o último despacho do processo e "
    "o respectivo PDF no repositório de informações (info_despacho.sql); (2) extrai do texto do "
    "despacho, por meio do modelo de linguagem, os nomes das pessoas cujos antecedentes foram "
    "requeridos, desconsiderando conselheiros, advogados e servidores (extrair_pessoas.md); "
    "(3) identifica o CPF de cada pessoa entre os responsáveis do processo (cpf_responsavel.sql) e "
    "levanta os débitos com trânsito em julgado vinculados a esse CPF (transito_cpf.sql), "
    "recorrendo à busca por nome apenas quando não houver CPF (transito_nome.sql), caso em que o "
    "resultado exige conferência para afastar homônimos; e (4) preenche o modelo antecedentes.docx.",

    # desconto em folha: só o preenchimento do modelo desconto_folha.docx
    # (automacao/desconto_folha/service.py: _QUERY_DESCONTOS + gerar_documentos)
    "A automação de desconto em folha preenche o modelo desconto_folha.docx, informação instrutiva "
    "que remete os autos à Diretoria de Expediente para notificar o órgão de vínculo do servidor a "
    "promover o desconto da multa em folha de pagamento. Segue três passos: (1) seleciona os "
    "processos em trâmite na CCD com o marcador \"DESCONTO EM FOLHA - Implementar\" "
    "(01_candidatos_e_despacho.sql); (2) levanta, para cada processo, os débitos com dívida em "
    "aberto, o nome e o CPF do responsável, o valor atualizado da multa e o órgão pagador, obtido "
    "da folha mais recente do servidor no SIAI Pessoal; e (3) soma os valores por processo, "
    "responsável e órgão e preenche o quadro de identificação do modelo (processo, assunto, "
    "servidor, órgão e valor da multa, por extenso), gerando uma informação por servidor.",

    "As consultas exigem acesso de leitura aos bancos e ao repositório indicados no quadro a seguir.",
]

ARTEFATOS = [
    ["antecedentes/sql/candidatos.sql", "Processos com marcador de antecedentes", "processo"],
    ["antecedentes/sql/info_despacho.sql", "Último despacho e PDF de origem", "processo"],
    ["antecedentes/sql/cpf_responsavel.sql", "CPF do responsável citado", "processo"],
    ["antecedentes/sql/transito_cpf.sql", "Débitos transitados por CPF", "processo"],
    ["antecedentes/sql/transito_nome.sql", "Débitos transitados por nome", "processo"],
    ["antecedentes/templates/antecedentes.docx", "Modelo da informação de antecedentes", "—"],
    ["antecedentes/prompts/extrair_pessoas.md", "Prompt de extração dos nomes", "LLM"],
    ["desconto_folha/sql/00_tabelas_controle.sql", "Tabelas de controle do fluxo", "BdDIP"],
    ["desconto_folha/sql/01 a 05", "Candidatos, cadastro, notificação, resposta e PGE",
     "processo, BdDIP"],
    ["desconto_folha/sql/06_conciliacao_frap.sql", "Conciliação com créditos do FRAP", "BdDIP"],
    ["desconto_folha/sql/07_siai_retencoes.sql", "Retenções no contracheque", "BDSiaiPessoal"],
    ["desconto_folha/templates/desconto_folha.docx", "Despacho de implantação", "—"],
    ["desconto_folha/templates/modelo_informacao.docx", "Informação de arquivamento", "—"],
    ["desconto_folha/prompts/extrair_resposta.md", "Prompt de extração do valor descontado", "LLM"],
]

ACESSOS = [
    ["processo (MSSQL)", "Processos, marcadores, informações, débitos, citações e PGE",
     "Ambos"],
    ["BdDIP (MSSQL)", "Tabelas CCDDescontoFolha*, FRAPLancamento, vwSiaiPessoalFolhaResumida",
     "Desconto em folha"],
    ["BDSiaiPessoal / Bdc (MSSQL)", "Contracheques e cadastro de órgãos", "Desconto em folha"],
    ["Informacoes_PDF (rede)", "PDFs das informações dos processos", "Ambos"],
    ["Modelo de linguagem", "DeepSeek no Azure AI Foundry do SERPRO", "Ambos"],
]


def _rotulos(d) -> None:
    """Documento sem processo: retira o cabeçalho Processo/Assunto/Relator e troca o título."""
    cab = next(p for p in d.paragraphs if p.text.startswith("Processo n"))
    cab._p.getparent().remove(cab._p)
    for p in d.paragraphs:
        for r in p.runs:
            r.text = r.text.replace("INFORMAÇÃO INSTRUTIVA", "SOLICITAÇÃO DE FUNCIONALIDADES NO ADELIA")


def main() -> None:
    doc = DocxTemplate(str(TEMPLATE))
    doc.render({
        "processo": "Não se aplica",
        "assunto": "Migração das automações de desconto em folha e antecedentes para o Adelia",
        "relator": "Diretoria de Inovação Tecnológica",
        "parágrafos": PARAGRAFOS,
    })
    d = doc.docx  # pós-processar aqui: get_docx() descartaria o render
    _rotulos(d)
    gi._tabela_apos(d, "organizados conforme", "Quadro 1 – Artefatos entregues",
                    ["Arquivo", "Finalidade", "Fonte"], ARTEFATOS)
    gi._tabela_apos(d, "acesso de leitura aos bancos", "Quadro 2 – Acessos necessários",
                    ["Recurso", "Conteúdo", "Automação"], ACESSOS)

    assinado = next(p for p in d.paragraphs if "assinado digitalmente" in p.text)
    data = assinado.insert_paragraph_before(gi.DATA)
    data.runs[0].font.name = assinado.runs[0].font.name
    # espaçamento da versão editada: uma linha em branco antes e outra depois da data
    for _ in range(2):
        antes = data._p.getprevious()
        if antes is not None and antes.tag == data._p.tag and not "".join(antes.itertext()).strip():
            antes.getparent().remove(antes)
    assinado.insert_paragraph_before("")
    # data, assinatura e nome na mesma página
    ps = d.paragraphs
    i = next(k for k, p in enumerate(ps) if p._p is data._p)
    for p in ps[i:-1]:  # o último não tem "próximo"
        p.paragraph_format.keep_with_next = True

    if OUT.exists():  # preserva a versão anterior
        shutil.copy2(OUT, OUT.with_name(f"{OUT.stem}_{datetime.now():%Y%m%d_%H%M%S}.docx"))
    doc.save(str(OUT))
    docx_to_pdf(str(OUT), str(PASTA))
    print(OUT)


if __name__ == "__main__":
    main()
