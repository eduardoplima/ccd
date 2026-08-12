# Linhas de pesquisa em IA com os dados do repositório `ccd` (TCE/RN)

> Relatório para pesquisa acadêmica (mestrado em IA). Mapeia os dados acessíveis por este
> repositório — decisões extraídas pelo fluxo CGAD, cadeia de execução/monitoramento e o
> corpus textual processual — para linhas de pesquisa, desenhos experimentais e a
> literatura seminal de cada área. Gerado em 16/07/2026.

---

## 1. Sumário executivo — as 3 linhas mais promissoras

Ranqueadas por **dado já pronto × ineditismo × esforço até um artigo submissível**:

| # | Linha | Por que é a mais promissora |
|---|-------|------------------------------|
| 1º | **L2 — Predição de cumprimento/desfecho de decisões** | É o diferencial deste repositório frente a toda a literatura de *legal judgment prediction*: aqui existe o **desfecho real** (pagamento, protesto, PGE, parcelamento, prescrição, desconto em folha) ligável ao texto da decisão. Quase todos os trabalhos da área predizem o *resultado do julgamento*; predizer o *cumprimento* da decisão é lacuna aberta. |
| 2º | **L1 — Extração de informação jurídica com LLMs + dataset paper** | O pipeline CGAD já produz um dataset supervisionado (spans NER + registros estruturados + **rótulos de revisão humana** approved/rejected). Publicar o corpus anonimizado como benchmark pt-BR de extração de obrigações/multas/ressarcimentos preencheria lacuna real (LeNER-Br e UlyssesNER-BR cobrem entidades genéricas, não *dispositivos decisórios*). O comparativo BiLSTM-BERT vs. LLM já foi experimentado em `repos/decicontas.app/`. |
| 3º | **L3 — Monitoramento preditivo de processos (predictive process monitoring)** | `Pro_ProcessoEvento`/`Ata_Informacao` formam um *event log* natural de dezenas de milhares de traces. Aplicar o arcabouço de *outcome-oriented predictive process monitoring* a processos de controle externo (prever duração, prescrição, gargalo) é interseção pouco explorada entre process mining e o domínio judicial/de contas. |

As demais linhas (L4–L8) são viáveis como artigos secundários ou seções de um trabalho maior.

---

## 2. Inventário de dados

| Fonte | Conteúdo | Granularidade | Onde no repositório |
|-------|----------|---------------|---------------------|
| `vw_ia_votos_acordaos_decisoes` (banco `processo`) | Texto integral das decisões: `texto_acordao`, `Relatorio`, `FundamentacaoVoto`, `Conclusao`, `ementa`, `assunto`, tipo de voto, divergência, órgão de origem | 1 linha por voto/decisão, sessões ≥ 2020 | `web/tools/cgad/sql/decisions_*.sql` |
| Pipeline CGAD — stage 1 (NER) | Spans literais de 4 entidades: multa, ressarcimento, obrigação, recomendação; com `Modelo`, `VersaoPrompt`, `RunId`, `RawJson` | N entidades por decisão, chave `(IdProcesso, IdComposicaoPauta, IdVotoPauta)` | `web/tools/cgad/cgad/` (`schema.py`, `prompt.py`, `utils.py`); tabelas `NERDecisao`+filhas em BdDIP |
| Pipeline CGAD — stage 2 (estruturado) | `Obrigacao` (de fazer/não fazer, prazo, órgão, multa cominatória com valor/período/solidários) e `Recomendacao` (prazo, responsável, órgão) com FKs `IdPessoa`/`IdOrgao` resolvidas | 1 registro por obrigação/recomendação | `web/tools/cgad/cgad/etl/pipeline.py`; tabelas `Obrigacao`/`Recomendacao` em BdDIP |
| Revisão humana do CGAD | `Status` (pending/approved/rejected), `Revisor`, `DataRevisao`, `PayloadOriginal`, `ObservacoesRevisao` — **gold labels** sobre a saída do LLM | 1 linha de auditoria por revisão | `web/backend/app/cgad/review/service.py`; tabelas `ObrigacaoStaging`/`RecomendacaoStaging` |
| Cadeia de execução/cobrança (banco `processo`) | `Exe_Debito` (valor original/atualizado, `dataTransito`, status da dívida, `StatusProtesto`, `Status_PGE`), `Exe_Parcelamento`, `Processo_TransitoJulgado`, desconto em folha, `PGE_Pagamento` | 1 linha por débito/parcelamento | `ccd/sql/processos_transito_nome.sql`, `scripts/consultas/`, `scripts/analise/parcelamentos.ipynb` |
| Conciliação de pagamentos FRAP (BdDIP) | `FRAPLancamento` (lançamento bancário, CPF/CNPJ do depositante, categoria), matches pessoa/OB/guia/desconto-folha, boletos `Exe_Retorno_Boleto` | 1 linha por lançamento de extrato | `web/tools/frap/frap/` |
| Citações e prazos | `Cit_Citacoes`: `DataInicioContagem`, `DataFinalResposta`, citado, órgão | 1 linha por citação | `web/tools/cgad/sql/citations_by_process*.sql` |
| Corpus procedimental (PDFs) | Informações e despachos de todos os setores, texto extraível | 1 PDF por informação, indexado por `Ata_Informacao`/`Pro_ProcessoEvento` | share `Informacoes_PDF` via `ccd/processo.py` + `ccd/pdf.py` |
| Eventos de tramitação | Sequência de eventos e movimentações por processo | 1 linha por evento | `scripts/consultas/processos_eventos_ccd.sql`, `Pro_ProcessoEvento` |
| Pessoas e órgãos | `GenPessoa` (CPF/CNPJ, tipo F/J), `Orgaos`, gestores com período de gestão (`BdSIAI/Anexo42_*`) | Cadastro | `web/tools/cgad/sql/units.sql`, `responsible_unit.sql` |
| Telemetria do pipeline | `Extracao`/`ExtracaoEvento`: modelo usado (histórico gpt-4 → gpt-5.4-nano → deepseek-v4-flash), contadores, eventos por decisão | 1 linha por execução/evento | `web/backend/app/cgad/tasks.py` |
| Triagem de monitoramento | Classificação LLM de cada obrigação em CCD/UNIDADE_TECNICA/DAP/DUVIDA com trecho, confiança, sinais e justificativa | 1 registro por obrigação triada | `scripts/analise/crivo_monitoramento.py` |
| Experimentos prévios de NER | Notebooks de BiLSTM-BERT vs. LLM, k-fold, análise de erro, significância estatística | — | `repos/decicontas.app/notebooks/` (`ner_bilstm_bert*.ipynb`, `ner_llm.ipynb`, `error_analysis.ipynb`, `statistical_significance.ipynb`) |
| Pares dado→documento | Templates docxtpl + dados estruturados de origem (antecedentes, despachos, informações) | 1 documento por processo | `scripts/automacao/templates/`, `gerar_antecedentes.py` |
| Dicionários de dados | Semântica de BdDIP (79 objetos), BdSIAI (490), BdSIAIPessoal (134) | — | `scripts/analise/dicionario_dados/` |

---

## 3. Linhas de pesquisa

### L1. Extração de informação jurídica com LLMs (NER + extração estruturada) — *dataset paper* + benchmark

**Dados**: corpus de decisões (view de IA) + spans NER stage-1 + registros estruturados stage-2 + gold labels da revisão humana (`*Staging`).

**Experimentos possíveis**
- **Dataset paper**: publicar o corpus anonimizado de decisões do TCE/RN anotado com dispositivos decisórios (multa, ressarcimento, obrigação, recomendação) — não existe benchmark público pt-BR com esse tipo de entidade (LeNER-Br cobre legislação/jurisprudência/pessoa/local; UlyssesNER-BR cobre textos legislativos).
- **Benchmark de métodos**: BiLSTM-CRF, BERTimbau/LegalBert-pt fine-tuned, LLM few-shot com *function calling* (o pipeline atual), LLM fine-tuned — medindo F1 por entidade, custo e latência. O repositório legado já tem k-fold e teste de significância prontos para reaproveitar.
- **Extração estruturada em dois estágios**: avaliar a arquitetura span-first→estruturação (stage-1→stage-2) contra extração direta em um passo; medir propagação de erro entre estágios usando `RawJson` + payload revisado.
- **Robustez a troca de modelo**: a telemetria registra três gerações de modelo (gpt-4, gpt-5.4-nano, deepseek-v4-flash) sob o mesmo prompt versionado (`VersaoPrompt`) — comparação natural de estabilidade de extração entre LLMs em produção.

**Ponto de partida no repo**: `repos/decicontas.app/notebooks/` (experimento quase completo), `web/tools/cgad/cgad/schema.py` (definição das entidades), `fewshot.py`/`prompt_engineering.py`.

**Artigos seminais e influentes**
- Lample et al. (2016). *Neural Architectures for Named Entity Recognition*. NAACL. (BiLSTM-CRF, baseline clássico)
- Devlin et al. (2019). *BERT: Pre-training of Deep Bidirectional Transformers*. NAACL.
- Souza, Nogueira & Lotufo (2020). *BERTimbau: Pretrained BERT Models for Brazilian Portuguese*. BRACIS.
- Luz de Araujo et al. (2018). *LeNER-Br: A Dataset for Named Entity Recognition in Brazilian Legal Text*. PROPOR.
- Albuquerque et al. (2022). *UlyssesNER-Br: A Corpus of Brazilian Legislative Documents for NER*. PROPOR.
- Chalkidis et al. (2020). *LEGAL-BERT: The Muppets straight out of Law School*. Findings of EMNLP.
- Brown et al. (2020). *Language Models are Few-Shot Learners* (GPT-3). NeurIPS.
- Hendrycks et al. (2021). *CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review*. NeurIPS Datasets & Benchmarks. (modelo de dataset paper jurídico)
- Chalkidis et al. (2022). *LexGLUE: A Benchmark Dataset for Legal Language Understanding in English*. ACL.
- Xu et al. (2024). *Large Language Models for Generative Information Extraction: A Survey*. [arXiv:2312.17617](https://arxiv.org/pdf/2312.17617).
- Trabalho recente correlato: *Large Language Models for Judicial Entity Extraction: A Comparative Study* ([arXiv:2407.05786](https://arxiv.org/pdf/2407.05786)); *LegalBert-pt* ([ResearchGate](https://www.researchgate.net/publication/374645610_LegalBert-pt_A_Pretrained_Language_Model_for_the_Brazilian_Portuguese_Legal_Domain)); *LegalBench-BR* ([arXiv:2604.18878](https://arxiv.org/abs/2604.18878)) — mostra que benchmarks jurídicos brasileiros estão em alta e que ainda não há um de extração de dispositivos.

**Venues típicos**: NLLP Workshop (co-located EMNLP), ICAIL, JURIX, LREC-COLING, PROPOR, BRACIS; periódico *Artificial Intelligence and Law*.

---

### L2. Predição de cumprimento e desfecho de decisões (a linha mais inédita)

**Dados**: texto da decisão + entidades extraídas (L1) como *features*, e como **variável-alvo** o desfecho real na cadeia de execução: `Exe_Debito.CodigoStatusDivida` (pago/quitado/prescrito), `StatusProtesto`, `Status_PGE`, `Exe_Parcelamento.SituacaoParcelamento` (2=em curso, 3/5=cancelado, 4=quitado), pagamentos conciliados no FRAP, `DataCumprimento` das obrigações, prazos de `Cit_Citacoes`.

**Experimentos possíveis**
- **Classificação de desfecho**: dado o texto/atributos de uma multa ou ressarcimento no momento da decisão, prever se será pago espontaneamente, parcelado, protestado, ajuizado (PGE) ou prescrito. Features: valor, tipo de débito, órgão, perfil do responsável (PF/PJ), texto da fundamentação.
- **Análise de sobrevivência**: tempo até pagamento/prescrição (censura à direita para débitos em aberto) — modelos de Cox, random survival forests; cruzamento com trânsito em julgado (`dataTransito`).
- **Estudo de política pública**: que características da decisão (clareza do dispositivo, prazo explícito, multa cominatória) correlacionam com cumprimento — interesse direto de *empirical legal studies* e e-gov.
- **Early warning**: modelo que ranqueia débitos recém-transitados por risco de inadimplência/prescrição, avaliado retrospectivamente — conecta com a missão real da CCD e gera avaliação extrínseca honesta.

**Ponto de partida no repo**: `ccd/sql/processos_transito_nome.sql` (toda a cadeia de execução em uma query), `scripts/analise/parcelamentos.ipynb`, `vantagens_trans.ipynb` (já cruza voto × status de cobrança), planilhas Nereu (caso de estudo com prescrição documentada em `nereu_prescritos.xlsx`).

**Artigos seminais e influentes**
- Aletras et al. (2016). *Predicting Judicial Decisions of the European Court of Human Rights: A NLP Perspective*. PeerJ Computer Science. (o seminal de legal judgment prediction)
- Katz, Bommarito & Blackman (2017). *A General Approach for Predicting the Behavior of the Supreme Court of the United States*. PLoS ONE.
- Chalkidis et al. (2019). *Neural Legal Judgment Prediction in English*. ACL.
- Medvedeva, Vols & Wieling (2020). *Using Machine Learning to Predict Decisions of the European Court of Human Rights*. Artificial Intelligence and Law. (também a crítica metodológica: vazamento temporal, o que "prever" significa)
- Lage-Freitas et al. (2022). *Predicting Brazilian Court Decisions*. PeerJ Computer Science ([arXiv:1905.10348](https://arxiv.org/pdf/1905.10348)). (precedente brasileiro direto)
- Cox (1972). *Regression Models and Life-Tables*. JRSS-B. (análise de sobrevivência)
- Ishwaran et al. (2008). *Random Survival Forests*. Annals of Applied Statistics.
- Recente e próximo do tema: Lokanan (2026). *Using Machine Learning to Predict Regulatory Fines* ([SAGE](https://journals.sagepub.com/doi/10.1177/2631309X251362852)) — prediz o valor da multa; prever o **cumprimento** continua lacuna.

**Venues típicos**: *Artificial Intelligence and Law*, ICAIL, JURIX; para o ângulo de administração pública: *Government Information Quarterly*, EGOV-CeDEM-ePart, dg.o; empirical legal studies: JELS.

---

### L3. Monitoramento preditivo de processos (predictive process monitoring)

**Dados**: event log derivado de `Pro_ProcessoEvento` + `Ata_Informacao` (evento, setor, ordem, data) por processo; atributos de caso (assunto, órgão, relator, tipo de decisão); marcadores (`Pro_Marcador`, incl. sobrestamento).

**Experimentos possíveis**
- **Descoberta de processo**: minerar o fluxo real dos processos de execução/monitoramento (Inductive Miner) e confrontar com o fluxo normativo (Resolução 013/2015 — a base legal está em `.claude/skills/legislacao-ccd/`); análise de conformidade.
- **Predição de outcome orientada a caso**: com prefixos do trace, prever (a) tempo restante até arquivamento, (b) risco de prescrição, (c) se o processo será sobrestado — exatamente o protocolo do benchmark de Teinemaa et al.
- **Predição de próxima atividade** com transformers sobre sequências de eventos (o corpus de traces é grande o bastante).
- **Ângulo aplicado**: priorização de fila da CCD (quais processos precisam de despacho agora) com avaliação retrospectiva; `processos_parados_nereu.py` já é um heurístico manual disso.

**Ponto de partida no repo**: `scripts/consultas/processos_eventos_ccd.sql`, `scripts/analise/tramitacao_cip.ipynb`, `stats_ccd.ipynb`/`stats_dip.ipynb` (estatísticas de estoque/produção que viram baseline descritivo).

**Artigos seminais e influentes**
- van der Aalst (2016). *Process Mining: Data Science in Action* (2ª ed.). Springer. (o livro-texto da área)
- Maggi et al. (2014). *Predictive Monitoring of Business Processes*. CAiSE.
- Teinemaa, Dumas, La Rosa & Maggi (2019). *Outcome-Oriented Predictive Process Monitoring: Review and Benchmark*. ACM TKDD ([arXiv:1707.06766](https://arxiv.org/abs/1707.06766); [benchmark no GitHub](https://github.com/irhete/predictive-monitoring-benchmark) com protocolo reutilizável).
- Verenich et al. (2019). *Survey and Cross-benchmark of Remaining Time Prediction Methods*. ACM TIST.
- Camargo, Dumas & González-Rojas (2019). *Learning Accurate LSTM Models of Business Processes*. BPM.

**Venues típicos**: BPM Conference, ICPM (International Conference on Process Mining), CAiSE, *Information Systems*, *Decision Support Systems*.

---

### L4. Qualidade de rótulos, human-in-the-loop e avaliação de LLMs em produção

**Dados**: `ObrigacaoStaging`/`RecomendacaoStaging` (approved/rejected + payload original + observações do revisor), telas de *dataset corrections* e "cleanlab-review" do frontend, telemetria `Extracao`/`ExtracaoEvento`.

**Experimentos possíveis**
- **Estudo de caso de HITL em produção**: taxa de rejeição por tipo de entidade/modelo/versão de prompt; taxonomia dos erros do LLM (a partir de `ObservacoesRevisao`); custo humano de revisão por entidade.
- **Confident learning** sobre os rótulos: usar cleanlab para detectar rótulos ruidosos na própria revisão humana (a tela admin já sugere isso) e medir impacto no benchmark da L1.
- **LLM-as-judge vs. revisor humano**: quão bem um segundo LLM prediz o veredito approved/rejected do revisor? (calibração, viés de auto-preferência).
- **Aprendizado ativo**: priorizar para revisão humana as extrações onde o modelo é menos confiável, medindo redução de esforço.

**Artigos seminais e influentes**
- Northcutt, Jiang & Chuang (2021). *Confident Learning: Estimating Uncertainty in Dataset Labels*. JAIR.
- Ratner et al. (2017). *Snorkel: Rapid Training Data Creation with Weak Supervision*. VLDB.
- Settles (2009). *Active Learning Literature Survey*. UW-Madison TR. (referência canônica de active learning)
- Zheng et al. (2023). *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*. NeurIPS.
- Sculley et al. (2015). *Hidden Technical Debt in Machine Learning Systems*. NeurIPS. (enquadramento de ML em produção)

**Venues típicos**: NeurIPS Datasets & Benchmarks, HCOMP, CHI (lado humano), EMNLP (avaliação).

---

### L5. Sumarização jurídica e geração de ementas

**Dados**: pares naturais texto-longo↔ementa na própria view (`Relatorio`+`FundamentacaoVoto`+`Conclusao` ↔ `ementa`); `ementas.ipynb` já gera ementas por LLM para informações (avaliação contra as oficiais é o experimento óbvio).

**Experimentos possíveis**
- Benchmark de sumarização de decisões de contas em pt-BR: extrativo (TextRank/LexRank) vs. abstrativo fine-tuned vs. LLM zero/few-shot; avaliação com ROUGE/BERTScore + LLM-as-judge + revisores da CCD (avaliação humana é o diferencial de aceite).
- Estudo de alucinação em sumarização jurídica (a literatura mostra taxa alta em decisões judiciais).

**Artigos seminais e influentes**
- Hachey & Grover (2006). *Extractive Summarisation of Legal Texts*. Artificial Intelligence and Law.
- Bhattacharya et al. (2019). *A Comparative Study of Summarization Algorithms Applied to Legal Case Judgments*. ECIR.
- Shukla et al. (2022). *Legal Case Document Summarization: Extractive and Abstractive Methods and their Evaluation*. AACL-IJCNLP.
- Lin (2004). *ROUGE: A Package for Automatic Evaluation of Summaries*. ACL Workshop.
- Recente: *Applicability of LLMs for Legal Case Judgement Summarization* ([arXiv:2407.12848](https://arxiv.org/pdf/2407.12848)); *Gavel: Evaluating LLMs on Long-Context Legal Summarization* ([arXiv:2601.04424](https://arxiv.org/pdf/2601.04424)); *CourtPressGER* ([arXiv:2512.09434](https://arxiv.org/pdf/2512.09434)) — modelo de dataset decisão↔resumo análogo ao par decisão↔ementa daqui.

**Venues**: *AI and Law*, JURIX/ICAIL, EMNLP/ACL Findings, PROPOR.

---

### L6. Resolução de entidades e desambiguação de homônimos

**Dados**: `GenPessoa` (CPF/CNPJ como chave-verdade), nomes em texto livre nas decisões/citações, a heurística anti-homônimo por CPF de `gerar_antecedentes.py`, fuzzy-matching de órgãos (`rapidfuzz` + LLM em `get_responsible_unit`), raiz de CNPJ no caso IPERN (`planilha_nereu.py`).

**Experimentos possíveis**: benchmark de record linkage nome-em-texto → pessoa cadastral usando CPF como gabarito (dataset com ground truth de graça, raro na área); comparação Fellegi-Sunter clássico vs. matchers neurais vs. LLM; avaliação do pipeline híbrido fuzzy+LLM já em produção.

**Artigos seminais**: Fellegi & Sunter (1969). *A Theory for Record Linkage*. JASA. — Christen (2012). *Data Matching*. Springer. — Mudgal et al. (2018). *Deep Learning for Entity Matching* (DeepMatcher). SIGMOD. — Li et al. (2020). *Deep Entity Matching with Pre-Trained Language Models* (Ditto). VLDB.

**Venues**: VLDB, SIGMOD (data management), ou como componente da L1.

---

### L7. Ontologia e grafo de conhecimento de decisões de controle externo

**Dados**: `preparacao_ontologia.ipynb` (já iniciado), entidades estruturadas do CGAD (pessoa—órgão—obrigação—prazo—sanção), relações processo-origem↔processo-execução (`Exe_Debito.IdProcessoOrigem/IdProcessoExecucao`), gestores com vigência (`Anexo42`).

**Experimentos possíveis**: construção automática de KG decisório com LLMs e avaliação de completude/correção contra o banco relacional; consultas de competência ("todas as obrigações vigentes do órgão X sob o gestor Y"); GraphRAG sobre o KG para perguntas da CCD.

**Artigos seminais**: Hoekstra et al. (2007). *The LKIF Core Ontology of Basic Legal Concepts*. LOAIT. — Casanovas et al. (2016). *Semantic Web for the Legal Domain*. Semantic Web Journal. — Ji et al. (2022). *A Survey on Knowledge Graphs*. IEEE TNNLS. — Edge et al. (2024). *From Local to Global: A GraphRAG Approach to Query-Focused Summarization*. arXiv.

**Venues**: JURIX, ISWC/ESWC (semântica), *Semantic Web Journal*.

---

### L8. Geração controlada de documentos oficiais (RAG / data-to-text)

**Dados**: pares dado-estruturado→documento dos fluxos de automação (antecedentes, despachos Nereu, cobrança judicial, envio DAP) — o template docxtpl define a estrutura-alvo e o banco define o conteúdo; a base legal versionada (`legislacao-ccd`) serve de corpus de grounding para RAG.

**Experimentos possíveis**: avaliação de fidelidade factual de despachos gerados por LLM vs. template determinístico (taxa de alucinação de valores/datas/dispositivos legais); RAG sobre a legislação para fundamentação; avaliação humana por servidores.

**Artigos seminais**: Gatt & Krahmer (2018). *Survey of the State of the Art in Natural Language Generation*. JAIR. — Lewis et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. NeurIPS. — Ji et al. (2023). *Survey of Hallucination in Natural Language Generation*. ACM Computing Surveys.

**Venues**: INLG, EMNLP, JURIX (aplicação jurídica).

---

## 4. Considerações éticas e legais (obrigatórias para publicação)

- **LGPD**: os dados contêm CPF, CNPJ, nomes de pessoas físicas e situação de dívida. Qualquer dataset publicado exige **anonimização/pseudonimização** (substituição consistente de nomes/documentos, supressão de valores raros reidentificáveis). Decisões do TCE são públicas, mas a *agregação* com status de dívida e folha de pagamento cria risco de reidentificação que a publicação isolada não tem.
- **Autorização institucional**: os bancos `processo`, BdDIP e BdSIAI são internos. Formalizar autorização do TCE/RN para uso em pesquisa (e citar no paper), idealmente com parecer do comitê de ética da universidade quando houver dados pessoais.
- **Vazamento temporal** (para L2/L3): separar treino/teste por data de decisão, nunca aleatoriamente — a crítica de Medvedeva et al. (2020) à literatura de judgment prediction se aplica integralmente.
- **Dual use**: modelos de "risco de inadimplência" sobre pessoas físicas exigem discussão de fairness (viés por órgão, região, porte do município) — trate isso como seção do paper, não como nota de rodapé.

## 5. Roadmap de publicação sugerido

1. **Artigo 1 (curto prazo)** — *dataset paper* + benchmark da L1: corpus anonimizado de dispositivos decisórios do TCE/RN com gold labels humanos, comparando BiLSTM-BERT (já rodado em `repos/decicontas.app/`) vs. LLMs. Alvo: LREC-COLING, PROPOR ou NLLP@EMNLP. É o artigo que legitima os dados e vira a citação-base dos demais.
2. **Artigo 2 (médio prazo)** — L2: predição de cumprimento/desfecho usando o corpus do Artigo 1 + cadeia `Exe_*`/FRAP. Alvo: *Artificial Intelligence and Law* ou ICAIL. Maior potencial de impacto por ineditismo.
3. **Artigo 3 (paralelo)** — L3: predictive process monitoring dos processos de execução, reutilizando o protocolo/benchmark de Teinemaa. Alvo: ICPM ou BPM. Independente dos outros dois em dados e método — bom hedge.
4. **Satélites** — L4 como estudo de caso HITL (workshop), L5/L6 como artigos curtos derivados dos mesmos dados.

---

*Fontes web consultadas na verificação de referências:*
[LegalBench-BR (arXiv)](https://arxiv.org/abs/2604.18878) ·
[LegalBert-pt (ResearchGate)](https://www.researchgate.net/publication/374645610_LegalBert-pt_A_Pretrained_Language_Model_for_the_Brazilian_Portuguese_Legal_Domain) ·
[Predicting Brazilian court decisions (arXiv)](https://arxiv.org/pdf/1905.10348) ·
[JUÁ — IR benchmark jurídico BR (arXiv)](https://arxiv.org/html/2604.06098v1) ·
[LLMs for Generative IE: Survey (arXiv)](https://arxiv.org/pdf/2312.17617) ·
[LLMs for Judicial Entity Extraction (arXiv)](https://arxiv.org/pdf/2407.05786) ·
[Outcome-Oriented PPM: Review and Benchmark (arXiv)](https://arxiv.org/abs/1707.06766) ·
[Benchmark de PPM (GitHub)](https://github.com/irhete/predictive-monitoring-benchmark) ·
[LLMs for Legal Case Judgement Summarization (arXiv)](https://arxiv.org/pdf/2407.12848) ·
[Gavel — long-context legal summarization (arXiv)](https://arxiv.org/pdf/2601.04424) ·
[CourtPressGER (arXiv)](https://arxiv.org/pdf/2512.09434) ·
[Lokanan 2026 — ML para prever multas regulatórias (SAGE)](https://journals.sagepub.com/doi/10.1177/2631309X251362852)
