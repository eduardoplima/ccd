# Débitos "Pago parcialmente" sem ValorPago — análise caso a caso

Resposta da CCD ao chamado da SETIC. Levantamento em 04/08/2026 sobre o banco `processo`
(consultas somente-leitura; nada foi alterado).

---

## 1. Resumo

O chamado apontou débitos em `CodigoStatusDivida = 3` ("Pago parcialmente") com `ValorPago`
nulo e sem boleto em `Exe_DebitoBoleto`, e levantou como hipótese principal uma **falha na
transação de pagamento** — o sistema teria gravado o status sem gravar o valor pago.

**O levantamento fecha o universo e afasta essa hipótese.**

| | |
|---|---|
| Débitos no defeito | **13** (folha da cadeia, status 3, `ValorPago` NULL, sem boleto) |
| Valor original somado | **R$ 190.631,15** (nominal, sem correção) |
| Processos envolvidos | 7 |
| Pessoas envolvidas | 7 |
| Comparativo — estado **normal** | 10.674 folhas em status 1 ("Em Aberto") com `ValorPago` NULL |
| Débitos status 3 + `ValorPago` NULL **com** filho | 0 |

Os 13 são exatamente os casos listados no chamado — **não há nenhum caso fora da lista**. O
problema é fechado e pequeno.

Nenhum pagamento foi perdido por falha de transação. Em todos os 13 casos o pagamento **foi**
registrado (está em `Exe_HistoricoDebito`, com guia ou justificativa) e os valores **foram**
gravados — só que no débito **pai**, não no órfão. O órfão é um registro paralelo criado a mais.

Há **um único caso com possível repercussão financeira** (débito 15601, item 6 abaixo). Nos
demais 12 a correção é puramente cadastral.

---

## 2. Como a cadeia de débitos funciona

`Exe_Debito.IdDebitoAnterior` encadeia versões sucessivas do mesmo débito. Registrar um
pagamento no débito X faz duas coisas:

1. grava `ValorPago` / `ValorOriginalPago` / `dataBaixa` em **X** e o põe em status 3
   ("Pago parcialmente"), além de inserir uma linha em `Exe_HistoricoDebito` com a
   `DataOperacao` e a justificativa (nº da guia, "PARCELA 8", "parcelado" etc.);
2. cria um **filho** Y (`Y.IdDebitoAnterior = X`) com o **saldo remanescente**
   (`valorOriginalDebito` reduzido), `ValorPago` NULL e status "Em Aberto".

Consequências que orientam toda a análise:

- **O débito vigente é a folha da cadeia** (o que não tem filho), não a raiz.
- **Folha com `ValorPago` NULL é normal** — é o saldo que ainda se deve. O que não é normal é
  ela estar em status **3** em vez de **1**.
- `Exe_HistoricoDebito.dataInclusao` bate **ao milissegundo** com o `datainclusao` do filho que
  aquela operação gerou. É por aí que se reconstrói o que o operador fez.

---

## 3. Causa raiz

São **duas** falhas independentes, e nenhuma delas é transação perdida.

### 3.1 O filho herda o status do pai

O débito remanescente nasce copiando `CodigoStatusDivida = 3` do pai em vez de nascer em 1
("Em Aberto"). É isso que produz a combinação denunciada no chamado: folha em "Pago
parcialmente" com `ValorPago` nulo.

### 3.2 Fork — segundo pagamento registrado no mesmo pai

Quando um segundo pagamento é registrado **no mesmo débito pai** — tela não recarregada,
duplo-clique, ou parcela relançada — nasce um **segundo filho do mesmo pai**, em vez de a cadeia
seguir a partir do primeiro filho. Um dos irmãos segue a cadeia; o outro fica órfão.

Em 11 dos 13 casos o órfão tem irmão com `ValorPago` preenchido. Há **351 pais com mais de um
filho** na base — a maioria já foi cancelada manualmente ao longo dos anos; os 13 são o resíduo
que ninguém limpou.

A evidência mais direta é o débito **8029**: quatro linhas em `Exe_HistoricoDebito`, todas com a
**mesma** `DataOperacao` (22/06/2015) e a **mesma** justificativa ("COMPROVANTE TRANSFERÊNCIA
BANCÁRIA"), incluídas às 16:41:38, 16:41:48, 16:42:00 e 16:42:29 — quatro submissões do mesmo
pagamento em 51 segundos, quatro filhos.

### 3.3 O que precisa mudar na rotina (para não voltar a acontecer)

Limpar os 13 registros não impede a recorrência. Na rotina de registro de pagamento:

**(a)** criar o débito remanescente com `CodigoStatusDivida = 1`, sem copiar o status do pai;

**(b)** bloquear o registro quando o débito já tiver filho — o que também resolve o duplo-clique:

```sql
-- guarda a ser aplicada antes de inserir o débito remanescente
IF EXISTS (SELECT 1 FROM Exe_Debito f WHERE f.IdDebitoAnterior = @IdDebito)
    -- este débito já foi processado; o pagamento deve ser registrado no filho
    RAISERROR('Débito já possui sucessor na cadeia.', 16, 1)
```

---

## 4. Parecer caso a caso

Legenda de status usada abaixo (`Exe_StatusDivida`): 1 Em Aberto · 2 Pago Integralmente ·
3 Pago parcialmente · 6 Cancelada por prescrição · 13 Cancelada por Reabertura de Parcelamento ·
14 Cancelada por Reabertura de Dívida Paga Parcialmente · 15 Cancelada por Erro de Cadastro ·
21 Cancelado por duplicidade.

### Caso 1 — Processo 012990/2010 · débitos **8031** e **8032**
**João Valdivino da Costa** (CPF ***.902.798-**) · R$ 3.629,86 cada

Um **único** pagamento (22/06/2015, transferência bancária) foi registrado **quatro vezes** no
pai 8029, criando 8030, 8031, 8032 e 8033 — todos com o mesmo valor original (R$ 3.629,8578),
todos sem `ValorPago`, todos folha. Alguém já cancelou 8030 (status 15) e 8033 (status 14);
8031 e 8032 ficaram para trás.

A dívida real desse processo correu por uma **cadeia paralela**: 8034 → 8035 → 8037 → 8039 →
8040 → **8041, em status 2 (Pago Integralmente)**, com 6 boletos e R$ 1.654,95 de baixa em
25/10/2016.

> **Ação:** cancelar **8031** e **8032** (21 – duplicidade, ou 15 – erro de cadastro, igualando
> ao irmão 8030). Sem impacto financeiro: a dívida está quitada.

### Caso 2 — Processo 002743/2008 · débitos **8586** e **8591**
**João de Deus Garcia de Araújo** (CPF ***.559.414-**) · R$ 2.668,11 e R$ 2.492,12

Confirma a leitura do chamado ("dois débitos fora da hierarquia"), com uma correção: não é erro
de cadastro genérico, são **duas guias registradas no débito errado**.

- guia **5839/2015** registrada em 8584 → criou 8585 (que seguiu a cadeia);
- guia **10157/2015** registrada **de novo em 8584** → criou o órfão **8586**;
- guia **10158/2015** registrada em 8585 → criou 8589 (que seguiu a cadeia);
- guia **15951/2015** registrada **de novo em 8585** → criou o órfão **8591**.

Os dois órfãos têm `valorOriginalDebito` **idêntico ao do irmão** (2.668,1057 e 2.492,1208) — ou
seja, não reduziram saldo nenhum. A cadeia seguiu 8585 → 8589 → 8592 → … → 8602 → 10083 →
**17476, em status 2 (Pago Integralmente)**, em 30/07/2019.

> **Ação:** cancelar **8586** e **8591**. Como a cadeia fechou paga, as duas guias acabaram
> absorvidas — mas vale a CCD conferir os comprovantes 10157/2015 e 15951/2015 antes do
> cancelamento.

### Caso 3 — Processo 018127/2000 · débito **12258**
**Pedro Lopes de Moura** (CPF ***.135.604-**) · R$ 294,54

**Corrige a hipótese do chamado** ("verificar se na verdade foi quitado integralmente"): **não
foi**. Dois depósitos distintos (05/03/2009, "Comprovante de depósito"; e 10/03/2009, "depósito
bancário") foram registrados ambos no pai 4626, em 07/08/2017, criando 12257 e 12258 — mesmo
valor original, ambos sem `ValorPago`. **12257 já foi marcado "Cancelada por prescrição"
(status 6); 12258 é a duplicata que sobrou.**

A cadeia legítima de 4626 é outra: 4628 → 4630 → 5459 → 5460, toda em status 14. Os demais
débitos do processo (4624, 4625) estão prescritos (status 6). Não há débito em aberto nesse
processo.

> **Ação:** cancelar **12258**, replicando o status do irmão 12257 (6 – prescrição) ou usando
> 15 – erro de cadastro. Não tratar como quitação.

### Caso 4 — Processo 005337/2010 · débitos **14527**, **14528**, **14529** e **14530**
**Daize Florencio da Costa Correia** (CPF ***.186.134-**) · ~R$ 27.330 cada

Confirma a leitura do chamado ("quatro débitos originados do mesmo débito"). O histórico do pai
14525 tem cinco linhas — PARCELA 7, 8, 9, 10 e 11 — lançadas em 09/08/2018 entre 13:39:51 e
13:42:43, cada uma criando um filho de 14525:

| operação | `DataOperacao` | filho gerado | `ValorPago` |
|---|---|---|---|
| PARCELA 7 | 20/02/2018 | 14526 | R$ 1.020,00 ✔ |
| PARCELA 8 | 06/03/2018 | **14527** | — |
| PARCELA 9 | 06/04/2018 | **14528** | — |
| PARCELA 10 | 07/05/2018 | **14529** | — |
| PARCELA 11 | 25/05/2018 | **14530** | — |

Onze minutos depois (13:50:04) o operador percebeu e lançou **"12 PARCELAS PAGAS"** em 14526,
que é quem de fato seguiu a cadeia. O processo hoje está em **20799, status 2 (Pago
Integralmente)**, baixado em 20/10/2020.

> **Ação:** cancelar os **quatro** (15 – erro de cadastro). Confirmar com a CCD que as 12
> parcelas ficaram contempladas no lançamento único de 14526 — a cadeia terminou quitada, o que
> indica que sim.

### Caso 5 — Processo 701054/2012 · débito **15555**
**João Batista de Pontes** (CPF ***.340.814-**) · R$ 6.943,98

**Corrige a sugestão do chamado** ("manter o 15554 cancelado e registrar o 15555 como débito
anterior do próximo da sequência"). O mesmo pagamento (20/07/2018, justificativa "parcelado")
foi registrado duas vezes no pai 14475, criando 15554 e 15555. **15554, embora cancelado
(status 15), é quem tem filho — 15556 — e é por ele que a cadeia continua** (15556 → … →
**20861, status 2, Pago Integralmente**, em 27/05/2022).

> **Ação:** apenas **cancelar 15555**. Não religar à sequência — a cadeia já está íntegra por
> 15554 → 15556, e religar o órfão criaria um segundo ramo.

### Caso 6 — Processo 005337/2010 · débito **15601** ⚠️
**Daize Florencio da Costa Correia** (CPF ***.186.134-**) · R$ 21.780,58

Confirma a leitura do chamado ("co-irmão 15600 com a mesma configuração"). Duas parcelas
distintas (31/07/2018 e 23/08/2018, ambas "parcelado") foram registradas no pai 14535, criando
15600 e 15601 — **com `valorOriginalDebito` exatamente igual: R$ 21.780,5809**.

Aqui está a diferença em relação aos outros casos: o pai 14535 partiu de R$ 22.689,02 e os dois
filhos ficaram em R$ 21.780,58 — **uma única redução de R$ 908,44 para duas parcelas
registradas**. A cadeia seguiu por 15600 → 15602 (R$ 20.876,85, −R$ 903,73). A parcela de
23/08/2018 **não reduziu saldo em ponto nenhum da cadeia viva**.

> **Ação:** cancelar **15601** — mas **antes** verificar se a parcela de 23/08/2018 (~R$ 908)
> foi abatida em outro lugar. É o único dos 13 casos em que o cancelamento puro e simples pode
> deixar valor sem abatimento. Mitigante: o processo fechou em **20799, status 2 (Pago
> Integralmente)**, o que sugere regularização posterior — mas convém confirmar o extrato do
> parcelamento.

### Caso 7 — Processo 700985/2012 · débito **15607**
**José de Arimateia Braz** (CPF ***.776.084-**) · R$ 27.341,73

Confirma a sugestão do chamado ("origina-se de cadeia já cancelada"). Dois pagamentos
(26/10/2017 e 21/11/2017, "parcelado") registrados no pai 4988 criaram 15606 e 15607.

**Toda a cadeia foi cancelada por erro de cadastro:** 4988, 15606, 15608 a 15621, 16409 a 16413
— todos em status 15. O débito foi **recadastrado do zero** em 01/02/2024 como **27106, status
1 (Em Aberto), R$ 27.448,00** (o valor original íntegro). **15607 é o único registro da cadeia
antiga que escapou do cancelamento em massa.**

> **Ação:** cancelar **15607** com status 15 (erro de cadastro), igualando ao restante da
> cadeia. Sem impacto financeiro: o débito vigente é o 27106.

### Caso 8 — Processo 700722/2011 · débito **16089**
**Josiano Ribeiro Bilro da Silva** (CPF ***.888.904-**) · R$ 12.531,21

Confirma a sugestão do chamado ("16087 já representa a hierarquia correta"). "PAGAMENTO
PARCELADO – PARCELA 2" e "PARCELA 3" foram registradas no pai 16084 em 30/05/2019, com **a mesma
`DataOperacao` (09/08/2018)**, criando 16087 e 16089. 16087 recebeu `ValorPago` R$ 100,00 e
seguiu para 16090; 16089 ficou órfão.

A cadeia atual do processo está em **17983, status 1 (Em Aberto), R$ 11.254,66**.

> **Ação:** cancelar **16089** (15 – erro de cadastro ou 21 – duplicidade). Sem impacto
> financeiro.

---

## 5. Quadro-resumo para a SETIC

| Débito | Processo origem | Pessoa | Status sugerido | Impacto financeiro |
|---|---|---|---|---|
| 8031 | 012990/2010 | João Valdivino da Costa | 21 ou 15 | não |
| 8032 | 012990/2010 | João Valdivino da Costa | 21 ou 15 | não |
| 8586 | 002743/2008 | João de Deus Garcia de Araújo | 15 | não (conferir guia 10157/2015) |
| 8591 | 002743/2008 | João de Deus Garcia de Araújo | 15 | não (conferir guia 15951/2015) |
| 12258 | 018127/2000 | Pedro Lopes de Moura | 6 (igual a 12257) ou 15 | não |
| 14527 | 005337/2010 | Daize Florencio da Costa Correia | 15 | não |
| 14528 | 005337/2010 | Daize Florencio da Costa Correia | 15 | não |
| 14529 | 005337/2010 | Daize Florencio da Costa Correia | 15 | não |
| 14530 | 005337/2010 | Daize Florencio da Costa Correia | 15 | não |
| 15555 | 701054/2012 | João Batista de Pontes | 15 | não |
| **15601** | 005337/2010 | Daize Florencio da Costa Correia | 15 | **⚠️ verificar parcela de 23/08/2018** |
| 15607 | 700985/2012 | José de Arimateia Braz | 15 | não |
| 16089 | 700722/2011 | Josiano Ribeiro Bilro da Silva | 15 ou 21 | não |

Nenhum ajuste de `IdDebitoAnterior` é necessário: em todos os casos a cadeia viva já está
íntegra pelo irmão que seguiu. Basta cancelar os órfãos.

---

## 6. Conferência

```bash
python -m scripts.analise.debitos_status3_orfaos
```

Lista os órfãos e sai com código 1 enquanto houver algum. Hoje devolve os 13 acima
(R$ 190.631,15); depois dos cancelamentos deve devolver zero e sair com 0. Somente leitura.

---

## Anexo A — Consultas usadas

**Universo do defeito (a consulta que fecha os 13):**

```sql
SELECT d.IdDebito, d.IdDebitoAnterior, d.valorOriginalDebito, d.datainclusao, d.usuarioinclusao
  FROM Exe_Debito d
 WHERE d.CodigoStatusDivida = 3
   AND d.ValorPago IS NULL
   AND NOT EXISTS (SELECT 1 FROM Exe_Debito f      WHERE f.IdDebitoAnterior = d.IdDebito)
   AND NOT EXISTS (SELECT 1 FROM Exe_DebitoBoleto b WHERE b.IdDebito        = d.IdDebito)
```

**Reconstrução do que o operador fez** (o `dataInclusao` da operação bate com o `datainclusao`
do filho que ela gerou):

```sql
SELECT h.IdDebito, h.DataOperacao, h.dataInclusao, h.UsuarioInclusao, h.Justificativa
  FROM Exe_HistoricoDebito h
 WHERE h.IdDebito = :id_pai
 ORDER BY h.dataInclusao
```

**Cadeia completa de um processo** (raiz → folha), para achar o débito vigente:

```sql
SELECT d.IdDebito, d.IdDebitoAnterior, d.CodigoStatusDivida, d.valorOriginalDebito,
       d.ValorPago, d.dataBaixa
  FROM Exe_Debito d
  JOIN Processos po ON po.IdProcesso = d.IdProcessoOrigem
 WHERE po.numero_processo = :numero AND po.ano_processo = :ano
 ORDER BY d.IdDebito
```

---

## Anexo B — Achado colateral: `IdDebitoAnterior IS NULL` não é o débito vigente

Fora do escopo do chamado, mas apurado no mesmo levantamento e com efeito nas análises da
própria CCD.

A convenção usada hoje em vários pontos do repositório é filtrar `e.IdDebitoAnterior IS NULL`
para "pegar o head do débito". **Isso devolve o débito ORIGINAL, não o vigente** — a cadeia
cresce para a frente, então o registro atual é a **folha** (`NOT EXISTS (SELECT 1 FROM Exe_Debito
f WHERE f.IdDebitoAnterior = d.IdDebito)`).

Panorama da tabela:

| | |
|---|---|
| Total de débitos | 27.709 |
| Raízes (`IdDebitoAnterior IS NULL`) | 17.115 |
| Folhas (sem filho) | 17.931 |
| **Raízes que têm filho** | **1.602** |

Nessas **1.602 cadeias**, raiz e folha são registros diferentes e a leitura pela raiz pega status
e saldo errados. Exemplo do próprio processo 002743/2008: a raiz **924** está em status 3 ("Pago
parcialmente", R$ 3.900,00), mas a folha da sua cadeia é **17476, status 2 (Pago Integralmente)**
— pela raiz, a dívida aparece como parcialmente paga quando já está quitada.

Pontos do repositório que usam a convenção da raiz:

- `scripts/analise/carteira_ipsas.py`
- `scripts/analise/debitos_nereu.py`, `atualizar_debitos_nereu_definitiva.py` e demais scripts nereu
- `ccd/sql/processos_transito_nome.sql` e `scripts/consultas/processos_transito_cpf.sql`
- `processos/nereu_desconto_folha/gerar.py`

Registrado aqui como pendência. **Nenhum desses arquivos foi alterado neste trabalho** — a
correção exige decidir caso a caso se a análise quer o débito original (valor da condenação) ou o
vigente (saldo atual), e dimensionar o efeito nos números já publicados.
