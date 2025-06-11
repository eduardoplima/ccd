import pymssql
import os
import pypdf

from dotenv import load_dotenv
from pathlib import Path

DIR_INFORMACOES = '/media/informacoes_pdf/'

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

def get_file_path(row):
    return Path(DIR_INFORMACOES) / row['setor'].strip() / row['arquivo']