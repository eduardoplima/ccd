# Memória do projeto CCD

Conhecimento incorporado ao Codex em **09/09/2026**, a pedido do usuário. O ponto de entrada é [AGENTS.md](../../AGENTS.md); a arquitetura detalhada continua em [CLAUDE.md](../../CLAUDE.md). Leia esta página e selecione as notas necessárias, sem carregar o acervo inteiro em toda tarefa.

## Acervo importado

- [Índice das memórias do Claude](claude/MEMORY.md): referências operacionais, preferências, diagnósticos e históricos de processos. Os links de tópicos levam às cópias locais em `claude/`.
- [Extração do projeto decisoes-etl](claude/project_decisoes_etl_extracted.md): decisão preservada da instalação antiga do CCD. Não recriar a árvore removida; confirme o repositório de destino quando necessário.
- [Manual da raiz](../../CLAUDE.md), [backend](../../web/backend/CLAUDE.md) e [frontend](../../web/frontend/CLAUDE.md): reutilizados pelos `AGENTS.md`, com ressalvas atualizadas onde havia divergência.
- [Wiki CCD](../../vault/AGENTS.md): já tinha integração para agentes. Fontes em `vault/raw/` são imutáveis; páginas em `vault/wiki/` seguem o manual do cofre. A wiki da aplicação em `web/backend/wiki/` é outro acervo.
- Skills: `.agents/skills/` já contém as skills e referências de `.claude/skills/`. Não foi necessária nova cópia. As duas diferenças encontradas eram adaptações de nomenclatura; os caminhos e a ressalva sobre hooks foram esclarecidos no `AGENTS.md`.
- Comando de dicionário de dados: [datadict.md](../../.claude/commands/datadict.md), com chamada direta documentada no `AGENTS.md`.

## Como usar os registros

As notas em `claude/` são uma fotografia da memória de origem na data de importação. A redação e os detalhes históricos foram preservados; elas não são um relatório de verificação atual nem autorizam atos novos. Caminhos de código mencionados no texto são relativos à raiz do CCD, salvo indicação contrária. `[[nome-da-nota]]` refere-se a outra memória quando houver arquivo homônimo.

1. Consulte a nota completa, não apenas o resumo do índice: algumas notas têm atualizações posteriores que contradizem a descrição inicial.
2. Revalide situação processual, valores, competência, legislação, cargos e estado de implantação nas fontes próprias antes de concluir ou executar.
3. Prefira instruções atuais do usuário e regras atualizadas do projeto às anotações antigas. Não reative tarefas encerradas nem restaure conteúdo removido por decisão do usuário.
4. Aprendizados novos ficam em notas nesta pasta, com data, fonte, motivo e forma de aplicação, e link neste índice. Use `AGENTS.md` para convenções permanentes. Não sobrescreva silenciosamente a fotografia importada.

## Atalhos por assunto

| Trabalho | Memórias de entrada |
|---|---|
| Redação e revisão de informações | [Edição mínima](claude/edicao-minima-preservar-versao.md), [legendas](claude/gerar-informacao-legendas-quadros.md), [numeração de eventos](claude/evento-e-sequencialprocessoevento.md), [docxtpl](claude/docxtpl-get-docx-descarta-render.md), [citações produzidas por LLM](claude/llm-citacao-precisa-ser-conferida.md) |
| Citação, revelia e suspensão | [Cit_Citacoes](claude/cit-citacoes-authoritative-source.md), [situação 21 ambígua](claude/cit-certidao-situacao-21-ambigua.md), [AR devolvido](claude/ar-baixa-entregue-pode-ser-devolucao.md), [sobrestamento](claude/sobrestamento-via-pro-marcador.md) |
| Débitos, parcelamento e dívida ativa | [Cadeia do débito](claude/exe-debito-cadeia-folha-vigente.md), [ValorAPagar](claude/exe-debito-valorapagar-vazio.md), [parcelamento](claude/exe-parcelamento-semantica.md), [PGE_Processo](claude/pge-processo-fonte-divida-ativa.md), [retornos rejeitados](claude/retorno-boleto-linha-rejeitada.md) |
| Folha e arrecadação | [Monitoramento](claude/monitoramento-desconto-folha-crud.md), [extratos BB](claude/frap-extrato-bb-armadilhas.md), [FRAP em BdDIP](claude/frap-tables-in-bddip.md), [competência SIAI](claude/siai-item-competencia-congelada.md), [SIAI antigo e atual](claude/siai-despesa-pessoal-vs-siai-pessoal.md), [origem multa/PGE](claude/arrecadacao-multa-vs-pge.md) |
| Área Restrita e e-Contas | [Distribuição antes da inclusão](claude/area-restrita-digitalizar-requer-distribuicao.md), [tramitação](claude/area-restrita-tramitar-flow.md), [restrição CCD→gabinete](claude/ccd-tramitacao-gabinete-bloqueada.md), [e-Contas](claude/econtas-api-migracao.md), [defasagem do banco](claude/read-db-lags-area-restrita.md), [Web PKI](claude/webpki-playwright-assinatura.md) |
| Nereu | [Baixa e arquivamento](claude/nereu-baixa-arquivamento.md), [desconto em folha](claude/nereu-desconto-folha-progresso.md), [auditoria das verbas de saúde](claude/nereu-ms-auditoria-verbas-saude.md), [histórico de envios](claude/nereu-ms-envio-progresso.md) |
| CGAD e benefícios | [Duplicação de finais órfãos](claude/cgad-stage2-dedup-orphan-finals.md), [Cancelado nulo](claude/cgad-cancelado-mostly-null.md), [obrigações curadas](claude/monitoramento-obrigacoes-curadas.md), [SisBenefícios](claude/sisbeneficios-ccd.md) |
| Ambiente e aplicação | [Consolidação web](claude/web-consolidacao-ccd.md), [workspace uv](claude/web-uv-workspace-all-packages.md), [LLM SERPRO](claude/azure-llm-v1-endpoint-gpt41.md), [instalação editável](claude/repo-moved-stale-editable-install.md), [incidente GitNexus](claude/gitnexus-index-quebrado.md) |
| Implantação e infraestrutura | [Host](claude/deploy-host-var-disk-tight.md), [migrações e configuração](claude/github-deploy-secrets-empty.md), [worker/CIFS](claude/worker-arq-cifs-fragility.md), [TLS corporativo](claude/node-fetch-tls-corporate-mitm.md), [SSH](claude/github-ssh-port-22-blocked.md) |
| Carteira e auditoria financeira | [IPSAS](claude/ipsas-carteira-ccd.md), [relatório da carteira](claude/relatorio-auditoria-financeira-ccd.md), [multa cominatória](claude/multa-cominatoria-liquidacao-ccd.md) |

Os demais tópicos e casos individuais permanecem acessíveis pelo índice completo.

## Divergências resolvidas na integração

- **Pastas de processos:** prevalece `processos/<grupo>/<numero_ano>/`, com abertura “Trata-se de...”, fontes explícitas e preservação de versão, conforme orientação do usuário em 09/09/2026. Exemplos antigos em `processos/<numero_ano>/` não mudam essa regra para peças novas.
- **Auth:** o código atual em `web/backend/app/auth/models.py` mapeia `Usuarios` e `TokensRenovacao`. A menção a tabelas `FRAPUsuario`/`FRAPRefreshToken` no manual antigo do backend está superada.
- **Consolidação:** o resumo de `MEMORY.md` ainda apresenta fases da web como pendentes, mas o corpo de `web-consolidacao-ccd.md` registra sua conclusão. Datas, contagens, falhas e pendências da nota permanecem históricas; não foram reexecutados os trabalhos.
- **Testes:** a CI da raiz contém Ruff e mypy; existem testes em `web/backend/tests/` e scripts de teste no frontend. “Sem suíte de testes” não descreve toda a aplicação.
- **Tramitação:** o registro de migração para e-Contas convive com relatos posteriores de uso da Área Restrita. Não foi eleita uma dessas memórias como prova de exclusividade do sistema atual. Consulte a integração existente e o estado ao vivo na tarefa autorizada.
- **GitNexus:** a memória de incompatibilidade de versões não remove a obrigação de tentar `impact` antes de editar símbolos e `detect_changes` antes de commit. Falhas devem ser relatadas, sem atribuir resultado de ferramenta a uma análise manual.
- **Skills e hooks:** os exemplos antigos `.Codex/skills/` e “AGENTS.md / AGENTS.md” são erros de adaptação. Use `.agents/skills/`; a reanálise GitNexus pode gerar `CLAUDE.md` e `AGENTS.md`. Um hook documentado para Claude não comprova sua instalação no Codex.
- **Windows:** exemplos antigos de `Start-Process` com janela minimizada devem ser adaptados para `-WindowStyle Hidden`, conforme as instruções atuais. Diagnóstico de processos órfãos não autoriza encerrar processos alheios à tarefa.
- **Validação de citações:** busca de prefixo normalizado é uma proteção de pipeline descrita na memória; para transcrição jurídica literal, confira o trecho completo no documento original.
- **Dados financeiros e jurídicos:** estimativas de carteira, tetos de multa e conclusões sobre processos nas notas são datados. A importação não recalculou valores nem verificou alterações legais ou decisões posteriores.

## Proveniência e manutenção

Fontes das cópias locais:

- `~/.claude/projects/C--Users-05911205424-Dev-ccd/memory/*.md`;
- `~/.claude/projects/C--Users-05911205424-Documents-Dev-ccd/memory/project_decisoes_etl_extracted.md`.

As fontes do Claude foram preservadas. Não foram importados históricos de conversa, credenciais, permissões locais, índices binários, configurações de hooks nem cópias de worktrees. O índice copiado recebeu somente o cabeçalho de contexto, o link da skill ajustado para o repositório e a entrada da memória do caminho antigo; as notas de assunto foram mantidas integralmente.

A organização por `AGENTS.md` e instruções de subdiretório segue a [documentação oficial de instruções do Codex](https://learn.chatgpt.com/docs/agent-configuration/agents-md). Esta integração é local ao projeto e não altera a configuração global do Codex.
