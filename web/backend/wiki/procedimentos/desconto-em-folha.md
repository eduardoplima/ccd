# POP-CCD-004 — Desconto em folha

| Campo | Valor |
|---|---|
| **Código** | POP-CCD-004 |
| **Versão** | 2.0 |
| **Data de emissão** | 25/11/2026 |
| **Elaborado por** | CCD |
| **Aprovado por** | _pendente de aprovação_ |
| **Próxima revisão** | 11/2027 |

## 1. Objetivo

Executar multas mediante desconto em folha de pagamento do responsável que possui vínculo com a administração pública, com crédito ao FRAP.

## 2. Escopo

Processos de execução com multa cuja modalidade determinada pelo Relator seja o desconto em folha (marcadores "Desconto em Folha" e variantes).

## 3. Referências normativas

- Res. nº 013/2015-TCE, art. 25, I — desconto integral da dívida nos vencimentos, subsídios, salários ou proventos, observados os limites legais; art. 25, § 1º, I — desconto com crédito ao FRAP; art. 25, §§ 3º e 4º — comprovação do desconto e do crédito em 15 dias (ver [POP-CCD-011](verificacao-frap)).
- LC Estadual nº 464/2012, título VI.

## 4. Definições e siglas

- **FRAP**: Fundo de Reaparelhamento do TCE/RN, destinatário do crédito dos descontos.
- **SIAI-DP**: sistema de auditoria de pessoal usado para verificar vínculo estadual/municipal.
- **DE**: Diretoria de Expediente (expede a notificação ao órgão).
- **Cadastro**: registro do desconto em folha no módulo **Desconto em Folha** da webapp da CCD — um por processo, débito e responsável —, que reúne notificação, recebimento, resposta do órgão, valores e conciliação com o FRAP.
- **Conciliação**: vínculo entre uma parcela informada pelo órgão e o crédito correspondente no FRAP.

## 5. Responsabilidades

- **Servidor da CCD**: verificar vínculo, preparar o despacho de notificação, conferir o cadastro, a resposta extraída e a conciliação, e acompanhar o retorno.
- **DE**: expedir a notificação ao órgão pagador.
- **Órgão pagador**: efetuar o desconto e repassar ao FRAP, comprovando nos termos do art. 25, §§ 3º e 4º.

## 6. Recursos e sistemas

- SIAI-DP; Portal da Transparência do Governo Federal; Câmara dos Deputados; Senado Federal (verificação de vínculo).
- Webapp da CCD: **Automação → Desconto em Folha** (geração do despacho) e módulo **Desconto em Folha** (cadastro, notificação, recebimento, resposta, valores e conciliação com o FRAP; retenções do SIAI Pessoal, inclusive pensionistas).
- Área Restrita / e-Contas (CADINQ, despachos, marcadores).

## 7. Descrição das atividades

1. Verificar se o responsável tem vínculo com a administração estadual, municipal ou federal, através do **SIAI-DP** (também disponível no módulo Desconto em Folha, que cobre servidores e pensionistas), do **Portal da Transparência do Governo Federal**, da **Câmara dos Deputados** e do **Senado Federal**.
2. **Sem vínculo:** proceder com outra modalidade — [protesto](protesto) ou [inscrição na dívida ativa](divida-ativa), conforme decisão do Relator.
3. **Com vínculo:**
   1. Verificar se o [CADINQ](cadinq) está atualizado.
   2. **Despacho:** gerar o despacho em **Automação → Desconto em Folha**, a partir dos processos com o marcador "DESCONTO EM FOLHA - Implementar" (órgão, responsável e valores já preenchidos); conferir, cadastrar nos autos e encaminhar à DE para notificar o órgão.
   3. A DE expede a notificação para o órgão que fará o desconto.
   4. **Cadastro:** conferir o cadastro no módulo Desconto em Folha (processo, débito, responsável e órgão notificado). A varredura diária cria o cadastro quando localiza notificação nova; não havendo, usar **"Novo cadastro"**.
   5. **Retorno da notificação:** acompanhar as colunas **Notificação**, **Recebimento** e **Resposta** da lista. O botão **"Localizar notificações"** atualiza o mandado da DE e o recebimento (comunicação eletrônica, recebimento tácito, AR ou certidão da DE).
   6. **Resposta do órgão:** no detalhe do cadastro, acionar a extração da resposta (lida no processo apensado ou no principal) e **conferir o trecho citado e as parcelas** contra o documento. Resposta com status **"Conferir"** exige a leitura do PDF; parcela não extraída é lançada manualmente.
   7. **Conciliação:** a conciliação automática roda diariamente e vincula a parcela ao crédito do FRAP quando há um único candidato. Nos demais casos, vincular manualmente no painel **"Créditos no FRAP"**. As retenções TCE/FRAP do SIAI Pessoal, exibidas no detalhe, servem de contraprova do desconto.
   8. O desfecho — informação de conciliação nos autos, notificação por repasse não localizado — segue o [POP-CCD-011 — Verificação de transferência ao FRAP](verificacao-frap); a baixa da dívida segue o [POP-CCD-012 — Baixa e saldo residual](baixa-saldo-residual).

## 8. Registros

- Despacho de notificação encaminhado à DE.
- Cadastro no módulo Desconto em Folha, com notificação, recebimento, resposta do órgão, valores e conciliação — registro do acompanhamento.
- Marcadores do ciclo: **Implementar → Verificar transferência FRAP (5953) → Fim**.
- Marcadores de acompanhamento: "Desconto em Folha Acompanhamento Geral"/"Acompanhamento Nereu" (desconto confirmado, pagamento não confirmado); "Desconto em Folha - Suspensão por Decisão Judicial".
- Informação de conciliação registrada conforme POP-CCD-011.

## 9. Pontos de controle e exceções

- A extração da resposta é automatizada e **pode citar trecho inexistente** — a conferência do servidor contra o documento é obrigatória antes de considerar o valor.
- Em processo com **vários responsáveis**, conferir se os valores extraídos são da pessoa do cadastro, e não de outro responsável do mesmo processo.
- Cada crédito do FRAP vincula-se a **uma única parcela**; o sistema recusa o reaproveitamento.
- Uma única transferência pode cobrir um **par de processos** — conciliar o par junto (ver POP-CCD-011).
- O órgão desconta pela referência do **débito original**, ainda que ele tenha sido desdobrado; manter o cadastro vinculado a esse débito.
- Cadastro cujo débito foi enviado à PGE é **desativado automaticamente**; se o envio foi indevido, marcar "PGE indevido" para mantê-lo ativo.
- Resposta digitalizada sem texto, ou que apenas acusa o recebimento, fica **sem valor** — lançar as parcelas manualmente quando houver comprovante.

> **Lacuna:** o módulo não cobra o órgão que deixa de responder em 15 dias (art. 25, §§ 3º e 4º). A reiteração via DE é manual, a partir dos cadastros com recebimento e sem resposta.

## 10. Histórico de revisões

| Versão | Data | Alteração |
|---|---|---|
| 1.0 | 20/08/2026 | Versão inicial — conversão ao formato POP (ISO 10013:2021). |
| 2.0 | 25/11/2026 | Incorpora o módulo Desconto em Folha da webapp (cadastro, notificação/recebimento, resposta do órgão e conciliação com o FRAP); elimina as lacunas de acompanhamento do retorno e de controle dos pagamentos. |
