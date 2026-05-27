# Wiki CCD — manual operacional

Cofre Obsidian que funciona como **segundo cérebro da Coordenadoria de Controle de Decisões (CCD)** do TCE-RN. Segue o padrão **[[llm-wiki]]**: o LLM lê fontes brutas e **constrói e mantém incrementalmente** uma wiki interligada de markdown. Você (humano) cura fontes e faz perguntas; o LLM escreve e mantém as páginas, os cruzamentos e os índices.

> **Idioma:** todo conteúdo voltado ao usuário é em **pt-BR**. Preserve verbatim os termos de domínio: `numero_processo/ano_processo`, `setor`, `Ata_Informacao`, `Pro_ProcessoEvento`, `Exe_Debito`, `Processo_TransitoJulgado`, `CIP`, `DAP`, `PGE`, `nereu`, `trânsito em julgado`, `multa`, `ressarcimento`, `débito`, `sobrestamento`.

## As três camadas

1. **`raw/`** — fontes curadas, **imutáveis**. O LLM lê, **nunca** modifica. Fonte da verdade. Hoje: `raw/leis/` (legislação que interessa à CCD) e `raw/informacoes/` (despachos/processos produzidos no setor).
2. **`wiki/`** — páginas markdown geradas pelo LLM. Resumos, normas, conceitos, processos, pessoas, um catálogo (`index.md`) e um log (`log.md`). O LLM é dono total desta camada.
3. **Schema** — este arquivo. Ensina o LLM a manter a wiki. Co-evolui com o uso.

## Estrutura da `wiki/`

| Pasta/arquivo | Papel |
|---|---|
| `wiki/index.md` | **Catálogo** — toda página listada com link + resumo de 1 linha + metadados, por categoria. Atualizar a cada ingest. |
| `wiki/log.md` | **Cronológico, append-only** — `## [AAAA-MM-DD] ingest \| <fonte>`, queries e lints. |
| `wiki/leis/` | 1 página por norma (lei, lei complementar, resolução, regimento, regulamento). |
| `wiki/conceitos/` | Páginas de conceito CCD — nós **definicionais**; as normas e fontes chegam por backlink. |
| `wiki/processos/` | 1 página por processo (`numero_processo/ano_processo`). *(passadas futuras)* |
| `wiki/relatores/` | 1 página por relator/conselheiro/pessoa. *(passadas futuras)* |
| `wiki/informacoes/` | Resumos das informações/despachos produzidos no setor. *(passadas futuras)* |

Pastas agrupam para navegar; **links agrupam por significado**. Uma nota vive em UMA pasta, mas linka a MUITAS.

## Tipos de nota e frontmatter

**Global (toda nota):** `date` (AAAA-MM-DD), `description` (~150 caracteres), `tags`.

| Tipo | Pasta | `tags` | Campos extras | Seções típicas |
|---|---|---|---|---|
| Lei/Norma | `leis/` | `lei` | `tipo`, `numero`, `ano`, `orgao`, `ementa`, `status` (vigente/alterada/revogada) | Identificação · Ementa · Dispositivos relevantes p/ CCD · Conceitos relacionados · Fonte · Relacionados |
| Conceito CCD | `conceitos/` | `conceito` | `aliases` (opcional) | Definição · Base normativa · Relacionados |
| Processo | `processos/` | `processo` | `numero_processo`, `ano_processo`, `relator`, `situacao` | Resumo · Histórico · Decisão · Relacionados |
| Relator/Pessoa | `relatores/` | `relator` | `cargo` | Atuação · Processos · Relacionados |
| Informação/Despacho | `informacoes/` | `informacao` | `numero_processo`, `ano_processo`, `tipo_doc`, `data_doc` | Contexto · Conteúdo · Fundamentação · Relacionados |

- **Fonte:** páginas derivadas de `raw/` apontam para o arquivo de origem com link relativo, ex.: `[Resolução 13/2015 (PDF)](../../raw/leis/Resolução_0132015_...pdf)`.
- Datas relativas viram **absolutas** (hoje é 2026-05-27).

## Operações

### Ingest
Ao processar uma fonte de `raw/`:
1. Ler a fonte (a ferramenta **Read** lê PDF nativamente; PDFs grandes em blocos via `pages`).
2. Identificar a fonte e extrair o que interessa à CCD.
3. Criar/atualizar a página correspondente em `wiki/`; criar/atualizar as páginas de **conceito** que ela toca.
4. **Linkar** (ver abaixo) — bidirecional entre fonte e conceitos.
5. Atualizar `wiki/index.md` e anexar entrada em `wiki/log.md`.
6. Buscar duplicatas/relacionados antes de criar páginas novas.

### Query
Ao responder perguntas: ler `index.md` primeiro para achar páginas relevantes, depois aprofundar. **Boas respostas viram páginas** (uma comparação, uma síntese) — file de volta na wiki, não deixe sumir no chat.

### Lint
Periodicamente, checar saúde: contradições entre páginas, afirmações superadas por fontes novas, **órfãos** (sem links de entrada), conceitos citados sem página própria, cruzamentos faltando.

## Linking — isto é crítico

- **Graph-first.** **Toda nota deve linkar ≥1 outra nota. Nota sem link é um bug.** Após escrever o conteúdo, a 1ª coisa é adicionar `[[wikilinks]]`.
- **Atomicidade:** se uma nota tem 3+ seções independentes que não precisam uma da outra, divida em notas atômicas que se linkam.
- **Nós de conceito** ficam definicionais; recebem evidência por **backlink** das normas/processos.
- Sintaxe: `[[Título]]`, `[[Título|texto exibido]]`, `[[Título#Seção]]`, `![[Título]]` (embed).

## Busca

1. **qmd** (busca semântica) — **instalado**. Índice `ccd-wiki` (store em `~/.cache/qmd/ccd-wiki.sqlite`), com a coleção `ccd-wiki` escopada a `vault/wiki/` (`**/*.md`). Use **proativamente** antes de ler arquivos e antes de criar notas (checar duplicatas):
   - `qmd --index ccd-wiki query "<termo>"` — híbrida com rerank (recomendada); `search` (BM25) e `vsearch` (vetorial) como alternativas.
   - `qmd --index ccd-wiki get qmd://ccd-wiki/<caminho>.md` — abrir um documento.
   - Após criar/editar páginas: `qmd --index ccd-wiki update` (reindexa BM25) e `qmd --index ccd-wiki embed` (atualiza vetores).
   - Rodar a partir da raiz `ccd` (onde o Claude Code abre). O MCP (`mcp__qmd__*`) não está registrado; uso por CLI.
   - **Rede do TCE intercepta TLS** — se um comando qmd que baixa modelo falhar com `fetch failed` / `SELF_SIGNED_CERT_IN_CHAIN` (ex.: 1º `query` baixa o reranker ~1,28 GB), prefixe com a CA do Windows já exportada: `NODE_EXTRA_CA_CERTS="C:/Users/05911205424/.qmd-ca-bundle.pem" qmd ...`. O modelo de embeddings (~333 MB) já está em cache em `~/.cache/qmd/models/`.
2. **Grep / Glob / Read** — fallback sobre o markdown da `wiki/`.

## Skills Obsidian

Disponíveis via Skill tool (instaladas em `ccd/.claude/skills/`). Carregue-as antes do trabalho relevante:
- **obsidian-markdown** — wikilinks, embeds, callouts, properties. Prefira `[[wikilinks]]` a links markdown.
- **obsidian-bases** / **json-canvas** — visões `.base` e canvases `.canvas` (opcional).
- **obsidian-cli** — operações no cofre quando o Obsidian está aberto (senão, use o filesystem).
- **defuddle** — extrair markdown de páginas web (requer CLI; não instalado).

## Regras

- **Nunca** alterar `raw/` (fonte da verdade) nem `.obsidian/` (config do Obsidian) sem pedido explícito.
- Preserve frontmatter ao editar; toda nota tem `description` (~150 chars).
- Sempre sugira conexões entre notas; verifique órfãos após sessões substanciais.
- Zero perda de dados: ao reorganizar, mova (não delete sem confirmação).
- Versionamento da wiki é decisão do usuário (a wiki é um repo git de markdown). Não auto-commitar.
