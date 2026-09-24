# POP-CCD-013 — Monitoramento de obrigações e recomendações

| Campo | Valor |
|---|---|
| **Código** | POP-CCD-013 |
| **Versão** | 0.1 (minuta) |
| **Data de emissão** | 04/09/2026 |
| **Elaborado por** | CCD |
| **Aprovado por** | _pendente de aprovação_ |
| **Próxima revisão** | 03/2027 |

> **MINUTA PARA VALIDAÇÃO.** Antes da aprovação, conferir o número do item da seção "Monitoramento" da NBASP 100 no documento oficial do IRB (ver §3).

## 1. Objetivo

Acompanhar o cumprimento das obrigações de fazer ou não fazer e das recomendações fixadas nas deliberações do Tribunal, a partir do acervo já extraído e revisado no CGAD, de modo que cada item tenha uma situação conhecida — prazo não iniciado, prazo em curso, prazo vencido ou situação a apurar — e um próximo ato definido.

## 2. Escopo

Todas as obrigações e recomendações **curadas**, isto é, aprovadas na revisão por decisão do CGAD (`Status = 'approved'` em `ObrigacaoStaging` e `RecomendacaoStaging`, no BdDIP).

O escopo **não** é o conjunto de processos hoje lotados na CCD. O acervo curado acompanha a decisão, não a tramitação: na medição de 04/09/2026, dos 813 itens curados apenas 31 estavam em processo com setor atual CCD, enquanto 216 estavam em processos já arquivados. A competência do art. 32 da Res. 042/2024 é sobre o cadastro e o monitoramento, e não se extingue quando o processo sai do setor.

Ficam fora, por competência de outra unidade (Res. nº 042/2024-TCE, art. 32, I e II, parte final):

- obrigações e recomendações que envolvam implicações mais amplas **e** demandem relatório adicional da unidade técnica que realizou a fiscalização — as duas condições são cumulativas;
- as relativas a atos de pessoal sujeitos a registro (DAP).

## 3. Referências normativas

### Normas de auditoria

O TCE/RN aderiu às Normas Brasileiras de Auditoria do Setor Público (NBASP), expedidas pelo Instituto Rui Barbosa, pela **Resolução nº 010/2020-TCE, de 07 de julho de 2020**. Nas NBASP, o *follow-up* tem nome próprio: **Monitoramento**.

- **NBASP 100 (ISSAI 100)** — Princípios Fundamentais de Auditoria do Setor Público, entre os princípios relacionados ao processo de auditoria, seção **"Monitoramento"**:

  > As EFS têm um papel no monitoramento das ações tomadas pela parte responsável em resposta às questões levantadas em um relatório de auditoria. O foco do monitoramento está em verificar se a entidade auditada deu tratamento adequado às questões levantadas, incluindo quaisquer implicações mais amplas. Ações insuficientes ou insatisfatórias por parte da entidade auditada podem exigir um relatório adicional por parte da EFS.

- **NBASP 300 (ISSAI 300)**, item 42 — Monitoramento:

  > Os auditores devem monitorar achados e recomendações de auditorias anteriores sempre que apropriado.

Registre-se que a repartição de competência do art. 32, I e II, da Res. nº 042/2024-TCE reproduz o vocabulário da NBASP 100: fica fora da CCD o item que envolva **"implicações mais amplas"** e demande **"relatório adicional"** da unidade técnica. A norma interna já é, nesse ponto, a norma de auditoria aplicada.

_Pendência desta minuta: o número do item da seção "Monitoramento" na NBASP 100 não foi confirmado em fonte oficial e por isso a citação é feita pelo nome da seção. Conferir no PDF do IRB antes da aprovação._

### Normas internas

- **Regimento Interno** (Res. nº 009/2012-TCE, atualizado até a Res. nº 46/2024):
  - art. 288 — monitoramento é o instrumento de fiscalização para verificar o cumprimento das deliberações do Tribunal e os resultados delas advindos;
  - art. 296, II e III — encaminhamento ao órgão responsável pelo CGR para fins de monitoramento;
  - art. 299 e §§ 1º e 2º — Cadastro Geral de Recomendações (CGR), de consulta obrigatória pelas unidades técnicas, com apontamento da inobservância nos relatórios de períodos subsequentes;
  - art. 431, IV, "c" — o CGR integra o Cadastro Geral de Acompanhamento de Decisões (CGAD), para acompanhamento permanente das decisões de obrigação de fazer ou não fazer.
- **Res. nº 028/2012-TCE** (atualizada até a Res. nº 013/2015), Capítulo III:
  - art. 27 — a execução de obrigação de fazer ou não fazer se dá em **decisão definitiva**, por processo próprio de monitoramento;
  - art. 28 — constituição e instrução do processo de monitoramento;
  - art. 31 — cabe ao **Relator** atestar o cumprimento, mediante prova apresentada pelo responsável e após pronunciamento do corpo técnico;
  - art. 32 — cumprida a obrigação, o processo de monitoramento é arquivado;
  - art. 33 — cumprimento intempestivo com previsão de multa de mora enseja processo de execução;
  - art. 45 — alimentação do CGAD.
- **Res. nº 042/2024-TCE** (Regulamento da SECEX), art. 30, III e art. 32, I e II.

## 4. Definições e siglas

- **Item curado**: obrigação ou recomendação extraída da decisão e **aprovada na revisão humana** do CGAD. A linha de *staging* é o registro da revisão: guarda o revisor, a data e o texto original proposto pelo modelo antes da edição.
- **CGR**: Cadastro Geral de Recomendações (art. 299 do Regimento Interno), integrante do **CGAD** (art. 431, IV).
- **Triagem**: classificação determinística do item curado quanto ao estado do prazo. Não usa modelo de linguagem.
- **Varredura**: leitura assistida por modelo de linguagem das peças posteriores à decisão, à procura de prova de cumprimento. É **insumo de trabalho**, não juízo de cumprimento.
- **Ficha de monitoramento**: documento por processo que reúne a decisão, os itens curados, a triagem e o resultado da varredura.

## 5. Responsabilidades

- **Revisor do CGAD**: aprovar ou rejeitar a extração, produzindo o acervo curado que alimenta este procedimento.
- **Servidor da CCD**: executar a rotina, ler a ficha, decidir o próximo ato de cada item e registrar no CGR.
- **Coordenador da CCD**: priorizar a fila e decidir sobre a instauração de processo de monitoramento (Res. 028/2012, art. 28).
- **Relator**: atestar o cumprimento (Res. 028/2012, art. 31). **A CCD não atesta cumprimento.**

## 6. Recursos e sistemas

- `scripts/analise/monitoramento_obrigacoes.py` — rotina de triagem, varredura e geração das fichas.
- `BdDIP` — `ObrigacaoStaging`, `RecomendacaoStaging` (acervo curado); `processo` — `Processos`, `Processo_TransitoJulgado`, `vw_ata_informacao`, `Obg_Obrigacao` (CGR).
- Área Restrita / e-Contas — conferência da tramitação e das comunicações recentes, que o banco reflete com atraso.
- Modelo de linguagem: exclusivamente o DeepSeek do Azure AI Foundry do SERPRO, por exigência de LGPD.

## 7. Descrição das atividades

1. **Executar a triagem.** `python scripts/analise/monitoramento_obrigacoes.py --sem-llm`. Produz a planilha `monitoramento.xlsx` e uma ficha por processo. Cada item recebe uma situação:

   | Situação | Significado | Leitura |
   |---|---|---|
   | `SEM_TRANSITO` | não há trânsito em julgado | o prazo ainda não corre (Res. 028/2012, art. 27); não é inércia |
   | `PRAZO_EM_CURSO` | trânsito ocorrido, vencimento futuro | acompanhar |
   | `PRAZO_VENCIDO` | trânsito ocorrido, vencimento passado | verificar cumprimento |
   | `PRAZO_INDETERMINADO` | prazo ausente, ilegível, ou contado de âncora sem data | leitura humana |

   Duas marcas acompanham a situação sem competir com ela: **processo arquivado** e **sem registro no CGR**.

2. **Executar a varredura**, em lotes: `--limite N`. A rotina prioriza prazo vencido, depois processo arquivado, depois ausência de registro no CGR. Cada processo já varrido é pulado nas rodadas seguintes.

3. **Ler a ficha do processo.** Conferir a obrigação transcrita, o prazo e a data de vencimento calculada.

4. **Decidir o próximo ato**, entre:
   - cadastrar o item no CGR, quando ausente (art. 299 e art. 431, IV, "c");
   - instaurar processo de monitoramento (Res. 028/2012, art. 28);
   - submeter ao Relator para atestar o cumprimento (art. 31);
   - instaurar execução, no cumprimento intempestivo com multa de mora prevista (art. 33);
   - encaminhar à unidade técnica ou à DAP, quando o item estiver fora da competência da CCD (§2).

5. **Registrar** o ato praticado no CGAD (Res. 028/2012, art. 45).

## 8. Registros

- `output/analise/monitoramento_obrigacoes/monitoramento.xlsx` — um registro por item curado, com triagem e resultado da varredura.
- `output/analise/monitoramento_obrigacoes/fichas/ficha_<processo>.md` — ficha por processo.
- `output/analise/monitoramento_obrigacoes/varredura/<processo>.json` — saída bruta da varredura, com as peças lidas e as citações.
- Registro no CGR e no CGAD, na Área Restrita / e-Contas.

## 9. Pontos de controle e exceções

- **A varredura não atesta cumprimento.** Quem atesta é o Relator (Res. 028/2012, art. 31). O resultado da varredura é indício que orienta a leitura, nunca fundamento de arquivamento.
- **Ausência de prova nos autos não é prova de descumprimento.** A rotina responde `SEM_ELEMENTOS` por padrão e só registra descumprimento quando alguma peça o afirma.
- **Citação conferida.** Toda citação devolvida pelo modelo é confrontada com o texto das peças efetivamente lidas; a que não é encontrada faz a avaliação ser rebaixada a `SEM_ELEMENTOS`, e a ficha registra o descarte. O controle não é teórico: na primeira rodada real, o processo 000926/2022 recebeu duas avaliações "cumprida" com confiança alta citando trecho inexistente, ambas rebaixadas pela conferência.
- **Varredura parcial.** Processos com muitas peças não cabem em uma só leitura. A ficha e o JSON informam quantas peças foram lidas de quantas existem; quando a varredura for parcial em caso relevante, reexecutar com `--orcamento` maior.
- **Prazo em dias úteis** é contado sem calendário de feriados. Em caso concreto que dependa da diferença, conferir manualmente.
- **Prazo contado da cientificação** não é calculado: o script não dispõe dessa data e classifica o item como `PRAZO_INDETERMINADO` em vez de estimar. Nesses casos vale a advertência do levantamento de obrigações sem citação — sem cientificação do responsável, o prazo não corre e a obrigação é inexigível.
- **O banco atrasa em relação à Área Restrita.** Para tramitação e comunicações recentes, a Área Restrita é autoritativa.
- **Cobertura temporal.** O acervo curado cobre apenas as decisões já revisadas no CGAD, e cresce a cada revisão. É um piso, não o universo das obrigações do Tribunal.
- **Situação do CGR na emissão desta minuta (04/09/2026).** Dos 813 itens curados, apenas 16 pertenciam a processo com algum registro em `Obg_Obrigacao`, e a última inclusão no cadastro datava de 07/02/2025. O cadastro que o art. 299 manda manter estava sem alimentação, e esse é o principal achado que motivou este procedimento.

## 10. Histórico de revisões

| Versão | Data | Alteração |
|---|---|---|
| 0.1 | 04/09/2026 | Minuta inicial — monitoramento do acervo curado do CGAD, ancorado na NBASP 100. |
