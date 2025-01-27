import os
import json
import math
import locale
import pymssql
import argparse

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
    df['valor_original'] = df['valor_original'].apply(lambda x: locale.currency(x, grouping=True, symbol=False) if x and not math.isnan(x) else '-')
    df['valor_atualizado'] = df['valor_atualizado'].apply(lambda x: locale.currency(x, grouping=True, symbol=False) if x and not math.isnan(x) else '-')
    df.fillna('', inplace=True)
    valores = df.to_dict(orient='records')
    context['valores'] = valores
    doc.render(context)
    doc.save(doc_name)

def create_context_processo(numero_processo, ano_processo):
    with open("consultas/processo.sql") as f:
        query = f.read()
    with get_connection() as conn:
        df = pd.read_sql(query.format(numero_processo=numero_processo, ano_processo=ano_processo), conn)
    return df.to_dict(orient='records')[0]


def create_antecedentes(cpf, json_file, doc_name):
    with open(json_file) as json_f:
        json_txt = json_f.read()
    context = json.loads(json_txt)
    create_antecedentes_doc(cpf, context, doc_name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='antecedentes',  description='Cria despacho de antecedentes')
    parser.add_argument('--cpf', '-c', help='CPF do interessado')
    parser.add_argument('--json', '-j',help='Arquivo JSON com o contexto do despacho')
    parser.add_argument('--doc_name', '-d', help='Nome do arquivo docx')
    args = parser.parse_args()
    create_antecedentes(args.cpf, args.json, args.doc_name)
