import os
import pymssql
import pytest
import pypdf
import json

from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def connection():
    return pymssql.connect(server='10.24.0.77\\ControleExterno',
                                    user=os.getenv('SQLSERVER_USER'),
                                    password=os.getenv('SQLSERVER_PASS'),
                                    port=59678,
                                    database='processo',
                                    charset='WINDOWS-1252')

@pytest.fixture
def query():
    return '''
    SELECT 
RTRIM(setor) as setor, 
resumo, 
data_resumo, 
Decisao, 
concat(rtrim(setor),'_',numero_processo ,'_',ano_processo,'_',RIGHT(concat('0000',ordem),4),'.pdf') as arquivo
FROM processo.dbo.Ata_Informacao
WHERE Decisao IS NOT NULL
AND year(data_resumo) = 2024
    '''

@pytest.mark.skip
def test_conn(connection, query):
    cursor = connection.cursor(as_dict=True)
    cursor.execute(query)
    rows = cursor.fetchall()
    assert len(rows) > 0
    cursor.close()
    connection.close()
    print(f'Test passed! {len(rows)} rows returned.')

@pytest.mark.skip
def test_pdf(connection, query):
    dir_pdf = '/mnt/informacoes_pdf'
    assert os.path.exists(dir_pdf)

    cursor = connection.cursor(as_dict=True)
    cursor.execute(query)
    rows = cursor.fetchall()
    
    row = rows[2]

    arquivo = Path(dir_pdf) / row['setor'].strip() / row['arquivo']
    print(f'File {arquivo}')
    text = []
    json_dicts = []
    
    pdf = pypdf.PdfReader(arquivo)
    for page in pdf.pages:
        text.append(page.extract_text())
    row['texto'] = text
    row['data_resumo'] = row['data_resumo'].strftime('%Y-%m-%d')
    json_dicts.append(row)

    print(f'Resumo: {row["resumo"]}')

    print(f'Texto: {row['texto']}')

    with open('output_test_2.json', 'w+', encoding='utf8') as f:
        json.dump(json_dicts, f, ensure_ascii=False)

    print(f'Test passed! {len(rows)} rows returned.')