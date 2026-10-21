# Monitoramentos na CCD: natureza e próximos passos

**Posição em 21/10/2026.** Universo: processos com `setor_atual = 'CCD'` (sem apensados) do tipo **MON** (17) ou com o marcador CCD **5734 "Monitorar obrigação de fazer"** (24 de outros tipos: APR, AUD, CGE, REP, PEN, OFC, EXE). Total: **41**. Ficaram fora os acompanhamentos de desconto em folha/FRAP (5953, 5469), "NEREU - verificar data" (6039) e "DECISÃO JUDICIAL - Acompanhamento" (5966).

Fontes: banco `processo` (peças da `vw_ata_informacao` e texto dos PDFs, tramitações, marcadores, `Exe_Debito`). A leitura foi feita sem LLM. "Dias na CCD" conta da última entrada DIP→CCD. Datas de mora e tetos são estimativas da leitura e **precisam ser conferidos antes de qualquer liquidação**.

## Pontos transversais

1. **Teto da cominatória: falta definir o critério.** Os acórdãos do lote citam o art. 323, II, "b" do RI. A CCD usou no 002234/2024 o valor máximo da Portaria **do ano do acórdão**. Outra leitura usa o art. 323, II, "f": 50%, ou R$ 10.746,54 em 2026 pela Portaria 007/2026. Fixar um critério antes de liquidar o 003632, 002459, 000599, 002893, 001834, 003442, 004339 e 101227.
2. **A DCD devolveu tudo em 28/05/2026.** Foram 12 processos (MON e APR) com o mesmo despacho, invocando o art. 30, III, da Res. 042/2024: monitoramento sem novo relatório é da DIP/CCD. Não cabe reenviar à DCD. Exceções que dependem de outra unidade: 001877/2020 (recursos pendentes), 001305/2020 (sem mérito), 004339/2019 (o acórdão manda a DCP monitorar) e 003973/2025 (a CCD decidiu remeter à DCD no Ev. 21, mas a tramitação nunca saiu).
3. **Lote Portal da Transparência 2019: 20 processos** (7 MON + 13 APR). A jurisprudência recente afasta a multa diária com base na LINDB, art. 22, §1º, e na série histórica de 3 anos do PNTP: Ac. 686/2025, 40, 82, 96, 140, 171 e 223/2026. Em sentido contrário, os Ac. 456/2026 e 602/2025 (obrigação ainda descumprida) e o Ac. 238/2026 (o cumprimento superveniente não elide as astreintes vencidas). Dá para fazer a aferição dos portais e as informações em lote, com um gerador único no estilo `processos/utils/gerar_informacoes_*.py`, em três variantes:
   - **(a) citado e revel:** liquidação e alternativa LINDB;
   - **(b) sem citação da gestão atual:** prejudicialidade ou citação;
   - **(c) com resposta:** análise.
4. **Marcadores e peças a corrigir:**
   - 000629/2026: é uma EXE quitada; a obrigação de fazer é do 000906/2020.
   - 300734/2026: o ofício deve ser juntado ao MON 003973/2025.
   - 001877/2020: o processo não transitou.
   - 002234/2024: o débito 28768 está vinculado à execução 002002/2024, que está arquivada.
   - 009050/2018: a informação da CCD no Ev. 224 descreve outro processo (Labinbraz/SESAP).
   - 000924/2020: o relatório cita o "Ac. 118/2021", mas o correto é o 108/2021.

## Fila de ação sugerida

| # | Ação | Processos |
|---|------|-----------|
| 1 | **Liquidar a cominatória, cadastrar o débito tipo 5 e instaurar a execução** (há ordem do relator ou a mora está acima do teto) | **003632/2024** (o teto de R$ 20 mil é atingido em 26/10/2026), 002459/2023, 000599/2026 |
| 2 | **Levar o fato novo ao relator antes de cadastrar** | 002893/2025 (parcelamento CADPREV juntado em 09/10/2026) |
| 3 | **Cobrança parada** (citação do art. 117 / execução) | 002234/2024 (débito 28768), 000908/2020 (multa sem citação desde 07/2023), 000742/2020 (parcelamento cancelado, 467 dias na CCD) |
| 4 | **Informação de descumprimento com cominatória correndo** | 004339/2019 (R$ 1.000/dia desde 25/04/2026), 101227/2022 (R$ 50/dia) |
| 5 | **Analisar resposta ou prova já juntada** | 003973/2025 + 300734/2026, 003974/2025, 001513/2024, 000537/2026, 004079/2021, 009050/2018, 007970/2018, 014254/2015, 001311/2020, 007869/2019, 006688/2019, 006945/2019 |
| 6 | **Aferir o portal e fazer informação em lote** (Portal 2019) | 001834/2024, 003442/2025, 004809/2024, 000137/2026, 000454/2026, 006683/2019, 006940/2019, 002056/2020, 002074/2020 |
| 7 | **Verificar o envio das contas de gestão no SIAI** (dá para fazer de uma vez) | 002365/2023, 000599/2026, 002459/2023, 002967/2018 (no 002967, a notificação do gestor atual também não foi expedida) |
| 8 | **Formalizar o cumprimento** (obrigação satisfeita antes do trânsito) | 017807/2014, 200192/2021, 005106/2020 (é só recomendação: CGAD) |
| 9 | **Só tramitar ou encerrar** | 000924/2020 (relatório pronto → GCGIL), 000629/2026 (quitada → GCPOT, tirar o marcador), 001877/2020 (devolver para os recursos) |
| 10 | **Acompanhar** | 000523/2021 (parcelamento 3/24 em dia), 014254/2015 (TAG: última comprovação até 25/12/2026) |

## Quadro-resumo

| Processo | Tipo | Relator | Jurisdicionado | Natureza | Próximo passo | Urg. |
|---|---|---|---|---|---|---|
| 000523/2021 | MON | Ana Paula | EMGERN | Ac. 196/2026: multa parcelada em 24x | Acompanhar as parcelas e certificar | baixa |
| 004079/2021 | MON | Ana Paula | EMGERN | Ac. 413/2021: governança (Lei 13.303) | Analisar o apensado 300619/2025 e fazer informação de cumprimento | média |
| 002365/2023 | MON | Ana Paula | Pref. Taipu | Ac. 522/2021: contas de gestão 2015 | SIAI: enviou? Se sim, arquivar; se não, multa do art. 107 + nova cominatória | média |
| 002459/2023 | MON | Antonio Ed | F. Nilo Pereira / Pref. Ceará-Mirim | Ac. 317/2021: contas de gestão 2019 | Liquidar no teto, cadastrar e executar (Antônio Henrique) | alta |
| 001513/2024 | MON | Renato | Pref. Pau dos Ferros | Ac. 88/2021: obras paralisadas | Analisar a manifestação (Ev. 40–47) | média |
| 001834/2024 | MON | Marco Antônio | Pref. Fernando Pedroza | Portal 2019 (Ac. 191/2020) | Liquidação ou LINDB ao relator | média |
| 002234/2024 | MON | Marco Antônio | Pref. Doutor Severiano | Portal 2019 (Ac. 229/2022) | Citar (art. 117) e corrigir o vínculo do débito 28768 | alta |
| 003632/2024 | MON | Gilberto Jales | SEEC | Ac. 88/2021: obras (Galinhos) | Liquidar R$ 500/dia (teto R$ 20 mil), cadastrar e executar | **alta** |
| 004809/2024 | MON | Potiguar | Câm. Grossos | Portal 2019 (Ac. 174/2021) | Aferir o portal: arquivar ou citar a gestão atual | baixa |
| 002893/2025 | MON | Antonio Ed | Pref. Senador Elói de Souza | Ac. 29/2025: débito previdenciário do RPPS | Fato novo + liquidação ao relator | alta |
| 003442/2025 | MON | Antonio Ed | Pref. Patu | Portal 2019 (Ac. 31/2021) | Liquidação ou LINDB ao relator | média |
| 003973/2025 | MON | Paulo Roberto | DETRAN | Ac. 213/2025: FUNSET/PASEP/CTB | Analisar a resposta tempestiva (com o OFC 300734) | alta |
| 003974/2025 | MON | Carlos Thompson | CONTROL | Ac. 331/2023: anexo bimestral 2016 | Informação conclusiva (enviaram o RREO, não o anexo) | média |
| 000137/2026 | MON | Gilberto Jales | Pref. São Pedro | Portal 2019 (Ac. 68/2023) | Prejudicialidade (Ac. 686/2025) ou citação | baixa |
| 000454/2026 | MON | Renato | Câm. Caiçara do Norte | Portal 2019 (Ac. 12/2021) | Encerrar sem cominatória (sinalizado pelo relator) | baixa |
| 000537/2026 | MON | Paulo Roberto | Pref. Pau dos Ferros | Portal 2019 (Ac. 369/2021) | Analisar a alegação de impossibilidade | média |
| 000599/2026 | MON | Antonio Ed | Câm. Serra de São Bento | Ac. 174/2025: contas de gestão 2015 | SIAI: se não enviou, liquidar no teto e executar | alta |
| 017807/2014 | APR | Potiguar | Câm. São Tomé | Ac. 209/2017: SIAI-DP 2013/14 | Formalizar o cumprimento (anterior ao acórdão) | média |
| 006683/2019 | APR | Antonio Ed | Câm. Alexandria | Portal 2019 (Ac. 10/2021) | Aferir o portal e dar baixa da multa quitada | alta |
| 006688/2019 | APR | Ana Paula | Câm. Apodi | Portal 2019 (Ac. 310/2020), R$ 200/dia | Responder aos quesitos do MPC e aferir | alta |
| 006940/2019 | APR | Gilberto Jales | Pref. Campo Redondo | Portal 2019 (Ac. 49/2022) | Aferir o portal (gestão atual) | alta |
| 006945/2019 | APR | Renato | Pref. Caraúbas | Portal 2019 (Ac. 335/2020) | Ler o doc. 301616/2026 e aferir | média |
| 007869/2019 | APR | Gilberto Jales | Câm. Ielmo Marinho | Portal 2019 (Ac. 341/2023) | Analisar o doc. 300680/2025 e dar baixa da multa | média-alta |
| 000742/2020 | APR | Paulo Roberto | Câm. Janduís | Portal 2019 (Ac. 186/2021) | Executar a multa e reconhecer o cumprimento | alta |
| 000908/2020 | APR | Renato | Pref. Passa e Fica | Portal 2019 (Ac. 368/2021) | Citar pelo art. 117 e aferir | alta |
| 000924/2020 | APR | Gilberto Jales | Câm. Lagoa Salgada | Portal 2019 (Ac. 108/2021) | Tramitar o relatório pronto (corrigir o nº do acórdão) | média |
| 001305/2020 | APR | Marco Antônio | Pref. Rio do Fogo | Portal 2019, cautelar (Ac. 31/2022) | Informação conclusiva aos quesitos do MPC | alta |
| 001311/2020 | APR | Renato | Pref. Santo Antônio | Portal 2019 (Ac. 35/2021 + monocrática de 12/2025) | Analisar a resposta do Ev. 124 | alta |
| 001877/2020 | APR | Paulo Roberto | Câm. São Bento do Trairi | Portal 2019 (Ac. 32/2021), sem trânsito | Devolver para os recursos e rever o marcador | média |
| 002056/2020 | APR | Renato | Câm. Serra de São Bento | Portal 2019 (Ac. 27/2025) | Aferir o portal (multa quitada) | média |
| 002074/2020 | APR | Marco Antônio | Câm. Severiano Melo | Portal 2019 (Ac. 506/2024) | Aferir; liquidar desde 23/01/2026 ou LINDB | média-alta |
| 005106/2020 | APR | Ana Paula | Câm. Viçosa | Ac. 8/2022: LRF 2016 (recomendação) | Anotar no CGAD e arquivar | baixa |
| 200192/2021 | APR | Gilberto Jales | IFESP | Ac. 165/2022: anexos SIAI 2016 | Informação de cumprimento (DAI, Ev. 86) | baixa |
| 014254/2015 | AUD | Ana Paula | Câm. Natal | Ac. 142/2025: TAG 001/2025 (CEAPM) | Acompanhamento parcial do TAG | média |
| 002967/2018 | CGE | Potiguar | Câm. Passa e Fica | Ac. 287/2021: contas de gestão 2015 | SIAI + notificar o gestor atual | média |
| 007970/2018 | REP | Renato | Pref. Espírito Santo | Ac. 602/2025: acúmulo de cargos | Conferir os 33 processos administrativos | média |
| 009050/2018 | REP | Paulo Roberto | CEASA | Ac. 406/2021: requisitos da Diretoria | Analisar o Ev. 211 e corrigir o Ev. 224 | alta |
| 004339/2019 | REP | George | Pref. Vila Flor | Ac. 196/2025: temporários | Descumprimento do item c + DCP | alta |
| 101227/2022 | PEN | Marco Antônio | MACAUPREV | Decisão 637/2025: regularizar a pensão | Descumprimento + liquidar R$ 50/dia | alta |
| 300734/2026 | OFC | (Paulo Roberto) | CONTROL/DETRAN | Ac. 213/2025: comunicação de cumprimento | Juntar ao MON 003973/2025 | média |
| 000629/2026 | EXE | Potiguar | Nova Cruz (exec. do 000906/2020) | Multa quitada em 19/10/2026 | Encerrar e tirar o marcador | baixa |

---

# Fichas por processo

## Grupo 1: processos MON (17)

### 000523/2021 — Empresa Gestora de Ativos do RN (EMGERN)
- **Tipo / relator:** MON · Ana Paula de Oliveira Gomes (em substituição: Marco Antônio)
- **Natureza:** monitoramento da obrigação de fazer do Acórdão nº 189/2020-TC (proc. 2674/2020; Portal da Transparência / LAI, 180 dias). Julgado pelo **Acórdão nº 196/2026-TC** (2ª Câmara, 23/06/2026): irregularidade; multa de R$ 6.447,92 a Kathia Frassinetti Palhano de Oliveira (art. 107, II, "b"); recomendação à atual gestão (item 2), com anotação no CGR e eventual novo monitoramento em processo autônomo.
- **Situação atual:** débito 29.187 cadastrado pela CCD (Ev 148) e **parcelado em 24x** (Ev 154, 07/08/2026). Parcelas 2/24 e 3/24 pagas (Ev 170, 17/09/2026; Ev 171, 19/10/2026). Kathia intimada e sem recurso (certidão DE, Ev 158). MPC (Ev 164) considera cumprido o item 2 com a intimação efetiva. Relator (Ev 167, 16/09/2026) mandou à DIP "para monitorar o pagamento das demais parcelas". Marcador: PARCELAMENTO EM CURSO (16/09/2026). Está na CCD há 35 dias.
- **Próximo passo (CCD):** acompanhar as parcelas mensais (próxima em nov/2026) e emitir a certidão de cada pagamento até a 24/24. Nada a fazer quanto à recomendação, que fica no CGR. Se houver inadimplência, seguir o rito de rescisão do parcelamento.
- **Urgência:** baixa. O parcelamento está em dia.

### 004079/2021 — Empresa Gestora de Ativos do RN (EMGERN)
- **Tipo / relator:** MON · Ana Paula de Oliveira Gomes
- **Natureza:** obrigações de fazer do **Acórdão nº 413/2021-TC** (2ª Câmara, Ev 46 do proc. 3452/2020; levantamento sobre o cumprimento da Lei 13.303/2016 pelas estatais): regularizar em 180 dias as desconformidades de governança apontadas no Relatório de Auditoria (Ev 1). Não foi localizada multa cominatória. Data do trânsito: não localizada (a CPACE apenas registra que houve trânsito).
- **Situação atual:** a EMGERN manifestou-se no apensado 300619/2025 (Ev 99) com plano de ação. Essa manifestação **nunca foi examinada**. A CCD (Ev 112, 31/07/2025) entendeu necessária a inclusão no PFA. O MPC (Quota 42/2026) pediu parecer da SECEX. A CPACE (Ev 125) concluiu que não se trata de nova fiscalização, mas de exame documental enquadrado na ação do PACE 2026 da DIP (ID 9.17.2026.057.000). A SECEX acompanhou e a relatora remeteu à DIP (Ev 129, 24/07/2026). Marcador: Monitorar obrigação de fazer (04/08/2026). Está na CCD há 89 dias.
- **Próximo passo (CCD):** analisar a manifestação do apensado 300619/2025 item a item, contra as desconformidades do Relatório de Auditoria (Ev 1) e a Informação nº 016/2024-DAI (Ev 56). Depois, elaborar informação de cumprimento integral, parcial ou descumprimento, com sugestão de encaminhamento (arquivamento ou citação do atual Diretor-Presidente para complementar). Remeter à relatora.
- **Urgência:** média. A pendência é instrutiva, há 3 meses na CCD, e a SECEX/CPACE já atribuíram a tarefa à DIP.

### 002365/2023 — Prefeitura Municipal de Taipu
- **Tipo / relator:** MON · Ana Paula de Oliveira Gomes
- **Natureza:** item "c" do **Acórdão nº 522/2021-TC** (proc. 2927/2018; trânsito em 07/09/2022). Obrigação de entregar, pelo Portal do Gestor e em 40 dias, as **contas anuais de gestão de 2015**, sob pena de multa (art. 107 c/c art. 21 da Res. 012/2016), **multa diária pessoal de R$ 200/dia** (teto do art. 323, II, "b" do RI) e suspensão da certidão de adimplência.
- **Situação atual:** na origem, o atual gestor Ariosvaldo Bandeira Junior foi citado e não respondeu. A cominatória já foi liquidada e executada: **débito 27340, tipo 5, R$ 9.829,92**, mora de 27/04 a 16/06/2023, execução 000447/2024. O MPC (Quota 009/2024, Ev 12) propôs multa (art. 107, II, "f") e renovação da determinação com multa diária majorada. Em 2024 houve busca de antecedentes de Sebastião Ambrósio de Melo (Ev 34/35). A relatora mandou à DCD verificar o item "c" (Ev 43, 17/06/2025). A DCD devolveu em 28/05/2026 alegando competência da DIP (art. 30, III, Res. 42/2024). Marcador: Monitorar obrigação de fazer (29/05/2026). Está na CCD há 145 dias.
- **Próximo passo (CCD):** verificar no SIAI/Portal do Gestor se as contas de gestão de 2015 de Taipu foram enviadas.
  - **Se foram enviadas:** informação de cumprimento (intempestivo) e arquivamento.
  - **Se não foram:** informação à relatora que registre a cominatória já executada no teto e proponha o que o MPC sugeriu: multa do art. 107 e renovação da determinação, com nova multa diária, ao prefeito atual (gestão 2025–2028, nome não localizado), citado na forma do art. 29 da Res. 28/2012.
- **Urgência:** média. Está parado há quase 5 meses, mas a cominatória do ciclo anterior já foi executada.

### 002459/2023 — Fundação (Cultural) Nilo Pereira / Prefeitura de Ceará-Mirim
- **Tipo / relator:** MON · Antonio Ed Souza Santana
- **Natureza:** itens "b" e "c" do **Acórdão nº 317/2021-TC** (1ª Câmara, proc. 4954/2020): entrega das contas anuais de gestão de 2019 da Fundação, ou comprovação de justo impedimento e instauração de TCE em 40 dias, sob **multa diária de R$ 100/dia** (art. 110), limitada ao teto do art. 107, II da LCE 464/2012. A Fundação foi extinta e incorporada à administração direta pela LC Municipal 041/2023, e a responsabilidade passou ao Prefeito de Ceará-Mirim. A cominatória do gestor anterior (Carlos Augusto Borges da Penha) já tem execução: proc. 3706/2020 segundo o relator; débito 25219 vinculado à execução 003706/2022.
- **Situação atual:** o Prefeito foi notificado (Not. 002106/2024, intimação de 25/11/2024; nova Not. 000321/2025) e não se manifestou (certidão DE, Ev 69). O MPC (Parecer 152/2025) pediu a conversão em obrigação de pagar pelo valor máximo da multa diária, com mora desde 17/12/2024. O **despacho do relator de 24/02/2026 (Ev 79)** determinou: (i) remessa à SECEX para excluir a Fundação do rol de jurisdicionados e (ii) à DIP para **instaurar processo autônomo de execução da cominatória contra Antônio Henrique Câmara Bezerra**. Não há tramitação registrada para a SECEX. Não há débito cadastrado em nome dele. Marcador: EXECUÇÃO - Instaurar processo (30/04/2026). Está na CCD há 174 dias.
- **Próximo passo (CCD):**
  1. Liquidar a multa diária. A mora é de mais de 670 dias desde 17/12/2024, portanto **limitada ao teto do art. 107, II** (valor máximo pela Portaria aplicável; conferir o critério de ano).
  2. Cadastrar o débito tipo 5 (`Exe_Debito` + `Exe_Debito_MultaCominatoria`) em nome de Antônio Henrique Câmara Bezerra.
  3. Instaurar a execução e citar na forma do art. 117 (5 dias).
  4. Registrar na informação que a etapa SECEX (exclusão cadastral) ficou pendente.
- **Urgência:** alta. Há determinação expressa do relator desde fev/2026 e o processo está há 174 dias na CCD.

### 001513/2024 — Prefeitura Municipal de Pau dos Ferros (obras paralisadas)
- **Tipo / relator:** MON · Renato Costa Dias (em substituição: Marco Antônio)
- **Natureza:** determinações do **Acórdão nº 88/2021-TC** (Pleno, proc. 6791/2019; levantamento de obras paralisadas), no prazo de 180 dias:
  - "a": proposta de adequação ao art. 45 da LRF na LDO;
  - "b": plano de retomada das obras (Pavimentação da Rua Canadá/Trecho Rua Brasil; Ginásio Poliesportivo 2ª etapa) ou justificativa;
  - "c": cronograma de sistema de controle e registro de obras;
  - "d": informar as obras no relatório de transição;
  - recomendações "g"–"i" (SIAI-Obras).

  Não foi fixada multa cominatória. O MPC (Parecer 356/2025, Ev 36) opinou por multas à gestora Marianna Almeida Nascimento.
- **Situação atual:** a citação 000859/2024 (obrigação de fazer, 180 dias) não foi cumprida no prazo (Ev 30, 08/04/2025). Em 14/07/2026 o Município apresentou **manifestação de cumprimento** (Ev 40–47): LDO com art. 16, §1º (item a); termos de recebimento definitivo das duas obras (2020 e 05/12/2022) e recibos SIAI-Obras (itens b/i); justificativa da demora. O relator (Ev 48, 20/07/2026) pediu análise e pronunciamento da DIP. Marcador: Monitorar obrigação de fazer (29/07/2026). Está na CCD há 84 dias.
- **Próximo passo (CCD):** informação analisando item a item a manifestação dos Ev 40–47.
  - Reconhecer, se confirmada, a perda de objeto do item "b" (obras concluídas).
  - Avaliar se o art. 16, §1º da LDO atende ao item "a".
  - Apontar que os itens "c" (cronograma do sistema de controle de obras) e "d" (relatório de transição) não aparecem comprovados no excerto.
  - Registrar a intempestividade, para que o relator delibere sobre a multa do art. 107, II, "e" proposta pelo MPC.
  - Devolver ao relator.
- **Urgência:** média. Há resposta pendente de análise há quase 3 meses.

### 001834/2024 — Prefeitura Municipal de Fernando Pedroza
- **Tipo / relator:** MON · Marco Antônio de Moraes Rêgo Montenegro
- **Natureza:** lote **Portal da Transparência 2019**. O **Acórdão nº 191/2020-TC** (proc. 7098/2019; trânsito em 06/06/2023) aplicou multas de R$ 4.621,08 e R$ 770,18 a Sandra Jaqueline Jota Ribeiro (execução 003290/2023) e determinou à Prefeitura alimentar o Portal da Transparência em 30 dias, sob **multa diária de R$ 50/dia**, limitada ao teto do art. 323, II, "b" do RI.
- **Situação atual:** houve citação na origem (prazo até 19/10/2023, "obrigação NÃO cumprida") e nova citação (001214/2025, prazo de 14/08 a 25/09/2025), sem resposta (Ev 28). A DCD (Ev 13, 06/05/2025) concluiu pelo **cumprimento parcial**: em 2019 faltam LOA, LDO, prestação de contas, RREO, RGF e ordem cronológica de pagamentos. A DCD citou o PNTP (série histórica). A DCD devolveu à DIP em 28/05/2026 (art. 30, III, Res. 42/2024). Não há cominatória cadastrada. Marcador: Monitorar obrigação de fazer (29/05/2026). Está na CCD há 145 dias.
- **Próximo passo (CCD):** informação ao relator com duas partes.
  - **(i) Liquidação:** mora desde 26/09/2025, ou desde 20/10/2023 se contada a primeira citação, a R$ 50/dia, já **no teto**. Pelo critério usado no 002234/2024 (Portaria do ano do acórdão), o valor máximo de 2020 é R$ 15.403,60; conferir.
  - **(ii) Afastamento:** apontar a linha do Ac. 686/2025 e seguintes (afastamento da cominatória pelo art. 22, §1º da LINDB, já que o PNTP só exige 3 exercícios), para que o relator delibere (art. 34 da Res. 28/2012).
  - Se a cominatória for mantida: cadastrar o débito tipo 5 e executar.
- **Urgência:** média. O teto já foi atingido e não há prescrição imediata, mas o processo está parado há quase 5 meses.

### 002234/2024 — Prefeitura Municipal de Doutor Severiano
- **Tipo / relator:** MON · Marco Antônio de Moraes Rêgo Montenegro
- **Natureza:** lote **Portal da Transparência 2019**. O **Acórdão nº 229/2022-TC** (proc. 7040/2019; de 19/07/2022, trânsito em 19/07/2023) aplicou multas a Francisco Neri de Oliveira (R$ 3.000 + R$ 1.772,83, execução 002002/2024, hoje arquivada) e determinou divulgar as informações em 30 dias, sob multa diária de R$ 100/dia (teto do art. 323, II, "b").
- **Situação atual:** a DCD (Ev 13) e o MPC concluíram pelo cumprimento parcial (falta a lista de exigibilidades de 2019). O relator mandou executar a multa (Ev 23). A **CCD liquidou a cominatória no teto, R$ 17.728,31** (Ev 27, 13/03/2026; **débito 28768, tipo 5**, mora de 05/10/2022 a 12/04/2024). O relator (Ev 30, 17/03/2026) mandou a DE citar Francisco Neri (art. 117, 5 dias). A DE passou por DE_MANDA e devolveu à DIP no mesmo dia 19/03/2026. **Não há mandado juntado.** No banco, o débito 28768 está vinculado à execução 002002/2024, que está **arquivada**. Marcador: CADASTRAR DÉBITO (20/03/2026), aparentemente defasado. Está na CCD há 215 dias.
- **Próximo passo (CCD):**
  1. Confirmar se a citação do art. 117 foi expedida.
  2. Se não foi: devolver à DE para a citação de Francisco Neri e/ou instaurar (ou reativar) o processo autônomo de execução do débito 28768. A vinculação à execução 002002/2024, já arquivada, precisa ser corrigida.
  3. Depois, sugerir o arquivamento do monitoramento.
  4. Atualizar o marcador.
- **Urgência:** alta. Há 7 meses na CCD com débito cadastrado e sem cobrança.

### 003632/2024 — Secretaria de Estado da Educação, da Cultura, do Esporte e do Lazer (SEEC)
- **Tipo / relator:** MON · Antonio Gilberto de Oliveira Jales
- **Natureza:** **Acórdão nº 88/2021-TC** (Pleno, proc. 6791/2019; obras paralisadas: Unidade de Ensino de 6 salas e Quadra Coberta em Galinhos). As determinações "a"–"c" não foram cumpridas (Relatório de Monitoramento 31/2024-ICE). O relator fixou cominatória pessoal à Secretária **Maria do Socorro da Silva Batista**:
  - **Ev 21 (30/06/2025):** R$ 200/dia, limite de R$ 20.000, prazo de 180 dias.
  - **Ev 31 (06/08/2026):** renovação por servidor designado, com prazo de 10 dias úteis para apresentar (a) informações e plano de retomada da obra, ou prova da conclusão, e (b) cronograma do sistema de controle de obras, sob **R$ 500/dia, limite de R$ 20.000**. A DE foi autorizada a constituir de imediato a execução se houvesse nova inércia (com possibilidade de desconto em folha).
- **Situação atual:** a citação 003178/2026 correu de **01/09 a 15/09/2026, sem resposta** (Ev 38). O relator (Ev 41, 30/09/2026) remeteu à DE "conforme Ev 31". O processo voltou pela DIP à CCD em 19/10/2026 com o marcador CADASTRAR DÉBITO. A mora corre desde 16/09/2026: 35 dias × R$ 500 = R$ 17.500 em 21/10. **O teto de R$ 20.000 é atingido em 26/10/2026.** Está na CCD há 2 dias.
- **Próximo passo (CCD):**
  1. Liquidar a cominatória: R$ 500/dia, início em 16/09/2026, LimiteValor de R$ 20.000. Cadastrar após 26/10 já no teto, ou "até a data", com complementação.
  2. Cadastrar o débito tipo 5 em nome de Maria do Socorro da Silva Batista.
  3. Instaurar o processo autônomo de execução (parágrafo único do art. 34 da Res. 28/2012) e citar na forma do art. 117. Avaliar a consulta de vínculo para desconto em folha (art. 25 da Res. 13/2015).
  4. Na informação, perguntar ao relator se a cominatória anterior (R$ 200/dia, Ev 21; certidão de inércia no Ev 28, 21/07/2026) também deve ser liquidada.
- **Urgência:** alta. A mora está em curso, o teto chega em poucos dias e há ordem do relator para executar.

### 004809/2024 — Câmara Municipal de Grossos
- **Tipo / relator:** MON · Francisco Potiguar Cavalcanti Júnior
- **Natureza:** lote **Portal da Transparência 2019**. O **Acórdão nº 174/2021-TC** (02/06/2021, proc. 7871/2019; mantido pelo Ac. 369/2024 em reconsideração; **trânsito em 26/09/2024**) aplicou multa de R$ 5.000 a Francisco Richarllyton de Oliveira Gomes (execução 000723/2025) e determinou à atual gestão da Câmara a divulgação das informações faltantes em 90 dias, sob **multa diária de R$ 100/dia** e suspensão da certidão.
- **Situação atual:** o monitoramento foi autuado em 13/11/2024 e ficou parado na DE até 2025. **Não há citação da atual gestão para a obrigação de fazer** (art. 29 da Res. 28/2012), portanto a mora não começou a correr. O relator (Ev 11, 16/09/2026) mandou à DIP "realizar o monitoramento, certificando o cumprimento". Marcador: Monitorar obrigação de fazer (18/09/2026). Está na CCD há 33 dias.
- **Próximo passo (CCD):** verificar o portal da Câmara de Grossos.
  - **Se regular:** informação de cumprimento e arquivamento.
  - **Se não:** sugerir a citação do atual Presidente da Câmara (art. 29 da Res. 28/2012, 90 dias) ou, alternativamente, a prejudicialidade pela linha PNTP/LINDB (Ac. 686/2025), já que os dados de 2019 estão fora da série histórica de 3 anos.
- **Urgência:** baixa. A mora não foi constituída, mas o processo é antigo.

### 002893/2025 — Prefeitura Municipal de Senador Elói de Souza
- **Tipo / relator:** MON · Antonio Ed Souza Santana
- **Natureza:** o **Acórdão nº 29/2025-TC** (24/02/2025, proc. 2502/2024; RPPS SouzaPrev) aplicou multas a Maciel Gomes da Silva e Euclides Teixeira Neto (execução 000950/2026). Determinou ainda:
  - **item "d" (cautelar):** o atual gestor deve regularizar o débito previdenciário de 2023 (pagamento ou parcelamento) em 90 dias úteis;
  - **item "e":** comprovar nos 5 dias úteis seguintes, sob **multa pessoal e diária de R$ 500/dia** (teto do art. 323, II, "b").
- **Situação atual:** a DCP (Informação 029/2026, Ev 5) apontou que o débito seguia em aberto no CADPREV. A citação 000962/2026 correu de 06/04 a 18/08/2026, sem resposta (Ev 15). O relator (**Ev 18, 05/10/2026**) mandou a DIP **liquidar a multa diária e instaurar a execução**. Depois disso, em **09/10/2026 (Ev 21–29)**, o Município juntou 5 termos de parcelamento no CADPREV, assinados em **19/03/2026** e em 300 meses (EC 136/2025; Leis Municipais 521/2025 e 526/2026), que incluem as competências de 2023. Marcador: CADASTRAR DÉBITO (06/10/2026). Está na CCD há 15 dias.
- **Próximo passo (CCD):** informação ao relator noticiando o **fato novo**: o cumprimento material ocorreu antes da citação, mas a comprovação foi intempestiva. Junto, apresentar a liquidação da mora de comprovação: de 26/08/2026 (dia seguinte aos 5 dias úteis após 18/08) até 09/10/2026, 44 dias × R$ 500 = R$ 22.000, **limitada ao teto do art. 323, II, "b"** (R$ 20.585,16 pela Portaria 005/2025, a mesma do acórdão). O relator decide se mantém, reduz ou afasta (parágrafo único do art. 110). Só então cadastrar o débito tipo 5 em nome do prefeito Kerginaldo Medeiros de Araújo Júnior e instaurar a execução. Sugerir também a conferência no CADPREV do pagamento das parcelas, que começaram em 10/05/2026.
- **Urgência:** alta. Há ordem do relator para liquidar e a resposta nova altera o quadro.

### 003442/2025 — Prefeitura Municipal de Patu
- **Tipo / relator:** MON · Antonio Ed Souza Santana
- **Natureza:** lote **Portal da Transparência 2019**. O **Acórdão nº 31/2021-TC** (04/02/2021, proc. 907/2020; mantido pelo Ac. 235/2025; **trânsito em 26/06/2025**) aplicou multa de R$ 5.000 a Rivelino Câmara (execução 003049/2025) e determinou à atual gestão a divulgação das informações faltantes em 30 dias, sob **multa diária de R$ 100/dia** e suspensão da certidão.
- **Situação atual:** a citação 001172/2025 (obrigação de fazer) correu de 12/08 a 23/09/2025, **sem resposta**. Na origem, o relator mandou a DCD verificar. A DCD devolveu sem análise em 28/05/2026 (art. 30, III, Res. 42/2024). Não há cominatória cadastrada. Marcador: Monitorar obrigação de fazer (29/05/2026). Está na CCD há 145 dias.
- **Próximo passo (CCD):** verificar o portal de Patu e elaborar informação com duas partes.
  - **(i) Liquidação:** mora desde 24/09/2025, cerca de 392 dias × R$ 100, a ser limitada ao teto (o acórdão não fixou teto expressamente; aplicar o art. 323, II do RI).
  - **(ii) Afastamento:** o relator Antonio Ed é autor de 5 dos acórdãos que afastaram a cominatória neste lote (40, 82, 96, 140 e 171/2026); sugerir a mesma solução se a pendência for apenas de dados de 2019.
- **Urgência:** média. A mora já supera o teto e o processo está parado há quase 5 meses.

### 003973/2025 — Departamento Estadual de Trânsito (DETRAN/RN)
- **Tipo / relator:** MON · Paulo Roberto Chaves Alves
- **Natureza:** o **Acórdão nº 213/2025-TC** (04/09/2025, proc. 460/2022) determinou ao DETRAN, em 30 dias úteis:
  - (a) registro contábil dos repasses de multas de trânsito ao FUNSET;
  - (b) registro do PIS/PASEP sobre as multas em contas de controle;
  - (c) divulgação no site das informações do art. 320, §2º do CTB (Portaria 85/2018-DENATRAN), desde 2020.

  Não foi localizada multa cominatória.
- **Situação atual:** a citação 000214/2026 recebeu **resposta tempestiva** em 03/03/2026 (Ev 9–14): despachos SEI, registro extraorçamentário do FUNSET a partir de jan/2026, relatório SIGEF do PASEP e links de publicação de 2020 a 2025. O relator (Ev 18) pediu análise à DIP. A **CCD (Ev 21, 10/04/2026) decidiu remeter à DCD, mas não há tramitação**: o processo continua na CCD desde 11/03/2026. Marcador: Monitorar obrigação de fazer (11/03/2026). Está na CCD há 224 dias.
- **Próximo passo (CCD):** a DCD tem devolvido monitoramentos desse tipo (art. 30, III, Res. 42/2024). Por isso, convém a própria CCD examinar a resposta: conferir os links do DETRAN (arrecadação e despesas de 2020 a 2025), os lançamentos SIGEF e a sistemática FUNSET (Portaria SENATRAN 985/2022). Em seguida, emitir informação de cumprimento (integral ou parcial) ao relator. Alternativa mínima: efetivar a tramitação à DCD decidida no Ev 21.
- **Urgência:** alta. A resposta tempestiva está sem análise há 7 meses, por erro de fluxo.

### 003974/2025 — Controladoria-Geral do Estado (CONTROL)
- **Tipo / relator:** MON · Carlos Thompson Costa Fernandes
- **Natureza:** item "b" do **Acórdão nº 331/2023-TC** (Pleno, 22/06/2023, proc. 200016/2021; **trânsito em 08/10/2024**). O atual gestor da CONTROL deve remeter em 60 dias úteis o **anexo bimestral da execução da despesa do 6º bimestre de 2016** e comprovar nos 10 dias seguintes, sob **multa pessoal e diária de R$ 500/dia** (art. 110). Na impossibilidade, deve comprovar as medidas do art. 33, §2º, I a III, da Res. 011/2016. Houve ainda multa de R$ 5.000 a Alexandre Pinto Varella (débito 25433).
- **Situação atual:** a citação 000215/2026 (prazo até 06/05/2026) teve **resposta tempestiva** pelo Doc. 300372/2026 (Ofício 381/2026-CONTROL, 02/03/2026, Ev 7). A CONTROL juntou o **RREO do 6º bimestre de 2016** extraído com a SEFAZ e indicou o SICONFI. O relator (Ev 11, 11/05/2026) pede que a DIP **informe expressamente se o item "b" foi cumprido**. Marcador: Monitorar obrigação de fazer (12/05/2026). Está na CCD há 162 dias.
- **Próximo passo (CCD):** informação conclusiva ao relator sobre o item "b". Ponto central: o documento enviado é o RREO (Anexo 01, Balanço Orçamentário), e não necessariamente o "anexo bimestral da execução da despesa" exigido pela Res. 011/2016 via SIAI. Conferir no SIAI se a remessa foi feita. Se não foi, verificar se o envio equivale à comprovação das medidas do art. 33, §2º. Concluir por cumprimento (arquivamento) ou descumprimento (art. 34 da Res. 28/2012).
- **Urgência:** média. A resposta foi tempestiva e o processo está parado há 5 meses.

### 000137/2026 — Prefeitura Municipal de São Pedro
- **Tipo / relator:** MON · Antonio Gilberto de Oliveira Jales
- **Natureza:** lote **Portal da Transparência 2019**. Item "c" do **Acórdão nº 68/2023-TC** (04/04/2023, proc. 1823/2020; **trânsito em 08/05/2024**): a atual gestão deve divulgar as informações faltantes em 90 dias, sob **multa diária de R$ 100/dia** e suspensão da certidão. A multa de R$ 5.000 a Miguel Cabral Nasser (débito 27978, saldo de R$ 2.000) é cobrada à parte.
- **Situação atual:** o monitoramento foi autuado em 26/01/2026. O relator remeteu à DCD (Ev 4), que devolveu à DIP em 28/05/2026. **Não foi localizada citação da atual gestão** para a obrigação de fazer (art. 29 da Res. 28/2012), portanto a mora não foi constituída. Marcador: Monitorar obrigação de fazer (29/05/2026). Está na CCD há 145 dias.
- **Próximo passo (CCD):** verificar o portal de São Pedro quanto aos itens de 2019. Em seguida, informação ao relator: o próprio Cons. Gilberto Jales relatou o *leading case* **Ac. 686/2025** (PNTP/LINDB), o que favorece propor a prejudicialidade e o arquivamento. Se o relator preferir prosseguir, propor a citação do atual prefeito (90 dias).
- **Urgência:** baixa. Não há mora constituída e a tese de afastamento é do próprio relator.

### 000454/2026 — Câmara Municipal de Caiçara do Norte
- **Tipo / relator:** MON · Renato Costa Dias
- **Natureza:** lote **Portal da Transparência 2019**. O **Acórdão nº 12/2021-TC** (26/01/2021, proc. 7226/2019; **trânsito em 23/04/2021**) aplicou multa de R$ 3.000 a Janailton Francisco Pereira (execução 003024/2022) e determinou à atual gestão da Câmara a divulgação das informações faltantes em 30 dias, sob **multa diária de R$ 100/dia**.
- **Situação atual:** na origem houve as citações 3173/2022 e 300/2023. A Câmara respondeu (doc. 301171/2023) e a DCD apontou **cumprimento parcial**: receitas e despesas, lista de exigibilidades e e-SIC. O MPC (Parecer 036/2025) pediu a conversão em obrigação pecuniária. O relator, ao mandar instaurar o monitoramento (origem, Ev 152), **sinalizou a prejudicialidade à luz do PNTP**. A DCD devolveu à DIP em 28/05/2026. Marcador: Monitorar obrigação de fazer (02/06/2026). Está na CCD há 145 dias.
- **Próximo passo (CCD):** fazer uma verificação rápida do portal atual da Câmara. Depois, informação ao relator propondo o encerramento sem cominatória (PNTP + art. 22, §1º da LINDB; Ac. 686/2025 e 223/2026), com registro da posição contrária do MPC. Se o relator mantiver a cominatória, liquidar desde o fim do prazo da citação de 2022/2023 (data não localizada nesta coleta).
- **Urgência:** baixa. Há tendência de arquivamento, sinalizada pelo próprio relator.

### 000537/2026 — Prefeitura Municipal de Pau dos Ferros (transparência)
- **Tipo / relator:** MON · Paulo Roberto Chaves Alves
- **Natureza:** lote **Portal da Transparência 2019**. Item "c" do **Acórdão nº 369/2021-TC** (2ª Câmara, 24/08/2021, proc. 912/2020; **trânsito em 29/07/2025**): a Prefeita Marianna Almeida Nascimento deve divulgar as informações faltantes em 90 dias, sob **multa diária de R$ 100/dia** e suspensão da certidão. A multa de R$ 4.000 a Leonardo Nunes Rêgo está em cobrança (execução 000625/2026). O Relatório de Monitoramento da origem (Ev 119) apontou como pendência apenas a **ordem cronológica de pagamentos de 2019**.
- **Situação atual:** a citação 001671/2026 (prazo de 29/05 a 08/10/2026) teve **resposta tempestiva** em 29/07/2026 (Ev 7–10). A Prefeitura alega **impossibilidade material** de publicar a ordem cronológica de pagamentos de 2019, de gestão anterior, e preliminar de nulidade por falta de intimação pessoal. O relator (Ev 14) remeteu à DIP. Marcador: Monitorar obrigação de fazer (12/08/2026). Está na CCD há 70 dias.
- **Próximo passo (CCD):** informação analisando a manifestação.
  - Afastar a nulidade: a citação pessoal foi feita agora, e a mora só se conta a partir dela (art. 29 da Res. 28/2012).
  - Sobre o mérito, conferir no portal se a ordem cronológica de 2019 segue ausente e propor o reconhecimento da impossibilidade, ou prejudicialidade (PNTP + LINDB, Ac. 686/2025), com arquivamento sem cominatória.
  - Devolver ao relator.
- **Urgência:** média. A resposta tempestiva aguarda análise e não há mora constituída.

### 000599/2026 — Câmara Municipal de Serra de São Bento
- **Tipo / relator:** MON · Antonio Ed Souza Santana
- **Natureza:** item "b" do **Acórdão nº 174/2025-TC** (2ª Câmara, 25/08/2025, proc. 2996/2018; **trânsito em 01/12/2025**). A atual gestão da Câmara deve enviar pelo Portal do Gestor, em 40 dias, as **contas anuais de gestão de 2015**, sob:
  - multa (art. 107 c/c art. 21 da Res. 012/2016);
  - **multa diária pessoal de R$ 200/dia** (teto do art. 323, II, "b");
  - suspensão da certidão de adimplência;
  - representação ao MPE.
- **Situação atual:** na origem, a citação 000759/2026 da Câmara correu de 18/03 a 20/05/2026, **sem resposta**. O relator (origem, Ev 109) mandou instaurar o monitoramento e determinou que a DIP, com a DE, efetive as medidas remanescentes, frisando que "já incide" a multa diária. O monitoramento só tem capa e volume (Ev 0–2). Marcador: Monitorar obrigação de fazer (15/06/2026). Está na CCD há 128 dias.
- **Próximo passo (CCD):** verificar no SIAI se as contas de 2015 foram enviadas.
  - **Se não foram:** liquidar a cominatória com mora desde 21/05/2026 (cerca de 153 dias × R$ 200 = R$ 30.600, acima do teto). Limitar ao teto do art. 323, II, "b" (R$ 20.585,16 pela Portaria 005/2025, do ano do acórdão; conferir). Cadastrar o débito tipo 5 em nome do Presidente da Câmara (nome não localizado; a citação foi dirigida à Câmara). Instaurar a execução. Pedir à DE a suspensão da certidão e a representação ao MPE. Sugerir ao relator a multa do art. 107.
  - **Se foram:** informação de cumprimento intempestivo e cobrança da mora.
- **Urgência:** alta. A mora já passou do teto e o processo está há 4 meses na CCD sem movimento.

#### Observações: MON

1. **Lote "Portal da Transparência 2019": 7 dos 17 processos** (001834, 002234, 003442, 004809, 000137, 000454 e 000537). São acórdãos de 2020–2023 com multa diária de R$ 50–100. A jurisprudência recente (Ac. 686/2025, *leading*, Gilberto Jales; 40, 82, 96, 140 e 171/2026, Antonio Ed; 223/2026) **afasta a cominatória** pelo art. 22, §1º da LINDB e pela série histórica de 3 anos do PNTP. Contra: Ac. 456/2026 e 602/2025, quando a obrigação segue descumprida; e Ac. 238/2026, pelo qual o cumprimento superveniente não elide as astreintes já vencidas. Isso permite **tratamento em lote**: uma verificação padronizada do portal e uma informação-modelo em três variantes.
   - **(a) Já citados e revéis:** 001834, 003442 e, de certo modo, 000454. A informação traz a liquidação no teto e a alternativa LINDB/PNTP para o relator escolher (art. 34 da Res. 28/2012).
   - **(b) Sem citação da atual gestão:** 004809 e 000137. Propor a prejudicialidade/arquivamento; a citação fica como alternativa.
   - **(c) Com resposta:** 000537 (impossibilidade material).

   O **002234 é exceção**: a cominatória já foi liquidada (R$ 17.728,31) e acolhida pelo relator, de modo que falta apenas citar e executar.
2. **Cominatória a liquidar, cadastrar ou executar (marcadores CADASTRAR DÉBITO / EXECUÇÃO):** 003632 (urgente: teto de R$ 20.000 em 26/10/2026), 002893 (fato novo de 09/10/2026: levar ao relator antes de cadastrar), 002459 (ordem do relator desde fev/2026) e 000599 (mora acima do teto). No 002234, o débito 28768 já existe, mas está vinculado à execução 002002/2024, que está **arquivada**, e a citação do art. 117 não foi expedida.
3. **Omissão de contas anuais de gestão** (002365 Taipu/2015, 000599 Serra de São Bento/2015, 002459 Nilo Pereira/2019): o primeiro passo comum é **consultar o SIAI/Portal do Gestor** quanto ao envio, o que pode ser feito de uma vez para os três.
4. **Devoluções da DCD de 28/05/2026** (002365, 001834, 003442, 000137 e 000454): todas com o mesmo despacho padrão (art. 30, III, Res. 42/2024). Isso confirma que esses monitoramentos sem relatório adicional ficam com a DIP/CCD. Em sentido oposto, o **003973 (DETRAN)** ficou preso por 7 meses porque a CCD decidiu remeter à DCD (Ev 21) e a tramitação não foi feita. Convém alinhar o critério (art. 32, I e II, Res. 42/2024) e tratar o DETRAN na própria CCD.
5. **Respostas aguardando análise da CCD:** 001513 (obras), 003973 (DETRAN), 003974 (CONTROL), 000537, 002893 e 004079 (apensado 300619/2025). Nesses casos o próximo passo é uma informação de análise de cumprimento, não um ato de cobrança.
6. **Critério do teto da cominatória:** no 002234/2024 a CCD usou o valor máximo da Portaria do **ano do acórdão** (2022). Para os novos casos (002459, 001834, 000599 e 002893), convém fixar o mesmo critério e conferir também o percentual da alínea: art. 107, II da LCE (002459), art. 323, II, "b" do RI (demais) e a nota de que o art. 323, II, "f" limita a 50%.
7. **000523/2021** é só acompanhamento de parcelamento (3/24 pagas). Pode ficar com o marcador até a quitação; a recomendação já está no CGR.

## Grupo 2: APR com obrigação de fazer (16)

### 017807/2014 — Câmara Municipal de São Tomé
- **Tipo / relator:** APR · Francisco Potiguar Cavalcanti Júnior (GCPOT). **Fora do lote Portal 2019**: trata da inadimplência no SIAI-DP (jan–dez/2013 e jan–jun/2014).
- **Natureza:** Acórdão nº 209/2017-TC (2ª Câmara, 15/08/2017): multa de R$ 22.500,00 a Josinaldo Amaro de Lima e determinação à Câmara, na pessoa do atual Presidente, de enviar em 20 dias os dados do SIAI-DP (folha e cadastro, jan/2013–jun/2014), sob multa diária de R$ 50,00 (art. 110 LCE 464). O recurso não foi conhecido (Acórdão nº 68/2026, Pleno, 02/03/2026: perda de objeto pelo parcelamento). Trânsito em julgado em 10/04/2026 (Ev. 79).
- **Situação atual:** a Notificação 001466/2017 foi expedida à Câmara em 2017. Segundo a Informação nº 042/2018-DDP (Ev. 38), as remessas já tinham sido feitas: 2013 a partir de 30/07/2015 e jan–jun/2014 em 30/12/2014, ou seja, antes do acórdão. A multa não foi recolhida e foi instaurada a Execução 000612/2026 (débito em aberto). Em 11/06/2026 o GCPOT pediu à DIP que verifique a obrigação de fazer (Ev. 91). Marcador desde 30/06/2026. Está na CCD há 124 dias (desde 19/06/2026).
- **Próximo passo (CCD):** conferir no SIAI-DP (tabelas `SiaiDp_*`) as remessas de jan/2013 a jun/2014 e elaborar a informação de cumprimento (obrigação satisfeita antes da decisão, com base no Ev. 38). Sugerir o reconhecimento do cumprimento e o arquivamento quanto ao item de fazer (a multa segue na Execução 000612/2026). Tramitar CCD→DIP "ENVIO A GCPOT".
- **Urgência:** média. Falta só formalizar uma obrigação aparentemente cumprida, mas há despacho do relator pendente há 4 meses.

### 006683/2019 — Câmara Municipal de Alexandria
- **Tipo / relator:** APR · Antonio Ed Souza Santana (GCAED, sucessor de Maria Adélia).
- **Natureza:** Acórdão nº 10/2021-TC: multa de R$ 5.000,00 a Raymara Rayane Andrade da Silva. Item b: determinação à atual gestão de divulgar em 30 dias as informações faltantes, sob multa diária de R$ 100,00 ao gestor (art. 110) e suspensão da certidão de adimplência (art. 33, II, Res. 011/2016). Trânsito em julgado em 05/04/2021.
- **Situação atual:** a Citação 000178/2024 (Câmara, gestor Francisco Jandui Fernandes Júnior) teve prazo de 22/02 a 08/04/2024 e venceu sem cumprimento (certidão item 23, Ev. 124). Em 31/01/2025 o GCAED mandou a DIP verificar a obrigação. Pelo `Exe_Debito`, a multa foi quitada (último elo da cadeia "Pago Integralmente"), mesmo com a Execução 001849/2025 instaurada. Os autos fizeram ida e volta: CCD→DCD em 16/07/2025 e DCD→DIP em 28/05/2026 (art. 30, III, Res. 042/2024). Marcador desde 29/05/2026. Está na CCD há 145 dias.
- **Próximo passo (CCD):** a CCD mesma deve aferir o portal (PNTP/Atricon Avalia e site da Câmara, janela 2023–2025, método do 000924/2020) e emitir o relatório de monitoramento. Se houver cumprimento, sugerir o reconhecimento e o arquivamento. Se não houver, apontar o descumprimento desde 09/04/2024 e propor a cominatória, ou o afastamento pela LINDB, art. 22, §1º, conforme a série PNTP. Registrar a quitação da multa (baixa na Execução 001849/2025). Tramitar CCD→DIP "ENVIO A GCAED".
- **Urgência:** alta. O prazo venceu em 04/2024, o despacho do relator é de 01/2025 e já houve uma devolução pela DCD.

### 006688/2019 — Câmara Municipal de Apodi
- **Tipo / relator:** APR · Ana Paula de Oliveira Gomes (GAANA).
- **Natureza:** Acórdão nº 310/2020-TC (1ª Câmara, 10/12/2020): multa de R$ 3.000,00 a Francisco de França Pinheiro. Item b: o atual responsável deve "alimentar" o portal em 30 dias, sob astreinte de **R$ 200,00/dia** e suspensão da certidão. Trânsito em julgado em 13/08/2021, segundo o MPC (Ev. 75) e o `Exe_Debito`. A DCD (Ev. 102) informa 10/12/2020, que é a data do acórdão.
- **Situação atual:** a diligência requerida pelo MPC está pendente desde 30/01/2023 (Ev. 80: informar o recolhimento da multa, a execução e o cumprimento da obrigação). A Citação 002098/2026 (obrigação de fazer) teve prazo de 12/06 a 27/07/2026 e venceu sem resposta. A Citação 002118/2026 (multa) não teve recolhimento, e foi instaurada a Execução 000673/2026 (Ev. 132). O GAANA (29/07/2026) mandou a DIP prestar os esclarecimentos ao MPC. Segundo o Ev. 132, há o documento apensado 302578/2021 a examinar. Marcador desde 05/08/2026. Está na CCD há 82 dias.
- **Próximo passo (CCD):** examinar o doc. 302578/2021, aferir o portal atual e elaborar a informação que responde aos três quesitos do MPC (multa → Execução 000673/2026; obrigação → certidão de inércia + aferição) e, havendo descumprimento, trata da astreinte de R$ 200/dia (ou do seu afastamento pela LINDB). Tramitar CCD→DIP "ENVIO A GAANA".
- **Urgência:** alta. A diligência do MPC está parada há mais de 3 anos, há ordem expressa da relatora e a citação já venceu.

### 006940/2019 — Prefeitura Municipal de Campo Redondo
- **Tipo / relator:** APR · Antonio Gilberto de Oliveira Jales (GCGIL).
- **Natureza:** Acórdão nº 49/2022-TC: multa de R$ 3.000,00 a Alessandru Emmanuel Pinheiro e Alves e determinação à atual gestão de regularizar em 30 dias as informações faltantes no portal, sob multa diária de R$ 100,00 ao gestor e suspensão da certidão. Trânsito em julgado em 26/06/2023 (Ev. 135). O ex-gestor faleceu (Ev. 119) e a dívida foi cancelada (Ev. 130). Resta só a obrigação de fazer.
- **Situação atual:** a Citação 000443/2025 teve prazo de 14/04 a 03/06/2025 e venceu sem cumprimento comprovado (Ev. 140). O MPC (Quota 077/2025) e o GCGIL (07/07/2025) determinaram o monitoramento. Os autos fizeram ida e volta: CCD→DCD em 14/10/2025 e DCD→DIP em 28/05/2026. Marcador desde 29/05/2026. Está na CCD há 145 dias.
- **Próximo passo (CCD):** aferir o portal da Prefeitura (PNTP e site) e emitir o relatório de monitoramento: cumprimento leva a reconhecimento e arquivamento; descumprimento desde 04/06/2025 leva à proposta sobre a multa diária ao gestor atual (ou ao seu afastamento pela LINDB). Tramitar CCD→DIP "ENVIO A GCGIL".
- **Urgência:** alta. O despacho do relator é de 07/2025, o prazo venceu em 06/2025 e já houve uma devolução pela DCD.

### 006945/2019 — Prefeitura Municipal de Caraúbas
- **Tipo / relator:** APR · Renato Costa Dias (GCREN).
- **Natureza:** Acórdão nº 335/2020-TC (2ª Câmara, 15/12/2020): multa de R$ 3.000,00 a Antônio Alves da Silva e determinação à atual gestão de divulgar em 30 dias as informações faltantes, sob multa diária de R$ 100,00 e suspensão da certidão (monitoramento pela DAM). O Acórdão nº 799/2025 (Pleno, 17/12/2025) manteve a decisão e acrescentou uma recomendação para manter a divulgação em tempo real. O recurso alegava saneamento posterior. Trânsito em julgado em 02/03/2026, conforme o `Exe_Debito`.
- **Situação atual:** a recomendação foi anotada no CGAD (Ev. 96). A Prefeitura foi intimada apenas para ciência (Intimação 000611/2026). Nos autos não se localizou citação específica para a obrigação de fazer. A multa não foi recolhida após três citações e foi instaurada a Execução 000960/2026 (Ev. 132). Há notificações de 01/07/2026 à CAERN (001696/2026) e à COSERN (001695/2026), com prazo de 10 dias, e o doc. 301616/2026 apensado em 21/07/2026. A finalidade dessas notificações e do documento não aparece no material coletado. Marcador desde 08/10/2026. Está na CCD há 33 dias.
- **Próximo passo (CCD):** ler o doc. 301616/2026 e as notificações CAERN/COSERN e aferir o portal. Se estiver regular, emitir informação de cumprimento e sugerir o arquivamento do item de fazer (a recomendação já está no CGAD). Se não estiver, sugerir ao GCREN a citação da Prefeitura para cumprir a obrigação (art. 29 da Res. 028/2012). Tramitar CCD→DIP "ENVIO A GCREN".
- **Urgência:** média. Entrou há pouco tempo, mas a obrigação nunca foi aferida desde 2020.

### 007869/2019 — Câmara Municipal de Ielmo Marinho
- **Tipo / relator:** APR · Antonio Gilberto de Oliveira Jales (GCGIL, por sucessão presidencial).
- **Natureza:** Acórdão nº 341/2023-TC (2ª Câmara, 19/12/2023): multa de R$ 5.000,00 a Júnior Nunes Cabral. Item b: divulgar em **90 dias** os RGFs, receitas, despesas, licitações e lista de exigibilidades, sob multa diária de R$ 100,00 e suspensão da certidão. O Acórdão nº 784/2024 (pedido de reconsideração) e o Acórdão nº 112/2026 (embargos) mantiveram a decisão. Trânsito em julgado em 13/04/2026, conforme o `Exe_Debito`.
- **Situação atual:** a Câmara protocolou o doc. 300680/2025 (Ev. 141, 06/03/2025) em cumprimento à obrigação de fazer. O GCGIL (Ev. 163, 07/05/2026) mandou a DIP analisá-lo. Foi instaurada a Execução 000613/2026, mas o `Exe_Debito` mostra a multa paga integralmente. Marcador desde 07/07/2026. Está na CCD há 140 dias.
- **Próximo passo (CCD):** analisar o doc. 300680/2025, aferir o portal atual e emitir o relatório de monitoramento (cumprimento leva a arquivamento; parcialidade, à proposta de cominatória ou LINDB). Registrar a quitação da multa (extinguir a Execução 000613/2026). Tramitar CCD→DIP "ENVIO A GCGIL".
- **Urgência:** média-alta. A documentação aguarda análise desde 03/2025 e o despacho do relator está pendente há 5 meses.

### 000742/2020 — Câmara Municipal de Janduís
- **Tipo / relator:** APR · Paulo Roberto Chaves Alves (GCPRO).
- **Natureza:** Acórdão nº 186/2021-TC (2ª Câmara, 18/05/2021): multa de R$ 4.000,00 a Arthur Barbosa de Lima. Item b: a Câmara, pelo próprio Arthur, deve divulgar em 30 dias as informações faltantes, sob multa pessoal de R$ 100,00/dia e suspensão da certidão. O Acórdão nº 281/2025 (Pleno, 11/04/2025) manteve a decisão. Trânsito em julgado em 06/06/2025.
- **Situação atual:** em 2021 a DAM (Ev. 66) já constatou a ordem cronológica publicada desde 10/2020, os RGFs publicados e as "demais exigências cumpridas" até 29/08/2021, ou seja, antes do trânsito. O GCPRO (Ev. 105, 10/07/2025) mandou a DIP apenas acompanhar as parcelas. Houve sucessivos parcelamentos cancelados, o último em 21/07/2026. O débito 29227 está em aberto e **não há execução instaurada**. Marcador desde 21/07/2026. Está na CCD há **467 dias** (desde 11/07/2025).
- **Próximo passo (CCD):** (1) certificar a inadimplência e instaurar a execução (art. 118 da LCE 464 e art. 25 da Res. 013/2015), salvo novo parcelamento; (2) emitir a informação de monitoramento reconhecendo o cumprimento da obrigação de fazer (Ev. 66 e aferição atual) e sugerir o arquivamento. Tramitar CCD→DIP "ENVIO A GCPRO".
- **Urgência:** alta. É o processo mais antigo do grupo na CCD (15 meses) e o parcelamento foi cancelado sem execução.

### 000908/2020 — Prefeitura Municipal de Passa e Fica
- **Tipo / relator:** APR · Renato Costa Dias (GCREN).
- **Natureza:** Acórdão nº 368/2021-TC (2ª Câmara, 24/08/2021): multa de R$ 4.000,00 a Celso Luiz Marinho Lisboa. Item b: a Prefeitura, pelo gestor Flaviano Correia Lisboa (mandato 2021–2024), deve divulgar em 90 dias as informações faltantes, sob multa de R$ 100,00/dia e suspensão da certidão, "a serem apuradas em processo autônomo". O Acórdão nº 303/2023 (Pleno, 13/06/2023) manteve a decisão. Trânsito em julgado em 18/07/2023.
- **Situação atual:** após o trânsito, os autos foram à DAM/DCD para o item c (Ev. 90 e 99), e a DCD devolveu à DIP em 28/05/2026. **A multa de R$ 4.000,00 está em aberto, sem execução, e nos autos não se localizou citação do art. 117.** A obrigação de fazer também não tem citação nem aferição. Marcador desde 29/05/2026. Está na CCD há 145 dias.
- **Próximo passo (CCD):** (1) propor ao GCREN, ou providenciar se houver autorização, a citação de Celso pelo art. 117 e a execução (art. 118); (2) aferir o portal e emitir o relatório de monitoramento. Se houver descumprimento, a cominatória deve ser apurada em processo autônomo, como manda o próprio acórdão. Tramitar CCD→DIP "ENVIO A GCREN".
- **Urgência:** alta. A multa ficou parada sem citação desde 07/2023 (prescrição executória a vigiar) e a obrigação nunca foi aferida.

### 000924/2020 — Câmara Municipal de Lagoa Salgada
- **Tipo / relator:** APR · Antonio Gilberto de Oliveira Jales (GCGIL).
- **Natureza:** Acórdão nº 108/2021-TC (1ª Câmara, 15/04/2021): multa de R$ 5.000,00 a Ozivaldo Nascimento Queiroz e determinação de divulgar em 90 dias as informações faltantes (ausência de portal), sob multa diária de R$ 100,00 e suspensão da certidão. O agravo foi desprovido (Acórdão nº 106/2023).
- **Situação atual:** a multa foi quitada em 25/09/2026 (Certidão 02342/2026, Ev. 167). O **Relatório de Monitoramento da CCD (Ev. 169, 14–15/10/2026) já está pronto**: portal existente (lagoasalgada.rn.leg.br/acessoainformacao), cumprimento integral (1/1), com proposta de reconhecimento e arquivamento (RI art. 209, V). A tramitação ainda não aparece (última entrada DIP→CCD em 10/02/2025). Marcador desde 06/10/2026. Está na CCD há cerca de 617 dias.
- **Próximo passo (CCD):** assinar, se ainda faltar, e tramitar CCD→DIP "ENVIO A GCGIL". Atenção: o relatório cita "Acórdão nº 118/2021" no item 10 e o Ev. 168 traz "108/202". O número correto é 108/2021.
- **Urgência:** média. Só falta tramitar, mas o processo está há muito tempo na CCD.

### 001305/2020 — Prefeitura Municipal de Rio do Fogo
- **Tipo / relator:** APR · Marco Antônio de Moraes Rêgo Montenegro (GAMAR).
- **Natureza:** **o mérito ainda não foi julgado.** O Acórdão nº 31/2022-TC (2ª Câmara, 01/02/2022, voto-vista do Cons. Gilberto Jales) é de natureza cautelar: concedeu 20 dias para a melhoria do portal (links, todas as informações, lista de exigibilidades de exercícios anteriores) e mais 5 dias para comprovar, sob multa de **R$ 1.000,00/dia** ao gestor (Márcio Luiz Pereira Barbosa). Não há multa aplicada (nenhum débito no `Exe_Debito`). O trânsito foi cancelado (Ev. 92).
- **Situação atual:** a DAM concluiu por cumprimento parcial (Ev. 85, 17/08/2022, e Ev. 100: faltavam contratos e lista de exigibilidades de 2020–2022). A DCD concluiu por cumprimento em 20/02/2025 (Ev. 114). A Quota 42/2025 do MPC (Ev. 119) pede uma informação conclusiva sobre (a) se houve cumprimento (a matéria ainda não tem mérito) e (b) se foi tempestivo e, se não foi, quais sanções cabem. O GAMAR mandou à DCD em 28/08/2025, e a DCD devolveu à DIP em 28/05/2026 como "monitoramento". Marcador desde 29/05/2026. Está na CCD há 145 dias.
- **Próximo passo (CCD):** elaborar a informação conclusiva respondendo aos quesitos do MPC. A cronologia é: intimação 000377/2022 (AR de 04/2022), prazo de 20+5 dias, cumprimento parcial em 08/2022 e cumprimento só constatado em 02/2025, o que torna o cumprimento intempestivo. A informação deve propor sanção (multa diária limitada, ou seu afastamento pela LINDB) e um encaminhamento para o mérito, verificando a prescrição da pretensão punitiva quanto ao gestor de 2019 (Laerte Ney de Paiva Fagundes). Tramitar CCD→DIP "ENVIO A GAMAR". Alternativa: se a instrução de mérito for considerada de outra unidade, registrar isso em despacho.
- **Urgência:** alta. É um processo de 2020 sem mérito, com o MPC aguardando desde 08/2025.

### 001311/2020 — Prefeitura Municipal de Santo Antônio
- **Tipo / relator:** APR · Renato Costa Dias (GCREN).
- **Natureza:** Acórdão nº 35/2021-TC: multa de R$ 3.000,00 a Josimar Custódio Ferreira e determinação de divulgar em 30 dias as informações faltantes (editais de licitação, entre outras), sob multa diária de R$ 100,00 e suspensão da certidão. Trânsito em julgado em 04/2021 (Ev. 47). A decisão monocrática do GCREN de 10/12/2025 (Ev. 118), após a DAM e o MPC (Ev. 105 e 115) atestarem o descumprimento, concedeu **novo prazo de 30 dias**, com multa diária de **R$ 100,00 limitada a R$ 5.000,00**, e determinou que, havendo inércia, se instaure a execução (art. 34 da Res. 028/2012) e os autos voltem ao gabinete.
- **Situação atual:** a Citação 002679/2025 teve prazo de 21/01 a 06/03/2026. A **resposta foi tempestiva em 03/03/2026** (Ev. 124, PDF sem texto extraível). O GCREN mandou à DCD, e a DCD devolveu à DIP em 28/05/2026. A multa de Josimar está em aberto na Execução 003023/2021. Marcador desde 29/05/2026. Está na CCD há 145 dias.
- **Próximo passo (CCD):** ler a resposta do Ev. 124 e aferir o portal (editais, orçamentárias, execução, e-SIC). Emitir a informação ao GCREN: cumprimento leva a reconhecimento e arquivamento; descumprimento leva à quantificação da multa diária a partir de 07/03/2026, até o teto de R$ 5.000,00, e à instauração da execução. Tramitar CCD→DIP "ENVIO A GCREN".
- **Urgência:** alta. Há resposta aguardando análise desde 03/2026 e a decisão do relator depende desse retorno.

### 001877/2020 — Câmara Municipal de São Bento do Trairi
- **Tipo / relator:** APR · Paulo Roberto Chaves Alves (GCPRO).
- **Natureza:** Acórdão nº 32/2021-TC (1ª Câmara, 04/02/2021): multa de R$ 5.000,00 a José Vanderley Soares Silva e determinação de divulgar em 30 dias as informações faltantes, sob multa diária de R$ 100,00 e suspensão da certidão. O Acórdão nº 476/2023 (Pleno) negou o pedido de reconsideração do gestor.
- **Situação atual:** **o processo não transitou em julgado e ainda está em fase recursal.** Estão pendentes os embargos de declaração do gestor (doc. 303809/2023) e o pedido de reconsideração da Câmara (doc. 301231/2021), que nunca foi instruído. O GCPRO (Ev. 114, 23/08/2024) e o MPC (Ev. 111) pediram análise técnica do conjunto recursal. A CIP encaminhou à DCD (03/07/2025), mas a DCD devolveu como "monitoramento" (28/05/2026) sem fazer a análise. A multa está sem trânsito no `Exe_Debito`. Marcador desde 29/05/2026. Está na CCD há 145 dias.
- **Próximo passo (CCD):** não é caso de monitoramento. Emitir uma informação/despacho registrando a fase recursal pendente e propondo o retorno ao GCPRO, ou à DCD/CIP, para a análise técnica dos recursos (art. 2º, III, do Provimento 001/2020-CORREG). Retirar ou rever o marcador até o trânsito.
- **Urgência:** média. O monitoramento ainda não cabe, mas os recursos estão parados há cerca de 2 anos.

### 002056/2020 — Câmara Municipal de Serra de São Bento
- **Tipo / relator:** APR · Renato Costa Dias (GCREN).
- **Natureza:** Acórdão nº 27/2025-TC (2ª Câmara, sessão virtual de 28/02/2025): multa de R$ 3.000,00 a José Sérgio do Carmo Dias e determinação de divulgar em 90 dias as informações faltantes, sob multa diária de R$ 100,00 e suspensão da certidão. O acórdão atribui expressamente à **DIP** o monitoramento. Trânsito em julgado em 09/04/2025.
- **Situação atual:** a multa foi quitada (Certidão de quitação, Ev. 92, 01/04/2025). A Câmara foi apenas intimada para ciência (Intimação 000505/2025, 03/2025). Não se localizou citação específica nem aferição. O prazo de 90 dias já venceu, em 2025 (data exata não localizada). A CCD enviou à DCD em 22/08/2025, apesar de o acórdão indicar a DIP, e a DCD devolveu em 28/05/2026. Marcador desde 29/05/2026. Está na CCD há 145 dias.
- **Próximo passo (CCD):** aferir o portal da Câmara (PNTP e site) e emitir o relatório de monitoramento. Cumprimento leva a reconhecimento e arquivamento, já que a multa está quitada. Descumprimento leva a sugerir ao GCREN a citação para cumprir a obrigação (art. 29 da Res. 028/2012). Tramitar CCD→DIP "ENVIO A GCREN".
- **Urgência:** média. A multa está paga, mas a obrigação não foi aferida um ano e meio depois do trânsito.

### 002074/2020 — Câmara Municipal de Severiano Melo
- **Tipo / relator:** APR · Marco Antônio de Moraes Rêgo Montenegro (GAMAR).
- **Natureza:** Acórdão nº 506/2024-TC (1ª Câmara, sessão virtual de 13/12/2024): multa de R$ 5.000,00 a Rosemberg Monteiro de Carvalho. Determinação de alimentar o portal em 90 dias, sob multa diária de R$ 100,00, "passível de revisão, limitado ao teto do **art. 323, II, b**, do RI", e suspensão da certidão, com monitoramento em processo próprio. Trânsito em julgado em 06/03/2025, conforme o `Exe_Debito`.
- **Situação atual:** a Citação 001142/2025 (obrigação de fazer) teve prazo de 13/08/2025 a **22/01/2026** e venceu sem resposta (Ev. 72). A multa foi parcelada, reaberta e **quitada em 29/05/2026** (Certidão 02273/2026, Ev. 85). O GAMAR (Ev. 77) pediu à DIP que verifique a adimplência do parcelamento. Marcador desde 01/06/2026. Está na CCD há 265 dias (desde 29/01/2026).
- **Próximo passo (CCD):** informar a quitação da multa. Aferir o portal e emitir o relatório de monitoramento: havendo descumprimento, liquidar a cominatória a partir de 23/01/2026, limitada ao teto do art. 323, II, b (e não ao da alínea f), ou propor o afastamento pela LINDB, art. 22, §1º; havendo cumprimento, propor o arquivamento. Tramitar CCD→DIP "ENVIO A GAMAR".
- **Urgência:** média-alta. A citação venceu há 9 meses, o despacho do relator está pendente e o teto difere do restante do lote.

### 005106/2020 — Câmara Municipal de Viçosa
- **Tipo / relator:** APR · Ana Paula de Oliveira Gomes (GAANA, redistribuído em 10/09/2026). **Fora do lote Portal 2019**: trata de infrações à LRF em 2016 (SIAI 3º bimestre e RGF).
- **Natureza:** Acórdão nº 8/2022-TC (2ª Câmara, 25/01/2022): multas que somam R$ 24.490,00 a Manoel Gilberto Lopes. Item b: **recomendação**, e não determinação com prazo e multa, ao atual chefe do Legislativo para que o RGF atenda aos arts. 48 e 55 da LRF e ao MDF. O Acórdão nº 246/2026 (Pleno, 25/05/2026) manteve a decisão. Trânsito em julgado em 20/07/2026, conforme o `Exe_Debito`.
- **Situação atual:** sem recolhimento, foi instaurada a Execução 000944/2026 (Ev. 100, 11/09/2026). A CCD manteve os autos na DIP "para análise da obrigação de fazer". Marcador desde 11/09/2026. Está na CCD há 40 dias.
- **Próximo passo (CCD):** emitir uma informação curta: o item b é recomendação. Propor a anotação no CGAD (RI art. 431, IV, c), se ainda não feita, e o arquivamento do processo originário, já que a multa segue na Execução 000944/2026. Opcionalmente, conferir no SIAI o RGF recente da Câmara. Tramitar CCD→DIP "ENVIO A GAANA".
- **Urgência:** baixa. Não há prazo nem cominatória.

### 200192/2021 — Instituto de Educação Superior Presidente Kennedy (IFESP)
- **Tipo / relator:** APR · Antonio Gilberto de Oliveira Jales (GCGIL). **Fora do lote Portal 2019**: trata dos anexos bimestrais de 2016 no SIAI.
- **Natureza:** Acórdão nº 165/2022-TC (1ª Câmara, 18/08/2022): multa total de R$ 15.000,00 a Antônia Zélia de Assis Dantas. Determinação ao atual gestor de remeter em 60 dias úteis os anexos do 6º bimestre de 2016, sob multa diária de R$ 500,00. O Acórdão nº 20/2026 (Pleno, 02/02/2026) não conheceu do recurso. Trânsito em julgado em 07/05/2026, conforme o `Exe_Debito`.
- **Situação atual:** a Informação nº 092/2024-DAI (Ev. 86) constatou no SIAI o 6º bimestre/2016 processado em 14/03/2024, a partir do doc. 302233/2024, e concluiu que a obrigação foi cumprida antes do trânsito, o que afasta mora para a cominatória. A multa está parcelada em 36 vezes, com 18 parcelas pagas e em dia (última em 13/10/2026). O GCGIL (01/06/2026) mandou a DIP analisar o Ev. 80. Marcador desde 02/06/2026. Está na CCD há 141 dias.
- **Próximo passo (CCD):** emitir a informação de cumprimento da obrigação de fazer (base: DAI Ev. 86) e sugerir o reconhecimento do cumprimento, sem cominatória. A multa parcelada continua em acompanhamento até a quitação, e o arquivamento vem depois. Tramitar CCD→DIP "ENVIO A GCGIL".
- **Urgência:** baixa. A obrigação está cumprida e o parcelamento está em dia, mas o despacho do relator já tem 4 meses.


#### Observações: APR

**Composição.** São 16 processos APR. **13** são do lote "Portal da Transparência 2019": 006683, 006688, 006940 e 006945/2019; 007869/2019; 000742, 000908, 000924, 001305, 001311, 001877, 002056 e 002074/2020. **3** ficam fora do lote: 017807/2014 (SIAI-DP 2013/14), 005106/2020 (LRF 2016, só recomendação) e 200192/2021 (anexos bimestrais SIAI 2016, IFESP).

**Padrão comum do lote Portal 2019.** O acórdão traz multa ao gestor de 2019 (art. 107, II, f + art. 33, I, c, Res. 011/2016) e uma determinação à atual gestão para divulgar as informações faltantes em 30 ou 90 dias. A pena é multa diária de R$ 100,00 (art. 110), salvo nas exceções abaixo, mais suspensão da certidão de adimplência e ciência ao MPE. Originalmente o monitoramento cabia à DAM.

**Gargalo institucional.** Em **28/05/2026** a DCD devolveu de uma vez, com o mesmo despacho (art. 30, III, Res. 042/2024: monitoramento sem novo relatório é da DIP), os processos 006683, 006940, 000908, 001305, 001311, 001877 e 002056. Em 2025 a CCD tinha remetido vários deles à DCD com base no art. 32 da mesma resolução. **Conclusão: o monitoramento desses portais é da CCD, e não cabe nova remessa à DCD**, com duas exceções. O 001877/2020 depende de análise recursal pela unidade técnica. O 001305/2020 precisa de instrução de mérito, e é preciso definir quem responde aos quesitos do MPC.

**O que dá para fazer em lote:**
1. **Aferição padronizada dos portais.** Usar o método do relatório do 000924/2020: PNTP/Atricon Avalia, site oficial e janela de 2023–2025, com 2019 apenas como marco. Gerar um relatório de monitoramento por processo a partir de um gerador único, no estilo de `processos/utils/gerar_informacoes_*.py`. Candidatos: 006683, 006688, 006940, 006945, 007869, 000742, 000908, 002056, 002074, e o 001311 junto com a resposta do Ev. 124.
2. **Tese uniforme para a cominatória nos casos de descumprimento ou cumprimento tardio.** Afastamento pela LINDB, art. 22, §1º, com a série histórica do PNTP (precedentes: Acórdãos 686/2025, 171/2026 e 223/2026). Quando for liquidar, o teto é de 50% (RI art. 323, II, f), o que dá R$ 10.746,54 em 2026 (Portaria 007/2026), e a contagem começa no dia seguinte ao fim do prazo da citação.
3. **Tramitação imediata**, sem análise nova: 000924/2020 (relatório pronto).
4. **Saneamento pecuniário** junto com o monitoramento:
   - 000908/2020: multa sem citação do art. 117 desde 07/2023.
   - 000742/2020: parcelamento cancelado em 07/2026, sem execução.
   - 006683/2019 (Execução 001849/2025) e 007869/2019 (Execução 000613/2026): multas quitadas, registrar a baixa.
   - 002074/2020 e 002056/2020: multas quitadas, informar ao relator.

**Exceções que pedem tratamento individual:**
- **001877/2020:** ainda não transitou (embargos e pedido de reconsideração da Câmara pendentes). O marcador é prematuro.
- **001305/2020:** sem mérito. O Acórdão nº 31/2022 é cautelar, com astreinte de **R$ 1.000,00/dia**, e o MPC formulou quesitos sobre a tempestividade. Verificar a prescrição quanto ao gestor de 2019.
- **001311/2020:** a decisão monocrática de 10/12/2025 fixou novo prazo e **teto próprio de R$ 5.000,00**.
- **002074/2020:** o teto da cominatória é o do **art. 323, II, b**, e não o da alínea f.
- **006688/2019:** astreinte de **R$ 200,00/dia**, além da diligência do MPC pendente desde 2023.
- **000908/2020:** a cominatória deve ser apurada "em processo autônomo".
- **006940/2019:** o gestor sancionado faleceu e a dívida foi cancelada. Resta só a obrigação da gestão atual.
- **000742/2020 e 200192/2021:** obrigação cumprida antes do trânsito (DAM 2021 / DAI 2024), sem mora para a cominatória.
- **017807/2014:** remessas do SIAI-DP feitas em 2014/2015, antes do acórdão. Basta formalizar o cumprimento.
- **005106/2020:** recomendação sem prazo. Anotação no CGAD e arquivamento.

**Prioridade sugerida:**
1. 000742/2020 e 000908/2020 (débitos sem execução).
2. 001311/2020 e 001305/2020 (resposta ou quesitos aguardando, relator esperando).
3. 006688/2019, 006683/2019 e 006940/2019 (despachos de relator antigos e prazos vencidos).
4. 007869/2019 e 002074/2020.
5. 000924/2020 (só tramitar).
6. Demais.

## Grupo 3: demais tipos com obrigação de fazer (8)

### 014254/2015 — Câmara Municipal de Natal
- **Tipo / relator:** AUD · Ana Paula de Oliveira Gomes (GAANA)
- **Natureza:** auditoria da verba de gabinete/CEAPM (ressarcimento de despesas que não podem ser indenizadas). Decisão-âncora: **Acórdão nº 142/2025-TC (2ª Câmara, 21/07/2025)**, que homologou o **TAG nº 001/2025-PROC-GRC** (art. 122, §3º, LC 464/2012 c/c art. 352 RI) e mandou registrar os prazos para acompanhamento (art. 355 RI). Obrigações do TAG (conforme a petição da Câmara): adequar o Portal da Transparência (29/10/2025); aprovar lei da CEAPM (28/11/2025); regulamentar o controle interno dos processos de CEAPM (15/12/2025); comprovar que segue cumprindo em 30/06/2026 e em 15/12/2026. Cada cumprimento deve ser comunicado em até 10 dias (cláusula terceira). O acórdão não fixou multa nem cominatória.
- **Situação atual:** a Câmara peticionou duas vezes. Ev. 337/338 (27/11/2025) informam a **Lei Municipal nº 8.009/2025** (DOM de 26/11/2025, dentro do prazo) e dizem que a própria lei faz as vezes do regulamento de controle interno; segundo a Câmara, o portal já fora comprovado no apensado 3173/2025 (não conferi). Ev. 343/344 (30/06/2026) comprovam a 1ª etapa de permanência e a suspensão do ressarcimento de publicidade no período eleitoral. A obrigação do controle interno (15/12/2025) só tem essa alegação genérica de que "a lei é o regulamento". Falta a última etapa: 15/12/2026, com comunicação até 25/12/2026. Foi a relatora que mandou à DIP "efetivar o monitoramento requisitado pelo Parquet" (Ev. 333, 13/10/2025). Marcador ativo desde 03/12/2025. **Está na CCD desde 02/12/2025 (~10,5 meses)**, e as duas petições ainda não foram analisadas.
- **Próximo passo (CCD):** fazer uma informação de acompanhamento parcial do TAG, cláusula por cláusula: (i) comparar a Lei 8.009/2025 com as alíneas da cláusula segunda; (ii) checar no portal da Câmara a transparência da CEAPM e o apensado 3173/2025; (iii) avaliar se a lei basta como "regulamento de controle interno" ou se é preciso pedir o ato normativo do Núcleo da Verba Indenizatória e da Controladoria. Remeter à relatora, com vista ao MPC, que é o compromissário e foi pedida pela Câmara. A informação conclusiva, para arquivamento ou para apontar descumprimento, fica para depois de **25/12/2026**.
- **Urgência:** média. Não há prazo vencido sem resposta, mas o processo está parado há 10 meses com duas petições sem análise.

### 002967/2018 — Câmara Municipal de Passa e Fica
- **Tipo / relator:** CGE (omissão das contas anuais de gestão de 2015) · Francisco Potiguar Cavalcanti Júnior (GCPOT)
- **Natureza:** decisão-âncora **Acórdão nº 287/2021-TC (1ª Câmara, Ev. 65)**, mantido pelo **Acórdão nº 129/2026-TC (Pleno, 30/03/2026)**, que não conheceu dos pedidos de reconsideração por falta de interesse recursal. Determinações: notificar o **atual gestor** da Câmara para apresentar as contas anuais de gestão de 2015 em **40 dias**, sob pena de multa; manter suspensa a certidão de adimplência enquanto durar a omissão. Os ex-gestores (Francisco Pinto Ferreira e Maria Eliete Ferreira Borges) não foram multados.
- **Situação atual:** o relator originário (Ev. 112, 27/04/2026) mandou à DIP verificar o cumprimento da obrigação de fazer, ou seja, a apresentação das contas de 2015. Nas peças, **não localizei mandado de notificação ao atual gestor** depois do Ac. 287/2021: só há as intimações de 2021 aos dois ex-gestores para recurso (Ev. 70/71). Por isso o prazo de 40 dias provavelmente nunca começou a correr. No banco `processo` também não achei processo de prestação das contas de 2015 da Câmara (o único CGE de 2015 é este). Marcador desde 04/05/2026. **Está na CCD desde 04/05/2026 (~5,5 meses).**
- **Próximo passo (CCD):** confirmar no SIAI/protocolo se as contas de 2015 foram enviadas. Se não foram, fazer informação ao relator (GCPOT) registrando que o atual Presidente da Câmara nunca foi notificado e sugerindo envio à DE para notificá-lo (art. 45, II, LOTCE), com prazo de 40 dias e advertência de multa, mantida a suspensão da certidão de adimplência. Depois, aguardar o prazo e aferir.
- **Urgência:** média. A obrigação está em aberto desde 2021 sem que a notificação tenha sido expedida, e o processo ficou parado 5 meses na CCD.

### 007970/2018 — Prefeitura Municipal de Espírito Santo
- **Tipo / relator:** REP (acúmulo de cargos públicos, jun/2018) · Renato Costa Dias (GCREN)
- **Natureza:** acúmulo irregular de cargos por 33 servidores. O **Ac. 282/2021-TC (2ª Câmara)** concedeu cautelar mandando abrir processos administrativos individuais em 180 dias e comprovar o resultado em 30 dias, juntando relatórios finais e portarias de exoneração ou demissão. O **Ac. 37/2024-TC (1ª Câmara)** multou o ex-prefeito Fernando Luiz Teixeira de Carvalho (pelo resumo da CIP, houve também astreinte; detalhes não conferidos). O **Ac. 602/2025-TC (Pleno, 15/09/2025)** deu provimento parcial ao recurso só para fixar **20 dias úteis** para envio dos relatórios dos processos administrativos já concluídos, e mandou a DIP monitorar.
- **Situação atual:** o ex-prefeito morreu (Ev. 140). A CCD cadastrou e cancelou os débitos e abriu a execução **000671/2026** (Ev. 175–177, 31/07/2026). O MPC pediu notificação do atual gestor (Quota 020/2026), feita pela Notificação 730/2026 (AR em 15/04/2026). A DE certificou ausência de resposta (Ev. 156, 13/05/2026) e inércia também após a citação para a obrigação de fazer (Ev. 168/169). Em **28/08/2026** o Município respondeu **fora do prazo** (Ev. 186/187): juntou os processos de apuração "na forma em que foram encontrados" (ex.: Proc. 002/2021, servidora Mônica Cortez Alves, só com notificação para fazer a opção) e alegou três trocas de gestão. O MPC (Quota 063/2026) e o relator (Ev. 191, 15/09/2026) mandaram à DIP analisar a resposta. Marcador desde 16/09/2026. **Está na CCD desde 16/09/2026 (~5 semanas).**
- **Próximo passo (CCD):** conferir os processos juntados contra a lista dos 33 servidores do Ev. 4: quantos foram concluídos, com relatório final e com exoneração, demissão ou opção. Se possível, checar no SIAI-DP se os acúmulos ainda existem. Fazer informação de cumprimento parcial ou de descumprimento ao relator (GCREN), sugerindo, se for o caso, nova notificação do atual prefeito com prazo para os processos pendentes.
- **Urgência:** média. A resposta é recente e o monitoramento acabou de chegar, mas a obrigação vem de 2021.

### 009050/2018 — Centrais de Abastecimento do RN S/A (CEASA/RN)
- **Tipo / relator:** REP (descumprimento da Lei 13.303/2016) · Paulo Roberto Chaves Alves (GCPRO)
- **Natureza:** decisão-âncora **Acórdão nº 406/2021-TC (2ª Câmara, 14/09/2021)**, mantido pelo Ac. 559/2023-TC e reformado em parte pelo Ac. 164/2024-TC (Flávio Morais pode continuar como Diretor-Presidente depois de colar grau em 21/08/2023). Pontos que importam ao monitoramento:
  - item "c": minutas-padrão em 30 dias, com multa diária de R$ 100 ao Diretor-Presidente. Cumprido, segundo a DCD (Ev. 197).
  - item "e": cautelar de 30 dias para que **todos os membros da Diretoria** atendam aos requisitos legais de posse, incluindo formação superior compatível (art. 8º, II, Ato Normativo 25/2018-CONTROL; art. 22, II, do Estatuto).
  - item "f": **multa de R$ 500/dia** de descumprimento do item "e", a cargo do Presidente do Conselho de Administração.
- **Situação atual:** por sugestão da CCD (Ev. 202), a CEASA foi notificada (Not. 1485/2025) e respondeu **no prazo** em 06/10/2025 (Ev. 211; certidão Ev. 212), juntando só o processo de eleição do novo Diretor Administrativo, Caio Cezar Ferreira Targino (bacharel em Administração, dez/2024). O relator mandou à DIP (Ev. 215, 15/10/2025). A informação da CCD (Ev. 224, 20/02/2026) remeteu à DCD, mas **o texto relata outro caso** (denúncia da Labinbraz, SESAP/Hospital Giselda Trigueiro), um erro de modelo. A DCD devolveu em 28/05/2026 dizendo que a competência é da DIP (art. 30, III, Res. 042/2024). Marcador desde 29/05/2026. **Está na CCD desde 29/05/2026 (~4,7 meses)**, e a resposta da CEASA tem mais de um ano.
- **Próximo passo (CCD):** analisar a resposta do Ev. 211 contra o item "e". Ela comprova os requisitos de um diretor só; é preciso conferir a composição atual da Diretoria, incluindo o Diretor-Presidente Matheus Silva de Freitas Galvão. Fazer informação ao relator (GCPRO): **cumprimento**, com sugestão de arquivamento ("c" cumprido, "d" é declaratório e "h" é recomendação), ou **cumprimento parcial**, com sugestão de notificação complementar para comprovar a formação de toda a Diretoria. Na mesma peça, apontar o erro de conteúdo da informação do Ev. 224 para não contaminar o histórico.
- **Urgência:** alta. Está parado há quase 5 meses, a resposta tempestiva ficou sem análise por um ano e há uma peça da CCD com conteúdo trocado nos autos.

### 004339/2019 — Prefeitura Municipal de Vila Flor
- **Tipo / relator:** REP (excesso de contratações temporárias) · George Montenegro Soares (GCGEO)
- **Natureza:** decisão-âncora **Acórdão nº 196/2025-TC (1ª Câmara, 07/08/2025)**, transitado em 23/03/2026 depois de um recurso indeferido liminarmente por intempestividade. Itens:
  - a) multa de R$ 10.000,00 a Thuanne Karla Carvalho de Souza;
  - b) **18 meses** para sanear as contratações temporárias irregulares, sob multa diária de R$ 1.000 ao atual gestor (art. 110 LOTCE);
  - c) **60 dias** para apresentar um plano com cronograma de eliminação das irregularidades, sob multa diária de R$ 1.000;
  - d) monitoramento atribuído à **DCP**.
- **Situação atual:** a multa (a) não foi paga após a citação de 5 dias (prazo terminou em 11/08/2026). A CCD abriu a **execução 000951/2026** e deixou os autos na CCD para monitorar a obrigação de fazer (Ev. 109, 07/10/2026). Pela certidão da DE (Ev. 100, 20/08/2026), a Prefeitura foi intimada (Int. 2735/2025, prazo iniciado em 16/01/2026): **o plano de 60 dias venceu em 24/04/2026 sem resposta**; o saneamento de 18 meses vence em **21/07/2027**. Até 21/10/2026 são cerca de 180 dias de mora no item "c" (valor nominal muito acima de qualquer teto). Marcador desde 07/10/2026. **Está na CCD desde 15/09/2026 (~5 semanas).**
- **Próximo passo (CCD):** fazer informação ao relator (GCGEO) registrando que o item "c" não foi cumprido. Sugerir: (i) liquidar a multa cominatória do item "c" a partir de 25/04/2026 contra o atual prefeito (nome não localizado nos autos), observado o teto regimental, que deve ser confirmado; (ii) nova notificação para entregar o plano; (iii) remessa à **DCP**, a quem o acórdão deu o monitoramento do mérito (item d). A CCD acompanha o prazo final de 21/07/2027.
- **Urgência:** alta. Há obrigação vencida há quase 6 meses, com cominatória correndo, e o monitoramento designado (DCP) ainda não foi acionado.

### 101227/2022 — Fundo de Seguridade Social de Macau (MACAUPREV)
- **Tipo / relator:** PEN · Marco Antônio de Moraes Rêgo Montenegro (GAMAR)
- **Natureza:** decisão-âncora **Decisão nº 637/2025-TC (Pleno, 09/07/2025)**, transitada em 16/03/2026. Itens:
  - a) denegação do registro da pensão por morte de Antônia da Silva;
  - b) multa de R$ 1.100,00 ao ex-Diretor-Presidente João Batista Bezerra Filho;
  - c) **60 dias úteis contados do trânsito** para o MACAUPREV regularizar o ato concessivo e o cálculo dos proventos (item C.1 do voto);
  - multa diária de **R$ 50/dia** ao gestor responsável em caso de descumprimento (art. 110), com o teto do art. 323, II, "f", RI.
- **Situação atual:** a multa (b) não foi paga; a CCD abriu a **execução 000941/2026** e manteve os autos para analisar a obrigação de fazer (Ev. 83, 10/09/2026). Os Ev. 56/57 citados pela CCD são só a resposta à Not. 1913/2025, de 2025 e anterior ao trânsito: um formulário cadastral do ex-diretor. **Não comprovam a regularização.** Pela certidão da DE (Ev. 77, 06/08/2026), a citação 1375/2026 ao MACAUPREV teve prazo até **04/08/2026 sem resposta**. Contando do trânsito, como diz a decisão, o prazo teria vencido por volta de 12/06/2026 (estimativa minha). A partir de 05/08/2026 são 78 dias de mora até 21/10/2026, R$ 3.900 nominais e ainda correndo. Marcador desde 08/10/2026. **Está na CCD desde 21/08/2026 (~2 meses).**
- **Próximo passo (CCD):** fazer informação ao relator (GAMAR) registrando que o item "c" não foi cumprido. Sugerir a liquidação da multa diária (termo inicial 05/08/2026 pela contagem da DE, ou em torno de 12/06/2026 pela letra da decisão; cabe ao relator definir) contra o atual Diretor-Presidente do MACAUPREV (nome não localizado nos autos), com o teto da alínea "f", mais nova notificação para regularizar o ato. A regularização em si deve ser aferida depois pela DAP.
- **Urgência:** alta. A obrigação está vencida e a cominatória cresce todo dia; a análise prevista no Ev. 83 está parada há 6 semanas.

### 300734/2026 — Controladoria-Geral do Estado (CONTROL) / DETRAN-RN
- **Tipo / relator:** OFC (Ofício nº 492/2026/CONTROL) · sem relator; quem despachou foi Paulo Roberto Chaves Alves (GCPRO), relator do processo principal
- **Natureza:** comunica o cumprimento do **Acórdão nº 213/2025-TC (1ª Câmara, 04/09/2025)**, dado no proc. **000460/2022** (auditoria de conformidade das multas de trânsito do DETRAN/RN). O acórdão deu **30 dias úteis** ao DETRAN para: (a) registrar contabilmente os repasses mensais ao FUNSET; (b) registrar o PIS/PASEP incidente sobre as multas em contas de controle; (c) publicar no site as informações do art. 320, §2º, do CTB (Portaria 85/2018-DENATRAN), a partir de 2020. Também recomendou indicar o fundamento legal nos processos de despesa. Não houve multa nem cominatória.
- **Situação atual:** o principal 000460/2022 está **arquivado** (ARQUI desde 22/12/2025). A DE abriu o **MON 003973/2025** para monitorar (Ev. 108 do principal), e esse MON **está na CCD** desde 11/03/2026. No principal, o DETRAN não respondeu à intimação (prazo até 27/11/2025; certidão Ev. 100). A comprovação veio só em 14/04/2026, pela CONTROL: Informação 12/NAI e Ofício 492/2026 atestam o cumprimento de (a), (b) e (c), **com a ressalva de que a verificação foi apenas formal, sem análise contábil**. O relator mandou à DIP "inclusive quanto à remessa ao setor competente" (Ev. 4, 15/04/2026). Marcador desde 17/04/2026. **Está na CCD desde 16/04/2026 (~6 meses).**
- **Próximo passo (CCD):** juntar (apensar) este OFC ao **MON 003973/2025** e fazer a análise lá. Conferir os links do portal do DETRAN (arrecadação e despesas de 2020 a 2025) e as evidências de FUNSET/PASEP (relatórios SEI 39376435, 39377353 e anexos de out–dez/2025). Fazer informação de cumprimento ao relator (GCPRO), sugerindo arquivamento do MON. Se a validação contábil for considerada necessária, remeter à DCD.
- **Urgência:** média. O processo está parado há 6 meses, mas não há multa correndo e a prova já está nos autos.

### 000629/2026 — Prefeitura Municipal de Nova Cruz (execução do proc. 000906/2020)
- **Tipo / relator:** EXE · Francisco Potiguar Cavalcanti Júnior (GCPOT)
- **Natureza:** execução da multa de R$ 3.000,00 aplicada a Flávio César Nogueira, ex-prefeito, pelo **Acórdão nº 114/2021-TC (15/04/2021)**, transitado em 10/04/2026, no proc. 000906/2020 (Portal da Transparência 2019). A obrigação de fazer do acórdão (divulgar as informações que faltavam no portal e representar ao MPRN) **fica no processo de origem 000906/2020**, que hoje está no GCPOT, e não nesta execução.
- **Situação atual:** a Prefeitura não respondeu à determinação de desconto em folha (certidão Ev. 59, prazo até 28/09/2026). O responsável não tem vínculo no SIAI-DP (Ev. 64). Foi inscrito no Cadastro de créditos não quitados (Cert. 601014/2026, R$ 4.281,97) e **pagou integralmente em 19/10/2026** (Certidão de quitação 502352/2026, Ev. 65). A informação da CCD (Ev. 66, 20/10/2026) manda à relatoria, mas cita "obrigações pendentes" e "monitoramento", o que não se aplica à execução. Marcador desde 20/10/2026. **Está na CCD desde 30/09/2026 (~3 semanas).**
- **Próximo passo (CCD):** tramitar CCD→DIP→GCPOT com a informação de pagamento integral, sugerindo extinção da execução e arquivamento, e **retirar o marcador "Monitorar obrigação de fazer" desta EXE**. Se for preciso acompanhar a obrigação de fazer, o marcador e o monitoramento ficam no 000906/2020. Não é preciso protesto.
- **Urgência:** baixa. A dívida está quitada; falta só encerrar e corrigir o marcador.

#### Observações: demais tipos
- **Três casos com cominatória vencida e sem liquidação:** 004339/2019 (R$ 1.000/dia desde 25/04/2026), 101227/2022 (R$ 50/dia desde 05/08/2026, ou antes pela letra da decisão) e, eventualmente, 009050/2018 (R$ 500/dia do item "f", se a Diretoria não atender ao item "e"). Nos dois primeiros, a informação ao relator deve trazer a memória de cálculo com o teto regimental e o nome do gestor atual (não localizado nos autos), seguindo o padrão do caso 101053/2022 do MACAUPREV.
- **Monitoramento atribuído a outra unidade:** o Ac. 196/2025 (004339/2019) põe o monitoramento na DCP, e o Ac. 406/2021 (009050/2018) o punha na DAI, cujo papel a DCD devolveu à DIP. Convém deixar claro na informação o que fica com a CCD (prazos, cominatória) e o que vai para a unidade técnica (mérito).
- **Marcador fora de lugar:** 000629/2026 é uma execução já quitada; a obrigação de fazer é do 000906/2020. 300734/2026 é um ofício avulso e deve ser juntado ao MON 003973/2025, que também está na CCD.
- **Peça da CCD com conteúdo errado:** a Informação Instrutiva do Ev. 224 do 009050/2018 (20/02/2026) descreve outro processo (Labinbraz/SESAP). Vale registrar a correção na próxima peça.
- **Os mais antigos parados na CCD:** 014254/2015 (~10,5 meses), 300734/2026 (~6 meses), 002967/2018 (~5,5 meses) e 009050/2018 (~4,7 meses), todos com resposta ou prova nos autos esperando análise ou com notificação nunca feita (002967).
- **Notificação nunca expedida:** no 002967/2018, o atual gestor não aparece notificado desde o Ac. 287/2021; o prazo de 40 dias não começou. Isso precisa ser confirmado antes de qualquer informação de descumprimento.
- **Prazo a acompanhar:** TAG 001/2025 da Câmara de Natal, última comprovação até 25/12/2026 (15/12 + 10 dias).
