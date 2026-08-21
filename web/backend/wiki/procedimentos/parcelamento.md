# POP-CCD-009 — Monitoramento de parcelamento

| Campo | Valor |
|---|---|
| **Código** | POP-CCD-009 |
| **Versão** | 1.0 |
| **Data de emissão** | 20/08/2026 |
| **Elaborado por** | CCD |
| **Aprovado por** | _pendente de aprovação_ |
| **Próxima revisão** | 08/2027 |

## 1. Objetivo

Acompanhar os parcelamentos concedidos, a adimplência das parcelas e as providências em caso de inadimplência ou quitação.

## 2. Escopo

Processos nos marcadores "Parcelamento em Curso" e "Parcelamento Inadimplentes". Executado no início do mês (primeiros 5 dias úteis).

## 3. Referências normativas

- Res. nº 013/2015-TCE, art. 20 — parcelamento requerido no Portal do Responsável; deferimento pelo pagamento da 1ª parcela; a falta de qualquer parcela acarreta o vencimento antecipado do saldo; art. 21 — certidão de quitação ao fim do parcelamento.
- Regimento Interno, art. 337, §§ 1º e 2º — valor mínimo e número máximo de parcelas.

## 4. Definições e siglas

- **Parcelamento em curso**: parcelamento ativo com parcelas a vencer.
- **Inadimplência**: falta de pagamento de parcela — vencimento antecipado do saldo e execução forçada.

## 5. Responsabilidades

- **Servidor da CCD**: receber pendências, atualizar marcadores, emitir certidões e despachos, tratar inadimplência.
- **Relator**: decidir sobre arquivamento e providências pós-quitação.

## 6. Recursos e sistemas

Área Restrita (aba de pendências, marcadores); alerta de "parcelamento cancelado" no módulo CCD da webapp.

## 7. Descrição das atividades

1. Receber no início do mês (primeiros 5 dias úteis) os pagamentos através da aba de pendências.
2. Verificar parcelamentos iniciados no mês corrente e colocar no marcador **"Parcelamento em Curso"**.
3. Verificar os processos com pagamento integral e providenciar: despacho ao relator com sugestão de arquivamento, ou outras providências para outras possíveis dívidas e/ou responsáveis (certidão de quitação — art. 21).
4. No marcador **"Parcelamento em Curso"**: analisar se há débitos inadimplentes há mais de 2 meses e mover para **"Parcelamento Inadimplentes"**.
5. No marcador **"Parcelamento Inadimplentes"**: para os inadimplentes há mais de 2 meses, conforme o caso:
   1. Abrir [processo de execução](instaurar-execucao) (se já autorizado) ou enviar ao relator;
   2. Enviar para [protesto](protesto) em cartório, se possível;
   3. Verificar vínculo para [desconto em folha](desconto-em-folha).
6. Gerenciar parcelamentos cancelados por inadimplência; havendo novo pedido do responsável, seguir o [POP-CCD-010 — Reabertura de parcelamento](reabertura-parcelamento).

## 8. Registros

- Marcadores "Parcelamento em Curso"/"Parcelamento Inadimplentes" atualizados.
- Certidões de quitação e despachos ao relator.
- Situação do parcelamento no sistema (`Exe_Parcelamento`).

## 9. Pontos de controle e exceções

- O período de cumprimento do parcelamento **suspende a prescrição** da pretensão executória — considerar ao avaliar "está perto de prescrever?".
- O pagamento aparece na aba de pendências, não necessariamente refletido de imediato na situação da dívida.

## 10. Histórico de revisões

| Versão | Data | Alteração |
|---|---|---|
| 1.0 | 20/08/2026 | Versão inicial — conversão ao formato POP (ISO 10013:2021). |
