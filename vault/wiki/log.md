---
date: 2026-05-27
description: Log cronológico append-only da wiki CCD — ingests, queries e lints, com prefixo consistente para parsing simples.
tags:
  - log
---

# 🕒 Log da Wiki CCD

Registro append-only. Cada entrada começa com `## [AAAA-MM-DD] <tipo> | <fonte>`. Veja o [[index|índice]] para o catálogo de páginas.

## [2026-05-27] setup | criação do cofre

Estrutura inicial: schema ([[CLAUDE]]), [[Home]], [[index]], [[log]] e esqueleto de `wiki/` (`leis/`, `conceitos/`). Padrão [[llm-wiki]]. Fontes em `raw/leis/` e `raw/informacoes/`.

## [2026-05-27] ingest | raw/leis (7 normas)

Ingeridas as 7 normas de `raw/leis/` → 7 páginas em `wiki/leis/` e 18 páginas de conceito em `wiki/conceitos/`.

- Leis: [[LCE 464-2012 — Lei Orgânica do TCE-RN]], [[Regimento Interno do TCE-RN (Res 009-2012)]], [[Regulamento da SECEX (Res 042-2024)]], [[Resolução 028-2012 — Processo de execução]], [[Resolução 013-2015 — Execução de multas e ressarcimento]], [[Lei 9.492-1997 — Lei do Protesto]], [[Resolução 012-2020 — Provimento da Corregedoria]].
- Conceitos centrais: [[Coordenadoria de Controle de Decisões (CCD)]], [[Execução das decisões do TCE-RN]], [[CGAD — Cadastro Geral de Acompanhamento de Decisões]], [[Trânsito em julgado]], [[Multa]], [[Ressarcimento ao erário (débito)]].
- Achados de domínio: **CCD** é definida no art. 32 do Regulamento da SECEX (Res 42/2024), dentro da **DIP**, ao lado da **CIP** (= Coordenadoria de Instrução Processual, *não* o cadastro de créditos). O **TAG** dos despachos corresponde ao subcadastro CGTAG do CGAD.
- Extração: PDFs lidos via `pypdf` (venv) — a ferramenta Read recusa esses PDFs (protegidos por permissão).

## [2026-05-27] setup | busca qmd instalada e indexada

`@tobilu/qmd` 2.5.2 instalado (após adicionar o workload C++ "VCTools" ao VS Build Tools, necessário para compilar o `better-sqlite3`). Criado o índice `ccd-wiki` com a coleção `ccd-wiki` escopada a `vault/wiki/` (`**/*.md`): **29 documentos** indexados (BM25) + embeddings. Consulta: `qmd --index ccd-wiki query "<termo>"`. Reindexar após edições com `qmd --index ccd-wiki update` / `embed`.

## [2026-05-27] ingest | informações lote 1 (despachos avulsos 2025)

Ingeridos 9 despachos avulsos de `raw/informacoes/despachos/2025/` (extração via `pypdf`/`python-docx` do venv) → tipos **Informação** e **Relator** estabelecidos.

- **9 informações** em `wiki/informacoes/`: 300134/2025, 000475/2024, 10772/2017 (sobrestado), 001541/2024, 002058/2020, 002127/2023, 002843/2025, 004879/2014, 009673/2015.
- **5 relatores** em `wiki/relatores/`: [[George Montenegro Soares]], [[Renato Costa Dias]], [[Paulo Roberto Chaves Alves]], [[Antônio Gilberto de Oliveira Jales]], [[Marco Antônio de Moraes Rêgo Montenegro]].
- **4 conceitos** novos: [[Sobrestamento]], [[Dívida Ativa]], [[Ministério Público de Contas]], [[Diretoria de Expediente (DE)]].
- Norma referenciada e ainda não ingerida: **Resolução 043/2024-TCE** (competência da DE para certificar trânsito em julgado). Restam ~339 arquivos em `raw/informacoes/` (despachos por mês/relator, ~79 sobrestados, 27 pastas de processos).

## [2026-05-27] ingest | raw/leis Resolução 043/2024-TCE

Ingerida a Resolução nº 043/2024-TCE (Regulamento da SEAD) → 1 página em `wiki/leis/`.

- Lei: [[Resolução 043-2024 — Regulamento da Secretaria de Administração (SEAD)]].
- Dispositivo-chave: art. 12, IV — DE competente para expedir certidões, **inclusive de trânsito em julgado**. Art. 15, XIV confirma a atribuição do cargo de Diretor de Expediente.
- Conceito atualizado: [[Diretoria de Expediente (DE)]] agora aponta para a lei ingerida (antes referenciada como "não ingerida").
- 4 novos relatores criados em `wiki/relatores/`: [[Ana Paula de Oliveira Gomes]], [[Antônio Ed Souza Santana]], [[Carlos Thompson Costa Fernandes]], [[Francisco Potiguar Cavalcanti Júnior]].

## [2026-05-27] ingest | informações lote 2 (Agosto-Outubro 2025)

Ingeridos 13 despachos de `raw/informacoes/despachos/2025/Agosto-25/`, `Setembro-25/`, `Outubro-25/` (estruturados por relator) → **12 novas informações** criadas.

- **12 informações** em `wiki/informacoes/`: 003314/2009, 200006/2021, 101410/2022, 200023/2022, 200023/2023, 200049/2023 (Agosto); 008390/2013, 000970/2021, 002013/2024 (Setembro); 000081/2022, 002605/2020, 005310/2017 (Outubro).
- **3 relatores** adicionados: [[Antônio Ed Souza Santana]], [[Francisco Potiguar Cavalcanti Júnior]] (já havia George Montenegro Soares, Marco Antônio de Moraes Rêgo Montenegro, Renato Costa Dias).
- **Padrão observado**: Agosto = 6 encaminhamentos à DE; Setembro = 2 análises + 1 caso especial (prescrição/MPC); Outubro = 2 análises + 1 protesto. Todos os 12 arquivos eram .docx com PDF gêmeo (processados apenas .docx).
- **Termos novos encontrados** (em CAPS): CDD, CPF, DAE, DAM, DAT, DIP, EVARISTO PEIXOTO, FUNDEF, LUCIANO AUGUSTO DA CRUZ, LUIZ ALBERTO BEZERRA FERREIRA DE SOUZA, LUIZ GONZAGA CAVALCANTE DANTAS, MARIA FERNANDA SIMAS ARANHA TEIXEIRA DE CARVALHO, MENINO DOS SANTOS, SIAI, ZENILDO BATISTA DE SOUSA (a maioria pessoas/entidades mencionadas, não termos técnicos novos). Destaque: **DIP** (reconfirma que referência à Diretoria de Instrução Processual); **SIAI** (sistema novo, investigar); **CPF** (pessoa física).
- Estrutura: arquivo → parse nome (`PROC. [Nº]\d+[-–]\d{4}_<ação>`) → relator (pasta) → tipo_doc (ação) → wikilinks (inferidos do texto + mapa de ação). Cada wiki page tem frontmatter com `numero_processo`, `ano_processo`, `relator`, `assunto`, `tipo_doc`, `lote`.

## [2026-05-27] ingest | informações lote 3 (Novembro-Dezembro 2025)

Ingeridos 22 despachos/análises de `raw/informacoes/despachos/2025/Novembro-25/` e `Dezembro-25/`.

- 6 relatores: [[Antônio Ed Souza Santana]], [[Antônio Gilberto de Oliveira Jales]], [[Carlos Thompson Costa Fernandes]], [[Francisco Potiguar Cavalcanti Júnior]], [[Marco Antônio de Moraes Rêgo Montenegro]], [[Paulo Roberto Chaves Alves]].
- Tipos: Envio_DE (12 páginas), Análise do Relator — Protesto, MPC, Quitação da dívida (8 páginas), Análise do MPC/Prescrição (1 página), Encaminhamento à DE (1 página).
- Exemplos: [[000066-2021 — Encaminhamento à DE para certificação de trânsito ]], [[004906-2024 — Análise do Relator]], [[005187-2019 — Análise do Relator]].

## [2026-05-27] ingest | informações lote 4 (despachos 2026, Janeiro–Maio)

Ingeridos 58 despachos de `raw/informacoes/despachos/2026/` (5 meses, 9 relatores).

- Meses: Janeiro-26 (5), Fevereiro-26 (12), Março-26 (15), Abril-26 (25), Maio-26 (1).
- Tipos dominantes: Envio_DE e Análise do Relator (variantes). Mesmo padrão estrutural dos lotes anteriores.
- Exemplos: [[200145-2023 — Encaminhamento à DE para certificação de trânsito ]], [[3003-2021 — Despacho]], [[1454-2024 — Despacho]].

## [2026-05-27] ingest | Processos sobrestados completos (47 páginas, 9 relatores)

Ingeridos 81 arquivos de `raw/informacoes/despachos/2025/Processos sobrestados/` (9 relatores) → **47 análises do relator** criadas em `wiki/informacoes/` (tipo_doc: analise).

- **Ana Paula de Oliveira Gomes** (17 processos): série 100XXX/2019-2021 (ex. [[100074-2019 — Processo nº 100074_2019-TC Relatora]], [[101435-2019 — Processo nº 101435_2019-TC Relatora]]).
- **Antônio Ed Souza Santana** (2), **Antônio Gilberto de Oliveira Jales** (2), **Carlos Thompson Costa Fernandes** (3), **Francisco Potiguar Cavalcanti Júnior** (2), **Marco Antônio de Moraes Rêgo Montenegro** (2), **Renato Costa Dias** (2).
- **George Montenegro Soares** (2): [[002601-2024 — Análise do Relator (sobrestado)]], [[005921-2014 — Análise do Relator (sobrestado)]].
- **Paulo Roberto Chaves Alves** (11): [[010105-2014 — Análise do Relator (sobrestado)]], [[015407-2000 — Análise do Relator (sobrestado)]] e outros (processos 2000–2022).
- Padrão: todos aguardam trânsito em julgado de processo conexo ou decisão judicial superveniente; recomendação recorrente de retorno ao gabinete do relator.

## [2026-05-27] ingest | raw/informacoes/processos (lote 27 pastas)

Ingeridos 27 pastas de processos de `raw/informacoes/processos/` → **25 novas informações** criadas em `wiki/informacoes/`, lote `processos`.

- **25 informações** criadas: 000070/2025, 000084/2021 (sem despacho, pasta só com leis), 000411/2025, 001827/2010, 002019/2025, 002177/2018, 003110/2025, 003366/2024, 003404/2020, 003525/2024, 003713/2022, 003966/2025, 004340/2019, 004424/2020, 004777/2024, 004916/2024, 005303/2017, 006552/2019, 008182/2018, 012970/2017, 014479/2016, 017663/2017, 019336/2017, 021694/2016, 200016/2021.
- **2 puladas**: 000475/2024 (já tinha página wiki), 003314/2009 (página wiki já existe).
- **Extração**: via `python-docx` (venv); documentos primários identificados por padrão (NNNNNN_YYYY.docx, despacho_*.docx, etc.). Cada página recebe frontmatter com `numero_processo`, `ano_processo`, `tipo_doc: informacao`, `lote: "processos"`, `relator` e `interessado` quando extraídos do texto.
- **Estrutura**: cada pasta = 1 processo; documento principal extraído para texto, parsed para `assunto`, `relator`, `interessado`, `data_doc` (quando presente); summary de 300–400 chars do início do documento.
- **Achado**: 000084/2021 contém apenas referências legais (pasta `Leis/`) — página criada com referência mínima, conforme protocolo.
- **Index atualizado** com todas as 25 páginas em nova seção "Lote processos".

**Próximas etapas:** reindexação qmd (`update` + `embed` para o corpus novo), lint de órfãos e conceitos não capturados.

- **George Montenegro Soares** (2 processos): 002601/2024, 005921/2014. Padrão: sobrestamento vinculado a decisão judicial superveniente; recomendação de retorno ao gabinete e pronuciamento da Consultoria Jurídica.
- **Paulo Roberto Chaves Alves** (11 processos): 010105/2014, 001369/2021, 015407/2000, 001707/2022, 002701/2022, 004063/2000, 004173/2000, 004391/2007, 005919/2014, 006791/2014, 007692/2000. Variações: 2 processos com decisão judicial pendente (001707/2022, 002701/2022 ligado a processo DAP 13883/2017-TC); demais com padrão similar ao de George.
- **Conceitos reforçados**: [[Sobrestamento]] (processo aguardando evento externo), [[Consultoria Jurídica]] (recomendação frequente), [[Diretoria de Expediente (DE)]] (notificações), [[DAP]] (Diretoria de Registro de Atos de Pessoal).
- **Fontes**: .docx extratos com pypdf/docx (os PDFs gêmeos descartados). Estrutura de nomes normalizada e campos de frontmatter consistentes (data_doc, tipo_doc, lote).
