import os
import pymssql
import pypdf
import json
import datetime

from pathlib import Path

from dotenv import load_dotenv

from docling.document_converter import DocumentConverter


load_dotenv()

class ETL:
    def __init__(self):
        self.conn = self.get_connection()
        self.docling_converter = DocumentConverter()
        
    def get_connection(self):
        return pymssql.connect(server='10.24.0.77\\ControleExterno',
                                    user=os.getenv('SQLSERVER_USER'),
                                    password=os.getenv('SQLSERVER_PASS'),
                                    port=59678,
                                    database='processo',
                                    charset='WINDOWS-1252')
    
    def get_query(self):
        return '''
    SELECT 
    p.numero_processo,
p.ano_processo,
p.codigo_tipo_processo,
p.assunto,
inf.setor, 
inf.resumo, 
inf.data_resumo,  
concat(rtrim(inf.setor),'_',inf.numero_processo ,'_',inf.ano_processo,'_',RIGHT(concat('0000',inf.ordem),4),'.pdf') as arquivo

FROM processo.dbo.Ata_Informacao inf INNER JOIN Processos p ON inf.numero_processo = p.numero_processo AND inf.ano_processo = p.ano_processo
WHERE Decisao IS NOT NULL
AND p.ano_processo > 2015
AND year(data_resumo) = 2024
--AND p.codigo_tipo_processo IN ('ACO', 'ADS', 'AGE', 'AGF', 'AOP', 'APR', 'AUD', 'BGE', 'BLC',
  --     'CFM', 'CGE', 'CNV', 'CTR', 'CTV', 'DCD', 'DEN', 'DLC',
    --   'EXE', 'FIN', 'FUN', 'INA', 'INE', 'INP', 'LIC',
      -- 'LRF', 'MON', 'PAG', 'PCC', 'PCF', 'PCO', 'PFA', 
       -- 'REL', 'REP', 'RPG', 'RRE', 'TAD', 'TAG', 'TOM')
    '''

    def get_rows(self):
        cursor = self.conn.cursor(as_dict=True)
        cursor.execute(self.get_query())
        rows = cursor.fetchall()
        cursor.close()
        return rows
    
    def close(self):
        self.conn.close()

    def get_dir_pdf(self):
        dir_pdf = '/mnt/informacoes_pdf'
        assert os.path.exists(dir_pdf)
        return dir_pdf
    
    def get_file_path(self, row):
        return Path(self.get_dir_pdf()) / row['setor'].strip() / row['arquivo']

    def get_pdf_text(self, row):
        arquivo = self.get_file_path(row)
        print(f'File {arquivo} to pypdf text')
        try:
            pdf = pypdf.PdfReader(arquivo)
            text = []
            for page in pdf.pages:
                text.append(page.extract_text())
            return text
        except FileNotFoundError:
            print(f'File not found: {arquivo}')
            return ''
        
    def get_docling_pdf_text(self, row):
        arquivo = self.get_file_path(row)
        print(f'File {arquivo} to docling text')
        return self.docling_converter.convert(arquivo).document.export_to_text()
        
    
    def save_json(self, json_dicts, filename):
        with open(filename, 'w') as f:
            json.dump(json_dicts, f, ensure_ascii=False)

    def execute(self):
        rows = self.get_rows()
        print(f'{len(rows)} rows returned.')
        json_dicts = []
        for row in rows:
            text = self.get_docling_pdf_text(row)
            row['texto'] = text
            row['data_resumo'] = row['data_resumo'].strftime('%Y-%m-%d')
            json_dicts.append(row)
        self.save_json(json_dicts, 'output.json')

if __name__ == '__main__':
    etl = ETL()
    etl.execute()
    etl.close()