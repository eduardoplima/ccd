# POP-CCD-005 — Protesto extrajudicial

| Campo | Valor |
|---|---|
| **Código** | POP-CCD-005 |
| **Versão** | 1.0 |
| **Data de emissão** | 20/08/2026 |
| **Elaborado por** | CCD |
| **Aprovado por** | _pendente de aprovação_ |
| **Próxima revisão** | 08/2027 |

## 1. Objetivo

Executar multas mediante protesto eletrônico em cartório, do envio da remessa ao tratamento do retorno (pagamento, cancelamento ou insucesso).

## 2. Escopo

Processos de execução com multa cuja modalidade seja o protesto, com responsável residente no RN (marcadores da família "Protesto").

## 3. Referências normativas

- Lei federal nº 9.492/1997 — protesto de títulos e outros documentos de dívida (inclui certidões de dívida dos Tribunais de Contas).
- Res. nº 013/2015-TCE, art. 25, II — protesto em caso de insucesso do desconto em folha.

## 4. Definições e siglas

- **Remessa**: lote de processos enviado ao instituto de protesto.
- **CADINQ**: ver [POP-CCD-003](cadinq).

## 5. Responsabilidades

- **Servidor da CCD**: revisar processos, montar e enviar remessas, acompanhar o painel de pendências, tratar retornos.
- **Instituto de protesto / cartório**: processar as remessas e devolver os retornos.
- **Diretor**: definir o prazo de aguardo após o protesto sem pagamento.

## 6. Recursos e sistemas

Área Restrita — *Administrativo / Protesto Extrajudicial / Envio de Remessa*; painel de pendências. Ver também [Rotinas mensais](../rotinas-mensais).

## 7. Descrição das atividades

1. Verificar se o [CADINQ](cadinq) está atualizado.
2. Verificar se o responsável reside no RN.
3. Distribuir o processo para o usuário (habilita o efetivo envio para o protesto).
4. Revisar o processo no marcador **"Protesto Eletrônico - Revisar antes de enviar"**: garantir que está com todas as informações corretas, emitir ou atualizar o CADINQ, e mover para o marcador **"Protesto Eletrônico"**.
5. Incluir no lote: *Envio de Remessa* — selecionar os processos para incluir na remessa. Aguardar o dia seguinte para enviar.
6. No dia seguinte, na mesma tela, selecionar os processos incluídos na remessa (parte de baixo da página) e enviar. Mover os enviados para **"Protesto Eletrônico - Enviado"**.
7. Aguardar o retorno pelo painel de pendências:
   - **Confirmação de envio ao cartório:** *Enviado* → aguardar; *Não enviado* → identificar as razões e providenciar.
   - **Confirmação do protesto:** *Cancelado* → identificar as razões e providenciar; *Pago* → proceder conforme o acórdão; *Protestado* → verificar se houve pagamento após o protesto e providenciar.
8. Desfechos:
   - **Pagamento integral:** gerar certidão de quitação e enviar ao Relator, caso não haja outra providência ou outros responsáveis.
   - **Pagamento parcelado:** monitorar a adimplência e emitir certidões ([POP-CCD-009](parcelamento)).
   - **Sem pagamento / inadimplência:** aguardar o prazo definido pelo diretor e enviar ao MP de Contas para a [dívida ativa](divida-ativa).
   - **Protesto efetivo sem pagamento após 2 meses:** verificar vínculo para [desconto em folha](desconto-em-folha); sem vínculo, encaminhar ao MP de Contas (mala direta **"Protesto sem êxito e sem vínculo"**), atualizando o CADINQ.

### Fluxo dos marcadores

`Enviar para Protesto` → `Protesto Eletrônico - Revisar antes de enviar` → `Protesto Eletrônico` → `Protesto Eletrônico Incluído na Remessa` → `Protesto Eletrônico - Confirmação de Envio` → `Protesto Eletrônico - Enviado` → `Protesto Efetivo <mês>` **ou** `Protesto Sem Êxito/Sem Vínculo - Enviar MPContas`

## 8. Registros

- Remessas enviadas e retornos no painel de pendências da Área Restrita.
- Marcadores refletindo o estágio de cada processo (fluxo acima).
- Certidões de quitação; despachos de encaminhamento ao MP de Contas.

## 9. Pontos de controle e exceções

Restrições operacionais **invioláveis**:

- Só é possível protestar responsáveis que **residem no RN**.
- Lotes contam com os processos incluídos até **23h59**; só podem ser enviados os lotes incluídos **até o dia anterior**.
- Remessas só **entre os dias 1 e 15 do mês** e **até as 10h59**.
- Há um limite de protestos por remessa (**limitador ainda não identificado** — pendência).

Problemas no retorno (marcador **"Protesto - Cancelamento e Providências"**):

- Suporte com o **Jorge, da DTI**.
- Instituto de Protesto: **Kelly ou Karla**, telefone/WhatsApp **2010-7096**.

## 10. Histórico de revisões

| Versão | Data | Alteração |
|---|---|---|
| 1.0 | 20/08/2026 | Versão inicial — conversão ao formato POP (ISO 10013:2021). |
