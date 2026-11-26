# Manual do sistema

Documento de apoio para quem assume a manutenção técnica das ferramentas da CCD: o repositório `ccd`, a webapp (CCD + CGAD + FRAP + Wiki) e os scripts de geração e envio de informações. Pressupõe familiaridade com Python, git e Docker.

Este manual não contém senhas, CPFs nem dados de processo. Os valores ficam nos arquivos `.env`, que não entram no git.

## 1. Mapa do repositório

| Pasta | O que é | Onde roda |
|---|---|---|
| `ccd/` | Pacote Python: banco, PDF, geração de `.docx`, sessão no e-Contas e na Área Restrita, cliente de LLM. | Máquina do servidor. |
| `processos/` | Informações e despachos: `utils/` (geradores de lote), `projetos/<lote>/`, `informacoes/<numero_ano>/` (avulsos, fora do git), `modelos/` (templates). | Máquina do servidor. |
| `scripts/` | Notebooks de análise, automações (`automacao/`) e consultas SQL antigas (`consultas/`). | Máquina do servidor. |
| `web/` | Webapp: `backend/` (FastAPI), `frontend/` (Next.js), `tools/frap` e `tools/cgad` (pipelines). | Host de produção, em Docker. |
| `docs/runbooks/` | Passo a passo de envio de informações, antecedentes e exclusão de suspensão. | Leitura. |
| `docs/notas/` | Relatórios e análises. | Leitura. |

O arquivo `CLAUDE.md`, na raiz, descreve cada módulo do pacote `ccd` e as convenções de código. Leia-o antes de alterar qualquer coisa.

## 2. Montar o ambiente

**Raiz do repositório** (pacote `ccd`, scripts e notebooks), Python 3.12:

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install -e .
```

Se o repositório mudar de pasta, repita o `pip install -e .`: a instalação guarda o caminho absoluto, e `import ccd` passa a falhar fora da raiz.

**Webapp** (`web/` é um workspace do `uv`):

```
cd web
uv sync --all-packages
cd frontend && pnpm install
```

Use sempre `uv sync --all-packages`. O `uv sync` simples, na raiz de `web/`, desinstala os pacotes do backend.

**Arquivos `.env`** (`scripts/.env` para a raiz, `web/.env` para a webapp). Chaves esperadas:

- `SQL_SERVER_HOST`, `SQL_SERVER_PORT`, `SQL_SERVER_USER`, `SQL_SERVER_PASS`: banco MSSQL. O host é IP e porta, não instância nomeada.
- `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `OPENAI_API_VERSION`: Azure AI Foundry do SERPRO.
- `AR_USER`, `AR_PASS` (e, se diferentes, `ECONTAS_USER`, `ECONTAS_PASS`): credenciais **pessoais** de quem opera o e-Contas e a Área Restrita.
- `SHARE_USER`, `SHARE_PASS`, `SHARE_DOMAIN`: compartilhamento de PDFs das informações.
- `CPF_<CHAVE>`: CPFs usados por scripts, lidos por `ccd.config.cpf()`.

**Subir a webapp local**: `start-web.bat`, na raiz. Abre backend (porta 8000), worker e frontend (porta 3000). Exige o Docker Desktop aberto, por causa do Redis.

## 3. Deploy

O deploy é automático. Todo push na `main` que altere `web/**` dispara o workflow `.github/workflows/deploy.yml`, executado por um *runner* do GitHub Actions instalado no próprio host de produção.

O workflow:

1. Escreve o `web/.env` de produção a partir de `/home/sudip/.env`, no host. Os *secrets* do repositório no GitHub não são usados.
2. Executa `docker compose -f docker-compose.prod.yml up -d --build`.
3. Confere a saúde em `/api/v1/ccd/health`.

O backend aplica as migrações (`alembic upgrade head`) ao subir.

Pontos de atenção:

- **Migração nova tem de ir para o git no mesmo momento em que é aplicada.** Se o banco de produção tiver uma migração que não está no repositório, todo deploy falha com "Can't locate revision" e o backend fica fora do ar.
- **Deploy manual**: `gh workflow run deploy.yml`.
- **Imagem base** (LibreOffice, ODBC, Tesseract): só é reconstruída quando `web/backend/Dockerfile.base` muda, pelo workflow `build-base.yml`.
- `web/deploy/deploy_remote.py` é o caminho manual antigo, **não usado**. Não rode o `upload`: ele apaga a pasta remota.
- O host é `10.24.0.197` (usuário `sudip`, sem root, só grupo `docker`). O projeto do compose chama-se `frap-controle`; a pasta de trabalho é `~/actions-runner/_work/ccd/ccd/web`.

## 4. Quando quebra

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| Extração do CGAD, conciliação do FRAP ou geração de antecedentes fica "na fila" e não anda. | O container `frap-worker` morreu. Ele depende do compartilhamento de PDFs e não volta sozinho se a montagem falhar na criação. | No host, na pasta de trabalho: `docker compose -f docker-compose.prod.yml up -d worker`. |
| Webapp devolve erro 502. | Backend não subiu, quase sempre por migração (ver seção 3). | `docker logs frap-backend`; conferir `git status web/backend/app/migrations/versions/`. |
| Deploy falha por falta de espaço. | Cache do Docker. | O workflow já limpa antes do build; se persistir, `docker system df` no host. |
| Backend local responde com código antigo. | No Windows, encerrar o `uvicorn --reload` sem `/T` deixa um processo filho segurando a porta. | `taskkill /PID <pid> /T /F`. |
| `ModuleNotFoundError: No module named 'ccd'` em notebook. | Instalação editável apontando para pasta antiga. | `pip install -e .` na raiz. |
| `git push` por SSH não conecta. | Porta 22 bloqueada na rede do Tribunal. | Usar `ssh.github.com`, porta 443. |

## 5. Usuários e permissões

- Usuários ficam na tabela `Usuarios` do BdDIP. A tela **Admin → Usuários** cria, desativa e define o papel (`admin` ou `user`) e a matriz de permissões.
- `admin` vê e edita tudo.
- `user` vê todos os módulos por padrão. Para cada módulo, a matriz permite esconder ("ver" desmarcado) ou liberar a edição ("editar" marcado). Sem marcação, o usuário só visualiza.
- A lista de módulos está em `web/backend/app/permissoes.py` e é espelhada em `web/frontend/src/lib/permissoes.ts`. Módulo novo entra nos dois arquivos.
- Primeiro administrador de um banco vazio: `python -m app.scripts.create_user`, dentro do container do backend.

## 6. Manter a Wiki

As páginas são arquivos Markdown em `web/backend/wiki/`. Há dois caminhos para alterá-las:

- **Pelo git** (preferido): edite o `.md`, faça commit e push. O deploy publica. O histórico de versões é o do git.
- **Pela tela**: botão "Editar", visível para quem tem a permissão de edição do módulo Wiki. Em produção, o texto salvo fica num volume do Docker (`wiki_edits`), **fora do git e sem backup**, e passa a esconder a versão do repositório. A página ganha a etiqueta "editado na UI".

Reconciliar uma página editada pela tela:

1. Copie o texto da página para o `.md` correspondente no repositório.
2. Faça commit e push; aguarde o deploy.
3. Na página, clique em "Reverter edição".

Enquanto houver etiqueta "editado na UI", alterações feitas no git para aquela página não aparecem em produção.

Página nova:

- Em `procedimentos/`, aparece sozinha na lista de POPs, mas a tabela da [página inicial](index) é manual: acrescente a linha.
- Cada POP segue o modelo dos existentes: tabela de identificação no topo (código, versão, data, próxima revisão) e seção "Histórico de revisões" no fim. Toda alteração de conteúdo sobe a versão e ganha uma linha no histórico.

## 7. Restrições que o código impõe

- **LLM só pelo Azure AI Foundry do SERPRO.** Todo cliente de modelo é construído em `ccd/llm.py` ou em `web/tools/frap/frap/llm.py`, que recusam qualquer outro endereço. O `ruff` (regra `TID251`) rejeita a importação de outras bibliotecas de LLM. Provedor novo se muda no factory, nunca no ponto de uso.
- **Assistente de código não é ferramenta homologada** (Resolução nº 032/2026-TCE, art. 28). Assistentes trabalham só com código, esquemas, caminhos e contagens. Não consultam o banco, não leem `.env` nem pastas de processo, e não agem no e-Contas. O servidor executa os scripts no próprio terminal e não cola a saída na conversa. O arquivo `.claude/settings.json` bloqueia a leitura dessas pastas.
- **SQL novo usa parâmetros nomeados** (`:nome`) com `ccd.db.run_query_df`. Nunca montar consulta com `.format()`.
- **CI**: `ruff check` e `mypy ccd` em todo push.

## 8. Operação no e-Contas

O envio de uma informação (distribuir, cadastrar, assinar, tramitar à DIP) está descrito em `docs/runbooks/enviar-informacao.md`. Os demais fluxos estão na mesma pasta. A Área Restrita antiga só é usada para o que o e-Contas ainda não cobre.

A assinatura exige certificado A3 e a extensão Web PKI; o PIN é digitado por quem assina.

## 9. Acessos a transferir na troca de responsável

Nada desta lista passa junto com o repositório. Conferir item a item:

- [ ] Papel `admin` na webapp para o novo responsável (tela Admin → Usuários).
- [ ] Permissão de edição do módulo Wiki para quem vai manter os POPs.
- [ ] Acesso de escrita ao repositório no GitHub.
- [ ] Chave SSH do novo responsável autorizada no host de produção.
- [ ] Conteúdo de `/home/sudip/.env` no host: o novo responsável sabe onde está e quem renova cada credencial (banco, Azure, compartilhamento).
- [ ] `scripts/.env` e `web/.env` montados na máquina do novo responsável, com as credenciais **dele** em `AR_USER`/`AR_PASS`.
- [ ] Certificado A3 próprio e extensão Web PKI instalada.
- [ ] Lotação no setor CCD no e-Contas (a sessão dos scripts fixa o setor da CCD).
- [ ] Usuário do coordenador anterior desativado na webapp, depois de confirmado o acesso do novo.

## 10. Pendências conhecidas

- Edições da Wiki pela tela não têm histórico nem autor, e o volume não tem backup. Preferir o git.
- A Wiki não aceita imagens nem anexos.
- As datas de "Próxima revisão" dos POPs não têm lembrete automático.
- O container do worker não se recupera sozinho de falha na montagem do compartilhamento de PDFs.
- Dois scripts têm caminho de pasta pessoal fixo: `scripts/analise/planilha_nereu.py` e `web/tools/cgad/scripts/lancar_extracoes_remoto.py`.
- O índice do GitNexus está corrompido; a análise de impacto pedida no `CLAUDE.md` tem de ser feita por busca no código até ele ser refeito (`node .gitnexus/run.cjs analyze`).
