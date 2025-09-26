import os
import pypdf
import pymssql
import win32com.client
import subprocess

import pandas as pd

from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

def get_connection(db: str = 'processo') -> Engine:
    load_dotenv()
    
    server = os.getenv("SQL_SERVER_HOST")
    user = os.getenv("SQL_SERVER_USER")
    password = os.getenv("SQL_SERVER_PASS")
    port = os.getenv("SQL_SERVER_PORT", "1433")  # default MSSQL port
    database = db

    # Construct connection string for SQLAlchemy using pymssql
    connection_string = f"mssql+pymssql://{user}:{password}@{server}/{database}"

    # Create and return SQLAlchemy engine
    engine = create_engine(connection_string)
    return engine

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

def get_pdf_files_processo(processo, conn=None):
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
    return all_informacoes_processos['caminho_arquivo'].tolist()


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

def download_processo(processo, dir_destino, conn=None):
    infos = get_informacoes_processo(processo, conn)
    dir_destino = Path(dir_destino)
    dir_destino.mkdir(parents=True, exist_ok=True)

    for _, row in infos.iterrows():
        destino = dir_destino / row['arquivo']
        origem = row['caminho_arquivo']
        if origem.exists():
            with open(origem, 'rb') as fsrc:
                with open(destino, 'wb') as fdst:
                    fdst.write(fsrc.read())
        else:
            print(f"Arquivo não encontrado: {origem}")

    return infos


def merge_pdfs(pdf_files, output_path):
    writer = pypdf.PdfWriter()
    for pdf_file in pdf_files:
        reader = pypdf.PdfReader(str(pdf_file))
        for page in reader.pages:
            writer.add_page(page)
    with open(output_path, "wb") as fout:
        writer.write(fout)


def generate_pdf(doc_path, path):

    subprocess.call(['soffice',
                  '--headless',
                 '--convert-to',
                 'pdf',
                 '--outdir',
                 path,
                 doc_path])
    return doc_path

def generate_pdf_office(doc_path: str, output_dir: str) -> str:
    # Ensure paths are absolute
    doc_path = os.path.abspath(doc_path)
    output_dir = os.path.abspath(output_dir)
    pdf_path = os.path.join(output_dir, os.path.splitext(os.path.basename(doc_path))[0] + '.pdf')

    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False

    try:
        doc = word.Documents.Open(doc_path)
        doc.SaveAs(pdf_path, FileFormat=17)  # 17 = wdFormatPDF
        doc.Close()
    finally:
        word.Quit()

    return pdf_path