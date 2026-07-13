from ccd.area_restrita import AreaRestrita, parse_processo
from ccd.config import (
    DEFAULT_AZURE_DEPLOYMENT,
    DEFAULT_INFORMACOES_DIR,
    PACKAGE_DIR,
    REPO_ROOT,
    SQL_DIR,
    informacoes_dir,
    load_env,
    read_sql,
)
from ccd.db import get_connection, run_query, run_query_df
from ccd.docs import (
    docx_to_pdf,
    docx_to_pdf_libreoffice,
    docx_to_pdf_word,
    render_template,
)
from ccd.pdf import extract_text_from_pdf, merge_pdfs
from ccd.processo import (
    download_processo,
    get_info_file_path,
    get_informacoes_processo,
    get_pdf_files_processo,
)

__all__ = [
    "AreaRestrita",
    "parse_processo",
    "DEFAULT_AZURE_DEPLOYMENT",
    "DEFAULT_INFORMACOES_DIR",
    "PACKAGE_DIR",
    "REPO_ROOT",
    "SQL_DIR",
    "informacoes_dir",
    "load_env",
    "read_sql",
    "get_connection",
    "run_query",
    "run_query_df",
    "extract_text_from_pdf",
    "merge_pdfs",
    "download_processo",
    "get_info_file_path",
    "get_informacoes_processo",
    "get_pdf_files_processo",
    "docx_to_pdf",
    "docx_to_pdf_libreoffice",
    "docx_to_pdf_word",
    "render_template",
]
