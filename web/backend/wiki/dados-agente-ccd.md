# Views de dados para agentes de IA (vwCCD*)

Cinco views no banco **BdDIP** (SQL Server, mesma instância do `processo`) que expõem, já com as regras de negócio aplicadas, o que um agente precisa para redigir informações da CCD: situação dos débitos, determinações curadas e conciliação com o FRAP. Criadas pela migração `0022_views_agente_ccd`. Este texto foi escrito para ser colado no prompt do agente.

Convenções comuns: colunas em `snake_case`; textos `char` já vêm sem espaços à direita; processos no formato `NNNNNN/AAAA` (zero à esquerda, ex.: `005202/2020`); documentos (CPF/CNPJ) só dígitos; rótulos de domínio (`status`, `tipo`, `pge_status`, `protesto_status`) são fixos por código, com acentuação correta; datas em `date`/`datetime` do SQL Server.

## 1. `dbo.vwCCDDebito` — um débito por linha (grão: cadeia)

No sistema, cada pagamento parcial fecha o registro e cria um **filho** com o saldo (`Exe_Debito.IdDebitoAnterior`). A view junta essa cadeia numa linha: **identidade e valor imputado vêm da raiz; situação e saldo vêm da folha** (o registro vigente). Sem filtro de status: filtre por `cancelado = 0` para a carteira ativa.

| Coluna | Tipo | Significado |
|---|---|---|
| `id_debito` | int | Id da raiz (identidade do crédito, estável). Chave para `vwCCDDebitoResponsavel`, `vwCCDFrapLancamento.id_debito` e `vwCCDFrapDescontoFolha.id_debito` (esses guardam o id do nó da época — junte por `id_debito` **ou** `id_debito_vigente`). |
| `id_debito_vigente` | int | Id da folha (registro atual no sistema). |
| `nos_na_cadeia` | int | Quantos registros compõem a cadeia (1 = nunca teve pagamento parcial). |
| `cod_tipo`, `tipo` | int, texto | 1 Ressarcimento, 2 Multa, 3 Remanejamento, 4 Multa Percentual, 5 Multa Cominatória. |
| `natureza` | texto | `multa` (tipos 2, 4, 5) ou `ressarcimento`. |
| `cod_status`, `status` | int, texto | Situação **vigente** (`Exe_StatusDivida`): 1 Em Aberto, 2 Pago Integralmente, 3 Pago parcialmente, 8 Parcelado, 9 Pago Aguardando Compensação, 20 Suspenso; 4/6/10/17 canceladas por perda (extinção, prescrição, perdão, óbito); 7/16/19 canceladas por decisão (relator, novo acórdão, judicial); 5/13/14/15/18/21 canceladas por substituição ou erro de cadastro. |
| `cancelado` | bit | 1 quando o status é de cancelamento ou há `data_cancelamento`. |
| `valor_imputado` | money | Valor da condenação (raiz). Valor histórico, sem correção. |
| `valor_recuperado` | money | Soma do que foi pago em todos os registros da cadeia. |
| `saldo_registrado` | money | `valorOriginalDebito` da folha: saldo histórico, **sem** correção monetária. |
| `valor_atualizado` | money | Valor atualizado calculado pela função do sistema (`fn_Exe_RetornaValorAtualizado`) sobre a folha. É a coluna "Valor Atualizado" do despacho de antecedentes. |
| `data_decisao`, `data_ato` | datetime | Datas da decisão e do ato que imputou o débito. |
| `data_transito` | datetime | Trânsito em julgado registrado no débito (menor data da cadeia). NULL em ~11% das cadeias; a certidão de trânsito do processo não é consultada. |
| `data_baixa`, `data_cancelamento` | datetime | Da folha. |
| `setor_debito` | texto | Setor que cadastrou o débito. |
| `id_processo_origem`, `processo_origem`, `setor_origem`, `relator_origem`, `assunto_origem` | | Processo em que a condenação foi imputada. |
| `id_processo_execucao`, `processo_execucao`, `setor_execucao` | | Processo de execução, quando instaurado (NULL se ainda não há). |
| `responsaveis` | nvarchar(4000) | `Nome (documento); Nome (documento)` — responsáveis solidários do débito, em ordem alfabética. **Não** rateie o valor entre eles: a solidariedade é pelo total. Use `vwCCDDebitoResponsavel` para filtrar por CPF ou nome. |
| `protestado` | bit | Houve protesto em algum registro da cadeia. |
| `protesto_cod`, `protesto_status` | int, texto | Situação do protesto na folha: 1 Incluída em lote de remessa, 2 Enviada a Protesto, 3 Protestada, 4 Paga, 5 Solicitação de Desistência, 6 Solicitação de Cancelamento (Após o Protesto), 7 Solicitação de Autorização de Cancelamento (Dívida Paga ou Parcelada), 8 Cancelada antes do Protesto, 9 Cancelada após o Protesto, 10 Cancelada por Pagamento, 11 Sustada por Ordem Judicial, 12 Devolvida por Irregularidade. |
| `mc_valor_dia`, `mc_total`, `mc_teto`, `mc_data_inicio`, `mc_data_fim`, `mc_dias` | | Detalhe da multa cominatória (tipo 5). `mc_dias` = total ÷ valor/dia, que é o número de diárias imputado; **não** calcule por diferença de datas (dá resultado diverso). |
| `pge_id`, `pge_numero_cda`, `pge_status_cod`, `pge_status`, `pge_homologado`, `pge_data_envio`, `pge_valor_atualizado`, `pge_valor_pago` | | Inscrição em dívida ativa (`PGE_Processo`, registro mais recente da cadeia). `pge_status`: 1 Inscrito em Dívida Ativa, 2 Negociado, 3 Quitado, 4 Exigibilidade Suspensa, 5 Cancelado, 6 Pagamento em Atraso, 7 Remissão, 8 Prescrito. `pge_homologado = 1` é a inscrição efetiva. `pge_valor_atualizado` é datado (data de envio). **`pge_valor_pago` pode estar em dobro** por importações repetidas na PGE — não cite sem conferir. |
| `parc_id`, `parc_situacao_cod`, `parc_situacao`, `parc_ativo`, `parc_numero_parcelas`, `parc_parcelas_pagas` | | Parcelamento mais recente da cadeia. Situação: 1 Aguardando início, 2 Em curso, 3 Cancelado, 4 Quitado, 5 Cancelado por inadimplência, 6 Indefinida. `parc_ativo` = situação 1 ou 2 e débito não cancelado. |

Desempenho: filtrada por processo, CPF ou id, responde em ~1 s; a varredura completa (~17 mil linhas) leva ~1 min por causa da função de valor atualizado. Evite `SELECT *` sem filtro.

## 2. `dbo.vwCCDDebitoResponsavel` — pessoa × débito

Uma linha por pessoa vinculada ao débito. Use para achar débitos por CPF/CNPJ ou por nome e depois juntar com `vwCCDDebito` por `id_debito`.

| Coluna | Significado |
|---|---|
| `id_debito` | Raiz da cadeia (= `vwCCDDebito.id_debito`). |
| `id_pessoa`, `nome` | Da tabela de pessoas do sistema. |
| `nome_busca` | Nome em minúsculas, para `LIKE '%fulano%'`. Não remove acentos. |
| `documento` | CPF (11 dígitos) ou CNPJ (14). |
| `tipo_pessoa` | `CPF`, `CNPJ` ou NULL. |

Fluxo de antecedentes (POP-CCD-007): `SELECT d.* FROM vwCCDDebito d JOIN vwCCDDebitoResponsavel r ON r.id_debito = d.id_debito WHERE r.documento = '<cpf>'` (ou `r.nome_busca LIKE '%<nome>%'`, sujeito a homônimos). As colunas do despacho são `processo_origem`, `processo_execucao`, `tipo`, `valor_imputado`, `valor_atualizado`, `data_transito`, `status`, `protesto_status`, `pge_status`.

## 3. `dbo.vwCCDDeterminacao` — obrigações e recomendações curadas

Uma linha por obrigação ou recomendação **aprovada** na revisão humana do CGAD (`ObrigacaoStaging`/`RecomendacaoStaging` com `Status = 'approved'`). Itens pendentes ou rejeitados não aparecem. O acervo cresce a cada revisão.

| Coluna | Significado |
|---|---|
| `tipo` | `obrigacao` ou `recomendacao`. |
| `id_staging`, `id_ner`, `id_final` | Ids da linha revisada, da extração original (NER/LLM) e da tabela final `Obrigacao`/`Recomendacao` (pode ser NULL). |
| `id_processo`, `processo`, `setor_atual`, `assunto`, `interessado`, `relator` | Processo em que a determinação foi fixada. `setor_atual` é a tramitação de hoje, não o setor competente. |
| `id_composicao_pauta`, `id_voto_pauta`, `acordao`, `data_sessao` | Decisão (acórdão `NNN/AAAA` e data da sessão). |
| `data_transito` | Primeiro trânsito em julgado **posterior** à sessão — é dele que corre o prazo. |
| `tem_cgr` | O processo tem registro no Cadastro Geral (`Obg_Obrigacao`), que está sem alimentação desde 2025. |
| `descricao` | Texto **curado** pelo revisor. |
| `prazo_texto` | Prazo como escrito na decisão (texto livre: "30 dias", "72h", "dias úteis"...). |
| `data_cumprimento` | **Data-limite** calculada, não prova de cumprimento. A base não registra cumprimento efetivo. |
| `orgao_responsavel`, `id_orgao_responsavel` | Órgão destinatário. O placeholder "Desconhecido" do pipeline virou NULL. O mesmo órgão pode aparecer com grafias e ids distintos. |
| `nome_responsavel`, `id_pessoa_responsavel`, `documento_responsavel` | Pessoa destinatária (na obrigação, a responsável pela multa cominatória; documento só existe na obrigação). |
| `tem_multa_cominatoria`, `valor_multa_cominatoria` | Multa diária prevista em caso de descumprimento (obrigação). |
| `de_fazer` | 1 obrigação de fazer, 0 de não fazer (NULL na recomendação). |
| `cancelado` | Só na recomendação. |
| `revisor`, `data_revisao`, `observacoes_revisao` | Registro da revisão humana. |

## 4. `dbo.vwCCDFrapLancamento` — extrato bancário do FRAP

Lançamentos das contas do FRAP no Banco do Brasil. **Grão: lançamento × vínculo** — um lançamento sem conciliação tem uma linha; um lançamento conciliado tem uma linha por vínculo (um crédito de guias `EXATO_LOTE` pode casar dezenas de boletos/débitos). Para somar o extrato, use `SELECT DISTINCT id_lancamento, valor` ou filtre `matcher IS NULL OR ...` com cuidado.

| Coluna | Significado |
|---|---|
| `id_lancamento`, `conta`, `periodo`, `competencia` | `periodo` é `MMAAAA`; `competencia` é `AAAAMM` (ordenável). |
| `dt_movimento`, `historico`, `documento`, `doc_data`, `valor`, `valor_dc`, `descricao` | Linha do extrato. `valor_dc`: `C` crédito (entrada), `D` débito (saída). Em TED, `documento` identifica o **remetente** (agência+conta), não a transação. |
| `cod_categoria`, `categoria` | 1 `OB_RECEBIDA` (ordem bancária SIGEF — repasse de órgão, inclusive desconto em folha), 2 `GUIA_RECEBIMENTO` (boleto), 3 `TRANSFERENCIA` (TED/PIX), 4 aplicação/resgate, 5 linha de saldo, 9 outros. |
| `arrecadacao` | 1 = crédito nas categorias 1, 2, 3 ou 9 (o que conta como arrecadação; 4 e 5 não). |
| `cpf_cnpj_depositante`, `cpf_depositante`, `cpf_cnpj_ambiguo` | Extraídos da descrição; **NULL em ~98%** dos lançamentos. `cpf_depositante` = últimos 11 dígitos, para casar CPF com zeros à esquerda. |
| `matcher` | `GUIA` (boleto pago), `PESSOA` (CPF + valor), `OB` (ordem bancária SIGEF), `DESCONTO_FOLHA` (parcela de desconto em folha) ou NULL. |
| `status_match`, `conciliado` | Código do resultado do matcher; `conciliado = 1` só nos códigos de sucesso (`EXATO`, `EXATO_POR_ORDEM`, `EXATO_PESSOA_VALOR`, `EXATO_LOTE`, `OK_TUDO`, `MATCH_MANUAL`, `REPASSE_VIA_ORGAO`). |
| `id_debito`, `id_boleto`, `id_processo` | Do vínculo (GUIA/PESSOA/DESCONTO_FOLHA). OB não conhece o débito. |
| `cpf_cnpj_vinculo`, `nome_vinculo`, `valor_vinculo`, `data_pagamento_vinculo` | Pessoa e valor do lado casado (no OB: credor da ordem bancária). |
| `ob_ano_sigef`, `ob_numero`, `ob_credor`, `ob_unidade_gestora` | Só no matcher OB. |
| `df_id_plano`, `df_numero_parcela`, `df_competencia`, `df_valor_contracheque`, `df_is_manual` | Só no matcher DESCONTO_FOLHA. |

Limitação: o repasse da PGE (dívida ativa) **não tem vínculo** no extrato; a informação de pagamento pela PGE está em `vwCCDDebito.pge_*`.

## 5. `dbo.vwCCDFrapDescontoFolha` — parcelas do desconto em folha

Uma linha por parcela de plano de desconto em folha, com o resultado da conciliação parcela × contracheque (SIAI) × lançamento do extrato. É a base do POP-CCD-011.

| Coluna | Significado |
|---|---|
| `id_plano`, `origem` | Plano. `origem`: `P` cadastrado no processo, `M` manual, `S` derivado da folha SIAI (sem processo nem débito), `C` notificação da CCD. |
| `id_processo`, `processo`, `id_debito`, `id_parcelamento` | Vínculo com o processo e o débito (NULL em planos `S`/`M`). |
| `cpf_cnpj`, `nome_pessoa`, `id_orgao`, `nome_orgao` | Servidor descontado e órgão notificado. |
| `qtd_parcelas_planejadas`, `valor_total_esperado`, `situacao_parcelamento`, `plano_ativo` | Plano. **Plano concluído ≠ dívida quitada**: os planos são tranches menores que o débito. |
| `id_parcela`, `numero_parcela`, `competencia`, `valor_esperado`, `data_vencimento`, `data_pagamento_parcela`, `situacao_parcela` | Parcela. `competencia` é `AAAAMM`. `data_pagamento_parcela` preenchida = repasse confirmado. |
| `rn_duplicata` | A mesma parcela (CPF + competência + valor) aparece em até 5 planos sobrepostos. **Some só `rn_duplicata = 1`.** |
| `status_match`, `conciliado` | `OK_TUDO` (descontada e repassada), `DESCONTADA_SEM_REPASSE`, `REPASSADA_SEM_DESCONTO`, `PARCELA_AGUARDANDO`, `NAO_DESCONTADA`, `BAIXADA_SEM_RASTRO`, `MATCH_MANUAL`, `REPASSE_VIA_ORGAO`; NULL = ainda não conciliada. |
| `valor_contracheque`, `is_manual`, `observacao` | Valor da rubrica TCE/FRAP no contracheque e marca de conciliação manual. |
| `id_lancamento`, `lanc_dt_movimento`, `lanc_valor`, `lanc_historico` | Lançamento do extrato casado (junte com `vwCCDFrapLancamento`). |

O quadro de descontos de CPFs sem plano cadastrado não está aqui: vem da view `dbo.vwSiaiPessoalFolhaCompletaTodas` (BdDIP) filtrando `vantagem_desconto = 'D'` e `nome_rubrica` contendo `tce`, `frap` ou `tribunal de contas` (e não `VANT`), pela competência da **folha** (`ano`/`mes`), nunca pela do item.

## Permissões para o login do agente

As views ficam no BdDIP, mas leem tabelas do banco `processo` com nome de três partes; sem encadeamento de propriedade entre bancos, o login precisa de `SELECT` também nesses objetos (é o mesmo problema que já quebrou as `vwDespesa*` com o BdINFOCEX): `Exe_Debito`, `Exe_StatusDivida`, `Exe_DebitoPessoa`, `GenPessoa`, `Exe_Debito_MultaCominatoria`, `PGE_Processo`, `Exe_Parcelamento`, `Exe_Parcela`, `Processos`, `Relator`, `Processo_TransitoJulgado`, `vw_ia_votos_acordaos_decisoes`, `Obg_Obrigacao` e `EXECUTE` em `fn_Exe_RetornaValorAtualizado`. No BdDIP: `SELECT` nas cinco `vwCCD*` (e em `vwSiaiPessoalFolhaCompletaTodas`, se for usar o quadro de descontos).
