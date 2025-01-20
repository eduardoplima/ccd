import os
import pymssql
import math
import locale

import pandas as pd

from dotenv import load_dotenv
from docxtpl import DocxTemplate

def get_connection():
    load_dotenv()
    return pymssql.connect(
        server=os.getenv("SQL_SERVER_HOST"),
        user=os.getenv("SQL_SERVER_USER"),
        password=os.getenv("SQL_SERVER_PASS"),
        port=os.getenv("SQL_SERVER_PORT"),
        database='processo'
    )

def get_processos_transito_by_cpf(cpf):
    with open("consultas/processos_transito_cpf.sql") as f:
        query = f.read()
    with get_connection() as conn:
        return pd.read_sql(query.format(cpf=cpf), conn)

def create_antecedentes_doc(cpf, context, doc_name):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    doc = DocxTemplate("templates/antecedentes.docx")
    df = get_processos_transito_by_cpf(cpf)
    df['valor_original'] = df['valor_original'].apply(lambda x: locale.currency(x, grouping=True, symbol=False) if not math.isnan(x) else '-')
    df['valor_atualizado'] = df['valor_atualizado'].apply(lambda x: locale.currency(x, grouping=True, symbol=False) if not math.isnan(x) else '-')
    df.fillna('', inplace=True)
    valores = df.to_dict(orient='records')
    context['valores'] = valores
    doc.render(context)
    doc.save(doc_name)


