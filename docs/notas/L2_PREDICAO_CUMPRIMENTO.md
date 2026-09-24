# L2 — Predição de cumprimento de decisões do TCE/RN: formulação e engenharia de features

> Relatório dedicado à linha L2 de [LINHAS_DE_PESQUISA.md](LINHAS_DE_PESQUISA.md).
> Organiza a formulação do problema, a taxonomia de features (incluindo as apontadas pelo
> pesquisador: natureza do processo, elementos do relatório de auditoria, metafeatures de
> órgão/responsável) e as features adicionais sugeridas pela literatura análoga.
> Toda coluna/tabela citada foi conferida nos SQLs e dicionários deste repositório.
> Gerado em 16/07/2026.

---

## 1. Formulação do problema

### 1.1 Unidade de análise

**Principal: o par débito-pessoa** (`Exe_Debito ⨝ Exe_DebitoPessoa`, só débitos-raiz `IdDebitoAnterior IS NULL`). É a unidade com desfecho objetivo e datas completas. **Secundária: a obrigação** (`BdDIP.dbo.Obrigacao`, com `DataCumprimento`), quando o alvo for cumprimento de determinações de fazer/não fazer — dados mais novos e desfecho menos preenchido; tratar como estudo complementar.

### 1.2 Instante de predição (t₀)

**t₀ = trânsito em julgado** (`Exe_Debito.dataTransito`). É o momento em que a dívida se torna exigível e em que um sistema de *early warning* seria de fato usado pela CCD. Regra de ouro: **nenhuma feature pode usar informação posterior a t₀** (exceto no cenário dinâmico da §6.4).

### 1.3 Targets

| Target | Tipo | Fonte |
|--------|------|-------|
| **T1 — Desfecho da dívida** (multiclasse): pago espontâneo / parcelado / desconto em folha / protestado / ajuizado (PGE) / prescrito-cancelado / em aberto | Classificação | `CodigoStatusDivida` (dom. `Exe_StatusDivida`), `StatusProtesto` (dom. `Exe_StatusProtesto`), `Status_PGE` (dom. `PGE_StatusProcesso`), `dataBaixa`+`TipodeBaixa` (=1 pagamento de boleto), `Exe_Parcelamento.SituacaoParcelamento` (1=aguardando, 2=em curso, 3=cancelado, 4=quitado, 5=cancelado por inadimplência — domínio inferido em `web/backend/app/ccd/alertas/service.py:32-41`) |
| **T2 — Tempo até pagamento/baixa** (com censura à direita para dívidas abertas) | Sobrevivência | `dataTransito` → `dataBaixa` |
| **T3 — Fração recuperada** | Regressão | `ValorPago / ValorAPagar` (colunas em `web/tools/frap/frap/processo/repos.py:27-29`) |
| **T4 — Cumprimento de obrigação** (binário) | Classificação | `Obrigacao.DataCumprimento` (BdDIP) |

Decisões de projeto: T1 binarizado (recuperou algo em N meses: sim/não) é o começo mais robusto; T2 é a versão de artigo mais forte (evita arbitrariedade do horizonte); a hierarquia de status precisa de regra determinística de precedência (ex.: pago > parcelado em curso > protestado > PGE > prescrito) documentada no paper.

---

## 2. Heterogeneidade das naturezas de processo

O ponto levantado é real e a literatura confirma: tipo de caso é o maior correlato de complexidade e desfecho ([Predicting civil litigation outcomes, arXiv:2605.06151](https://arxiv.org/html/2605.06151)). Uma multa de prestação de contas de prefeitura, um ressarcimento de aposentadoria irregular (caso Nereu) e uma sanção de auditoria operacional têm dinâmicas de cumprimento incomparáveis.

**Fonte do tipo**: `Processos.codigo_tipo_processo` → `dbo.Tipo.descricao` (join pronto em `web/backend/app/ccd/service.py:87-101`); domínio observado no repo: REP, MON, AUD, APR (`scripts/analise/crivo_monitoramento.py:24-53`); `assunto` (texto livre) complementa.

**Estratégia recomendada (em três passos):**
1. **Fatia homogênea primeiro** — treinar e validar o modelo inicial só com multas de processos de fiscalização (AUD/REP/APR), excluindo os temas de massa (aposentadorias/Nereu), que distorceriam qualquer agregado. Publicável por si só e elimina o principal *confounder*.
2. **Tipo como feature + interações** — no modelo geral, `tipo_processo` entra como categórica; GBMs capturam interações automaticamente. Reportar métricas **desagregadas por tipo** (nunca só a média global).
3. **Modelos por estrato só se a ablação justificar** — se o desempenho desagregado divergir muito, um modelo por família de tipo; caso contrário é complexidade desnecessária.

---

## 3. Taxonomia de features — 6 blocos

Organização proposta: cada bloco tem dono de dado claro, pode ser construído/ablacionado de forma independente, e o **ganho incremental por bloco é o resultado científico do paper** (§6).

### Bloco A — A decisão (já extraído pelo CGAD)

| Feature | Fonte |
|---|---|
| Tipo de dispositivo (multa / ressarcimento / obrigação / recomendação) | `NERDecisao` + filhas (BdDIP) |
| Valor da sanção (fixo, percentual, base de cálculo, valor imputado) | `schema.py`: `Multa.valor_fixo/percentual/base_calculo`, `Ressarcimento.valor_dano/valor_imputado` |
| Prazo explícito no dispositivo (existe? quantos dias?) | `Obrigacao.prazo` |
| Multa cominatória (existe, valor, periodicidade) | `Obrigacao.valor_multa_cominatoria`, `periodo_multa_cominatoria` |
| Solidariedade (nº de solidários — diluição de responsabilidade) | `e_multa_solidaria`, `solidarios[]` |
| Embeddings do texto decisório (fundamentação, conclusão, ementa) | `vw_ia_votos_acordaos_decisoes` |

### Bloco B — O processo

| Feature | Fonte |
|---|---|
| Tipo do processo (§2) | `codigo_tipo_processo` → `Tipo.descricao` |
| Assunto (categorizado ou embedding) | `Processos.assunto` |
| Relator (identidade + metafeature de rigor, §5) | `codigo_relator` → `dbo.Relator` |
| Monocrática vs colegiada; voto divergente | `monocratica`, `isVotoDivergente` na view de IA |
| Duração até a decisão (autuação → sessão) e até o trânsito (sessão → `dataTransito`) | `Processos` + view + `Exe_Debito` |
| Complexidade: nº de eventos de tramitação, nº de débitos no mesmo processo, nº de responsáveis | `Pro_ProcessoEvento`, `Exe_Debito`, `Pro_ProcessosResponsavelDespesa` |

### Bloco C — O relatório de auditoria (a lacuna: exige extração LLM nova)

Único bloco **sem dado estruturado hoje**. Os relatórios existem como PDFs no share `Informacoes_PDF`, localizáveis por `vw_ata_informacao.setor` ∈ {DAI, DAD, DAM, DCD, DCC} (+ prefixos GAB/PROC), caminho montado por `ccd/processo.py` (`get_info_file_path`). A proposta é um **"stage-0"** espelhando a arquitetura do CGAD (schema Pydantic + few-shot + staging de revisão humana — reusar `web/tools/cgad/cgad/` como molde):

| Campo a extrair | Justificativa |
|---|---|
| `tipo_auditoria` (conformidade / operacional / financeira / inspeção) | Citado pelo pesquisador; correlato de gravidade |
| `materialidade_auditada` (R$ do escopo) e `materialidade_irregular` (R$ com achado) | A razão irregular/auditado é a feature de Ferraz & Finan (§4.2) |
| `num_achados`, `gravidade_achados` (escala) | Complexidade/severidade |
| `tipologia_achados` (desvio/superfaturamento vs falha formal vs licitação vs pessoal) | Corrupção vs má gestão têm cumprimento distinto (§4.2) |
| `houve_defesa`, `defesa_acatada_parcialmente` | Sinal de engajamento do responsável — preditor de pagamento |

Esse stage-0 é um artigo em si (extensão do dataset da L1) além de alimentar a L2.

### Bloco D — O órgão (cadastrais + metafeatures)

Cadastrais: natureza (`Anexo42_UnidadeJurisdicionada.IdNaturezaUnidade` → `Anexo42_NaturezaUnidade`), tipo de administração (`IdTipoAdministracaoUnidade`), esfera e poder (`vw_Gen_UnidadeJurisdicionada.Esfera`, `TipoOrgaoNatureza`; `Anexo07_Poderes`), porte fiscal (despesa anual via `BdDIP.dbo.vwDespesaPagamento`: `valor`, `data`, `id_orgao`, `funcao/subfuncao`).

Metafeatures (point-in-time, ver §5): nº de sanções anteriores a t₀, valor acumulado sancionado, taxa histórica de pagamento do órgão, nº de processos abertos — todas via `Exe_Debito ⨝ Processos.IdOrgaoEnvolvido` com filtro `dataTransito < t₀`, ou pelo star schema `Fato_Debito ⨝ Dim_Tempo ⨝ Dim_Orgao ⨝ Dim_StatusDivida` (BdDIP, ~48,7 mil fatos).

### Bloco E — O responsável (cadastrais + metafeatures)

Cadastrais: pessoa física vs jurídica (`GenPessoa.TipoPessoa`), papel no processo (`Pro_ProcessosResponsavelDespesa.TipoResponsavel`), cargo (`Anexo42_ResponsavelUnidade.Cargo`).

Derivadas de vigência — provavelmente as mais fortes do bloco:
- **"Ainda é gestor em t₀?"** — `DataInicioGestao ≤ t₀ ≤ DataTerminoGestao` (query pronta em `web/tools/cgad/sql/responsible_unit.sql`). Ex-gestor tem incentivo e mecanismo de cobrança muito diferentes.
- **É servidor ativo** (elegível a desconto em folha) — BdSIAIPessoal / fluxo `desconto_folha`.

Metafeatures (point-in-time): reincidência (nº de débitos anteriores via `Exe_DebitoPessoa`, chaveado por `GenPessoa.Documento` — usar CPF, não nome, pela lição anti-homônimo de `gerar_antecedentes.py`), taxa de pagamento histórica da pessoa, valor acumulado devido.

### Bloco F — Contexto de execução/cobrança em t₀

Histórico de interação: nº de citações do responsável (`Cit_Citacoes`), **respondeu citação no prazo** (`DataInicioContagem`/`DataFinalResposta` — proxy comportamental direto de engajamento), parcelamentos anteriores e como terminaram (`Exe_Parcelamento`), notificações de desconto em folha (`FRAPNotificacaoDescontoFolha`, BdDIP).

---

## 4. Features adicionais sugeridas pela literatura análoga

Pesquisa feita em quatro domínios com problemas estruturalmente idênticos (prever se um devedor/sancionado cumprirá). Além de fonte de features, são as literaturas com que o paper deve dialogar.

### 4.1 Cobrança e risco de crédito (debt collection ML)

O problema T1/T3 **é** um problema de *collections scoring*. A literatura ([Predicting Account Receivables with ML, arXiv:2008.07363](https://arxiv.org/pdf/2008.07363); [modelo de regras para recebíveis em massa, MDPI 2024](https://www.mdpi.com/2071-1050/16/14/5885)) usa consistentemente:

| Feature | Tradução para o TCE | Fonte no repo |
|---|---|---|
| Idade/vintage do débito | `dataAto` → `dataTransito` → t₀ (quanto mais velho o fato, menor a recuperação; conexão direta com prescrição) | `Exe_Debito.dataAto`, `dataTransito` |
| Valor ÷ capacidade de pagamento | débito ÷ despesa anual do órgão; para PF servidor, débito ÷ remuneração | `vwDespesaPagamento`; BdSIAIPessoal (folha) |
| Comportamento de pagamento prévio | já pagou parcialmente? aderiu e honrou parcelamento antes? | `ValorPago`, `Exe_Parcelamento` |
| Intensidade de contato/cobrança | nº de citações/notificações e resposta no prazo | `Cit_Citacoes`, `FRAPNotificacaoDescontoFolha` |
| Canal de cobrança disponível | elegibilidade a desconto em folha (servidor ativo) | fluxo `desconto_folha` |

### 4.2 Economia política de auditorias municipais brasileiras

A literatura mais próxima do domínio — e invisível para quem só lê legal NLP. [Ferraz & Finan (2008, QJE)](https://eml.berkeley.edu/~ffinan/Finan_Audit.pdf) e [Ferraz & Finan (2011, AER)](https://www.aeaweb.org/articles?id=10.1257%2Faer.101.4.1274) mostram, com as auditorias sorteadas da CGU, que **ciclo eleitoral e incentivo de reeleição mudam o comportamento do gestor** (27% menos desvio quando pode ser reeleito); [Avis, Ferraz & Finan (2018, JPE)](https://www.nber.org/system/files/working_papers/w22443/w22443.pdf) medem o efeito dissuasório das auditorias. Features derivadas:

- **Ano eleitoral**: decisão/trânsito em ano de eleição municipal ou estadual (calendário público — dado externo trivial).
- **Situação de mandato do gestor em t₀**: 1º mandato (reelegível) vs 2º; ainda no cargo vs ex-gestor (`DataInicioGestao`/`DataTerminoGestao`).
- **Materialidade relativa**: % dos recursos auditados com irregularidade (Ferraz & Finan usam exatamente essa razão) — vem do Bloco C.
- **Tipologia do achado**: desvio/corrupção vs falha formal/má gestão — a natureza da irregularidade prediz tanto punição eleitoral quanto, plausivelmente, disposição a pagar — vem do Bloco C.
- **Dependência de transferências / porte do município** (FPM, população, receita própria) — dado externo (IBGE/STN/Siconfi), enriquecimento por CNPJ/nome do ente.

### 4.3 Legal judgment prediction e litígio civil

Do [survey de LJP (Cui et al. 2022, arXiv:2204.04859)](https://arxiv.org/pdf/2204.04859) e de [arXiv:2605.06151](https://arxiv.org/pdf/2605.06151): além do texto, os modelos fortes usam **identidade e histórico do julgador** e **complexidade do caso**:

- **Metafeature de rigor do relator**: taxa histórica de sanção/valor médio sancionado pelo relator antes de t₀ (mesmo protocolo point-in-time da §5).
- Monocrática vs colegiada; existência de voto divergente (`isVotoDivergente`) — proxies de contenciosidade que preveem recurso.
- **Litigiosidade pós-decisão como risco**: interposição de recurso/MS suspende a cobrança (o caso Nereu — MS TJRN sobrestando ~90 execuções — é o exemplo concreto no repo). Em t₀ estrito isso é target, não feature; entra no cenário dinâmico (§6.4).
- Complexidade: nº de partes/solidários, nº de débitos do processo, volume de eventos, tamanho do relatório.

### 4.4 Reincidência e compliance tributário

A abordagem proposta pelo pesquisador — **categorizar órgãos/responsáveis por contagem de sanções** — é exatamente o *prior counts* da literatura de reincidência criminal e os históricos de compliance dos modelos tributários (Random Forest com 92–93% de acurácia em risco de compliance fiscal — [estudo comparativo, PMC 2025](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12483221/)). Valida a ideia e adiciona: **setor/função da despesa** irregular (`funcao`/`subfuncao` em `vwDespesaPagamento`) como categórica — saúde, educação e obras têm perfis de irregularidade e cobrança distintos.

---

## 5. Metafeatures de órgão/responsável sem vazamento (o cuidado central)

A intuição de "quantidade de sanções por órgão/responsável para categorizá-los" é o caminho certo — é *count/frequency encoding* de categóricas de alta cardinalidade. Três regras para ela não destruir a validade do estudo:

1. **Point-in-time sempre**: toda agregação usa só eventos com data **anterior ao t₀ do caso específico** (`dataTransito < t₀`, `dataAto < t₀`). Uma coluna "total de sanções do órgão" calculada sobre a tabela inteira embute o futuro — este é o erro nº 1 da área ([Kaufman et al. 2012, *Leakage in Data Mining*, TKDD](https://dl.acm.org/doi/10.1145/2382577.2382579)). O star schema `Fato_Debito ⨝ Dim_Tempo` já dá o corte temporal de graça.
2. **Contagens puras primeiro, desfechos depois**: contar *sanções* é seguro; agregar *desfechos* ("taxa de pagamento histórica do órgão") é target encoding — mais poderoso e mais perigoso. Quando usar, aplicar smoothing bayesiano ([Micci-Barreca 2001, SIGKDD Explorations](https://dl.acm.org/doi/10.1145/507533.507538)) e calcular dentro de validação cruzada **temporal** (nunca no dataset completo).
3. **Entidades raras**: órgão/pessoa com 1–2 sanções históricas produz agregados ruidosos — agrupar em *bucket* "histórico insuficiente" em vez de imputar zero (zero sanções ≠ sem histórico).

Caminho de evolução (do relatório geral, agora concreto): contagens point-in-time → target encoding com CV temporal → embeddings de entidade aprendidos. Para o primeiro artigo, o passo 1 basta e é defensável.

---

## 6. Desenho experimental

1. **Split temporal**, nunca aleatório: treino com trânsitos até T, teste com trânsitos depois de T (a crítica de Medvedeva et al. 2020 à área de LJP se aplica integralmente).
2. **Ablação por bloco = o resultado do paper**: baseline trivial (classe majoritária + valor do débito) → +A → +B → +D/E cadastrais → +metafeatures → +C (auditoria) → +texto (embeddings). A curva de ganho incremental responde à pergunta científica: *o que prediz cumprimento — o dispositivo, o histórico ou o contexto?* O Bloco C entra por último de propósito: seu ganho incremental justifica (ou não) o custo do stage-0.
3. **Modelos**: GBM (XGBoost/CatBoost — CatBoost trata categóricas de alta cardinalidade nativamente com ordered target statistics, alinhado à §5) para o tabular; fusão tardia com embeddings do texto. Deep tabular só se superar GBM — em tabular tipicamente não supera ([Grinsztajn et al. 2022, NeurIPS](https://arxiv.org/abs/2207.08815)).
4. **Cenário dinâmico (extensão)**: re-predição a cada evento pós-t₀ (citação respondida, parcelamento aderido, recurso interposto) — vira *predictive process monitoring* e conecta com a L3; features pós-t₀ são legítimas aqui porque o instante de predição se move.
5. **Métricas**: AUC-ROC e AUC-PR por classe (desbalanceamento certo), **calibração** (Brier, curvas — para priorização de fila importa mais que ranking), C-index/curvas de Kaplan-Meier por estrato para T2; tudo **desagregado por tipo de processo e esfera** (§2) + análise de fairness por porte de município.

## 7. Roteiro de construção do dataset

1. **Espinha dorsal**: partir de `ccd/sql/processos_transito_nome.sql` sem o filtro de nome → uma linha por débito-pessoa com t₀, valores e todos os status (targets prontos).
2. **Juntar o processo**: `Exe_Debito.IdProcessoOrigem` → `Processos` (+ join `Tipo`/`Relator`/`Orgaos` copiado de `web/backend/app/ccd/service.py:87-101`) → Bloco B.
3. **Juntar a decisão**: chave `(IdProcesso, IdComposicaoPauta, IdVotoPauta)` nas tabelas CGAD (BdDIP) e na view de IA → Bloco A. *Limitação a documentar: view cobre sessões ≥2020; a interseção com trânsitos define a janela do estudo.*
4. **Metafeatures**: agregações point-in-time sobre `Fato_Debito ⨝ Dim_Tempo ⨝ Dim_Orgao/Dim_Pessoa ⨝ Dim_StatusDivida` → Blocos D/E.
5. **Contexto**: `Cit_Citacoes` (nº, resposta no prazo), `Exe_Parcelamento`, notificações FRAP → Bloco F.
6. **Enriquecimento externo**: calendário eleitoral, população/receita municipal (IBGE/Siconfi) por ente.
7. **Stage-0 de auditoria** (Bloco C) por último — o dataset dos passos 1–6 já sustenta o primeiro artigo sem ele.

## 8. Referências

**Predição de desfecho judicial**: Aletras et al. (2016, PeerJ CS); Medvedeva, Vols & Wieling (2020, *AI and Law* — crítica metodológica/vazamento temporal); Lage-Freitas et al. (2022, PeerJ CS); [Cui et al. (2022) — survey de LJP](https://arxiv.org/abs/2204.04859); [complexidade e desfecho em litígio civil](https://arxiv.org/html/2605.06151).

**Economia política de auditorias (o diálogo interdisciplinar do paper)**: [Ferraz & Finan (2008, QJE)](https://eml.berkeley.edu/~ffinan/Finan_Audit.pdf); [Ferraz & Finan (2011, AER)](https://www.aeaweb.org/articles?id=10.1257%2Faer.101.4.1274); [Avis, Ferraz & Finan (2018, JPE)](https://www.nber.org/system/files/working_papers/w22443/w22443.pdf).

**Cobrança/recebíveis**: [Predicting Account Receivables with ML (arXiv:2008.07363)](https://arxiv.org/pdf/2008.07363); [debt collection para recebíveis em massa (MDPI 2024)](https://www.mdpi.com/2071-1050/16/14/5885); [Lokanan (2026) — predição de multas regulatórias](https://journals.sagepub.com/doi/10.1177/2631309X251362852).

**Método (features tabulares, encoding, vazamento, sobrevivência)**: Micci-Barreca (2001, SIGKDD Explorations — target encoding com smoothing); Kaufman et al. (2012, TKDD — leakage); Chen & Guestrin (2016, KDD — XGBoost); Prokhorenkova et al. (2018, NeurIPS — CatBoost/ordered target statistics); [Grinsztajn et al. (2022, NeurIPS — GBM vs deep em tabular)](https://arxiv.org/abs/2207.08815); Cox (1972, JRSS-B); Ishwaran et al. (2008, AoAS — random survival forests); [compliance tributário com ML (2025)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12483221/).

---

*Este relatório detalha a L2 de [LINHAS_DE_PESQUISA.md](LINHAS_DE_PESQUISA.md); o Bloco C (stage-0 sobre relatórios de auditoria) é também uma extensão natural do dataset da L1.*
