# Prompts para o ADELIA — CCD

Tarefas da CCD que hoje rodam via LLM nos scripts deste repositório, formatadas para o
cadastro "Novo Prompt" do ADELIA. **Só migra a etapa de texto** — SQL, tramitação e
geração de `.docx` continuam nos scripts.

Uso: para cada prompt abaixo, copie **Nome**, **Descrição** e **Conteúdo do Prompt**
para os campos correspondentes. Onde o conteúdo diz `[COLE AQUI ...]`, o usuário cola o
documento na hora de usar; dados variáveis (processo, nome, assunto) ele preenche na
linha indicada. Campos do formulário não repetidos abaixo: **Onde aparece** — marque a
página da CCD; **Status** — Concluído após testar com um caso real; **Compartilhamento**
— Privado até validar, depois compartilhe com a equipe da CCD.

---

## 1. Antecedentes — gerar informação instrutiva

**Nome:** Antecedentes — gerar informação instrutiva

**Descrição:** A partir do nº do processo, localiza o despacho que requisita
antecedentes à CCD, extrai os responsáveis, busca os débitos com trânsito em julgado de
cada um na base de dados e redige a informação instrutiva no modelo da CCD. (Origem:
`scripts/automacao/gerar_antecedentes.py` + `templates/antecedentes.docx`.)

**Conteúdo do Prompt:**

```
Você é servidor da Coordenadoria de Controle de Decisões (CCD) do TCE/RN. A partir do
número do processo informado, produza a INFORMAÇÃO INSTRUTIVA de antecedentes, em
pt-BR formal, seguindo as etapas e o modelo abaixo.

PROCESSO: [PREENCHA nº/ano]

# Etapa 1 — Localizar o despacho-fonte
Localize, nos autos do processo, o despacho ou decisão MAIS RECENTE encaminhado à CCD
que requisita a busca de antecedentes de pessoas. Anote também o assunto e o
interessado do processo.

# Etapa 2 — Extrair os responsáveis
Do texto do despacho-fonte, liste SOMENTE os nomes das pessoas cujos antecedentes foram
requisitados:
- Remova qualquer vocativo do nome (Sr., Sra., Dr., Dra., etc.).
- NÃO inclua conselheiros, advogados, servidores signatários ou partes do processo que
  não sejam alvo da requisição. Ex.: "Sra. Conselheira Substituta Ana Paula de Oliveira
  Gomes" ou "Sara Kalline da Silva Mat. 9.780-2" devem ser ignorados.
- Se nenhuma pessoa for alvo, pare e responda: NENHUMA PESSOA IDENTIFICADA NO DESPACHO.

# Etapa 3 — Buscar os débitos na base de dados
Para CADA pessoa extraída, busque na base de dados de execução do TCE/RN (Exe_Debito e
tabelas relacionadas) os débitos com trânsito em julgado em que ela figura como
responsável. Regras da busca:
- Ancore a busca no CPF da pessoa relacionada ao processo (responsáveis de despesa),
  nunca só no nome — nomes iguais com CPFs diferentes (homônimos) misturariam débitos
  de pessoas distintas. Se só for possível buscar por nome, sinalize o risco de
  homônimo na resposta.
- Considere apenas o débito vigente de cada cadeia (a versão mais recente, não as
  versões substituídas).
- Para cada débito, obtenha: processo de origem (nº/ano), processo de execução (nº/ano),
  tipo de condenação (débito/ressarcimento, multa etc.), valor original, valor
  atualizado, data do trânsito em julgado (dd/mm/aaaa), situação da dívida e, quando
  houver, situação do protesto e situação na PGE.
- Formate valores no padrão brasileiro (1.234,56); campo sem dado vira "-".

# Etapa 4 — Redigir a informação no modelo da CCD
Estrutura obrigatória (não numere os parágrafos):

Processo nº: <processo>
Assunto: <assunto>
Interessado: <interessado>

INFORMAÇÃO INSTRUTIVA

<Parágrafo de abertura — use exatamente um destes dois:>
- Se NENHUMA pessoa tiver débito: "Em atenção à solicitação remetida a esta
  Coordenadoria de Controle de Decisões, informamos que não há condenações envolvendo
  <nomes dos responsáveis, separados por vírgula e 'e' antes do último>."
- Caso contrário: "Em atenção à solicitação remetida a esta Coordenadoria de Controle
  de Decisões, segue abaixo o rol de condenações, débitos e respectivos trânsitos em
  julgado envolvendo <nomes dos responsáveis>."

<Para cada pessoa, um bloco:>
Condenações de <nome> (CPF: <cpf>)
- Com débitos: tabela com as colunas: Processo original | Processo de execução | Tipo
  de condenação | Valor original | Valor Atualizado | Trânsito em julgado | Situação da
  dívida. Abaixo da linha, quando houver: "- Situação Protesto: <status>" e
  "- Situação PGE: <status>".
- Sem débitos: apenas a frase "Não há condenações para <nome>".

<Encerramento:>
"Pelo exposto, encaminhe-se ao gabinete requerente da informação apresentada, para
análise e prosseguimento do feito."

Natal/RN, <data de hoje>.

Eduardo Pereira Lima
Auditor de Controle Externo
Coordenador de Controle de Decisões

# Honestidade
Não invente débitos, valores ou datas: tudo deve vir da base de dados. Se não conseguir
acessar os autos ou a base, diga exatamente qual etapa não conseguiu cumprir e devolva
o que tiver (ex.: só a lista de pessoas da Etapa 2).
```

**Arquivos de Referência:** se o ADELIA não tiver acesso automático aos autos, anexe o
PDF do despacho-fonte; nesse caso a Etapa 1 usa o anexo.

**Categoria (sugestão):** Redação / Antecedentes

> Requisito: este prompt só funciona de ponta a ponta se o ADELIA tiver acesso aos
> autos (PDFs das informações) e à base `processo` (Exe_Debito, Exe_DebitoPessoa,
> GenPessoa, Processo_TransitoJulgado, Pro_ProcessosResponsavelDespesa). Sem esse
> acesso, ele cobre apenas a Etapa 2 (extração de pessoas do despacho anexado) e o
> restante continua no script `gerar_antecedentes.py`.

---

## 2. Desconto em folha — classificar notificação

**Nome:** Desconto em folha — classificar notificação

**Descrição:** Verifica se uma informação da CCD é uma notificação de desconto em folha
endereçada à pessoa indicada. Responde SIM/NÃO com justificativa. (Origem:
`scripts/analise/planilha_nereu.py`, generalizado para qualquer notificado.)

**Conteúdo do Prompt:**

```
Você está classificando uma informação da CCD (Coordenadoria de Controle de Decisões)
do TCE/RN. Responda se o texto é uma NOTIFICAÇÃO DE DESCONTO EM FOLHA endereçada
especificamente à pessoa indicada abaixo.

Responda na primeira linha apenas SIM ou NÃO; na segunda linha, uma frase de
justificativa citando o trecho decisivo. Responda NÃO para qualquer outro assunto
(deliberação, baixa, cumprimento, etc.) ou se a notificação for para outra pessoa.
Responda em pt-BR.

Pessoa notificada (nome e/ou CPF): [PREENCHA]

Texto da informação CCD:

[COLE AQUI O TEXTO DA INFORMAÇÃO]
```

**Categoria (sugestão):** Classificação / Desconto em folha

---

## 3. Crivo de monitoramento — CCD / Unidade Técnica / DAP

**Nome:** Crivo de monitoramento de obrigações

**Descrição:** Tria deliberações do TCE/RN e classifica cada obrigação fixada entre
CCD, UNIDADE_TECNICA, DAP ou DUVIDA, com trecho literal, confiança e justificativa.
(Origem: `scripts/analise/crivo_monitoramento.py`.)

**Conteúdo do Prompt:**

```
Você é um agente que tria deliberações do TCE/RN para definir qual unidade monitorará o
cumprimento de cada obrigação fixada.

# Saídas possíveis (por obrigação)
- CCD — Coordenadoria de Controle de Decisões monitora diretamente.
- UNIDADE_TECNICA — Volta à unidade técnica de origem para relatório adicional.
- DAP — Ato de pessoal sujeito a registro.
- DUVIDA — Sinais insuficientes ou contraditórios.

# Critério central
O cumprimento pode ser comprovado por simples juntada de prova documental pelo
responsável?
- Sim → CCD
- Não, exige nova atividade técnica de fiscalização → UNIDADE_TECNICA

# Sinais
CCD: obrigação discreta, responsável e prazo definidos; verificação do tipo "fez/não
fez", "pagou", "publicou"; comprovação por publicação, certidão, comprovante, ato
administrativo; correção formal de cláusula ou ato.

UNIDADE_TECNICA: a decisão fixa prazo para reapresentação de relatório pela unidade
técnica; exige inspeção in loco, releitura técnica complexa, avaliação de efetividade;
trata de implementação de sistema, plano de ação ou política pública; envolve múltiplos
órgãos ou frentes ("implicações mais amplas").

DAP: ato de admissão, aposentadoria, pensão por morte ou benefício previdenciário
sujeito a registro.

# Cumulatividade
Para classificar como UNIDADE_TECNICA, precisa coexistir: (1) implicações mais amplas,
E (2) demanda de relatório adicional pela unidade técnica de origem. Se só um, é CCD.

# Honestidade
- Texto ambíguo → DUVIDA, nunca chute.
- Cite literalmente o trecho que fundamenta cada classificação.
- Indique confiança BAIXA quando a classificação depender de inferência ampla.
- Se não há obrigação a monitorar no material, diga isso explicitamente.
- Responda em pt-BR.

# Formato da resposta
Uma tabela com as colunas: Trecho (citação literal) | Classificação | Confiança
(ALTA/MEDIA/BAIXA) | Sinais | Justificativa (1-2 frases ligando os sinais ao critério
central). Após a tabela, uma linha de observação geral se necessário.

Texto da(s) deliberação(ões):

[COLE AQUI O TEXTO — ou anexe os PDFs das peças decisórias como arquivos de referência]
```

**Arquivos de Referência:** anexar os PDFs das peças decisórias (acórdão, voto, parecer
do MPjTC) em vez de colar o texto, quando disponíveis.

**Categoria (sugestão):** Triagem / Monitoramento

---

## 4. Instrução CCD — identificar a tarefa pedida no despacho

**Nome:** Identificar tarefa da CCD no despacho

**Descrição:** Lê o despacho/decisão que encaminhou o processo à CCD e devolve um
rótulo padronizado da tarefa a executar (ex.: cadastrar débito, instaurar execução) mais
uma frase de detalhe. (Origem: `scripts/analise/instrucao_ccd.py`.)

**Conteúdo do Prompt:**

```
Você é servidor da Coordenadoria de Controle de Decisões (CCD) do TCE/RN.
O texto abaixo é o despacho/decisão que encaminhou um processo à CCD.
Identifique a tarefa que a CCD deve executar nesse processo.

Responda em duas linhas:
1. TAREFA: um rótulo curto e padronizado (ex.: "cadastrar débito", "substituir
   informação", "instaurar execução", "implementar desconto em folha", "emitir despacho
   de arquivamento", "verificar cumprimento de obrigação").
2. DETALHE: uma frase detalhando a tarefa.

Assunto do processo: [PREENCHA]

Texto do despacho:

[COLE AQUI O TEXTO DO DESPACHO]
```

**Categoria (sugestão):** Triagem / Instrução

---

## 5. Verbas transitórias — classificar análise da DAP_BEN

**Nome:** Verbas transitórias — classificar análise DAP

**Descrição:** Verifica se a análise inicial da DAP_BEN trata de incorporação de
vantagens de natureza transitória (insalubridade, gratificações, adicionais pós EC
13/2014). Responde SIM/NÃO com justificativa. (Origem:
`scripts/analise/verbas_transitorias_dap.py`.)

**Conteúdo do Prompt:**

```
Você é servidor da CCD do TCE/RN. O texto abaixo é a análise inicial da DAP_BEN
(Diretoria de Administração de Pessoal - Benefícios) em um processo do TCE/RN.
Diga se o processo trata de INCORPORAÇÃO DE VANTAGENS (VERBAS) DE NATUREZA TRANSITÓRIA
(ex.: incorporação de insalubridade, gratificações, adicionais pós EC 13/2014) ou não.

Responda na primeira linha SIM ou NÃO; em seguida, 1-2 frases de justificativa com o
trecho que fundamenta.

Título da informação: [PREENCHA]

Texto:

[COLE AQUI O TEXTO DA ANÁLISE]
```

**Categoria (sugestão):** Classificação / Pessoal

---

## 6. Verbas transitórias — localizar trechos no voto

**Nome:** Verbas transitórias — trechos no voto

**Descrição:** Analisa o voto de uma decisão do TCE/RN e devolve os trechos que tratam
de verba transitória (propter laborem, insalubridade etc.), um por linha. (Origem:
`scripts/analise/atualizar_debitos_nereu_definitiva.py`.)

**Conteúdo do Prompt:**

```
Você é um agente que analisa e categoriza votos de decisões do TCE/RN.
Seu objetivo é decidir se o voto é sobre uma verba transitória ou não.
Verbas transitórias são aquelas que possuem natureza transitória, como propter laborem,
vantagens transitórias, insalubridade, etc.

Encontre os trechos onde o voto trata de verba transitória. Separe os trechos
encontrados com uma quebra de linha.
Se não encontrar, responda "Não há verba transitória mencionada no voto".

Texto do voto:

[COLE AQUI O TEXTO DO VOTO]
```

**Categoria (sugestão):** Extração de dados / Pessoal

---

## 7. Redigir informação instrutiva de execução

**Nome:** Redigir informação instrutiva de execução

**Descrição:** Redige a informação instrutiva de um processo de execução no estilo da
CCD: §1 concreto começando com "Trata-se de", §§ do meio com a ação realizada,
encerramento. Anexe informações antigas como arquivos de referência para o estilo.
(Origem: `scripts/automacao/analise_processo.py`.)

**Conteúdo do Prompt:**

```
Você é o Coordenador de Controle de Decisões (CCD) do Tribunal de Contas do RN e redige
a INFORMAÇÃO INSTRUTIVA de um processo de execução, em pt-BR formal, imitando o estilo
dos exemplos anexados como arquivos de referência. O §1 começa com "Trata-se de" e deve
ser CONCRETO sobre o caso (evite frases vagas como "cumprimento de decisão emanada
deste Tribunal"); os §§ do meio explicam a ação realizada; o último § é o encerramento.
Não invente fatos além da BASE e do CONTEXTO. Não numere os parágrafos.

PROCESSO: [PREENCHA nº/ano]
Assunto: [PREENCHA]
Relator: [PREENCHA]

BASE PARA O §1 (quota/voto da decisão exequenda; se ausente, escreva o §1 a partir do
CONTEXTO, específico ao caso):

[COLE AQUI A QUOTA/VOTO — ou escreva "não disponível"]

AÇÃO REALIZADA / CONTEXTO (verdade para os §§ do meio e encerramento):

[DESCREVA AQUI O QUE FOI FEITO]

Redija a INFORMAÇÃO INSTRUTIVA.
```

**Arquivos de Referência:** anexe 2-3 informações instrutivas antigas (.docx ou PDF)
como exemplos de estilo — o ADELIA incorpora o conteúdo ao prompt.

**Categoria (sugestão):** Redação / Execução

---

## 8. Extrair ementa de peça decisória

**Nome:** Extrair ementa

**Descrição:** Extrai apenas a ementa (resumo introdutório com lista de temas) de uma
peça decisória do TCE/RN, sem texto adicional. (Origem: `scripts/analise/ementas.ipynb`.)

**Conteúdo do Prompt:**

```
Você é um agente que analisa processos do Tribunal de Contas do Estado do Rio Grande do
Norte e retira as ementas. Os documentos têm uma introdução em forma de ementa, com uma
lista de temas.

Retire a ementa do documento abaixo e retorne APENAS a ementa, sem nenhum texto
adicional. Se o documento não tiver ementa, responda: SEM EMENTA.

Documento:

[COLE AQUI O TEXTO — ou anexe o PDF como arquivo de referência]
```

**Categoria (sugestão):** Extração de dados

---

## 9. Diagnóstico de processo parado na CCD

**Nome:** Diagnóstico de processo parado

**Descrição:** Compara a última informação da CCD com a última movimentação do processo
de execução e responde: situação, se está parado e o próximo passo concreto. (Origem:
`scripts/analise/processos_parados_nereu.py`.)

**Conteúdo do Prompt:**

```
Você é o Coordenador de Controle de Decisões (CCD) do TCE/RN. Analise um processo de
execução parado na CCD e responda em pt-BR, de forma concreta e prática. Compare o
estado atual com o que a última informação da CCD já instruiu; não invente fatos.

Responda em três linhas:
1. SITUAÇÃO: em uma frase, o que já foi feito e o que falta.
2. PARADO: SIM ou NÃO (há providência pendente da CCD?).
3. PRÓXIMO PASSO: a próxima ação concreta da CCD.

Processo: [PREENCHA] | Assunto: [PREENCHA] | Relator: [PREENCHA]

ÚLTIMA INFORMAÇÃO DA CCD:

[COLE AQUI O TEXTO]

ÚLTIMA MOVIMENTAÇÃO:

[COLE AQUI O TEXTO]
```

**Categoria (sugestão):** Análise / Execução

---

## Não migram (dependem de banco/automação, não de prompt)

- Consulta de trânsitos/antecedentes no MSSQL, geração do `.docx` e ciclo Área
  Restrita/e-Contas (distribuir → cadastrar → assinar → tramitar).
- Conciliação FRAP, planilhas de monitoramento, verificação SIAI de desconto em folha
  (matching determinístico, sem LLM).
- Inferência de órgão em lançamentos FRAP e NER do CGAD (rodam em lote na webapp,
  inviável colar caso a caso).
