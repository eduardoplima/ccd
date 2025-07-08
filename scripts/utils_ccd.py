import pymssql
import os
import pypdf

import pandas as pd

from dotenv import load_dotenv
from pathlib import Path



def get_connection(db='processo'):
    load_dotenv()
    return pymssql.connect(
        server=os.getenv("SQL_SERVER_HOST"),
        user=os.getenv("SQL_SERVER_USER"),
        password=os.getenv("SQL_SERVER_PASS"),
        port=os.getenv("SQL_SERVER_PORT"),
        database=db
    )

def extract_text_from_pdf(file_path):
    try:
        with open(file_path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            text = ''
            for page in reader.pages:
                text += page.extract_text() or ''
            return text
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ''

DIR_INFORMACOES = '/media/informacoes_pdf/'
def get_info_file_path(row, dir_info=r'\\10.24.0.6\tce$\Informacoes_PDF'):
    return Path(dir_info) / row['setor'].strip() / row['arquivo']


def get_informacoes_processo(processo, conn=None):
    sql_all_informacoes_processos = '''
    SELECT concat(rtrim(inf.setor),'_',inf.numero_processo ,'_',inf.ano_processo,'_',RIGHT(concat('0000',inf.ordem),4),'.pdf') as arquivo,
    ppe.SequencialProcessoEvento as evento,
    CONCAT(inf.numero_processo,'/', inf.ano_processo) as processo,
    inf.*
    FROM processo.dbo.vw_ata_informacao inf INNER JOIN processo.dbo.Pro_ProcessoEvento ppe 
        ON inf.idinformacao = ppe.idinformacao
    WHERE concat(inf.numero_processo, '/', inf.ano_processo) = '{}'
    '''.format(processo)
    
    all_informacoes_processos = pd.read_sql(sql_all_informacoes_processos, conn)
    all_informacoes_processos['caminho_arquivo'] = all_informacoes_processos.apply(get_info_file_path, axis=1)
    all_informacoes_processos['texto'] = all_informacoes_processos['caminho_arquivo'].apply(extract_text_from_pdf)

    return all_informacoes_processos