# Proposta de publicação — créditos sancionatórios de Tribunais de Contas sob as IPSAS

> Revisão da literatura e desenho de um trabalho publicável a partir do exercício de
> `IPSAS_APLICACAO_CCD.md`. Complementa `LINHAS_DE_PESQUISA.md`, que cobre as linhas de IA sobre os
> mesmos dados — aqui a disciplina é contabilidade pública, não aprendizado de máquina.
> Levantamento em 03/08/2026.

---

## 1. Estado da arte: quatro literaturas que se tocam mas não se encontram

### 1.1 Adoção do regime de competência e das IPSAS

É a literatura mais madura, e o achado dominante é negativo. A revisão sistemática de **Bonollo
(2023)**, com 106 artigos entre 1980 e 2021, conclui que os benefícios da contabilidade por
competência no setor público **ainda não foram substanciados empiricamente**, e aponta
explicitamente como agenda futura a *mensuração de ativos públicos*. Revisões paralelas — **Azhar et
al. (2022)** na *Australian Accounting Review* e a análise bibliométrica de economias emergentes em
*Public Money & Management* (2023) — chegam ao mesmo diagnóstico: muita pesquisa sobre *adoção*,
pouca sobre *o que os números passaram a dizer*.

Há trabalho recente sobre efeitos institucionais (adoção plena × parcial das IPSAS e corrupção no sul
da Europa, *JRFM* 2025), mas segue no nível macro.

**Onde isso deixa espaço:** quase ninguém pega uma classe de ativo concreta, aplica as regras de
reconhecimento e mensuração, e mostra o que a competência revela que o caixa escondia.

### 1.2 Tribunais de Contas como atores da reforma contábil (literatura brasileira)

Há um grupo consolidado — **André Feliciano Lino** (UFPA) e **Ricardo Rocha de Azevedo** (UFU/USP),
com Ricardo Lopes Cardoso — que publica exatamente sobre TCs em periódicos internacionais de peso:
*Critical Perspectives on Accounting* ("Fighting or supporting corruption? The role of public sector
audit organizations in Brazil", 2022), *International Journal of Public Sector Management* (2020),
*JPBAFM* (2023), *Financial Accountability & Management*, além de RAP e *Sociedade, Contabilidade e
Gestão* sobre o gap entre normas de auditoria e prática nos TCs. A tese de Lino (USP, 2015) é
literalmente *Reforma da contabilidade pública e os tribunais de contas*.

**Mas o enquadramento é sempre o mesmo:** o TC como **regulador e fiscal da contabilidade alheia**.
Nenhum desses trabalhos trata o TC — ou o ente credor das sanções que ele impõe — como **entidade que
reporta seus próprios créditos**.

### 1.3 Dívida ativa e ajuste para perdas no Brasil

Literatura e normativo bem desenvolvidos, e inteiramente **tributários**. O MCASP substituiu
"provisão" por *ajuste para perdas* (retificadora de ativo), exige avaliação de recuperabilidade, e
há estudos aplicados a municípios (ex.: ajuste para perdas da dívida ativa em municípios
pernambucanos). O próprio **TCU** é o fiscal mais duro dessa conta: apontou **R$ 330 bilhões de
créditos tributários indevidamente reconhecidos** no BGU, com crítica direta à metodologia do
*índice de recebibilidade* e à superavaliação do ativo.

As taxas de recuperação conhecidas são desoladoras: **2% a 3%** no contencioso tributário
tradicional, contra **15,4%** via protesto de CDA no município do Rio em 2021.

**O que falta:** os créditos **sancionatórios** — multas e ressarcimentos impostos por decisão de
Tribunal de Contas — não são dívida ativa tributária. Têm fato gerador distinto (uma decisão de
controle externo, não um fato tributável), cadeia de cobrança distinta (protesto, PGE, desconto em
folha), regime prescricional próprio, e não aparecem nessa literatura.

### 1.4 Modelagem de recuperabilidade

Existe e é sofisticada, mas fora do setor público-sancionatório: o IRS estima *long-run
collectability* de assessments não pagos com modelos logísticos por vida remanescente do statute;
há regressão de sobrevivência aplicada a otimização de cobrança (*Operational Research*, 2022) e
predição de recebíveis com ML (arXiv:2008.07363). **Lokanan (2026)** prediz o *valor* de multas
regulatórias — não a sua recuperação.

### 1.5 O momento normativo (e por que ele importa agora)

- **IPSAS 47 – Revenue** entrou em vigor em **1º de janeiro de 2026**, substituindo IPSAS 9, 11 e 23.
  Troca a lógica de *condições e restrições* pela de ***binding arrangement***. Multas são transação
  **sem** binding arrangement, e o reconhecimento do ativo passa a depender explicitamente da
  *"ability to enforce this right through legal or equivalent means"* e da *"past experience with
  similar transactions"*.
- **IPSAS 41** trouxe perda esperada prospectiva (substituindo o modelo de perda incorrida do
  IPSAS 29), com reconhecimento mais precoce e maior.
- **STF, Tema 899 (RE 636.886, 20/04/2020)**: *"É prescritível a pretensão de ressarcimento ao erário
  fundada em decisão de Tribunal de Contas."* A pretensão punitiva (multa) já seguia o prazo
  quinquenal da Lei 9.873/1999.

**A conjunção é a oportunidade:** uma norma de receita recém-vigente cujo teste de reconhecimento
depende de experiência histórica de execução, aplicada a uma classe de ativo que sofreu um choque
jurídico exógeno de exigibilidade em 2020 — e que ninguém mediu.

---

## 2. A lacuna, em uma frase

> Não existe estudo que meça os créditos sancionatórios de um Tribunal de Contas sob as regras de
> reconhecimento e mensuração das IPSAS. A literatura trata o TC como fiscal da contabilidade alheia,
> e trata recebíveis não-contratuais como se fossem apenas crédito tributário.

O dado do exercício já feito mostra por que isso não é detalhe: **provisão para perdas de 88,6% sobre
R$ 356,7 milhões reconhecidos**, com taxa acima de 90% em todas as faixas de aging, porque o Tribunal
recebe as dívidas pequenas (mediana de R$ 600) e perde as grandes (mediana de R$ 10.252).

---

## 3. O trabalho proposto

**Título (pt):** *Ativo ou ficção? Reconhecimento e mensuração de créditos sancionatórios de
Tribunais de Contas sob as IPSAS*

**Título (en):** *Recognising the unrecoverable: audit court sanction receivables under IPSAS 47 and
IPSAS 41*

**Pergunta de pesquisa.** Quando a perda esperada de um crédito não-contratual se aproxima da
totalidade, a questão contábil ainda é de **mensuração** — ou já é de **reconhecimento**?

Essa é a pergunta que dá densidade teórica ao trabalho e que o IPSAS 47 tornou respondível. Se o
reconhecimento do ativo depende da capacidade de fazer valer o direito e da experiência passada com
transações similares, um crédito cuja experiência histórica é de ~90% de perda testa a fronteira
entre **ativo** (IPSAS 47/41, reconhecido e provisionado) e **ativo contingente** (IPSAS 19, apenas
divulgado). A resposta não é óbvia, e é generalizável para toda receita sancionatória de Estado.

### Desenho

**Três contribuições encadeadas:**

**(a) Empírica — a primeira mensuração da carteira.** 16.249 créditos, 28 coortes anuais de trânsito
em julgado (1998–2026), classificados nos estados das normas e submetidos a uma matriz de perda
esperada por aging. O trabalho pesado já está feito e é reprodutível
(`scripts/analise/carteira_ipsas.py`).

**(b) Metodológica — o choque do Tema 899 como identificação.** É o diferencial frente à literatura
descritiva de dívida ativa. A decisão do STF em abril de 2020 alterou a exigibilidade dos
**ressarcimentos** fundados em decisão de TC; as **multas** já eram prescritíveis pela Lei
9.873/1999. Isso dá **tratamento e controle dentro da mesma carteira, mesma cobrança, mesmo
tribunal**. Análise de sobrevivência (Cox / risco competitivo entre "pago" e "prescrito") com o
choque como quebra estrutural, ou diferenças-em-diferenças sobre a taxa de baixa por prescrição.

O achado, qualquer que seja o sinal, é publicável: se o choque alterou a recuperação, quantifica-se
o efeito de uma decisão judicial sobre o valor recuperável de um ativo público — que é exatamente a
*informação prospectiva* que o IPSAS 41 exige e que nenhuma matriz retrospectiva captura.

**(c) Institucional — o argumento que fecha o artigo.** O TCU acusa R$ 330 bilhões de créditos
tributários mal reconhecidos no BGU e exige índice de recebibilidade dos jurisdicionados. Os créditos
gerados pelas decisões dos próprios Tribunais de Contas não passam por crivo equivalente. Isso
conversa diretamente com a linha de Lino & Azevedo sobre o papel das organizações de auditoria
pública — e é o gancho para *Critical Perspectives on Accounting* se o enquadramento for crítico.

### Dados

Já disponíveis e verificados: `Exe_Debito` e cadeia de execução do banco `processo` (TCE/RN);
domínios de status mapeados; arrecadação conciliada do FRAP como validação externa do lado do caixa.

### Onde submeter

| Alvo | Ajuste |
|---|---|
| **Journal of Public Budgeting, Accounting & Financial Management** (Emerald) | **Primeira escolha.** Publicou a revisão de Bonollo, cuja agenda futura é literalmente mensuração de ativos públicos — o artigo responde a um chamado explícito |
| *Financial Accountability & Management* (Wiley) | Igualmente adequado; publica o grupo brasileiro de TCs |
| *Critical Perspectives on Accounting* | Se o enquadramento for o (c) — o auditor que não se audita |
| *Revista Contabilidade & Finanças* (USP) ou *RAP* (FGV) | Versão em português, Qualis A, e o público que pode agir sobre o achado |
| CIGAR Network; EGPA PSG XII; Congresso USP de Controladoria; ANPCONT | Conferências para rodar o paper antes da submissão |

---

## 4. Riscos, e o que fazer com eles

- **Poder estatístico do choque de 2020.** Há 6 anos de janela pós-tratamento, mas prescrição leva
  anos para se materializar e as coortes recentes são menores (533 em 2024, 411 em 2025). *Mitigação:*
  risco competitivo com censura à direita em vez de DiD ingênuo; se ainda assim ficar frágil, o
  desenho vira estudo de caso profundo com o choque como covariável discutida, e a extensão
  multi-TCE fica para o artigo seguinte.
- **Generalização a partir de um único tribunal.** Assumir isso como escolha: é um *deep case study*
  com acesso a dado transacional que nenhum survey alcança. Replicação em outros TCEs é a agenda.
- **Autorização e LGPD.** Dados internos, com CPF e situação de dívida. Exige autorização formal do
  TCE/RN e pseudonimização — mesmas ressalvas da seção 4 de `LINHAS_DE_PESQUISA.md`.
- **Sensibilidade institucional.** O achado central é que o Tribunal recupera ~10% do que condena.
  Publicar isso exige alinhamento interno prévio; a anonimização como "um tribunal de contas estadual
  brasileiro" é praxe aceita e reduz atrito sem custo científico.
- **Limitações já conhecidas da mensuração.** Carteira a valor histórico (`ValorAPagar` nunca
  alimentado), taxa de perda retrospectiva, censura à direita — todas documentadas em
  `IPSAS_APLICACAO_CCD.md` §5 e que precisam ir para a seção de limitações do artigo.

---

## 5. IPSAS × inteligência artificial: o que existe (e o que não existe)

Levantamento em 03/08/2026. **O resultado principal é negativo: praticamente não há artigos que
cruzem IPSAS com aprendizado de máquina.** O que existe são cinco literaturas vizinhas, nenhuma
delas ocupando a interseção.

### 5.1 O artigo-âncora, e a lacuna declarada

**Agostino, D. et al. (2025). *Data science and public sector accounting: Reviewing impacts on
reporting, auditing, and accountability practices*. Public Money & Management** (publicado em
21/07/2025). Revisa tecnologias algorítmicas — IA e ML — na contabilidade, no relato financeiro e na
auditoria do setor público. A conclusão é a nossa deixa:

> há *"considerable shortage of research about data science on public sector financial information
> reporting, auditing and accountability"*, e a maioria dos estudos *"lacks theoretical background
> and focuses on technical feasibility"*, com escassa evidência empírica.

Ou seja: quem publicar evidência empírica real nessa interseção entra num campo declaradamente vazio.

### 5.2 ML para perda esperada (IFRS 9) — a literatura tecnicamente mais próxima

É madura, sofisticada e **inteiramente bancária**. Nada em setor público, nada sob IPSAS 41.

- ***Probability of default for lifetime credit loss for IFRS 9 using machine learning competing
  risks survival analysis models*** (Elsevier). **É o método exato do desenho proposto na §3**:
  risco competitivo + sobrevivência + ML para perda esperada vitalícia.
- *Explainable and Calibrated Machine Learning Models for Probability of Default: an application to
  Expected Credit Loss under IFRS 9* — trata de desbalanceamento, governança e explicabilidade, que
  são exatamente os problemas de um modelo que vira número de balanço.
- *Stochastic Modeling of Expected Credit Loss Under IFRS 9: A Monte Carlo and Scenario-Based
  Approach*; e o consenso de que ensembles de árvore superam regressão logística em poder
  discriminante.

### 5.3 ML no setor público — mas prevendo a entidade, não o ativo

- **Liu, R., Li, H., Yoon, K. & Vasarhelyi, M. A. (2025?). *Using Machine Learning Algorithms to
  Improve Fiscal Distress Prediction Models: The Case of U.S. Local Governments*. Journal of
  Information Systems (AAA), 39(3), 131.** Seis algoritmos, governos locais de 49 estados,
  2015–2017; *Exactly Balanced Bagging* vence, F1 entre 53% e 55%.
- *Predicting municipalities in financial distress: a machine learning approach enhanced by domain
  expertise* (arXiv:2302.05780, municípios italianos).
- *Predicting bankruptcy of local government: A machine learning approach* (Elsevier, 2021).

Todos preveem a **saúde fiscal do ente**. Nenhum estima a **recuperabilidade de um ativo específico**.

### 5.4 IA em auditoria e nos Tribunais de Contas

- *Artificial Intelligence and Public Sector Auditing: Challenges and Opportunities for Supreme Audit
  Institutions* (MDPI, 2025).
- INTOSAI, *Auditing Machine Learning Algorithms: A White Paper for Public Auditors*.
- **Literatura brasileira, e diretamente sobre TCs:** artigo na SciELO sobre IA nos órgãos
  constitucionais de controle de contas, catalogando **Alice** (irregularidades em licitações, TCU),
  **Mônica**, **Íris** (fraude por cruzamento de dados), **Lais** (sobrepreço, TCE-RS), **Turmalina**
  (portais de transparência) e chatbots. Metodologia exploratória/documental.
- Cho, Vasarhelyi, Sun & Zhang (2020), *Learning from machine learning in accounting and assurance*
  (JETA); Rozario & Vasarhelyi (2022) sobre ML em modelos de estimativa e ceticismo do auditor.

Aqui a IA é ferramenta **de fiscalizar o outro** — nunca de mensurar o próprio ativo. É o mesmo viés
já identificado na §1.2, agora do lado tecnológico.

### 5.5 LLMs em contabilidade — emergente, sem IPSAS

*Automating Financial Statement Audits with Large Language Models* (arXiv:2506.17282); benchmark
*FinMaster* (arXiv:2505.13533); revisões bibliométricas de IA em contabilidade e finanças. O consenso
é que LLMs falham justamente no julgamento normativo — que é o coração de uma estimativa contábil.

### 5.6 A leitura: um segundo artigo, e a ponte com `LINHAS_DE_PESQUISA.md`

As lacunas se encaixam. A literatura de ML para perda esperada é bancária; a de ML no setor público
prevê a entidade, não o ativo; a de IA em TCs olha para fora. **Ninguém estimou perda esperada
vitalícia de uma carteira pública, não-contratual e sancionatória com métodos de aprendizado de
máquina** — que é precisamente o que os dados da CCD permitem.

Isso é o **artigo 2**, e é a versão contábil da linha **L2** de `LINHAS_DE_PESQUISA.md` (predição de
cumprimento de decisões). A diferença de enquadramento é o que o torna publicável nos dois mundos: em
vez de "prever se a decisão será cumprida", a pergunta vira *"estimar a perda de crédito esperada
vitalícia exigida pelo IPSAS 41, com risco competitivo entre pagamento e prescrição"*. Mesmo dado,
mesma modelagem — mas o produto é um número de balanço auditável, não um escore.

O artigo 1 (§3) estabelece a mensuração e a matriz retrospectiva; o artigo 2 substitui a matriz por
um modelo prospectivo, que é o que a norma pede e a matriz não entrega. Alvos possíveis: *Journal of
Emerging Technologies in Accounting*, *Intelligent Systems in Accounting, Finance & Management*,
*Journal of Information Systems* — ou *Public Money & Management*, respondendo diretamente ao chamado
de Agostino et al.

## 6. Referências a confirmar antes de citar

Levantadas por busca web; conferir autoria, ano, volume e página na fonte primária antes de usar.

- Bonollo, E. (2023). *Negative effects of the adoption of accrual accounting in the public sector:
  a systematic literature review and future prospects*. JPBAFM, 35(6).
- Azhar, Z. et al. (2022). *Accrual Accounting at Different Levels of the Public Sector: A Systematic
  Literature Review*. Australian Accounting Review.
- Lino, A. F. & Azevedo, R. R. et al. (2022). *Fighting or supporting corruption? The role of public
  sector audit organizations in Brazil*. Critical Perspectives on Accounting.
- Lino, A. F. (2015). *Reforma da contabilidade pública e os tribunais de contas*. Dissertação,
  FEA/USP.
- Sasso, M. (2017). *Adoção das normas de contabilidade oriundas do processo de convergência às
  IPSAS: respostas estratégicas de governos estaduais*. Dissertação, USP.
- Turk, A. et al. *Valuing Unpaid Tax Assessments: Estimating Long-Run Collectability*. IRS Research
  Conference. https://www.irs.gov/pub/irs-soi/17resconturk.pdf
- IPSASB. *IPSAS 47, Revenue* (2023, vigente em 01/01/2026); *IPSAS 41, Financial Instruments*;
  *IPSAS 19*. https://www.ipsasb.org/publications/ipsas-47-revenue
- STF. RE 636.886 / Tema 899, rel. Min. Alexandre de Moraes, j. 20/04/2020.
- TCU. Auditoria do BGU — reconhecimento indevido de créditos a receber.
  https://portal.tcu.gov.br/imprensa/noticias/auditoria-aponta-reconhecimento-indevido-de-330-bilhoes-em-creditos-a-receber
- CFC. NBC TSP 03 (R1) — Provisões, Passivos Contingentes e Ativos Contingentes; MCASP (2024),
  ajuste para perdas da dívida ativa.

Do levantamento de IA (§5):

- Agostino, D. et al. (2025). *Data science and public sector accounting*. Public Money & Management.
  https://doi.org/10.1080/09540962.2025.2529266
- Liu, R., Li, H., Yoon, K. & Vasarhelyi, M. A. *Using Machine Learning Algorithms to Improve Fiscal
  Distress Prediction Models: The Case of U.S. Local Governments*. Journal of Information Systems,
  39(3), 131. https://publications.aaahq.org/jis/article-abstract/39/3/131/13651/
- *Probability of default for lifetime credit loss for IFRS 9 using machine learning competing risks
  survival analysis models*. https://www.sciencedirect.com/science/article/abs/pii/S095741742400472X
  — **conferir autoria e periódico**; é a referência metodológica central do artigo 2.
- *Artificial Intelligence and Public Sector Auditing: Challenges and Opportunities for Supreme Audit
  Institutions*. MDPI (2025). https://www.mdpi.com/2673-4060/6/2/78
- *A inteligência artificial nos órgãos constitucionais de controle de contas da administração
  pública brasileira*. SciELO.
  https://www.scielo.br/j/rinc/a/WJgdHhvqpvyr7XnHhMN39Wz/?lang=pt
- Cho, S., Vasarhelyi, M. A., Sun, T. & Zhang, C. (2020). *Learning from machine learning in
  accounting and assurance*. Journal of Emerging Technologies in Accounting.
- INTOSAI. *Auditing Machine Learning Algorithms: A White Paper for Public Auditors*.
  https://intosaijournal.org/journal-entry/auditing-machine-learning-algorithms/
