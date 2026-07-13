---
name: legislacao-ccd
description: Base legal do TCE/RN para redação de informações, despachos e documentos da CCD destinados à Área Restrita (gerados a partir dos modelos .docx). Use SEMPRE que for redigir, revisar ou gerar uma informação/despacho da CCD — cobrança, execução de decisões, multa, ressarcimento, protesto, parcelamento, trânsito em julgado, envio à PGE/DAP, desconto em folha, antecedentes.
---

# Legislação de referência da CCD

Toda informação redigida para a Área Restrita (via `templates/*.docx` de `scripts/automacao/` — `modelo_informacao.docx`, `cobranca_judicial.docx`, `desconto_folha.docx`, `envio_dap.docx`, etc.) deve estar fundamentada nesta base legal. Antes de redigir, identifique o tema e leia (via Grep/Read) os artigos pertinentes em `referencias/`.

## Arquivos e quando usar

| Arquivo em `referencias/` | Norma | Tema — use quando a informação tratar de |
|---|---|---|
| `lce-464-2012-lei-organica-tce-rn.md` | LC Estadual 464/2012 (Lei Orgânica do TCE/RN) | Competências do Tribunal, julgamento de contas, imputação de débito e multa, título executivo, prescrição, recursos. Base primária de qualquer fundamentação. |
| `regimento-interno-tce-rn-atualizado-ate-a-resolucao-46-24.md` | Regimento Interno (até Res. 46/2024) | Rito processual interno, prazos, tramitação, fases, atribuições dos órgãos. |
| `resolucao-0132015-dispoe-sobre-a-execucao-das-decisoes-tcern-multaressarcimento.md` | Resolução 013/2015-TCE | **Execução das decisões** (multa e ressarcimento): cobrança, notificação, parcelamento, envio à PGE/dívida ativa, desconto em folha. É a norma central do trabalho da CCD. |
| `resolucao-28-2012-atualizada-ate-13-2015.md` | Resolução 028/2012-TCE (atual. até 013/2015) | Regulamentação do processo de execução no âmbito do TCE. Complementa a 013/2015. |
| `l9492-lei-protesto.md` | Lei Federal 9.492/1997 | Protesto de títulos e CDAs — fundamenta encaminhamentos para protesto de débitos/multas. |
| `resgulamento-da-secex-res-42-2024.md` | Resolução 42/2024 (Regulamento da SECEX) | Atribuições e organização das unidades de controle externo (inclui a CCD). |
| `resolucao-12-2020-cgp.md` | Resolução 012/2020-TCE (Corregedoria) | Envio de processos/documentos às unidades de controle externo para nova manifestação. |

## Regras de redação

1. **Fundamente citando artigo, norma e redação vigente** — ex.: "nos termos do art. X da Resolução nº 013/2015-TCE". Nunca cite artigo sem conferir o texto no arquivo de referência correspondente.
2. **Confira a redação literal** com Grep no arquivo (ex.: `Grep pattern:"Art\. 15" path:".claude/skills/legislacao-ccd/referencias/resolucao-0132015-*.md"`) antes de transcrever ou parafrasear.
3. Hierarquia em caso de conflito: LC 464/2012 > Regimento Interno > Resoluções. Norma mais recente prevalece sobre a mais antiga de mesma hierarquia.
4. Texto sempre em **pt-BR formal**, no padrão dos exemplos em `scripts/automacao/templates/exemplos_informacoes/`.
5. Os PDFs originais estão em `legislacao/`; os `.md` aqui são extração fiel — em caso de dúvida sobre formatação/tabelas, consulte o PDF.
