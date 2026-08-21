# POP-CCD-012 — Baixa da dívida e saldo residual pós-desconto

| Campo | Valor |
|---|---|
| **Código** | POP-CCD-012 |
| **Versão** | 1.0 |
| **Data de emissão** | 20/08/2026 |
| **Elaborado por** | CCD |
| **Aprovado por** | _pendente de aprovação_ |
| **Próxima revisão** | 08/2027 |

## 1. Objetivo

Dar baixa nas dívidas pagas por desconto em folha após a conciliação do repasse ao FRAP, comunicando o pagamento ao Relator e tratando o saldo residual gerado por atualização monetária posterior ao desconto.

## 2. Escopo

Processos de execução com multa paga por desconto em folha e transferência ao FRAP conciliada ([POP-CCD-011](verificacao-frap)).

## 3. Referências normativas

- Res. nº 013/2015-TCE, art. 26 — comprovado o recolhimento, exclusão do responsável do Cadastro Informativo de Créditos não Quitados e posterior arquivamento; parágrafo único — certidão declaratória da quitação nos autos; art. 25, II e § 7º.
- LC Estadual nº 464/2012, art. 159.

## 4. Definições e siglas

- **Cadeia de débitos**: versões do mesmo crédito encadeadas por `IdDebitoAnterior`; a situação vigente é a da **folha** (nó sem filho).
- **Saldo residual**: pequeno valor remanescente no débito-filho ("Em Aberto") decorrente da atualização monetária posterior ao desconto — o órgão pagador desconta e repassa o valor da notificação e não reprocessa a atualização perante o Tribunal.

## 5. Responsabilidades

- **Servidor da CCD**: verificar a cadeia do débito, elaborar a informação ao Relator e propor o desfecho.
- **Relator**: decidir sobre o cancelamento do resíduo e o arquivamento.

## 6. Recursos e sistemas

- Sistema de execução: cadeia `Exe_Debito`/`IdDebitoAnterior`, histórico do débito (`Exe_HistoricoDebito` — narrativa "Desconto em folha efetuado em \<mês\> ... Transferência para o FRAP verificada"), extrato do FRAP (nº da OB, datas de emissão e crédito).
- Área Restrita (informações, tramitação).
- Geração automatizada das informações no repositório da CCD (modelo `nereu_baixa`).

## 7. Descrição das atividades

1. **Verificar a cadeia do débito** (situação vigente = folha) e classificar o desfecho:
   - **Quitado**: débito-pai "Pago Integralmente" e eventual resíduo do filho já cancelado — não há o que cancelar;
   - **Com saldo residual**: pai "Pago parcialmente" e filho(s) "Em Aberto" com pequeno valor de atualização posterior ao desconto.
2. **Refazer a conciliação na informação**: resposta do órgão pagador (ofício autuado e apensado à execução, com o evento indicado), competência do desconto, o par de processos coberto pela mesma ordem bancária e o item do extrato do FRAP (nº da OB, data de emissão e data do crédito).
3. Se o processo estava **sobrestado**, remeter aos dois eventos do sobrestamento (última informação da CCD anterior à decisão + decisão do Relator).
4. **Propor o desfecho ao Relator**:
   - **Quitado**: tomar a conciliação como comprovação do recolhimento e pedir a exclusão do Cadastro Informativo e o **arquivamento** (art. 26), com certidão declaratória de quitação (art. 26, parágrafo único);
   - **Com saldo residual**: como o resíduo não é imputável ao responsável, sugerir o **cancelamento do valor residual** com quitação e arquivamento, e trazer no encaminhamento o **pedido subsidiário** de arquivamento sem cancelamento (art. 159 da LC 464/2012 e art. 25, II e § 7º, da Res. 013/2015).
5. Cadastrar, assinar e tramitar a informação ao gabinete do Relator.
6. Após a decisão: executar as providências (exclusão do Cadastro Informativo, baixa, arquivamento).

## 8. Registros

- Informação de baixa cadastrada, assinada e tramitada.
- Histórico do débito com a conciliação registrada.
- Certidão declaratória de quitação; exclusão do Cadastro Informativo.

## 9. Pontos de controle e exceções

- **É o saldo residual — dívida formalmente em aberto — que impede o arquivamento imediato** após a baixa; por isso o pedido de cancelamento vai junto da comunicação de pagamento.
- Casos "pago e conciliado, mas ainda Em Aberto" na cadeia indicam baixa não refletida no status — conferir o histórico do débito antes de tratar como inadimplência.
- Descontos em **pares de processos** (uma OB para dois): a informação de cada processo cita o par.
- O relator relevante é o do processo de **origem** (na execução, o relator registrado costuma ser o padrão da CCD e não distingue nada).

## 10. Histórico de revisões

| Versão | Data | Alteração |
|---|---|---|
| 1.0 | 20/08/2026 | Versão inicial — POP novo (ISO 10013:2021), a partir do fluxo de baixa em uso. |
