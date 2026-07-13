import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

from ccd.config import load_env
load_env()

from ccd.db import get_connection
conn = get_connection()

from langchain_openai import AzureChatOpenAI
llm_mini = AzureChatOpenAI(model='gpt-5.4-mini')

CPF_NEREU = '13006444434'
# Nereu é presidente do IPERN; citações ao IPERN contam como dele. O IPERN tem mais de um
# cadastro/estabelecimento (ex.: 08242034000102 e 08242034000285) — casamos pela RAIZ do CNPJ.
CNPJ_IPERN_RAIZ = '08242034'

import re
_ILLEGAL_XLSX = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')

def _strip_ctrl(v):
    return _ILLEGAL_XLSX.sub('', v) if isinstance(v, str) else v

import sys; print(sys.executable)
  # expect: C:\Users\05911205424\Dev\ccd\.venv\Scripts\python.exe
# Imports da seção: tudo o que as células abaixo precisam.
# Variáveis vêm do prelúdio acima: CPF_NEREU, conn, llm_mini, locale,
# _strip_ctrl (sanitizador de chars de controle do xlsx).
from pathlib import Path

import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from tqdm import tqdm

from ccd.db import run_query_df
from ccd.pdf import extract_text_from_pdf
from ccd.processo import get_info_file_path

from ccd.config import load_env
load_env(override=True)        # force re-read of .env over the stale value
from ccd.db import get_connection
conn = get_connection()        # rebuild the engine with the corrected host/port
import os
print("HOST =", os.getenv("SQL_SERVER_HOST"), "PORT =", os.getenv("SQL_SERVER_PORT"))
  # expect: HOST = 10.24.0.77   PORT = 59678
# Citação de 5 dias via Cit_Citacoes (fonte autoritativa). Cobre os processos de ORIGEM e de
# EXECUÇÃO dos débitos do Nereu — a citação pode estar em qualquer um dos dois. 'C05' (ou
# Tipo 'C' + Prazo 5) = citação de 5 dias. Inclui citações endereçadas ao NEREU (CPF) E ao
# IPERN (qualquer estabelecimento, raiz de CNPJ), pois ele é presidente do IPERN. A data vem
# da informação vinculada (Data_envio_AR está sempre vazia). Substitui a varredura LLM/PDF.

# CTE reutilizada: processos (origem + execução) dos débitos do Nereu.
_PROC_NEREU = '''
    SELECT e.IdProcessoOrigem AS idp FROM processo.dbo.Exe_Debito e
    JOIN processo.dbo.Exe_DebitoPessoa edp ON edp.IDDebito = e.IdDebito
    JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = edp.IDPessoa
    WHERE gp.Documento = :cpf AND e.IdDebitoAnterior IS NULL AND e.IdProcessoOrigem IS NOT NULL
    UNION
    SELECT e.IdProcessoExecucao FROM processo.dbo.Exe_Debito e
    JOIN processo.dbo.Exe_DebitoPessoa edp ON edp.IDDebito = e.IdDebito
    JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = edp.IDPessoa
    WHERE gp.Documento = :cpf AND e.IdDebitoAnterior IS NULL AND e.IdProcessoExecucao IS NOT NULL
'''

sql_citacoes_nereu = f'''
WITH proc_nereu AS ({_PROC_NEREU})
SELECT
    c.IdCitacao,
    CONCAT(p.numero_processo, '/', p.ano_processo) AS processo_citacao,
    c.IdInformacao,
    gp.Documento AS doc_citacao,
    COALESCE(inf.DataPublicacao, inf.data_ultima_atualizacao, c.DataInclusao) AS data_citacao,
    inf.setor AS setor_citacao,
    ppe.SequencialProcessoEvento AS evento_citacao_5d
FROM processo.dbo.Cit_Citacoes c
JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = c.IdPessoa
JOIN proc_nereu pn ON pn.idp = c.IdProcesso
LEFT JOIN processo.dbo.Processos p ON p.IdProcesso = c.IdProcesso
LEFT JOIN processo.dbo.vw_ata_informacao inf ON inf.idInformacao = c.IdInformacao
LEFT JOIN processo.dbo.Pro_ProcessoEvento ppe ON ppe.idInformacao = c.IdInformacao
WHERE (gp.Documento = :cpf OR LEFT(gp.Documento, 8) = :ipern_raiz)
  AND (c.Tipo = 'C05' OR (c.Tipo = 'C' AND c.Prazo = 5))
  AND c.DataExclusao IS NULL
'''


def _destinatario(doc):
    if doc == CPF_NEREU:
        return 'Nereu'
    if isinstance(doc, str) and doc.startswith(CNPJ_IPERN_RAIZ):
        return 'IPERN'
    return doc


_cit_raw = run_query_df(sql_citacoes_nereu, conn, cpf=CPF_NEREU, ipern_raiz=CNPJ_IPERN_RAIZ)
_cit_raw['data_citacao'] = pd.to_datetime(_cit_raw['data_citacao'], errors='coerce')
_cit_raw['destinatario'] = _cit_raw['doc_citacao'].apply(_destinatario)
# 1 linha por citação (rede de segurança contra fan-out de evento)
_cit_raw = _cit_raw.drop_duplicates('IdCitacao')

# quantidade de citações de 5 dias por processo
_qtd_cit = (_cit_raw.groupby('processo_citacao').size()
            .rename('qtd_citacoes_validas').reset_index())

# citação mais recente por processo (a mais nova é a vigente)
df_citacoes = (
    _cit_raw.sort_values('data_citacao', ascending=False)
    .drop_duplicates('processo_citacao', keep='first')
    [['processo_citacao', 'data_citacao', 'setor_citacao', 'destinatario', 'evento_citacao_5d']]
    .merge(_qtd_cit, on='processo_citacao', how='left')
    .reset_index(drop=True)
)
df_citacoes['evento_citacao_5d'] = df_citacoes['evento_citacao_5d'].astype('Int64')
_n_ipern = int((_cit_raw['destinatario'] == 'IPERN').sum())

# --- Diagnóstico: TODAS as citações (qualquer pessoa/tipo) por processo. Serve para EXPLICAR,
# na aba Processos, por que um processo está sem citação de 5 dias para Nereu/IPERN.
sql_cit_todas = f'''
WITH proc_nereu AS ({_PROC_NEREU})
SELECT CONCAT(p.numero_processo, '/', p.ano_processo) AS processo,
       c.Tipo, gp.Documento AS doc, gp.Nome AS nome
FROM processo.dbo.Cit_Citacoes c
JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = c.IdPessoa
JOIN proc_nereu pn ON pn.idp = c.IdProcesso
LEFT JOIN processo.dbo.Processos p ON p.IdProcesso = c.IdProcesso
WHERE c.DataExclusao IS NULL
'''
_cit_all = run_query_df(sql_cit_todas, conn, cpf=CPF_NEREU)
_doc_str = _cit_all['doc'].astype(str)
# C05 a terceiro = nem Nereu nem IPERN (qualquer estabelecimento)
_cit_all['_c05_terc'] = ((_cit_all['Tipo'] == 'C05')
                         & (_doc_str != CPF_NEREU)
                         & (~_doc_str.str.startswith(CNPJ_IPERN_RAIZ)))
df_cit_diag = _cit_all.groupby('processo').agg(
    n_cit=('Tipo', 'size'),
    tipos=('Tipo', lambda s: ', '.join(sorted(set(s)))),
    tem_c05_terc=('_c05_terc', 'any'),
).reset_index()
_terc = (_cit_all[_cit_all['_c05_terc']]
         .drop_duplicates('processo')[['processo', 'nome']]
         .rename(columns={'nome': 'c05_terceiro_nome'}))
df_cit_diag = df_cit_diag.merge(_terc, on='processo', how='left')

print(f'df_citacoes: {len(df_citacoes)} processos com citação de 5 dias (Nereu + IPERN) | '
      f'citações totais: {len(_cit_raw)} (IPERN: {_n_ipern}) | '
      f'diag: {len(df_cit_diag)} processos com alguma citação')
df_citacoes.head()

# Cache da classificação CCD: se o pickle existir, carrega df_ccd_infos e PULA as
# células de SQL + extração de PDFs + LLM abaixo. Apague o pickle para recalcular.
_ckpt_ccd = Path('docs/df_ccd_infos.pkl')
_ccd_cached = _ckpt_ccd.exists()
if _ccd_cached:
    df_ccd_infos = pd.read_pickle(_ckpt_ccd)
    print(f'CCD: carregado de {_ckpt_ccd} ({len(df_ccd_infos)} linhas) — inferência pulada.')
else:
    print('CCD: pickle não encontrado — vai rodar SQL + extração + LLM.')

if not _ccd_cached:
    # Todas as informações CCD dos processos onde Nereu tem débito (não só a última)
    sql_todas_ccd_nereu = '''
    WITH processos_nereu AS (
        SELECT DISTINCT pro.IdProcesso, pro.numero_processo, pro.ano_processo
        FROM processo.dbo.Processos pro
        INNER JOIN processo.dbo.Exe_Debito ed ON ed.IdProcessoExecucao = pro.IdProcesso
        INNER JOIN processo.dbo.Exe_DebitoPessoa edp ON edp.IDDebito = ed.IdDebito
        INNER JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = edp.IDPessoa
        WHERE gp.Documento = :cpf
          AND ed.IdDebitoAnterior IS NULL
    )
    SELECT
        CONCAT(inf.numero_processo, '/', inf.ano_processo) AS processo,
        inf.numero_processo,
        inf.ano_processo,
        inf.setor,
        inf.ordem,
        inf.data_ultima_atualizacao,
        inf.idInformacao,
        ppe.SequencialProcessoEvento AS evento,
        CONCAT(RTRIM(inf.setor), '_', inf.numero_processo, '_', inf.ano_processo,
               '_', RIGHT(CONCAT('0000', inf.ordem), 4), '.pdf') AS arquivo
    FROM processo.dbo.vw_ata_informacao inf
    INNER JOIN processos_nereu pn
        ON pn.numero_processo = inf.numero_processo
       AND pn.ano_processo   = inf.ano_processo
    LEFT JOIN processo.dbo.Pro_ProcessoEvento ppe ON ppe.idInformacao = inf.idInformacao
    WHERE LTRIM(RTRIM(inf.setor)) = 'CCD' and inf.resumo like '%folha%'
    ORDER BY inf.numero_processo, inf.ano_processo, inf.ordem
    '''

    df_ccd_infos = run_query_df(sql_todas_ccd_nereu, conn, cpf=CPF_NEREU)
    df_ccd_infos['caminho_arquivo'] = df_ccd_infos.apply(get_info_file_path, axis=1)
    print(f'Informações CCD nos processos do Nereu: {len(df_ccd_infos)} '
          f'(em {df_ccd_infos["processo"].nunique()} processos)')
    df_ccd_infos.head()

if not _ccd_cached:
    # Extrai texto de cada PDF da CCD (uma vez por arquivo)
    textos_ccd = []
    for caminho in tqdm(df_ccd_infos['caminho_arquivo'], desc='extraindo PDFs CCD'):
        try:
            textos_ccd.append(extract_text_from_pdf(caminho) if caminho.exists() else '')
        except Exception as e:
            textos_ccd.append(f'__ERRO_EXTRACAO__ {e}')
    df_ccd_infos['texto'] = textos_ccd

    vazios = (df_ccd_infos['texto'].str.len() == 0).sum()
    erros = df_ccd_infos['texto'].str.startswith('__ERRO_EXTRACAO__').sum()
    print(f'Textos extraídos: {len(df_ccd_infos)} | vazios: {vazios} | erros: {erros}')

if not _ccd_cached:
    # Classificador binário LLM: é notificação de desconto em folha endereçada ao Nereu?
    class NotificacaoNereu(BaseModel):
        eh_notificacao_desconto_folha_nereu: bool = Field(
            description='True se o texto for uma notificação de desconto em folha '
                        'endereçada a NEREU BATISTA LINHARES (CPF 13006444434).')
        justificativa: str = Field(
            description='Justificativa curta (1-2 frases, pt-BR) da classificação.')


    prompt_notif = ChatPromptTemplate.from_messages([
        ('system',
         'Você está classificando uma informação da CCD (Coordenadoria de Controle de Decisões) '
         'do Tribunal de Contas. Responda True somente se o texto for uma NOTIFICAÇÃO DE '
         'DESCONTO EM FOLHA endereçada especificamente a NEREU BATISTA LINHARES '
         '(CPF 13006444434). Responda False para qualquer outro assunto (deliberação, baixa, '
         'cumprimento, etc.) ou se a notificação for para outra pessoa. Responda em pt-BR.'),
        ('human', 'Texto da informação CCD:\n\n{texto}'),
    ])

    chain_notif = prompt_notif | llm_mini.with_structured_output(schema=NotificacaoNereu)

if not _ccd_cached:
    # Classifica cada informação CCD com a LLM
    classificacoes = []
    for _, row in tqdm(df_ccd_infos.iterrows(), total=len(df_ccd_infos),
                       desc='classificando informações CCD'):
        texto = (row['texto'] or '').strip()
        if not texto or texto.startswith('__ERRO_EXTRACAO__'):
            classificacoes.append({'eh_notificacao': False,
                                   'justificativa': '(texto vazio ou erro de extração)'})
            continue
        try:
            r = chain_notif.invoke({'texto': texto[:12000]})
            classificacoes.append({
                'eh_notificacao': bool(r.eh_notificacao_desconto_folha_nereu),
                'justificativa': r.justificativa,
            })
        except Exception as e:
            classificacoes.append({'eh_notificacao': False,
                                   'justificativa': f'__ERRO_LLM__ {str(e)[:200]}'})

    df_class = pd.DataFrame(classificacoes)
    df_ccd_infos['eh_notificacao'] = df_class['eh_notificacao'].values
    df_ccd_infos['justificativa']  = df_class['justificativa'].values
    print(f'Informações classificadas como notificação para Nereu: '
          f'{df_ccd_infos["eh_notificacao"].sum()} de {len(df_ccd_infos)}')
    df_ccd_infos[df_ccd_infos['eh_notificacao']].head()
    df_ccd_infos.to_pickle(_ckpt_ccd)
    print(f'CCD: inferência salva em {_ckpt_ccd}.')

# Agrega: para cada processo, lista de eventos da CCD identificados como notificação
df_notif = (
    df_ccd_infos[df_ccd_infos['eh_notificacao']]
    .groupby('processo')
    .agg(
        eventos_notificacao_ccd=('evento', lambda s: sorted(int(x) for x in s.dropna().unique())),
        qtd_notificacoes=('evento', 'count'),
    )
    .reset_index()
)
print(f'Processos com pelo menos uma notificação para Nereu: {len(df_notif)}')
df_notif.head()

from ccd.db import run_query_df

SQL_DEBITOS_NEREU = """
SELECT
    e.IdDebito AS id_debito,
    (SELECT CONCAT(p.numero_processo, '/', p.ano_processo)
        FROM processo.dbo.Processos p WHERE p.IdProcesso = e.IdProcessoOrigem) AS processo_origem,
    (SELECT CONCAT(p.numero_processo, '/', p.ano_processo)
        FROM processo.dbo.Processos p WHERE p.IdProcesso = e.IdProcessoExecucao) AS processo_execucao,
    etd.Descricao AS tipo_debito,
    esd.DescricaoStatusDivida AS situacao_divida,
    e.valorOriginalDebito AS valor_original,
    processo.dbo.fn_Exe_RetornaValorAtualizado(e.IdDebito) AS valor_atualizado,
    e.dataTransito AS data_transito
FROM processo.dbo.Exe_Debito e
INNER JOIN processo.dbo.Exe_DebitoPessoa edp ON edp.IDDebito = e.IdDebito
INNER JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = edp.IDPessoa
LEFT JOIN processo.dbo.Exe_TipoDebito etd ON etd.CodigoTipoDebito = e.CodigoTipoDebito
LEFT JOIN processo.dbo.Exe_StatusDivida esd ON esd.CodigoStatusDivida = e.CodigoStatusDivida
WHERE gp.Documento = :cpf
  AND e.IdDebitoAnterior IS NULL
  AND esd.StatusCancelamento IS NULL
"""


def carregar_debitos(cpf: str = CPF_NEREU) -> pd.DataFrame:
    df = run_query_df(SQL_DEBITOS_NEREU, cpf=cpf)
    df['tipo_debito'] = df['tipo_debito'].fillna('(sem tipo)')
    df['situacao_divida'] = df['situacao_divida'].fillna('(sem situação)')
    return df


debitos_nereu = carregar_debitos()
print(f'Débitos do Nereu (sem cancelados): {len(debitos_nereu)} linhas')
debitos_nereu.head()
# Metadados por processo (consultas baratas, sem LLM): setor atual e número do acórdão
# (mais recente, do processo de origem). Define também _fmt_data (formata datas como
# DD/MM/YYYY). O evento da citação 5d já vem de df_citacoes (via Cit_Citacoes.IdInformacao),
# então não há mais consulta separada de Pro_ProcessoEvento aqui.
from ccd.db import run_query_df


def _fmt_data(s):
    """Formata uma coluna de datas como DD/MM/YYYY (vazio quando NaT)."""
    if not pd.api.types.is_datetime64_any_dtype(s):
        s = pd.to_datetime(s, errors='coerce', format='mixed')
    return s.dt.strftime('%d/%m/%Y').fillna('')


_SUB_EXEC_ORIG = """
    SELECT e.IdProcessoExecucao AS idp FROM processo.dbo.Exe_Debito e
    JOIN processo.dbo.Exe_DebitoPessoa edp ON edp.IDDebito = e.IdDebito
    JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = edp.IDPessoa
    WHERE gp.Documento = :cpf AND e.IdDebitoAnterior IS NULL
    UNION
    SELECT e.IdProcessoOrigem FROM processo.dbo.Exe_Debito e
    JOIN processo.dbo.Exe_DebitoPessoa edp ON edp.IDDebito = e.IdDebito
    JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = edp.IDPessoa
    WHERE gp.Documento = :cpf AND e.IdDebitoAnterior IS NULL
"""
_SUB_ORIG = """
    SELECT e.IdProcessoOrigem AS idp FROM processo.dbo.Exe_Debito e
    JOIN processo.dbo.Exe_DebitoPessoa edp ON edp.IDDebito = e.IdDebito
    JOIN processo.dbo.GenPessoa gp ON gp.IdPessoa = edp.IDPessoa
    WHERE gp.Documento = :cpf AND e.IdDebitoAnterior IS NULL
"""

# setor atual (processos de execução + origem)
df_setor = run_query_df(f"""
SELECT DISTINCT CONCAT(p.numero_processo, '/', p.ano_processo) AS processo,
       RTRIM(p.setor_atual) AS setor_atual
FROM processo.dbo.Processos p
WHERE p.IdProcesso IN ({_SUB_EXEC_ORIG})
""", cpf=CPF_NEREU)

# número do acórdão (sessão mais recente) no processo de origem
_ac = run_query_df(f"""
SELECT CONCAT(v.NumeroProcesso, '/', v.AnoProcesso) AS processo_origem,
       v.numeroResultado, v.anoResultado, v.DataSessao
FROM processo.dbo.vw_ia_votos_acordaos_decisoes v
WHERE v.numeroResultado IS NOT NULL
  AND v.IdProcesso IN ({_SUB_ORIG})
""", cpf=CPF_NEREU)
_ac['DataSessao'] = pd.to_datetime(_ac['DataSessao'], errors='coerce')
df_acordao = (
    _ac.sort_values('DataSessao', ascending=False)
       .groupby('processo_origem', as_index=False)
       .head(1)
       .copy()
)
df_acordao['numero_acordao'] = (
    df_acordao['numeroResultado'].astype(str).str.strip() + '/'
    + df_acordao['anoResultado'].astype(str).str.strip()
)
df_acordao = df_acordao.rename(columns={'DataSessao': 'data_acordao'})[
    ['processo_origem', 'numero_acordao', 'data_acordao']]

print(f'setor: {len(df_setor)} | acórdãos: {len(df_acordao)} | '
      f'citações: {len(df_citacoes)} processos')
df_citacoes.head()

# SUBSTITUI a célula 12 (Aba 1 — Totais). Inalterada; opera sobre debitos_nereu sem cancelados.
processos_notificados = set(df_notif['processo'])
mask_notif = debitos_nereu['processo_execucao'].isin(processos_notificados)

qtd_total = len(debitos_nereu)
qtd_notif = int(mask_notif.sum())
val_total = float(debitos_nereu['valor_atualizado'].sum())
val_notif = float(debitos_nereu.loc[mask_notif, 'valor_atualizado'].sum())

tab_totais = pd.DataFrame([
    {'metrica': 'Total de débitos imputados a Nereu',
     'quantidade': qtd_total,
     'valor_atualizado_R$': locale.currency(val_total, grouping=True, symbol=True)},
    {'metrica': 'Total de débitos notificados (desconto em folha, Nereu)',
     'quantidade': qtd_notif,
     'valor_atualizado_R$': locale.currency(val_notif, grouping=True, symbol=True)},
])
tab_totais

# SUBSTITUI a célula 13 (Aba 2 — Processos). Grão: 1 linha por par (execução, origem).
base = (
    debitos_nereu.groupby(['processo_execucao', 'processo_origem'], dropna=False)
    .agg(
        valor_original=('valor_original', 'sum'),
        valor_atualizado=('valor_atualizado', 'sum'),
        data_transito=('data_transito', 'max'),
        tipos_debito=('tipo_debito', lambda s: sorted(set(s))),
    )
    .reset_index()
)

# setor atual: do processo de EXECUÇÃO; se só houver origem (sem execução), usa o da ORIGEM
_setor_map = df_setor.drop_duplicates('processo').set_index('processo')['setor_atual']
base['setor_atual'] = (base['processo_execucao'].map(_setor_map)
                       .fillna(base['processo_origem'].map(_setor_map)))
# acórdão mais recente (processo de origem)
base = base.merge(df_acordao, on='processo_origem', how='left')

# citação 5d: pode estar na ORIGEM ou na EXECUÇÃO do débito. Para cada par, escolhe a citação
# mais recente entre os dois processos. processo_citacao indica onde foi encontrada e
# destinatario_citacao a quem foi endereçada (Nereu ou IPERN).
_cit_idx = df_citacoes.set_index('processo_citacao')


def _attach_citacao(row):
    cands = [p for p in (row['processo_origem'], row['processo_execucao'])
             if isinstance(p, str) and p in _cit_idx.index]
    if not cands:
        return pd.Series({'data_citacao': pd.NaT, 'setor_citacao': None,
                          'destinatario_citacao': None,
                          'evento_citacao_5d': pd.NA, 'qtd_citacoes_validas': 0,
                          'processo_citacao': None})
    best = _cit_idx.loc[cands].sort_values('data_citacao', ascending=False).iloc[0]
    return pd.Series({'data_citacao': best['data_citacao'],
                      'setor_citacao': best['setor_citacao'],
                      'destinatario_citacao': best['destinatario'],
                      'evento_citacao_5d': best['evento_citacao_5d'],
                      'qtd_citacoes_validas': best['qtd_citacoes_validas'],
                      'processo_citacao': best.name})


base = base.join(base.apply(_attach_citacao, axis=1))

# obs_citacao: quando NÃO há citação 5d para Nereu/IPERN, explica o porquê olhando o que
# existe na Cit_Citacoes nos processos de origem/execução do par.
_diag_idx = df_cit_diag.set_index('processo')


def _obs_citacao(row):
    if isinstance(row['processo_citacao'], str) and row['processo_citacao']:
        return ''  # tem citação 5d (Nereu/IPERN) — nada a explicar
    procs = [p for p in (row['processo_origem'], row['processo_execucao'])
             if isinstance(p, str) and p in _diag_idx.index]
    if not procs:
        return 'sem citação na base'
    sub = _diag_idx.loc[procs]
    terc = sub['c05_terceiro_nome'].dropna()
    if len(terc):
        return f'citação 5d p/ terceiro: {terc.iloc[0]}'
    tipos = sorted({t for s in sub['tipos'] for t in str(s).split(', ') if t})
    return f'só citação de outro tipo: {", ".join(tipos)}' if tipos else 'sem citação na base'


base['obs_citacao'] = base.apply(_obs_citacao, axis=1)

# --- PRAZO PRESCRICIONAL ---------------------------------------------------------------
# Regra (vault/wiki/conceitos/Prescrição da pretensão executória.md): a pretensão executória
# de MULTA prescreve em 5 anos a contar do trânsito em julgado, INTERROMPIDA pela citação
# (art. 332 RI; arts. 36-38 Res 028-2012). Ressarcimento ao erário é IMPRESCRITÍVEL.
# Logo o relógio de 5 anos conta da CITAÇÃO (se houve) ou, na falta dela, do TRÂNSITO.
PRAZO_PRESCRICIONAL_ANOS = 5
_hoje = pd.Timestamp.now().normalize()
base['data_transito'] = pd.to_datetime(base['data_transito'], errors='coerce')
base['data_citacao'] = pd.to_datetime(base['data_citacao'], errors='coerce')
base['ano_transito_julgado'] = base['data_transito'].dt.year.astype('Int64')
base['dias_transito'] = (_hoje - base['data_transito']).dt.days.astype('Int64')
base['anos_transito'] = (base['dias_transito'] / 365).round(1)
base['dias_citacao'] = (_hoje - base['data_citacao']).dt.days.astype('Int64')
base['anos_citacao'] = (base['dias_citacao'] / 365).round(1)


def _risco_prescricao(row):
    eh_multa = any('Multa' in str(t) for t in row['tipos_debito'])
    if not eh_multa:
        return 'imprescritível (ressarcimento)'
    tem_cit = pd.notna(row['anos_citacao'])
    anos = row['anos_citacao'] if tem_cit else row['anos_transito']
    ref = 'citação' if tem_cit else 'trânsito'
    if pd.isna(anos):
        return 'sem data de referência'
    if anos >= PRAZO_PRESCRICIONAL_ANOS:
        return f'PRESCRITO ({anos:.1f}a desde {ref})'
    if anos >= PRAZO_PRESCRICIONAL_ANOS - 1:
        return f'risco (faltam {PRAZO_PRESCRICIONAL_ANOS - anos:.1f}a, desde {ref})'
    return f'ok ({anos:.1f}a desde {ref})'


base['risco_prescricao'] = base.apply(_risco_prescricao, axis=1)
# ---------------------------------------------------------------------------------------

# notificações CCD (processo de execução)
base = base.merge(
    df_notif[['processo', 'qtd_notificacoes', 'eventos_notificacao_ccd']]
        .rename(columns={'processo': 'processo_execucao'}),
    on='processo_execucao', how='left')

base['qtd_notificacoes'] = base['qtd_notificacoes'].fillna(0).astype(int)
base['qtd_citacoes_validas'] = base['qtd_citacoes_validas'].fillna(0).astype(int)
base['evento_citacao_5d'] = base['evento_citacao_5d'].astype('Int64')
base['eventos_notificacao_ccd'] = base['eventos_notificacao_ccd'].apply(
    lambda v: v if isinstance(v, list) else [])

tab_processos = base[[
    'processo_execucao', 'processo_origem', 'setor_atual',
    'numero_acordao', 'data_acordao', 'data_transito', 'data_citacao',
    'ano_transito_julgado', 'dias_transito', 'anos_transito',
    'dias_citacao', 'anos_citacao', 'risco_prescricao',
    'processo_citacao', 'destinatario_citacao', 'evento_citacao_5d',
    'setor_citacao', 'obs_citacao',
    'valor_original', 'valor_atualizado',
    'qtd_citacoes_validas', 'qtd_notificacoes', 'eventos_notificacao_ccd',
]].sort_values('valor_atualizado', ascending=False).copy()

for _c in ('data_acordao', 'data_transito', 'data_citacao'):
    tab_processos[_c] = _fmt_data(tab_processos[_c])

_com_cit = int((tab_processos['data_citacao'] != '').sum())
_com_ipern = int((tab_processos['destinatario_citacao'] == 'IPERN').sum())
print(f'tab_processos: {len(tab_processos)} pares (execução, origem) | '
      f'com citação 5d: {_com_cit} (via IPERN: {_com_ipern})')
print('risco_prescricao:')
print(tab_processos['risco_prescricao'].str.replace(r' \(.*', '', regex=True)
      .value_counts().to_string())
tab_processos.head()

# SUBSTITUI a célula 14 (Aba 3 — Débitos). Sem a coluna notificado_no_processo.
tab_debitos = debitos_nereu[[
    'id_debito', 'processo_origem', 'processo_execucao',
    'tipo_debito', 'situacao_divida',
    'valor_original', 'valor_atualizado', 'data_transito',
]].copy().sort_values('valor_atualizado', ascending=False)
tab_debitos['data_transito'] = _fmt_data(tab_debitos['data_transito'])
tab_debitos.head()

# NOVA — Aba 4 (Notificações desconto em folha): 1 linha por evento de notificação.
# Inclui a data em que a CCD fez a informação de notificação (data_ultima_atualizacao).
# Débitos do processo (execução) agregados em lista (não há vínculo direto evento->débito).
_notif_eventos = (
    df_ccd_infos[df_ccd_infos['eh_notificacao']]
    [['processo', 'evento', 'data_ultima_atualizacao']]
    .drop_duplicates()
    .rename(columns={'processo': 'processo_execucao',
                     'data_ultima_atualizacao': 'data_notificacao'})
)

_deb_por_proc = (
    debitos_nereu.groupby('processo_execucao')
    .agg(
        ids_debitos=('id_debito', lambda s: sorted(int(x) for x in s)),
        valor_original_total=('valor_original', 'sum'),
        valor_atualizado_total=('valor_atualizado', 'sum'),
    )
    .reset_index()
)

tab_notificacoes = (
    _notif_eventos.merge(_deb_por_proc, on='processo_execucao', how='left')
    .rename(columns={'processo_execucao': 'processo'})
)
tab_notificacoes['ids_debitos'] = tab_notificacoes['ids_debitos'].apply(
    lambda v: v if isinstance(v, list) else [])
tab_notificacoes['valor_original_total'] = tab_notificacoes['valor_original_total'].fillna(0.0)
tab_notificacoes['valor_atualizado_total'] = tab_notificacoes['valor_atualizado_total'].fillna(0.0)
tab_notificacoes = tab_notificacoes[[
    'processo', 'evento', 'data_notificacao', 'ids_debitos',
    'valor_original_total', 'valor_atualizado_total',
]].sort_values(['processo', 'evento']).reset_index(drop=True)
tab_notificacoes['data_notificacao'] = _fmt_data(tab_notificacoes['data_notificacao'])

# Dados do PROCESSO (débitos e valores) só na 1ª linha (menor evento) de cada processo
# -> somar valor_atualizado_total passa a bater com o total notificado da aba Totais.
_primeira = ~tab_notificacoes.duplicated('processo')
for _c in ('ids_debitos', 'valor_original_total', 'valor_atualizado_total'):
    tab_notificacoes[_c] = tab_notificacoes[_c].where(_primeira)
print(f"soma valor_atualizado_total (1x/processo): "
      f"{tab_notificacoes['valor_atualizado_total'].sum():.2f}")
print(f'Notificações (eventos): {len(tab_notificacoes)} | '
      f'processos: {tab_notificacoes["processo"].nunique()}')
tab_notificacoes.head()

# SUBSTITUI a célula 15 (escrita do xlsx) — agora com 5 abas. Datas já em DD/MM/YYYY.
out_xlsx = Path('docs/debitos_nereu_planilha_final.xlsx')
out_xlsx.parent.mkdir(parents=True, exist_ok=True)


def _sanitize(df):
    return df.map(_strip_ctrl) if hasattr(df, 'map') else df.applymap(_strip_ctrl)


# colunas-lista -> string (openpyxl não aceita listas)
tab_processos_xlsx = tab_processos.copy()
tab_processos_xlsx['eventos_notificacao_ccd'] = tab_processos_xlsx['eventos_notificacao_ccd'].apply(
    lambda v: ', '.join(str(x) for x in v) if isinstance(v, list) and v else '')

tab_notificacoes_xlsx = tab_notificacoes.copy()
tab_notificacoes_xlsx['ids_debitos'] = tab_notificacoes_xlsx['ids_debitos'].apply(
    lambda v: ', '.join(str(x) for x in v) if isinstance(v, list) and v else '')

# Aba "Conciliações FRAP": planilha externa de pagamentos via FRAP (docs/debitos_conciliados_nereu.xlsx).
tab_conciliacoes = pd.read_excel(Path('docs/debitos_conciliados_nereu.xlsx'))

with pd.ExcelWriter(out_xlsx, engine='openpyxl') as writer:
    _sanitize(tab_totais).to_excel(writer, sheet_name='Totais', index=False)
    _sanitize(tab_processos_xlsx).to_excel(writer, sheet_name='Processos', index=False)
    _sanitize(tab_debitos).to_excel(writer, sheet_name='Débitos', index=False)
    _sanitize(tab_notificacoes_xlsx).to_excel(
        writer, sheet_name='Notificações desconto em folha', index=False)
    _sanitize(tab_conciliacoes).to_excel(writer, sheet_name='Conciliações FRAP', index=False)

print(f'Planilha salva em: {out_xlsx.resolve()}')
print(f'Aba "Conciliações FRAP": {len(tab_conciliacoes)} linhas')
