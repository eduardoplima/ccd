---
name: enviar-informacao
description: Ciclo completo de UMA informação já gerada na Área Restrita — distribuir o processo ao usuário, cadastrar o PDF mais recente da informação, assinar (Web PKI/A3) e tramitar CCD→DIP com a providência escolhida. Use quando o usuário pedir para "enviar a informação", "cadastrar, assinar e tramitar", "mandar para a DIP" um ou mais processos cuja informação já existe em processos/informacoes/ ou processos/projetos/.
---

# Enviar informação (distribuir → cadastrar → assinar → tramitar à DIP)

Uso: `/enviar-informacao <numero/ano> [<numero/ano> ...] [providência]`
Ex.: `/enviar-informacao 12744/2014 ENVIO A GCAED`

Destino é **sempre DIP**. A providência (ex.: "ENVIO A GCAED", "ENVIO A DE", "ENVIO AO MPC") vem do usuário; se não veio, **pergunte** — não adivinhe. Siglas dos gabinetes: dict `GABINETES` em `ccd/area_restrita.py` (ana=GAANA, antonio_ed=GCAED, carlos=GCCTH, george=GCGEO, gilberto=GCGIL, marco=GAMAR, paulo=GCPRO, renato=GCREN).

Todos os comandos rodam da raiz com `.venv/Scripts/python.exe` e `PYTHONIOENCODING=utf-8`.

## Regras invioláveis

- **Toda ação irreversível tem `--dry-run` conferido antes da real** (distribuir, cadastrar, tramitar). Assinatura: `--dry-run` lista as pendências.
- **Distribuir antes de cadastrar** — sem distribuição, o cadastro falha silencioso ([[area-restrita-digitalizar-requer-distribuicao]]).
- Os alerts "Tamanho de data não permitido / Caracter inválido / numérico" são JS estático (falso positivo); confie no identificador retornado.

## 1. Achar o PDF da informação

Nome padrão: `informacao_NNNNNN_AAAA.pdf` (número com 6 dígitos). Procure em `processos/informacoes/NNNNNN_AAAA/` e `processos/projetos/*/NNNNNN_AAAA/` (e `envio/` do lote, se houver — envio montado com anexos tem prioridade):

```
ls -lt processos/informacoes/NNNNNN_AAAA/*.pdf processos/projetos/*/NNNNNN_AAAA/*.pdf processos/projetos/*/envio/*NNNNNN_AAAA*.pdf 2>/dev/null
```

Pegue o mais recente e **confira**:
- o `.docx` correspondente não é mais novo que o `.pdf` (senão o PDF está desatualizado — regenerar antes);
- se houver mais de um candidato (lotes diferentes), mostre ao usuário e pergunte qual.

Mostre caminho + data do PDF e peça confirmação antes de seguir.

## 2. Distribuir

```
python -m scripts.automacao.area_restrita distribuir <procs...> --dry-run
python -m scripts.automacao.area_restrita distribuir <procs...>
```

## 3. Cadastrar a informação

```
python -m scripts.automacao.area_restrita informacao <proc> --pdf <caminho.pdf> --dry-run
python -m scripts.automacao.area_restrita informacao <proc> --pdf <caminho.pdf>
```

Um processo por chamada (cada um tem seu PDF). Processos de CONTAS: os combos de auditoria já são preenchidos com "N" ([[contas-cadastro-combos-auditoria]]).

## 4. Assinar (usuário presente, token A3)

```
python -m scripts.automacao.assinar_informacoes <procs...> --dry-run
python -m scripts.automacao.assinar_informacoes <procs...> --cert "A3 : 05911205424" --timeout 600
```

Avise o usuário para digitar o PIN. Se houver informação pendente antiga que não deve ser assinada: `--pular-arquivo CCD_NNNNNN_AAAA_ORDEM.doc`. `ERR_ABORTED` na navegação → repetir. Verificação: o processo sai da lista de pendentes. Ver [[webpki-playwright-assinatura]].

## 5. Tramitar CCD → DIP

```
python -m scripts.automacao.area_restrita tramitar <procs...> --destino DIP --providencia "<PROVIDÊNCIA>" --dry-run
python -m scripts.automacao.area_restrita tramitar <procs...> --destino DIP --providencia "<PROVIDÊNCIA>"
```

Verificação: o processo some da listagem da CCD (sucesso — ver [[area-restrita-tramitar-flow]]).

## Fechamento

Informe por processo: PDF usado, identificador da informação (CCD_NNNNNN_AAAA_ORDEM), assinatura OK, tramitação com a providência. Se o processo tem memória de progresso (MEMORY.md), atualize-a com a data do envio.
