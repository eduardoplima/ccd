import pytest
import os

from antecedentes import get_connection, get_processos_transito_by_cpf, create_antecedentes_doc

@pytest.mark.skip
def test_get_connection():
    conn = get_connection()
    assert conn is not None
    conn.close()

@pytest.mark.skip
def test_get_processos_transito_by_cpf():
    cpf = '06979014757'
    os.chdir('/home/eduardo/Dev/ccd/scripts')
    df = get_processos_transito_by_cpf(cpf)
    assert df is not None
    assert len(df) > 0
    print(df)

def test_create_doc():
    cpf = '06979014757'
    os.chdir('/home/eduardo/Dev/ccd/scripts')
    context = {
        'nome': 'Eduardo Pereira Lima',
        'cargo': 'Coordenador de Controle de Decisões',
        'processo': '002479/2020',
        'assunto': 'CONTAS DO CHEFE DO PODER EXECUTIVO REFERENTE AO EXERCÍCIO DE 2016',
        'interessado': 'PREFEITURA MUNICIPAL DE SERRA CAIADA',
        'evento': '90',
        'responsavel': 'Maria do Socorro dos Anjos Furtado',
        'encaminhamento': 'Gabinete da Conselheira Relatora',
        'data': '21 de janeiro de 2025',
    }
    create_antecedentes_doc(cpf, context, 'antecedentes_maria.docx')

    cpf = '42164516400'
    context = {
        'nome': 'Eduardo Pereira Lima',
        'cargo': 'Coordenador de Controle de Decisões',
        'processo': '010354/2016',
        'assunto': ' CONTAS DO CHEFE DO EXECUTIVO (2015) / PROCESSO',
        'interessado': 'PREFEITURA MUNICIPAL DE ITAJÁ',
        'evento': '87',
        'responsavel': 'Licelio Jackson Guimarães',
        'encaminhamento': 'Gabinete da Conselheira Relatora',
        'data': '21 de janeiro de 2025',
    }
    create_antecedentes_doc(cpf, context, 'antecedentes_licelio.docx')