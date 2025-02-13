import pymssql
import os

from dotenv import load_dotenv

def get_connection(db='processo'):
    load_dotenv()
    return pymssql.connect(
        server=os.getenv("SQL_SERVER_HOST"),
        user=os.getenv("SQL_SERVER_USER"),
        password=os.getenv("SQL_SERVER_PASS"),
        port=os.getenv("SQL_SERVER_PORT"),
        database=db
    )