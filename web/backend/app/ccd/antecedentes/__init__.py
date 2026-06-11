"""Página de Antecedentes do módulo CCD.

Porta o fluxo do notebook `scripts/automacao/antecedentes.ipynb` para a web:
o usuário seleciona processos e o servidor, para cada um, lê o último despacho,
usa um LLM para extrair os responsáveis citados, consulta os débitos transitados
em julgado, renderiza o despacho `.docx`, converte para PDF e devolve um único
PDF (1 processo) ou um ZIP (vários). A geração roda de forma assíncrona via ARQ.
"""
