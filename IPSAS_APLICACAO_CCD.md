# IPSAS aplicado aos dados da CCD

> Mapa de onde as normas internacionais de contabilidade do setor público (IPSAS) encontram dados
> reais neste repositório, com um exercício prático por norma. Perspectiva única: **o TCE/Estado
> como entidade que reporta** — auditoria de convergência dos jurisdicionados está fora de escopo.
> Gerado em 03/08/2026.

---

## 1. Por que este repositório serve de laboratório

A CCD não se enxerga como área contábil, mas o que ela administra é, em termos de norma, uma
**carteira de créditos de transações sem contraprestação**: multas e ressarcimentos impostos por
decisão do Tribunal. Isso é o objeto literal da IPSAS 23, que cita multas nominalmente.

E o repositório já tem, sem precisar de nenhum dado novo, os quatro momentos do ciclo de vida
contábil de um ativo financeiro:

| Momento contábil | Onde está |
|---|---|
| Reconhecimento | `Exe_Debito.dataTransito` — o trânsito em julgado é o fato gerador |
| Mensuração | `valorOriginalDebito`, `ValorPago` |
| Deterioração | prescrição, protesto, dívida ativa, parcelamento cancelado |
| Baixa / realização | `CodigoStatusDivida`, arrecadação conciliada no FRAP |

A diferença entre a lente de cobrança (que a CCD já usa) e a lente contábil é justamente o objeto do
estudo: a cobrança pergunta "esse processo está andando?"; a norma pergunta "quanto desse ativo a
entidade realmente espera receber?". Ninguém no fluxo atual responde à segunda.

## 2. O que o primeiro exercício já produziu

`scripts/analise/carteira_ipsas.py` classifica os 16.249 créditos vivos e mede a carteira em
03/08/2026:

| Indicador | Valor | Créditos |
|---|---:|---:|
| Ativo reconhecido, bruto (IPSAS 23) | R$ 356,7 mi | 10.387 |
| (–) Provisão para perdas esperadas (IPSAS 41) | R$ 315,9 mi | — |
| **Ativo reconhecido, líquido** | **R$ 40,8 mi** | 10.387 |
| Ativo contingente, apenas divulgado (IPSAS 19) | R$ 286,5 mi | 1.436 |
| Perdas históricas acumuladas | R$ 61,1 mi | 2.018 |
| Receita efetivamente recuperada | R$ 5,1 mi | 3.185 |
| Desreconhecido por decisão superveniente | R$ 10,0 mi | 653 |

**A taxa de provisão é de 88,6%, e passa de 90% em todas as faixas de aging.** O número não é
artefato de classificação: historicamente, de cada R$ 100 que saem da carteira com desfecho
definitivo, cerca de R$ 90 saem como perda e R$ 10 como caixa. A razão aparece na mediana — multas
efetivamente pagas têm mediana de R$ 600, enquanto ressarcimentos prescritos têm mediana de
R$ 10.252. O Tribunal recebe as dívidas pequenas e perde as grandes.

Esse é o tipo de afirmação que só a lente contábil produz, e é matéria de nota explicativa, não de
despacho.

## 3. Mapa norma → dado → exercício

| Norma | O que ela exige | Dado que materializa | Exercício prático |
|---|---|---|---|
| **IPSAS 23** — Receita de transações sem contraprestação | Multas geram ativo e receita quando a entidade controla o recurso e o influxo é provável e mensurável | `Exe_Debito.dataTransito`, `Processo_TransitoJulgado` | *Feito.* Defender por que o trânsito em julgado — e não a decisão nem a citação — é o momento do reconhecimento |
| **IPSAS 19** — Ativos contingentes | Ativo provável mas não controlado: divulga, não reconhece | débitos com `dataDecisao` e sem `dataTransito`; `Pro_Marcador` (sobrestamento) | *Feito.* Os R$ 286,5 mi contingentes: quais viram ativo e em quanto tempo? |
| **IPSAS 41** — Instrumentos financeiros | Perda de crédito esperada por matriz de provisão; mensuração ao custo amortizado | `CodigoStatusDivida`, 28 anos de coortes de trânsito | *Feito (parcial).* Falta o ajuste a valor presente dos parcelamentos longos |
| **IPSAS 1 / 2 / Estrutura Conceitual** | Definição de ativo e de receita; apresentação; fluxo de caixa | arrecadação conciliada no FRAP | Confrontar o regime de competência (carteira) com o de caixa (extrato bancário) e explicar a diferença |
| **IPSAS 24** — Informação orçamentária | Comparação entre orçado e realizado | `FRAPLancamento` (categorias 1/2/3/9), `web/tools/frap/` | Montar o demonstrativo de arrecadação prevista × realizada do FRAP |
| **IPSAS 9** — Receita com contraprestação | Separar receita de troca da receita sem contraprestação | categorias do `FRAPLancamento` | Segregar, dentro da arrecadação, o que é multa do que é taxa por serviço |
| **IPSAS 39** — Benefícios a empregados | Obrigação de benefício pós-emprego | caso Nereu/IPERN: `planilha_nereu.py`, `verbas_transitorias_dap.py` | Ler os atos de aposentadoria e as verbas transitórias como obrigação atuarial do RPPS |
| **IPSAS 33** — Primeira adoção | Transição para o regime de competência | contexto da convergência NBC TSP no RN | Enquadramento — por que o Estado ainda não reconhece esses créditos assim |

## 4. Decisões contábeis embutidas no script

Três julgamentos que o banco não faz e a norma exige. Estão no código, mas o raciocínio é aqui:

**1. Cancelamento não é uma coisa só.** O `Exe_StatusDivida` tem 13 códigos de "Cancelada" tratados
como equivalentes. Contabilmente são três coisas distintas:

- *Perda de crédito* (prescrição, perdão, óbito do gestor, extinção): o ativo existia e não entrou.
  É o que calibra a matriz de provisão do IPSAS 41 — R$ 61,1 mi.
- *Desreconhecimento* (decisão do relator, novo acórdão, decisão judicial): o direito deixou de
  existir. É reversão de receita, não perda de crédito — R$ 10,0 mi. Somar isso à perda inflaria a
  provisão em 16%.
- *Nunca foi ativo* (erro de cadastro, duplicidade, unificação, reabertura): sai da base inteira.

**2. Sem trânsito não há ativo, mesmo cancelado.** Um crédito sem trânsito só é contingente enquanto
está vivo; se já foi cancelado, nunca chegou a existir nem como contingência.

**3. Pagamento parcial reduz o saldo.** Os 1.361 créditos pagos parcialmente já devolveram R$ 1,96 mi
ao erário. Contá-los pelo valor cheio inflaria o ativo e a provisão ao mesmo tempo — corrigir isso
derrubou a taxa de provisão de 93,6% para 88,6%.

O grão de tudo é o **débito, não a pessoa**: `Exe_DebitoPessoa` liga N responsáveis solidários ao
mesmo crédito, e juntar essa tabela multiplicaria a carteira. Solidariedade é matéria de divulgação,
não de mensuração.

## 5. Limitações a registrar antes de usar qualquer número

- **IPSAS ≠ NBC TSP ponto a ponto.** A norma aplicável no Brasil é a NBC TSP convergente, e a
  correspondência não é integral. Confirmar a numeração e as diferenças de cada par antes de citar
  em documento oficial — este documento usa a numeração IPSAS de propósito, por ser a da certificação.
- **A carteira está a valor histórico.** `ValorAPagar` existe na tabela mas está NULL em 10.144 dos
  10.155 créditos em aberto: o campo nunca foi alimentado. Não há saldo atualizado no banco, então
  correção monetária e juros não entram. Isso *subestima* o ativo bruto.
- **A taxa de perda é retrospectiva, não prospectiva.** A norma pede expectativa de perda; a matriz
  aqui usa o histórico observado. Há censura à direita — créditos antigos ainda em aberto podem vir
  a prescrever, o que subestima as faixas longas. Corrigir com análise de sobrevivência
  (ver L2 em `LINHAS_DE_PESQUISA.md`, que ataca o mesmo dado por outro ângulo).
- **O TCE não fecha as demonstrações do Estado.** O produto aqui é insumo para a contabilidade
  estadual e para a própria auditoria — não é a demonstração.

## 6. Próximos exercícios, em ordem de proveito

1. **Valor presente dos parcelamentos** (IPSAS 41). `Exe_Parcelamento` tem prazo e situação; um
   parcelamento de 60 meses sem juros vale menos que o valor de face.
2. **Conciliação competência × caixa** (IPSAS 1/2). A carteira diz o que era devido; o FRAP diz o que
   entrou. A diferença entre as duas séries é a prova real da provisão.
3. **Segregação da receita do FRAP** (IPSAS 9 × 23). Qual parte da arrecadação é sanção e qual é
   contraprestação por serviço.
4. **Divulgação dos contingentes** (IPSAS 19). Os R$ 286,5 mi sem trânsito precisam de uma nota que
   explique probabilidade de conversão — hoje não existe estimativa nenhuma.

---

*Como reproduzir os números deste documento:*

```
python -m scripts.analise.carteira_ipsas --self-check          # valida a lógica, sem banco
python -m scripts.analise.carteira_ipsas --data-corte 2026-08-03
```

Saída em `saidas/analise/ipsas/carteira_ipsas_<AAAAMMDD>.xlsx`, abas `carteira`, `matriz_ecl`,
`resumo`.
