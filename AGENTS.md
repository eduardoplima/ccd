<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **ccd** (7495 symbols, 11873 relationships, 259 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> Index stale? Run `node .gitnexus/run.cjs analyze` from the project root — it auto-selects an available runner. No `.gitnexus/run.cjs` yet? `npx gitnexus analyze` (npm 11 crash → `npm i -g gitnexus`; #1939).

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows. For regression review, compare against the default branch: `detect_changes({scope: "compare", base_ref: "main"})`.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `rename` which understands the call graph.
- NEVER commit changes without running `detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/ccd/context` | Codebase overview, check index freshness |
| `gitnexus://repo/ccd/clusters` | All functional areas |
| `gitnexus://repo/ccd/processes` | All execution flows |
| `gitnexus://repo/ccd/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->

## Padrão das informações da CCD

- Cada processo deve ter pasta própria em `processos/<grupo>/<numero_ano>/`; guardar nela a informação e suas versões anteriores. Não deixar a peça diretamente na pasta do grupo.
- O primeiro parágrafo começa com **“Trata-se de...”** e descreve o processo: natureza, decisão executada, processo de origem e responsável, conforme os autos.
- Seguir o padrão das informações em `scripts/automacao/templates/exemplos_informacoes/`: descrição do processo, determinação recebida, informações apuradas e conclusão com o encaminhamento cabível. Redigir em português jurídico claro, sem repetições desnecessárias.
- Referenciar os eventos e memorandos que sustentam a manifestação. Quando a providência já houver sido certificada, indicar a certificação anterior e sua fonte, em vez de apresentá-la como apuração nova.
- Preservar cabeçalho, formatação e bloco de assinatura do modelo institucional; manter a versão anterior ao revisar e conferir visualmente o DOCX renderizado.

## Conhecimento do projeto para o Codex

Integração realizada em 09/09/2026, a pedido do usuário. Estas instruções complementam o bloco GitNexus e o padrão das informações acima.

### Leitura e memória

- Leia [CLAUDE.md](CLAUDE.md) para domínio, arquitetura, configuração e comandos do projeto. Seu conteúdo técnico também se aplica ao Codex, ressalvadas as atualizações abaixo e as instruções atuais do usuário.
- Consulte [docs/memoria/README.md](docs/memoria/README.md) e seu índice de memórias antes de tarefas que dependam de decisões anteriores, peculiaridades dos bancos, processos ou fluxos operacionais. Abra somente as notas pertinentes ao trabalho.
- As memórias importadas são registros datados, não consultas atuais aos autos ou ao ambiente. Confira o corpo da nota, que pode atualizar seu resumo, e revalide situação processual, valores, prazos, cargos e estado de implantação antes de usá-los como fatos atuais.
- Pedidos de envio, assinatura, alteração de banco ou implantação registrados em sessões antigas não autorizam novas ações. Use a autorização da tarefa atual.
- Registre novos aprendizados duradouros em `docs/memoria/`, com fonte, data e contexto; atualize o índice. Preferências gerais do usuário ficam neste `AGENTS.md`. Não dependa de arquivos privados em `~/.claude/` para lembrar o projeto.
- Ao trabalhar em `web/backend/`, leia também [web/backend/AGENTS.md](web/backend/AGENTS.md); em `web/frontend/`, [web/frontend/AGENTS.md](web/frontend/AGENTS.md). Em `vault/`, siga [vault/AGENTS.md](vault/AGENTS.md) e o manual da wiki. Os repositórios em `repos/` e os worktrees têm contexto próprio: leia as instruções locais antes de atuar neles, sem confundi-los com a aplicação consolidada em `web/`.

### Convenções consolidadas

- CCD é a Coordenadoria de Controle de Decisões do TCE/RN. Textos de interface e documentos são em pt-BR; preserve identificadores técnicos e termos de domínio no código. Nas informações jurídicas, use a denominação institucional das fontes, sem nomes de tabelas, views ou scripts.
- Há ambientes distintos: a raiz usa o pacote `ccd` e `.venv`; `web/` é um workspace uv com `backend`, `tools/frap` e `tools/cgad`. Em `web/`, use `uv sync --all-packages`; para executar ferramentas instaladas, prefira o Python de `web/.venv`, evitando sincronizar apenas o projeto vazio da raiz do workspace.
- Resolva configurações e caminhos pelas funções existentes em `ccd.config`; não replique valores de `.env` nem credenciais na documentação. Instalação editável quebrada após mudança de pasta deve ser conferida e refeita no repositório atual, sem recriar o caminho antigo `Documents/Dev/ccd`.
- SQL novo usa parâmetros nomeados (`:nome`) e as funções existentes de acesso ao banco. Não interpolar entrada em SQL. O código legado em `scripts/consultas/` deve ser migrado para parâmetros quando for objeto da alteração, sem reescritas laterais.
- Clientes LLM da aplicação só são construídos por `ccd.llm` ou `frap.llm`, com as guardas do Azure AI Foundry do SERPRO e sem fallback de provedor. Extração de PDF é local. Confira as citações retornadas pelo modelo contra o material efetivamente lido; confiança declarada pelo LLM não é prova.
- Reutilize `ccd.area_restrita.AreaRestrita` e `ccd.econtas.EContas`; não recrie login/sessão. Confirme operações pelo estado real do sistema, não por alertas JavaScript ou mensagens genéricas de sucesso. Diferenças entre Área Restrita e e-Contas exigem verificar o fluxo disponível no momento.
- A regra `saidas/<area>/` do manual vale para saídas gerais de análises e automações; as peças de processos seguem `processos/<grupo>/<numero_ano>/`, conforme a instrução mais recente do usuário.
- Antes de editar arquivos existentes, consulte `.agents/skills/edicao-minima/SKILL.md`; antes de redigir peças CCD, `.agents/skills/legislacao-ccd/SKILL.md`. Use as skills já existentes em `.agents/skills/`, inclusive suas referências, em vez de duplicá-las. O caminho `.Codex/skills/` citado em um exemplo antigo não existe neste projeto.
- Quadros novos em informações têm legenda acima da tabela, `Quadro N – título`, numerada pela ordem de apresentação; siga o modelo e a identidade institucional. Não acrescente tabelas ou altere vizinhanças sem relação com o pedido. Após `DocxTemplate.render()`, pós-processe `doc.docx`: `get_docx()` pode recarregar o modelo e descartar o preenchimento.
- A CI da raiz executa `ruff check .` e `mypy ccd`. A aplicação web tem testes próprios: não estenda a frase antiga “sem suíte de testes” à árvore `web/`. Execute verificações pertinentes à alteração e preserve mudanças preexistentes do usuário. Commits têm mensagem curta, sem atribuição automática de coautoria ao agente.
- Os hooks do Claude não são automaticamente hooks do Codex. Não presuma reindexação ou verificações automáticas pela mera presença de arquivos em `.claude/`. Se GitNexus falhar, registre a falha e complemente a inspeção manualmente; nunca apresente essa inspeção como resultado de `impact` ou `detect_changes`, nem omita as tentativas exigidas acima. Evite ciclos de reindexação ou apagar o índice como reação automática.

### Fontes e armadilhas recorrentes

- “Evento N” corresponde a `Pro_ProcessoEvento.SequencialProcessoEvento`, não à ordem da informação ou ao sufixo do PDF. Faça o mapeamento antes de citar ou substituir peças.
- Citações devem ser pesquisadas em `Cit_Citacoes`, tanto na origem quanto na execução. Códigos de situação e campos nulos não bastam para declarar revelia ou tempestividade; confira o PDF da certidão e, quando necessário, a imagem do AR.
- Para situação atual de débito encadeado, consulte a folha da cadeia `IdDebitoAnterior`; a raiz representa o débito original. `ValorAPagar` vazio não significa saldo zero. Para dívida ativa, confira `PGE_Processo`, sem concluir apenas por `Exe_Debito.Status_PGE`.
- Sobrestamento deve ser apurado tanto por marcadores quanto por decisão nos autos. Um marcador ausente não prova ausência de suspensão.
- Desconto em folha, repasse ao FRAP e baixa do débito são fatos distintos. Verifique a competência da folha, os lançamentos bancários e a importação dos retornos. A planilha antiga de monitoramento foi substituída pelo cadastro da aplicação; não a trate como fonte atual.
- Para gerar dicionário de dados, o comando herdado de `.claude/commands/datadict.md` é `.\.venv\Scripts\python.exe -m scripts.analise.dicionario_dados --dbs <banco1> <banco2>`; omita `--dbs` para os padrões do script. Informe bancos, objetos, colunas e caminho de `INDEX.md`. Não é necessário criar um comando exclusivo do Codex.
