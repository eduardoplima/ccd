import pymssql
import os
import pypdf

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