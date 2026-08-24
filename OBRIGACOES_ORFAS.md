# Obrigações órfãs — obrigações sem cientificação do responsável

> Plano de levantamento. Ainda não executado — pendente de revisão prévia das obrigações.

## Contexto

Chegou à Coordenadoria a suspeita de que muitos processos fixam obrigações (determinações de
fazer) cujos responsáveis nunca foram citados a respeito: existem citações para as multas, mas
as obrigações teriam "ficado esquecidas" na marcha processual. Antes de qualquer providência
institucional é preciso saber se a suspeita se confirma e qual o seu tamanho.

A questão não é acadêmica. O prazo de uma obrigação só corre da cientificação do responsável.
Sem citação, o prazo registrado no sistema é ficção, a obrigação é inexigível e — onde houver
multa cominatória — cobra-se diária de descumprimento de quem nunca foi informado do dever.

**A sondagem já feita no banco confirma a suspeita.** `BdDIP.dbo.Obrigacao` tem 1.737 obrigações
não canceladas em 1.201 processos, todas de decisões entre 05/2021 e 07/2026:

| Situação do processo após a decisão | Processos | % |
|---|---|---|
| Nenhuma comunicação registrada | 241 | 20,1% |
| Só intimação genérica (I15/ISP/C05…) | 811 | 67,5% |
| Citação específica de obrigação de fazer (30C/C60/C12/C18/C40) | 149 | 12,4% |

E no recorte de risco: dos 598 processos com **multa cominatória**, apenas 109 tiveram citação
específica de obrigação e 54 não tiveram comunicação alguma. Das 570 obrigações com pessoa
nominalmente identificada na multa cominatória, **149 têm responsável que jamais foi citado**
no processo depois da decisão.

O que falta é converter esse indício em número defensável, tratando os dois falsos positivos
conhecidos, e produzir os instrumentos de trabalho.

### Como esses números foram obtidos

Consulta direta ao banco, em leitura, sem script persistido:

- Universo: `BdDIP.dbo.Obrigacao` com `Cancelado IS NULL`.
- Data da decisão: join em `processo.dbo.vw_ia_votos_acordaos_decisoes` por
  `(IdProcesso, IdComposicaoPauta, IdVotoPauta)` → `DataSessao`. Cobre 1.737 de 1.738 obrigações.
- Comunicação: `processo.dbo.Cit_Citacoes` no mesmo processo com
  `COALESCE(DataInicioContagem, DataInclusao) >= DataSessao`, tipada por
  `processo.dbo.Cit_Tipo_Citacao`.

## Decisões tomadas

- **Fonte das obrigações**: `BdDIP.dbo.Obrigacao` (não o `processo.dbo.Obg_Obrigacao`).
- **Critério de cientificação**: medir as duas faixas — piso (só citação específica conta) e
  teto (qualquer intimação pós-decisão conta) — e usar a validação por leitura para dizer onde
  o número real cai dentro do intervalo.
- **Entregas**: planilha de triagem + nota técnica.
- **Prioridade da validação**: os processos com multa cominatória primeiro.

## Abordagem

Duas camadas: uma medição barata que cobre 100% da base em SQL, e uma validação por leitura
que só roda na amostra priorizada. Nada de módulo novo em `ccd/`, nada de tabela nova — dois
scripts em `scripts/analise/` no mesmo padrão do `crivo_monitoramento.py` (JSON por processo +
planilha consolidada).

### Camada 1 — medição censitária (SQL + pandas)

**Arquivo novo: `scripts/analise/obrigacoes_sem_citacao.py`**

Reutiliza `ccd.notebook.setup()` (engine) e `ccd.db.run_query_df` com parâmetros nomeados.

1. `carregar_obrigacoes(engine)` — `BdDIP.dbo.Obrigacao` com `Cancelado IS NULL`, join em
   `processo.dbo.Processos` e em `processo.dbo.vw_ia_votos_acordaos_decisoes` por
   `(IdProcesso, IdComposicaoPauta, IdVotoPauta)` para obter a `DataSessao`.
2. `carregar_citacoes(engine, ids)` — `processo.dbo.Cit_Citacoes` + `Cit_Tipo_Citacao` (para
   `Descricao`/`Prazo`) + `GenPessoa` (nome/documento do citado). Data efetiva =
   `COALESCE(DataInicioContagem, DataInclusao)`.
3. `classificar(obg, cit)` — por obrigação, produz:
   - `situacao_comunicacao` ∈ {`cit_obrigacao`, `so_intimacao_generica`, `nenhuma_comunicacao`};
   - `cientificado_estrito` / `cientificado_amplo` (as duas faixas);
   - `pessoa_multa_citada` — cruza `IdPessoaMultaCominatoria` com `Cit_Citacoes.IdPessoa` no
     mesmo processo, após a decisão;
   - `prazo_vencido` — a partir de `Obrigacao.Prazo` (varchar, exige parse tolerante) contado
     da data da comunicação, quando existe;
   - `risco` — alto quando há multa cominatória e não há cientificação estrita.
   Os códigos de tipo de citação de obrigação ficam numa constante única no topo do arquivo.

**Tratar os dois falsos positivos** — sem isso o número não se sustenta:

- **Comunicação em processo apartado de monitoramento.** `BdDIP.dbo.Monitoramento` está vazia,
  então não há vínculo estruturado. Detectar pelo assunto: processos cujo
  `Processos.assunto` casa com `MONITORAMENTO ... <numero>/<ano>` referenciando um processo da
  base (o `crivo_monitoramento.py` já lida com esses processos e serve de referência para o
  padrão do assunto). Onde houver processo de monitoramento, procurar a citação **também nele**
  antes de classificar como "nenhuma comunicação".
- **Obrigação dirigida a órgão, não a pessoa.** `BdDIP.dbo.Obrigacao` só tem
  `IdOrgaoResponsavel`; pessoa natural só aparece quando há multa cominatória. Registrar isso
  como limitação explícita: para as 864 obrigações sem multa cominatória, a pergunta mensurável
  é "o órgão foi comunicado", não "o responsável foi citado". Não inventar o gestor à época.

Saída: `saidas/analise/obrigacoes_sem_citacao/obrigacoes_sem_citacao.xlsx`, uma linha por
obrigação, mais um resumo impresso com as duas faixas.

**Check obrigatório** (regra do repositório: lógica não trivial deixa uma verificação
executável): um `demo()` com `assert` no próprio arquivo, alimentado por DataFrames sintéticos,
cobrindo os três casos de `classificar` e o parse de `Prazo`. Sem framework, sem fixture.

### Camada 2 — validação por leitura (amostra priorizada)

O texto da citação não serve: `Cit_Citacoes.Texto` está preenchido em 15 de 4.594 registros. O
objeto da comunicação só se conhece lendo a informação vinculada
(`Cit_Citacoes.IdInformacao` / `IdInformacaoDeterminacao`, este preenchido em 1.286 dos 4.594).

**Arquivo novo: `scripts/analise/validar_citacao_obrigacao.py`**, decalcado da estrutura do
`crivo_monitoramento.py`: `ccd.processo.get_informacoes_processo` para o texto,
`ccd.llm.structured` para a saída tipada, um JSON por processo e consolidação a partir do disco
(rodadas parciais não apagam o já feito).

- Amostra: os processos com multa cominatória classificados como `so_intimacao_generica` —
  435 processos, o recorte onde a distinção entre piso e teto decide o resultado. Rodar em
  lotes, com `--limite`.
- Pergunta ao modelo, por processo: a comunicação cientificou o responsável do dever de fazer,
  com identificação da determinação e prazo? Saída `Literal["SIM","NAO","DUVIDA"]` + trecho
  literal citado + nome do arquivo de origem, no mesmo padrão de honestidade do
  `crivo_monitoramento.py` (ambíguo → `DUVIDA`, nunca chute).
- O resultado calibra a faixa: a proporção de `SIM` na amostra estima quantos dos 811
  "só intimação genérica" na verdade foram cientificados.

LGPD: o texto sai exclusivamente pelo factory `ccd.llm` (DeepSeek do Foundry do SERPRO) — o
lint já barra qualquer outro caminho.

### Entrega — nota técnica

Markdown como fonte única em `NOTA_OBRIGACOES_SEM_CITACAO.md` na raiz, convertido com o gerador
existente `scripts/automacao/gerar_relatorio_docx.py` (herda cabeçalho institucional, identidade
TCE/RN e numeração de páginas). Esse script hoje tem o destino fixo em
`saidas/analise/relatorio_auditoria_financeira` — acrescentar um `--destino` opcional, mudança
de três linhas, em vez de duplicar o gerador.

Conteúdo: objeto e método, as duas faixas com a estimativa calibrada, o recorte de multa
cominatória, as limitações (cobertura temporal, obrigação por órgão, amostra) e o que se propõe
fazer. Base legal pela skill `legislacao-ccd` na redação.

## Limitações a declarar na nota

1. **Cobertura temporal**: `BdDIP.dbo.Obrigacao` só contém decisões de 05/2021 em diante, e o
   registro estruturado começa a ter volume em 2016 (por ano de autuação). Obrigações fixadas
   em decisões anteriores estão fora — o levantamento é um piso, não o universo. Se o Tribunal
   quiser o acervo completo, a fonte seria `BdDIP.dbo.NERObrigacao` (extração por NER das
   decisões, usada pelo CGAD), em trabalho separado.
2. **Obrigação sem pessoa**: ver acima.
3. **Ausência de registro ≠ ausência de ato**: mede-se o que está em `Cit_Citacoes`. Comunicação
   feita por via não registrada no módulo de citações não aparece — daí a camada 2.

## Verificação

1. `python scripts/analise/obrigacoes_sem_citacao.py --demo` — os asserts do check embutido.
2. `ruff check scripts/analise/ && mypy ccd` — o que a CI roda.
3. Rodar a camada 1 completa e conferir que o total bate com a sondagem já feita
   (1.737 obrigações / 1.201 processos) antes do tratamento de monitoramento, e que o número de
   "nenhuma comunicação" **cai** depois dele — se não cair, a detecção de monitoramento não está
   funcionando.
4. Conferência manual na Área Restrita de 3 processos, um de cada classe, incluindo um dos 149
   com pessoa de multa cominatória nunca citada. O banco atrasa em relação à Área Restrita, que
   é autoritativa para tramitação e comunicações recentes.
5. `python -m scripts.automacao.gerar_relatorio_docx NOTA_OBRIGACOES_SEM_CITACAO.md` e abrir o
   `.docx` para checar tabelas e cabeçalho.
