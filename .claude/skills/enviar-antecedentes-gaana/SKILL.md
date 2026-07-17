---
name: enviar-antecedentes-gaana
description: Runbook para gerar as informações de antecedentes dos processos na CCD e enviá-las ao gabinete (por padrão GAANA, da Conselheira Ana) via Área Restrita. Use quando o usuário pedir para "enviar antecedentes", "gerar antecedentes", "processos de antecedentes na CCD", ou o fluxo distribuir→cadastrar→assinar→tramitar de antecedentes. Cobre a geração (LLM + trânsitos) e o ciclo completo na Área Restrita.
---

# Enviar antecedentes à GAANA

Fluxo de ponta a ponta: descobrir os processos de antecedentes no CCD, gerar as informações (docx→pdf), distribuir para o usuário, cadastrar as informações digitalizadas, assinar (Web PKI) e tramitar para a DIP com a providência do gabinete requerente. Todos os comandos rodam do venv principal (`.venv`) na raiz do repo, com `PYTHONIOENCODING=utf-8`.

## Regras invioláveis

- **Cada ação irreversível tem `--dry-run` conferido antes da execução real** (cadastro, assinatura, tramitação).
- **Distribuir SEMPRE antes de cadastrar** — o cadastro de informação digitalizada só abre para processo distribuído ao usuário (ver [[area-restrita-digitalizar-requer-distribuicao]]).
- **Gate de revisão** após gerar os PDFs: conferir responsável extraído, tabela de condenações e ausência de código cru **antes** de subir na Área Restrita. Estes documentos vão para o gabinete de um Conselheiro.
- Os alerts "Tamanho de data não permitido / Caracter inválido / Este campo deve ser numérico" são **JS estático (falso-positivo)** — confie nas verificações reais do CLI (identificador retornado, item que sai da lista).

## 1. Descobrir + gerar

```
python -m scripts.automacao.gerar_antecedentes --dry-run     # lista os candidatos (marcador antecedentes no CCD)
python -m scripts.automacao.gerar_antecedentes               # gera todos -> saidas/automacao/antecedentes/gaana_YYYYMMDD/
```

`gerar_antecedentes.py` (porta de `web/backend/app/ccd/antecedentes/service.py`): descobre por `ccd/sql/antecedentes_candidatos.sql`; para cada processo pega o despacho-fonte (`antecedentes_info_despacho.sql`) → LLM (`ChatOpenAI` com `base_url=AZURE_OPENAI_ENDPOINT`, model gpt-4.1 — **não** `AzureChatOpenAI`, ver [[azure-llm-v1-endpoint-gpt41]]) extrai os responsáveis → débitos transitados em julgado por CPF → renderiza `templates/antecedentes.docx` → PDF `NNNNNN_YYYY.pdf`. Saída em pasta datada dedicada (o `informacao-lote` consome a pasta inteira; não misturar com PDFs antigos).

Armadilhas conhecidas (checar no gate):
- **Despacho-fonte errado**: o pipeline pega a informação **mais recente**, que às vezes é um Termo de Apensamento (assinado pelo coordenador) e não a solicitação de antecedentes. Sintoma: responsável extraído = "Eduardo Pereira Lima" ou nome de servidor. Correção: achar a solicitação real (informação GAANA "Para verificar condenações…") e regenerar daquela fonte.
- **Homônimos**: nomes iguais com CPFs diferentes misturam débitos. `gerar_antecedentes.py` já ancora no CPF da pessoa relacionada ao processo (`Pro_ProcessosResponsavelDespesa`); confira que o CPF do responsável bate.

## 2. Distribuir + cadastrar

```
python -m scripts.automacao.area_restrita distribuir <procs...> --dry-run
python -m scripts.automacao.area_restrita distribuir <procs...>
python -m scripts.automacao.area_restrita informacao-lote --pasta saidas/automacao/antecedentes/gaana_YYYYMMDD --dry-run
python -m scripts.automacao.area_restrita informacao-lote --pasta saidas/automacao/antecedentes/gaana_YYYYMMDD
```

Nota: **processos de CONTAS** têm os combos `cboRelatorioInicialAuditoria`/`cboRelatorioAuditoria` obrigatórios; `cadastrar_informacao_digitalizada` já os preenche com "N" (antecedentes não é relatório de auditoria). Sem isso, a inclusão falha silenciosa.

## 3. Assinar (usuário presente, token A3)

```
python -m scripts.automacao.assinar_informacoes <procs...> --cert "A3 : 05911205424" --timeout 600
```

Playwright + Web PKI; o usuário digita o PIN no diálogo (lotes de até 20). Verificação: quem assinou sai da lista de pendentes. Se um processo tiver informação pendente antiga que não deva ser assinada, use `--pular-arquivo CCD_NNNNNN_AAAA_ORDEM.doc`. Se der `ERR_ABORTED` na navegação, repetir. Ver [[webpki-playwright-assinatura]].

## 4. Tramitar para o gabinete

```
python -m scripts.automacao.area_restrita tramitar <procs...> --destino DIP --providencia "ENVIO A GAANA" --dry-run
python -m scripts.automacao.area_restrita tramitar <procs...> --destino DIP --providencia "ENVIO A GAANA"
```

Destino DIP, providência **"ENVIO A GAANA"** (gabinete da Conselheira Ana). Verificação: os processos saem da listagem do CCD.

**Outros gabinetes**: trocar a sigla na providência (dict `GABINETES` em `ccd/area_restrita.py`): ana=GAANA, antonio_ed=GCAED, carlos=GCCTH, george=GCGEO, gilberto=GCGIL, marco=GAMAR, paulo=GCPRO, renato=GCREN. A GAANA é o padrão porque os pedidos de antecedentes costumam vir do gabinete da Ana.

## Sem etapa de substituição

Antecedentes **adiciona** informação nova; não substitui anterior (diferente do fluxo nereu_ms, onde havia informação prévia a substituir).
